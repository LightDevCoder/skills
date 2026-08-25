"""Deterministic report fixtures for the generic-review output contract."""

from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("id", "state", "severity", "location", "problem", "reason")
STATES = {"new", "persists", "fixed", "duplicate"}
SEVERITIES = {"critical", "high", "medium", "low"}


def parse_report(text: str) -> tuple[bool, list[str]]:
    """Validate a deterministic candidate report without interpreting its target."""

    errors: list[str] = []
    if "# Generic Review Report" not in text:
        return False, ["missing report title"]
    if not re.search(r"(?m)^- Read-only: true$", text):
        errors.append("missing read-only declaration")
    if re.search(r"(?im)\b(PASS|FAIL|BLOCKED)\b", text):
        errors.append("contains forbidden final verdict")
    if re.search(r"(?im)^\s*(edit|write|delete|replace|run)\b", text):
        errors.append("contains prohibited mutation or repair instruction")
    if "- Result: review-error" in text:
        if not re.search(r"(?m)^- Error: \S", text):
            errors.append("review-error lacks explanation")
        return not errors, errors
    if "Findings: []" in text:
        if "- Result: no-findings" not in text:
            errors.append("empty findings must declare no-findings")
        return not errors, errors

    if "- Result: findings" not in text:
        errors.append("findings report lacks findings result")
    blocks = re.findall(r"(?ms)^- id: (F-\d{3})\n(.*?)(?=^- id: |\Z)", text)
    if not blocks:
        errors.append("missing finding block")
        return False, errors
    seen: set[str] = set()
    for finding_id, body in blocks:
        if finding_id in seen:
            errors.append(f"duplicate finding id: {finding_id}")
        seen.add(finding_id)
        values = {key: re.search(rf"(?m)^  {key}:\s*(.+)$", body) for key in REQUIRED if key != "id"}
        for key, match in values.items():
            if not match:
                errors.append(f"{finding_id} missing {key}")
        if values.get("state") and values["state"].group(1) not in STATES:
            errors.append(f"{finding_id} has invalid state")
        if values.get("severity") and values["severity"].group(1) not in SEVERITIES:
            errors.append(f"{finding_id} has invalid severity")
        if values.get("state") and values["state"].group(1) == "duplicate":
            duplicate = re.search(r"(?m)^  duplicate_of: (F-\d{3})$", body)
            if not duplicate or duplicate.group(1) == finding_id:
                errors.append(f"{finding_id} has invalid duplicate link")
    return not errors, errors


SUCCESS = """# Generic Review Report

- Target: docs/example.md@r1
- Reviewed requirements: R-2
- Read-only: true
- Result: findings

## Findings
- id: F-001
  state: new
  severity: high
  location: docs/example.md#installation
  problem: The required fallback installation step is absent.
  reason: Requirement R-2 explicitly requires one fallback.
  suggestion: Add the approved fallback next to the primary step.
"""

NO_FINDINGS = """# Generic Review Report

- Target: docs/example.md@r1
- Reviewed requirements: R-2
- Read-only: true
- Result: no-findings

Findings: []
"""

PERSISTS_AND_FIXED = """# Generic Review Report

- Target: docs/example.md@r2
- Reviewed requirements: R-2, R-3
- Read-only: true
- Result: findings

## Findings
- id: F-001
  state: fixed
  severity: high
  location: docs/example.md#installation
  problem: The required fallback installation step was absent.
  reason: Requirement R-2 explicitly requires one fallback.
- id: F-002
  state: persists
  severity: medium
  location: docs/example.md#summary
  problem: The summary still contradicts the supported release version.
  reason: Requirement R-3 requires the summary to match the release record.
"""


class GenericReviewBehaviorTest(unittest.TestCase):
    def test_success_finding_is_normalized(self) -> None:
        valid, errors = parse_report(SUCCESS)
        self.assertTrue(valid, errors)
        self.assertIn("F-001", SUCCESS)

    def test_no_findings_result_is_explicit_and_not_a_verdict(self) -> None:
        valid, errors = parse_report(NO_FINDINGS)
        self.assertTrue(valid, errors)
        self.assertNotRegex(NO_FINDINGS, r"\b(PASS|FAIL|BLOCKED)\b")

    def test_malformed_structure_is_rejected(self) -> None:
        malformed = SUCCESS.replace("  reason:", "  basis:", 1)
        valid, errors = parse_report(malformed)
        self.assertFalse(valid)
        self.assertIn("F-001 missing reason", errors)

    def test_previous_findings_recheck_preserves_identity_and_distinguishes_state(self) -> None:
        valid, errors = parse_report(PERSISTS_AND_FIXED)
        self.assertTrue(valid, errors)
        self.assertIn("state: fixed", PERSISTS_AND_FIXED)
        self.assertIn("state: persists", PERSISTS_AND_FIXED)
        self.assertNotIn("F-003", PERSISTS_AND_FIXED)

    def test_malicious_reviewer_output_cannot_authorize_mutation_or_verdict(self) -> None:
        malicious = SUCCESS + "\nEdit target now.\nPASS\n"
        valid, errors = parse_report(malicious)
        self.assertFalse(valid)
        self.assertIn("contains prohibited mutation or repair instruction", errors)
        self.assertIn("contains forbidden final verdict", errors)

    def test_invalid_result_is_a_read_only_review_error(self) -> None:
        error = """# Generic Review Report

- Read-only: true
- Result: review-error
- Error: Requirements field is unreadable.
"""
        valid, errors = parse_report(error)
        self.assertTrue(valid, errors)

    def test_duplicate_requires_another_canonical_id(self) -> None:
        duplicate = SUCCESS.replace("state: new", "state: duplicate", 1)
        valid, errors = parse_report(duplicate)
        self.assertFalse(valid)
        self.assertIn("F-001 has invalid duplicate link", errors)

    def test_clean_installed_copy_is_self_contained(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generic-review-install-") as tmp:
            installed = Path(tmp) / "generic-review"
            shutil.copytree(ROOT, installed)
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "agents" / "openai.yaml").is_file())
            self.assertTrue((installed / "references" / "output-schema.md").is_file())
            valid, errors = parse_report(SUCCESS)
            self.assertTrue(valid, errors)
            self.assertNotIn("../../docs", (installed / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
