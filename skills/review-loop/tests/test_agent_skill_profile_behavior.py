"""Port of skills/review-loop/tests/agent-skill-profile-behavior-tests.ps1."""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_helpers import Checks  # noqa: E402
from review_protocol_helpers import (  # noqa: E402
    add_review_finding,
    get_confirmed_review_finding_ids,
    get_review_state,
    new_review_case,
    new_review_next_round,
    new_review_round,
    set_review_state,
    write_review_repair_evidence,
)


class AgentSkillScenario:
    def __init__(self, case_root: Path) -> None:
        self.case_root = case_root

    def state(self):
        return get_review_state(self.case_root)

    def set_state(self, status: str, round_no: int, next_action: str, *, charter_revision: str = "", last_completed_action: str = "protocol transition", blocker: str = "none") -> None:
        current = self.state()
        if not charter_revision:
            charter_revision = current.charter_revision
        set_review_state(self.case_root, status, round_no, next_action, "agent-skill", charter_revision, "", last_completed_action, blocker)

    def initialize(self, acceptance_source: Path, invocation_type: str = "model-invoked") -> None:
        if not acceptance_source.is_file():
            self.set_state("BLOCKED", 0, "record missing acceptance source", charter_revision="agent-skill-fixture-1", last_completed_action="agent-skill source check", blocker="missing approved package acceptance source")
            return
        package_root = self.case_root / "package"
        (package_root / "agents").mkdir(parents=True, exist_ok=True)
        (package_root / "SKILL.md").write_text("\n".join([
            "---",
            "name: fixture-skill",
            "description: Reusable fixture method for Agent-Skill Profile acceptance.",
            "---",
            "# Fixture Skill",
            "Use this package only for the frozen fixture acceptance target.",
        ]) + "\n", encoding="utf-8")
        (package_root / "agents" / "openai.yaml").write_text("\n".join([
            "interface:",
            '  display_name: "Fixture Skill"',
            '  short_description: "Reusable fixture method"',
            '  default_prompt: "Use the fixture skill for the approved case."',
            "policy:",
            "  allow_implicit_invocation: true",
        ]) + "\n", encoding="utf-8")
        charter = self.case_root / ".review-loop" / "charter.md"
        charter.parent.mkdir(parents=True, exist_ok=True)
        charter.write_text("\n".join([
            "# Acceptance Charter",
            "- Approval state: approved",
            "- Profile: agent-skill",
            "- Charter revision: approved-agent-skill-r2",
            "- Package revision: fixture-skill-1",
            f"- Invocation type: {invocation_type}",
            "- Discovery target: clean installed package",
            "- Acceptance source: acceptance.md",
        ]) + "\n", encoding="utf-8")
        set_review_state(self.case_root, "READY", 0, "collect Producer evidence", "agent-skill", "approved-agent-skill-r2", "", "agent-skill Charter freeze")

    def start_round(self, *, executable: bool = True, executable_evidence: bool = True, dependency_available: bool = True, invocation_type: str = "model-invoked", trigger_observed: bool = True) -> Path:
        evidence = [
            "Scope: frozen installable Agent Skill package and acceptance source",
            "Profile: agent-skill",
            "Package revision: fixture-skill-1",
            "Structure: SKILL.md, agents/openai.yaml, and declared references inspected",
            "Clean install: copied to an empty install root and discovered by metadata",
            "Evidence label: structural",
            "Evidence label: installation",
            f"Invocation: {invocation_type}; trigger observed: {trigger_observed}; downstream user-invoked Skills are recommended, not executed",
            "Evidence label: invocation",
            "Success path: fixture method returns expected reusable output",
            "Boundary path: non-trigger request returns no-op recommendation without execution",
            "Evidence label: behavioral",
            "Interaction seam: explicit input, output, authority owner, and stop condition preserved",
            "Dependency: fixture host requirement checked",
            "Evidence label: runtime",
        ]
        if executable:
            if executable_evidence:
                evidence.append("Executable script: focused assertion-bearing tests (12 assertions), negative/adversarial fixture, and code-review Standards/Spec reports retained")
                evidence.append("Evidence label: review")
            else:
                evidence.append("Executable script: focused or adversarial/code-review evidence missing")
                evidence.append("Evidence label: structural")
        else:
            evidence.append("Executable axis: not applicable; package has no scripts or executable resources")
            evidence.append("Evidence label: structural")
        if not dependency_available:
            evidence.append("Missing dependency: required host capability unavailable; smallest unblock is to install the declared dependency")
        round_path = new_review_round(self.case_root, "agent-skill", "request read-only package and invocation specialists", evidence)
        if executable and executable_evidence:
            (round_path / "focused-script-tests.md").write_text("\n".join([
                "# Focused executable Skill tests",
                "- Assertions: 12",
                "- Success, boundary, and failure scenarios: PASS",
                "- Negative/adversarial fixture: PASS",
                "- Evidence label: behavioral",
            ]) + "\n", encoding="utf-8")
            (round_path / "code-review-standards.md").write_text("\n".join([
                "# code-review Standards report",
                "- Fixed package revision: fixture-skill-1",
                "- Axis: Standards",
                "- Evidence label: review",
                "- Specialist verdict: PASS",
            ]) + "\n", encoding="utf-8")
            (round_path / "code-review-spec.md").write_text("\n".join([
                "# code-review Spec report",
                "- Fixed package revision: fixture-skill-1",
                "- Axis: Spec",
                "- Evidence label: review",
                "- Specialist verdict: PASS",
            ]) + "\n", encoding="utf-8")
        return round_path

    def write_specialist_report(self, *, disposition: str = "rejected", finding_id: str = "F-001", severity: str = "High", axis: str = "invocation contract", source_reference: str = "AS-AXIS-001", specialist_verdict: str = "PASS") -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("Agent-Skill specialist report requires CRITIC state")
        round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        (round_path / "agent-skill-specialist.md").write_text("\n".join([
            "# Agent-Skill Specialist Report",
            "- Package: package/SKILL.md",
            "- Profile: agent-skill",
            f"- Axis: {axis}",
            f"- Source finding reference: {source_reference}",
            f"- Stable candidate ID: {finding_id}",
            f"- Severity: {severity}",
            f"- Disposition candidate: {disposition}",
            f"- Specialist verdict: {specialist_verdict}",
            "- Evidence: clean installation, trigger boundary, method fixture, and interaction record",
            "- Evidence label: review",
        ]) + "\n", encoding="utf-8")

    def ingest_finding(self, *, disposition: str = "rejected", finding_id: str = "F-001", source_reference: str = "AS-AXIS-001") -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("Agent-Skill finding ingestion requires CRITIC state")
        round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
        report = (round_path / "agent-skill-specialist.md").read_text(encoding="utf-8")
        if f"Stable candidate ID: {finding_id}" not in report or "Evidence label: review" not in report:
            raise ValueError("specialist report lost stable ID or evidence class")
        add_review_finding(self.case_root, finding_id, "agent-skill specialist", "agent-skill package", source_reference, "High", disposition, "review")
        if disposition == "confirmed":
            self.set_state("REPAIR", state.round, "direct bounded package repair to Producer", last_completed_action="validated Agent-Skill candidate finding")
        else:
            self.set_state("EVALUATE", state.round, "request fresh Evaluator", last_completed_action="rejected Agent-Skill candidate")

    def apply_repair(self, in_scope: bool) -> None:
        state = self.state()
        if state.status != "REPAIR":
            raise ValueError("Agent-Skill repair requires REPAIR state")
        if not in_scope:
            self.set_state("FAIL", state.round, "scope-changing package repair rejected", last_completed_action="rejected out-of-scope Producer repair")
            return
        ids = get_confirmed_review_finding_ids(self.case_root)
        if not ids:
            raise ValueError("Agent-Skill repair requires a confirmed finding")
        write_review_repair_evidence(self.case_root, state.round, ids, [
            "Producer repair evidence: bounded and in-scope",
            "Changed scope: existing Skill package only",
            "Validation: focused success, boundary, failure and installation scenarios",
            "Evidence label: behavioral",
            "Evidence label: installation",
        ])
        self.set_state("EVALUATE", state.round, "request fresh Evaluator", last_completed_action="bounded Agent-Skill Producer repair")

    def write_evaluator(self, outcome: str, context_identity: str, executable_outcome: str = "PASS") -> None:
        state = self.state()
        round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        producer = (round_path / "producer-evidence.md").read_text(encoding="utf-8")
        exec_label = "structural" if "Executable axis: not applicable" in producer else "review"
        (round_path / "evaluator-verdict.md").write_text("\n".join([
            f"# Evaluator Verdict - Round {state.round:02d}",
            f"Context identity: {context_identity}",
            f"Charter revision: {state.charter_revision}; Profile: agent-skill",
            f"Criterion AC-1 (package structure and discoverability): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: {outcome}",
            f"Criterion AC-2 (installation and fresh discovery): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: installation | Outcome: {outcome}",
            f"Criterion AC-3 (invocation contract and boundaries): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: invocation | Outcome: {outcome}",
            f"Criterion AC-4 (reusable behavior and method fidelity): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: {outcome}",
            f"Criterion AC-5 (interaction and composition seams): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: {outcome}",
            f"Criterion AC-6 (executable artifact quality): {executable_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: {exec_label} | Outcome: {executable_outcome}",
            "Open blocking findings: none",
            f"Outcome: {outcome}",
            f"Verdict recommendation: {outcome}",
        ]) + "\n", encoding="utf-8")

    def evaluate(self, c: Checks, *, passed: bool, independent_context: bool, dependency_available: bool = True, executable_evidence: bool = True, maximum_round: int = 3) -> None:
        state = self.state()
        if state.status != "EVALUATE":
            raise ValueError("Agent-Skill evaluation requires EVALUATE state")
        if not independent_context:
            self.write_evaluator("BLOCKED", "unavailable independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "obtain independent Evaluator context", last_completed_action="independent context check", blocker="independent context unavailable")
            return
        if not dependency_available:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "install declared host dependency", last_completed_action="dependency check", blocker="required host dependency unavailable")
            return
        if not executable_evidence:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "obtain executable focused, adversarial, and code-review evidence", last_completed_action="executable evidence check", blocker="required executable evidence unavailable")
            return
        if passed:
            registry = self.case_root / ".review-loop" / "findings.md"
            for finding_id in get_confirmed_review_finding_ids(self.case_root):
                repair = self.case_root / f".review-loop/rounds/round-{state.round:02d}/repair-evidence-{finding_id}.md"
                if not repair.is_file():
                    raise ValueError(f"Missing repair evidence for {finding_id}")
                with registry.open("a", encoding="utf-8") as fh:
                    fh.write("\n".join([
                        f"Finding {finding_id}: Status: resolved",
                        "Resolution evidence: fresh independent Evaluator",
                        f"Repair evidence: rounds/round-{state.round:02d}/repair-evidence-{finding_id}.md",
                    ]) + "\n")
            self.write_evaluator("PASS", "fresh independent read-only Evaluator", "PASS")
            verdict = self.case_root / ".review-loop" / "verdict.md"
            verdict.write_text("\n".join([
                "# Review Loop Verdict",
                "Verdict: PASS",
                "Issued by: review-loop Core",
                "Evaluator: fresh independent read-only context",
                "Specialist input: package, installation, invocation, behavior, and interaction evidence",
            ]) + "\n", encoding="utf-8")
            self.set_state("PASS", state.round, "preserve Core verdict", last_completed_action="fresh Agent-Skill Evaluator PASS")
        elif state.round < maximum_round:
            self.write_evaluator("FAIL", "fresh independent read-only Evaluator", "PASS")
            self.set_state("FAIL", state.round, "CRITIC (next round); bounded package repair remains", last_completed_action="fresh Agent-Skill Evaluator FAIL")
        else:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "repair limit reached", last_completed_action="repair limit check", blocker="maximum rounds or no permitted repair")


