"""Port of skills/review-loop/tests/software-profile-contract-tests.ps1."""

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
    workflow_path = root / "references" / "WORKFLOW.md"
    metadata_path = root / "agents" / "openai.yaml"
    profile_path = root / "references" / "profiles" / "software.md"
    generic_path = root / "references" / "profiles" / "generic.md"
    finding_path = root / "references" / "finding-schema.md"
    evidence_path = root / "references" / "evidence-protocol.md"
    stopping_path = root / "references" / "stopping-rules.md"
    roles_path = root / "references" / "subagent-protocol.md"

    for label, path in (
        ("Skill", skill_path),
        ("Agent metadata", metadata_path),
        ("Software Profile", profile_path),
        ("Generic Profile", generic_path),
        ("Finding Schema", finding_path),
        ("Evidence Protocol", evidence_path),
        ("Stopping Rules", stopping_path),
        ("Role Protocol", roles_path),
    ):
        c.require_file(root, path.relative_to(root).as_posix(), label)

    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    workflow = workflow_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    profile = profile_path.read_text(encoding="utf-8", errors="replace")
    generic = generic_path.read_text(encoding="utf-8", errors="replace")
    finding = finding_path.read_text(encoding="utf-8", errors="replace")
    evidence = evidence_path.read_text(encoding="utf-8", errors="replace")
    stopping = stopping_path.read_text(encoding="utf-8", errors="replace")
    roles = roles_path.read_text(encoding="utf-8", errors="replace")

    c.require_match("TC-SW-001 profile link", skill, r"(?im)\[software\.md\]\(references/profiles/software\.md\)")
    c.require_match("TC-SW-001 profile heading", profile, r"(?im)^# Software Profile$")
    c.require_match("TC-SW-001 implicit invocation", metadata, r"(?im)^\s*allow_implicit_invocation:\s*true\s*$")
    c.require_match("TC-SW-001 generic preserved", generic, r"(?im)^# Generic Profile$")
    c.require_no_match("TC-SW-001 generic remains empty", generic, r"(?i)code-review|Standards findings|Spec findings")

    c.require_match("TC-SW-002 review axes", profile, r"(?im)^## Review axes$")
    c.require_match("TC-SW-002 evidence requirements", profile, r"(?im)^## Evidence requirements$")
    c.require_match("TC-SW-002 specialist reviewer", profile, r"(?im)^## Specialist reviewer: `code-review`$")
    c.require_match("TC-SW-002 severity guidance", profile, r"(?im)^## Severity guidance$")
    c.require_match("TC-SW-002 acceptance conditions", profile, r"(?im)^## Acceptance conditions$")
    c.require_match("TC-SW-002 failure cases", profile, r"(?im)^## Artifact-specific failure cases$")
    c.require_match("TC-SW-002 standards axis", profile, r"(?is)\*\*Standards\*\*.*code-review")
    c.require_match("TC-SW-002 spec axis", profile, r"(?is)\*\*Spec fidelity\*\*.*code-review")
    c.require_match("TC-SW-002 behavioral axis", profile, r"(?i)\*\*Behavioral correctness\*\*")
    c.require_match("TC-SW-002 safety axis", profile, r"(?i)\*\*Operational safety\*\*")
    c.require_match("TC-SW-002 severity values", profile, r"(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*")

    c.require_match("TC-SW-003 specialist evidence", profile, r"(?i)code-review.*findings.*review.*evidence")
    c.require_match("TC-SW-003 generic schema", profile, r"(?i)generic finding schema|Finding Schema")
    c.require_match("TC-SW-003 stable IDs", profile, r"(?i)stable.*F-###|stable.*Finding ID")
    c.require_match("TC-SW-003 dispositions", profile, r"(?is)confirmed.*rejected.*duplicate.*out-of-scope")
    c.require_match("TC-SW-003 evidence class", evidence, r"(?i)`review`")
    c.require_match("TC-SW-003 core flow", workflow, r"(?is)code-review.*Standards.*Spec.*findings.*generic lifecycle")

    c.require_match("TC-SW-004 specialist boundary", profile, r"(?is)code-review.*never.*Program.*acceptance verdict")
    c.require_match("TC-SW-004 Core ownership", profile, r"(?is)final `PASS`, `FAIL`, or `BLOCKED`.*project-review\s+Core")
    c.require_match("TC-SW-004 Core ownership in Workflow", workflow, r"(?is)code-review.*never issues.*final.*project-review.{0,5}Core owns")
    c.require_match("TC-SW-004 generic verdicts preserved", stopping, r"(?i)`PASS`.*`FAIL`.*`BLOCKED`")
    c.require_match("TC-SW-004 read-only specialist boundary", roles, r"(?i)Critic.*read-only|Evaluator.*read-only")

    c.require_match("TC-SW-005 bounded repair", profile, r"(?is)confirmed.*blocking finding.*resolved|bounded repair")
    c.require_match("TC-SW-005 scope stop", profile, r"(?i)scope|architecture.*decision|multiple new implementation tickets")
    c.require_match("TC-SW-005 generic stop", workflow, r"(?i)Stop scope expansion")
    c.require_match("TC-SW-005 no lifecycle duplication", profile, r"(?i)does not replace.*state machine|generic lifecycle.*stopping rules")

    return c.assertions, c.failures


class SoftwareProfileContractTest(unittest.TestCase):
    def test_software_profile_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"software-profile contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
