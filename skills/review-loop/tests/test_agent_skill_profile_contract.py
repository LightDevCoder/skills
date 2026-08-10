"""Port of skills/review-loop/tests/agent-skill-profile-contract-tests.ps1."""

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
    profile_path = root / "references" / "profiles" / "agent-skill.md"
    behavior_path = root / "tests" / "test_agent_skill_profile_behavior.py"
    generic_path = root / "references" / "profiles" / "generic.md"
    finding_path = root / "references" / "finding-schema.md"
    evidence_path = root / "references" / "evidence-protocol.md"
    stopping_path = root / "references" / "stopping-rules.md"
    roles_path = root / "references" / "subagent-protocol.md"

    for label, path in (
        ("Skill", skill_path),
        ("Agent metadata", metadata_path),
        ("Agent-Skill Profile", profile_path),
        ("Agent-Skill behavior tests", behavior_path),
        ("Generic Profile", generic_path),
        ("Finding Schema", finding_path),
        ("Evidence Protocol", evidence_path),
        ("Stopping Rules", stopping_path),
        ("Role Protocol", roles_path),
    ):
        c.require_file(root, path.relative_to(root).as_posix(), label)

    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    profile = profile_path.read_text(encoding="utf-8", errors="replace")
    behavior = behavior_path.read_text(encoding="utf-8", errors="replace")
    generic = generic_path.read_text(encoding="utf-8", errors="replace")
    finding = finding_path.read_text(encoding="utf-8", errors="replace")
    evidence = evidence_path.read_text(encoding="utf-8", errors="replace")
    stopping = stopping_path.read_text(encoding="utf-8", errors="replace")
    roles = roles_path.read_text(encoding="utf-8", errors="replace")

    c.require_match("TC-AS-001 profile link", skill, r"(?im)\[agent-skill\.md\]\(references/profiles/agent-skill\.md\)")
    c.require_match("TC-AS-001 profile heading", profile, r"(?im)^# Agent-Skill Profile$")
    c.require_match("TC-AS-001 implicit invocation", metadata, r"(?im)^\s*allow_implicit_invocation:\s*true\s*$")
    c.require_match("TC-AS-001 generic preserved", generic, r"(?im)^# Generic Profile$")
    c.require_no_match("TC-AS-001 generic remains empty", generic, r"(?i)agent-skill|installation|invocation|composition")

    c.require_match("TC-AS-002 review axes", profile, r"(?im)^## Review axes$")
    for axis in ("Package structure", "Installation", "Invocation", "Reusable behavior", "Interaction", "Executable artifact"):
        c.require_match(f"TC-AS-002 axis {axis}", profile, rf"(?i)\*\*{axis}")
    c.require_match("TC-AS-002 severity guidance", profile, r"(?im)^## Severity guidance$")
    c.require_match("TC-AS-002 acceptance conditions", profile, r"(?im)^## Acceptance conditions$")
    c.require_match("TC-AS-002 failure cases", profile, r"(?im)^## Artifact-specific failure cases$")
    c.require_match("TC-AS-002 severity values", profile, r"(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*")

    c.require_match("TC-AS-003 evidence requirements", profile, r"(?im)^## Evidence requirements$")
    for term in ("structural", "fresh-install|clean-copy installation", "discovery", "success", "boundary", "failure", "missing-dependency", "invocation", "interaction", "assertion-bearing", "negative|adversarial", "code-review", "fresh independent Evaluator"):
        c.require_match(f"TC-AS-003 evidence {term}", profile, rf"(?i){term}")
    c.require_match("TC-AS-003 protocol labels retained", evidence, r"(?is)source.*structural.*behavioral.*installation.*invocation.*review")
    c.require_no_match("TC-AS-003 unsupported primary labels absent", profile, r"(?im)(?:Evidence label|Label):\s*(?:render|visual)\b")
    c.require_no_match("TC-AS-003 behavior runner unsupported labels absent", behavior, r"(?im)(?:Evidence label|Label):\s*(?:render|visual)\b")

    c.require_match("TC-AS-004 focused tests", profile, r"(?i)focused automated tests")
    c.require_match("TC-AS-004 negative tests", profile, r"(?i)negative or adversarial")
    c.require_match("TC-AS-004 code review reports", profile, r"(?is)code-review.*Standards.*Spec")
    c.require_match("TC-AS-004 specialist read-only", profile, r"(?is)read-only.*never edits|never edits.*never issues")
    c.require_match("TC-AS-004 specialist evidence class", profile, r"(?i)`review` evidence")

    c.require_match("TC-AS-005 generic schema handoff", profile, r"(?i)generic finding schema|finding identity")
    c.require_match("TC-AS-005 generic dispositions", profile, r"(?is)confirmed.*rejected.*duplicate.*out-of-scope")
    c.require_match("TC-AS-005 Core verdict ownership", profile, r"(?is)generic Core.*final verdict|Core.*owns.*final.*`PASS`.*`FAIL`.*`BLOCKED`")
    c.require_match("TC-AS-005 Core lifecycle delegation", profile, r"(?is)does not replace.*finding.*repair.*state.*independence.*final verdict")
    c.require_no_match("TC-AS-005 no duplicate state section", profile, r"(?im)^## (State|Repair rounds|Finding Registry|Stopping Rules)$")
    c.require_no_match("TC-AS-005 no duplicate lifecycle transitions", profile, r"(?i)INIT\s*->\s*READY|READY\s*->\s*CRITIC")
    c.require_match("TC-AS-005 canonical finding schema unchanged", finding, r"(?im)^# Finding Registry$")
    c.require_match("TC-AS-005 canonical stop outcomes unchanged", stopping, r"(?i)`PASS`.*`FAIL`.*`BLOCKED`")
    c.require_match("TC-AS-005 read-only role boundary", roles, r"(?i)Critic.*read-only|Evaluator.*read-only")

    return c.assertions, c.failures


class AgentSkillProfileContractTest(unittest.TestCase):
    def test_agent_skill_profile_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"agent-skill-profile contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