def assert_agent_skill_evaluator_record(c: Checks, text: str, *, overall_outcome: str, executable_outcome: str = "PASS", name: str) -> None:
    exec_label = "structural" if "Executable axis: not applicable" in text else "review"
    expected = {
        1: ("structural", overall_outcome),
        2: ("installation", overall_outcome),
        3: ("invocation", overall_outcome),
        4: ("behavioral", overall_outcome),
        5: ("behavioral", overall_outcome),
        6: (exec_label, executable_outcome),
    }
    missing = []
    for criterion, (label, outcome) in expected.items():
        line = re.search(rf"(?m)^Criterion AC-{criterion} \([^\r\n]+\): {outcome} - Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: ([a-z]+) \| Outcome: {outcome}\r?$", text)
        if not line:
            missing.append(f"AC-{criterion} missing outcome/evidence/link")
            continue
        if line.group(1) != label:
            missing.append(f"AC-{criterion} expected label {label}, observed {line.group(1)}")
    if not re.search(rf"(?m)^Outcome: {overall_outcome}\r?$", text):
        missing.append(f"overall outcome {overall_outcome} missing")
    c.check(len(missing) == 0, f"{name} (AC-1..AC-6, links, labels)")


class AgentSkillProfileBehaviorTest(unittest.TestCase):
    def test_agent_skill_profile_behavior(self) -> None:
        c = Checks()
        with tempfile.TemporaryDirectory(prefix="review-loop-agent-skill-") as tmp:
            root = Path(tmp)
            installed = root / "installed-review-loop"
            shutil.copytree(ROOT, installed)
            c.check((installed / "references/profiles/agent-skill.md").is_file(), "fresh install includes Agent-Skill Profile")
            c.check((installed / "SKILL.md").is_file(), "fresh install is discoverable through SKILL.md")

            case_root = new_review_case(root, "integration", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            acceptance = case_root / "acceptance.md"
            acceptance.write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(acceptance, "model-invoked")
            c.check(scenario.state().profile == "agent-skill" and scenario.state().charter_revision == "approved-agent-skill-r2", "init freezes Agent-Skill Profile and package revision")
            integration_round = scenario.start_round()
            c.check((integration_round / "focused-script-tests.md").is_file() and (integration_round / "code-review-standards.md").is_file() and (integration_round / "code-review-spec.md").is_file(), "executable Skill evidence retains focused tests and separate code-review axes")
            scenario.write_specialist_report(disposition="rejected", finding_id="F-001", specialist_verdict="PASS")
            c.check(scenario.state().status == "CRITIC", "specialist PASS remains evidence while Core is in CRITIC")
            scenario.ingest_finding(disposition="rejected", finding_id="F-001")
            c.check(scenario.state().status == "EVALUATE", "rejected package candidate proceeds to fresh Evaluator")
            scenario.evaluate(c, passed=True, independent_context=True)
            evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            verdict = (case_root / ".review-loop/verdict.md").read_text(encoding="utf-8")
            assert_agent_skill_evaluator_record(c, evaluator, overall_outcome="PASS", name="fresh Evaluator records Agent-Skill axes and Core owns final PASS")
            c.check(scenario.state().status == "PASS" and "Issued by: review-loop Core" in verdict, "Core verdict record is separate from specialist evidence")

            case_root = new_review_case(root, "invocation-boundary", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md", "user-invoked")
            scenario.start_round(invocation_type="user-invoked", trigger_observed=False)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-002", axis="invocation contract and boundaries", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-002")
            scenario.evaluate(c, passed=True, independent_context=True)
            boundary_producer = (case_root / ".review-loop/rounds/round-01/producer-evidence.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "PASS" and "non-trigger request returns no-op recommendation" in boundary_producer and "recommended, not executed" in boundary_producer, "non-trigger boundary recommends without invoking another user Skill")

            case_root = new_review_case(root, "missing-source", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            scenario.initialize(case_root / "missing-acceptance.md")
            c.check(scenario.state().status == "BLOCKED" and "missing approved package acceptance source" in scenario.state().raw, "missing acceptance source blocks Agent-Skill init")

            case_root = new_review_case(root, "missing-dependency", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(dependency_available=False)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-003")
            scenario.ingest_finding(disposition="rejected", finding_id="F-003")
            scenario.evaluate(c, passed=True, independent_context=True, dependency_available=False)
            dependency_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_agent_skill_evaluator_record(c, dependency_evaluator, overall_outcome="BLOCKED", executable_outcome="BLOCKED", name="missing dependency Evaluator records all axes and BLOCKED")
            c.check(scenario.state().status == "BLOCKED" and "required host dependency unavailable" in scenario.state().raw, "missing dependency returns Core BLOCKED with unblock")

            case_root = new_review_case(root, "executable-evidence-block", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(executable_evidence=False)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-004")
            scenario.ingest_finding(disposition="rejected", finding_id="F-004")
            scenario.evaluate(c, passed=True, independent_context=True, dependency_available=True, executable_evidence=False)
            exec_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_agent_skill_evaluator_record(c, exec_evaluator, overall_outcome="BLOCKED", executable_outcome="BLOCKED", name="missing executable evidence blocks with valid labels")
            c.check(scenario.state().status == "BLOCKED" and "executable evidence unavailable" in scenario.state().raw, "missing executable evidence returns Core BLOCKED")

            case_root = new_review_case(root, "bounded-repair", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-005", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-005")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True)
            failed_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_agent_skill_evaluator_record(c, failed_evaluator, overall_outcome="FAIL", name="failed Agent-Skill round records all axes and valid labels")
            revision = scenario.state().charter_revision
            c.check(scenario.state().status == "FAIL" and revision == "approved-agent-skill-r2", "failed round retains frozen package revision and bounded next action")
            new_review_next_round(case_root, "agent-skill", "recheck stable Agent-Skill finding", ["Scope: same frozen Skill package; next round", "Evidence label: behavioral", "Evidence label: installation"])
            scenario.write_specialist_report(disposition="rejected", finding_id="F-005", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-005")
            scenario.evaluate(c, passed=True, independent_context=True)
            recheck_evaluator = (case_root / ".review-loop/rounds/round-02/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_agent_skill_evaluator_record(c, recheck_evaluator, overall_outcome="PASS", name="rechecked Agent-Skill round records all axes and valid labels")
            registry = (case_root / ".review-loop/findings.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "PASS" and len(re.findall(r"(?:Finding|Re-observed) F-005", registry)) == 2 and "Disposition: rejected" in registry, "bounded recheck preserves stable Agent-Skill finding ID")

            case_root = new_review_case(root, "scope-change", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-006", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-006")
            scenario.apply_repair(False)
            c.check(scenario.state().status == "FAIL" and "scope-changing" in scenario.state().next and not (case_root / ".review-loop/rounds/round-01/repair-evidence-F-006.md").is_file(), "scope-changing Agent-Skill repair is rejected without Producer edit")

            case_root = new_review_case(root, "independence-block", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-007")
            scenario.ingest_finding(disposition="rejected", finding_id="F-007")
            scenario.evaluate(c, passed=True, independent_context=False)
            c.check(scenario.state().status == "BLOCKED" and "independent Evaluator" in scenario.state().next, "missing independent Evaluator context blocks Agent-Skill verdict")

            case_root = new_review_case(root, "no-executable-axis", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(executable=False)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-008")
            scenario.ingest_finding(disposition="rejected", finding_id="F-008")
            scenario.evaluate(c, passed=True, independent_context=True)
            no_exec_producer = (case_root / ".review-loop/rounds/round-01/producer-evidence.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "PASS" and "Executable axis: not applicable" in no_exec_producer, "non-executable Skill records explicit executable-axis applicability")

            case_root = new_review_case(root, "maximum-round", "agent-skill")
            scenario = AgentSkillScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved fixture Skill package revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-009")
            scenario.ingest_finding(disposition="rejected", finding_id="F-009")
            scenario.evaluate(c, passed=False, independent_context=True, dependency_available=True, executable_evidence=True, maximum_round=1)
            limit_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_agent_skill_evaluator_record(c, limit_evaluator, overall_outcome="BLOCKED", executable_outcome="BLOCKED", name="maximum-round Agent-Skill Evaluator records all axes and valid labels")
            c.check(scenario.state().status == "BLOCKED" and "maximum rounds" in scenario.state().raw, "maximum repair round returns generic Core BLOCKED")

        self.assertFalse(c.failures, f"agent-skill-profile behavior failed: {c.failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
