"""Port of skills/review-loop/tests/generic-profile-contract-tests.ps1."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_path = root / "SKILL.md"
    metadata_path = root / "agents" / "openai.yaml"
    profile_path = root / "references" / "profiles" / "generic.md"
    charter_path = root / "references" / "acceptance-charter.md"
    evidence_path = root / "references" / "evidence-protocol.md"
    finding_path = root / "references" / "finding-schema.md"
    stopping_path = root / "references" / "stopping-rules.md"
    roles_path = root / "references" / "subagent-protocol.md"

    for label, path in (
        ("Agent metadata", metadata_path),
        ("Generic Profile", profile_path),
        ("Acceptance Charter", charter_path),
        ("Evidence Protocol", evidence_path),
        ("Finding Schema", finding_path),
        ("Stopping Rules", stopping_path),
        ("Role Protocol", roles_path),
    ):
        c.require_file(root, path.relative_to(root).as_posix(), label)

    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    profile = profile_path.read_text(encoding="utf-8", errors="replace")
    charter = charter_path.read_text(encoding="utf-8", errors="replace")
    evidence = evidence_path.read_text(encoding="utf-8", errors="replace")
    findings = finding_path.read_text(encoding="utf-8", errors="replace")
    stopping = stopping_path.read_text(encoding="utf-8", errors="replace")
    roles = roles_path.read_text(encoding="utf-8", errors="replace")

    c.require_match("TC-GEN-001 generic profile", skill, r"references/profiles/generic\.md")
    c.require_match("TC-GEN-001 generic profile", profile, r"(?im)^# Generic Profile$")
    c.require_no_match("TC-GEN-001 generic profile", profile, r"(?i)software|manuscript|agent-skill|specification|code-review")

    c.require_match("TC-GEN-002 public modes", skill, r"(?im)^- `init`:")
    c.require_match("TC-GEN-002 public modes", skill, r"(?im)^- `review`:")
    c.require_match("TC-GEN-002 public modes", skill, r"(?im)^- `resume`:")
    c.require_match("TC-GEN-002 invocation", skill, r"(?i)model-invoked")
    c.require_match("TC-GEN-002 invocation", skill, r"(?i)manually invoked")
    c.require_match("TC-GEN-002 invocation metadata", metadata, r"(?im)^\s*allow_implicit_invocation:\s*true\s*$")

    c.require_match("TC-GEN-003 baseline", charter, r"(?im)^## Acceptance baseline$")
    c.require_match("TC-GEN-003 profile", charter, r"(?im)^## Review Profile$")
    c.require_match("TC-GEN-003 state records", skill, r"(?m)^\|-- findings\.md$")

    c.require_match("TC-GEN-004 stable finding identity", findings, r"(?i)stable.*Finding ID|Finding ID.*stable")
    c.require_match("TC-GEN-004 stable finding identity", findings, r"(?i)must not be reused")
    c.require_match("TC-GEN-004 finding registry", findings, r"(?im)^# Finding Registry$")

    c.require_match("TC-GEN-005 rejected findings", findings, r"`rejected`")
    c.require_match("TC-GEN-005 rejected findings", findings, r"(?i)Resolution evidence")

    c.require_match("TC-GEN-006 bounded repair", skill, r"(?i)confirmed.*in-scope.*bounded|in-scope.*confirmed.*bounded")
    c.require_match("TC-GEN-006 Producer ownership", roles, r"(?is)Producer.*only.*modif")
    c.require_match("TC-GEN-006 read-only reviewers", roles, r"(?i)Critic.*read-only")
    c.require_match("TC-GEN-006 read-only reviewers", roles, r"(?i)Evaluator.*read-only")

    c.require_match("TC-GEN-007 missing acceptance source", skill, r"(?i)missing acceptance source.*BLOCKED|BLOCKED.*missing acceptance source")

    c.require_match("TC-GEN-008 missing independent context", roles, r"(?i)independence: unavailable")
    c.require_match("TC-GEN-008 missing independent context", roles, r"(?i)return `BLOCKED`")

    c.require_match("TC-GEN-009 maximum rounds", stopping, r"(?i)maximum round.*BLOCKED|BLOCKED.*maximum round")

    c.require_match("TC-GEN-010 verdicts", stopping, r"`PASS`")
    c.require_match("TC-GEN-010 verdicts", stopping, r"`FAIL`")
    c.require_match("TC-GEN-010 verdicts", stopping, r"`BLOCKED`")

    c.require_match("TC-GEN-011 resume", skill, r"(?im)^## `resume` workflow$")
    c.require_match("TC-GEN-011 resume", skill, r"(?i)append rather than rewrite")

    c.require_match("TC-GEN-012 evidence labels", evidence, r"(?im)^- Evidence label:")
    c.require_match("TC-GEN-012 evidence labels", evidence, r"`structural`")
    c.require_match("TC-GEN-012 evidence labels", evidence, r"`behavioral`")
    c.require_match("TC-GEN-012 evidence labels", evidence, r"`runtime`")
    c.require_match("TC-GEN-012 evidence labels", evidence, r"`review`")

    return c.assertions, c.failures


class GenericProfileContractTest(unittest.TestCase):
    def test_generic_profile_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertFalse(failures, f"generic-profile contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
