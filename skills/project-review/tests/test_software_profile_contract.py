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

    # TC-SW-006..009: three-field software baseline contract (breaks the old
    # two-value `<base> <candidate>` window rule; consumers fail closed on it).
    c.require_match("TC-SW-006 baseline record section", profile, r"(?im)^### Durable software baseline record$")
    c.require_match("TC-SW-006 fixed point grammar", profile,
                    r"(?is)`Fixed point`.*exactly one full 40-character commit SHA")
    c.require_match("TC-SW-006 fixed point is review base", profile,
                    r"(?is)`Fixed point`.*immutable base.*review base")
    c.require_match("TC-SW-006 effective-commit freeze rule", profile,
                    r"(?i)freeze the actual effective commit.*never the\s+mutable")
    c.require_no_match("TC-SW-006 two-value grammar removed", profile, r"<base> <candidate>")
    c.require_no_match("TC-SW-006 touched-window rule removed", profile,
                       r"paths the recorded window touched")
    c.require_match("TC-SW-006 singleton fields rule", profile,
                    r"(?is)Each field is a singleton field.*exactly\s+once"
                    r".*duplicated \(even identically\).*fail\s+closed")

    c.require_match("TC-SW-007 scope field grammar", profile,
                    r"(?is)`Implementation scope`.*repo-relative literal")
    c.require_match("TC-SW-007 scope projects In scope", profile,
                    r"(?is)machine-readable projection of this Charter's approved software\s+`In scope`")
    c.require_match("TC-SW-007 scope never inferred from changed paths", profile,
                    r"(?is)Never derive the scope from changed paths")
    c.require_match("TC-SW-007 unverifiable target blocked", profile,
                    r"(?is)cannot be\s+established reliably, return `BLOCKED`")
    c.require_match("TC-SW-007 whole-field rejection", profile, r"(?i)rejects the WHOLE field")
    c.require_match("TC-SW-007 no implicit readme exception", profile,
                    r"(?is)implicit documentation exceptions:\s*with scope `\.?`\s*"
                    r"a README change counts;\s*with scope `src/?`\s*a root README stays outside")
    c.require_match("TC-SW-008 final revision on verdict", profile,
                    r"(?is)`Reviewed implementation revision`.*\.project-review/verdict\.md")
    c.require_match("TC-SW-008 charter notes candidate lives on verdict",
                    Path(root / "references" / "acceptance-charter.md").read_text(encoding="utf-8"),
                    r"(?i)deliberately NOT frozen here")
    c.require_match("TC-SW-008 repair moves candidate C1 to C2", profile,
                    r"(?is)may move\s+the candidate from C1 to C2")
    c.require_match("TC-SW-008 pass requires clean in-scope tree", profile,
                    r"(?i)no uncommitted tracked, untracked, or ignored changes")
    c.require_match("TC-SW-008 ignored files count as scope drift", profile,
                    r"(?i)Git ignore rules\s+hide files from `git status`, not from the reviewed component")
    c.require_match("TC-SW-008 lifecycle rules section", profile,
                    r"(?im)^### Baseline lifecycle rules$")
    c.require_match("TC-SW-009 review metadata kept out of scope", profile,
                    r"(?is)Keep project-review's own mutable records out of the frozen target")
    c.require_match("TC-SW-009 metadata directories named", profile,
                    r"(?is)`\.project-review/`, `\.review-loop/`")
    c.require_match("TC-SW-009 whole-repo born-stale warning", profile,
                    r"(?is)whole-repo scope `\.`\s*includes them")
    c.require_match("TC-WF-008 init freezes base plus scope", workflow,
                    r"(?is)`- Fixed point:`.*one full commit SHA.*`- Implementation scope:`")
    c.require_match("TC-WF-008 init does not freeze final candidate", workflow,
                    r"(?is)do not freeze\s+the\s+final\s+implementation\s+candidate\s+at\s+`init`")
    c.require_match("TC-WF-008 verdict records evaluated revision", workflow,
                    r"(?i)`- Reviewed implementation revision: <full Git commit SHA>`")
    c.require_match("TC-EV-008 closeout carries revision binding", evidence,
                    r"(?i)Reviewed implementation revision")

    return c.assertions, c.failures


class SoftwareProfileContractTest(unittest.TestCase):
    def test_software_profile_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"software-profile contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
