"""Port of skills/review-loop/tests/specification-profile-behavior-tests.ps1."""

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
    get_review_finding_ids,
    get_review_state,
    new_review_case,
    new_review_next_round,
    new_review_round,
    set_review_state,
    write_review_repair_evidence,
)

PRIMARY_LABELS = ("source", "structural", "behavioral", "installation", "invocation", "runtime", "manual", "review")


class SpecificationScenario:
    def __init__(self, case_root: Path) -> None:
        self.case_root = case_root

    def state(self):
        return get_review_state(self.case_root)

    def set_state(self, status: str, round_no: int, next_action: str, *, charter_revision: str = "", last_completed_action: str = "protocol transition", blocker: str = "none") -> None:
        current = self.state()
        if not charter_revision:
            charter_revision = current.charter_revision
        set_review_state(self.case_root, status, round_no, next_action, "specification", charter_revision, "project-review Core", last_completed_action, blocker)

    def initialize(self, acceptance_source: Path, authority: str = "spec-source-2026-07-22-r4") -> None:
        if not acceptance_source.is_file():
            self.set_state("BLOCKED", 0, "record missing authoritative source", charter_revision="specification-fixture-1", last_completed_action="specification source check", blocker="missing approved authoritative Spec/brief/ticket")
            return
        charter = self.case_root / ".project-review" / "charter.md"
        charter.parent.mkdir(parents=True, exist_ok=True)
        charter.write_text("\n".join([
            "# Acceptance Charter",
            "- Approval state: approved",
            "- Profile: specification",
            "- Charter revision: approved-specification-r4",
            f"- Authority identity: {authority}",
            "- Authority precedence: approved source register entry 001",
            "- Target: frozen acceptance contract fixture",
            "- Scope: in-scope criteria AC-1..AC-7; exclusions: implementation and release",
            "- Acceptance source: acceptance.md",
        ]) + "\n", encoding="utf-8")
        set_review_state(self.case_root, "READY", 0, "collect Producer evidence", "specification", "approved-specification-r4", "project-review Core", "specification Charter freeze")

    def start_round(self, *, ambiguous: bool = False, contradictory: bool = False, traceability_complete: bool = True) -> Path:
        evidence = [
            "Scope: frozen Spec/brief/ticket and approved acceptance Charter",
            "Profile: specification",
            "Authority: spec-source-2026-07-22-r4; revision and approval state recorded",
            "Source precedence: approved source register entry 001",
            "Target and exclusions: acceptance contract only; implementation and release excluded",
            "Scope map: each in-scope outcome and non-goal linked to authoritative source location",
            "Acceptance matrix: stable AC-1..AC-7 IDs link source, observable outcome, owner, and evidence class",
            "Terminology register: terms, units, qualifiers, audience, and preconditions reviewed",
            "Dependencies and hand-offs: owners, gates, assumptions, and downstream seams recorded",
            "Evidence labels: source; structural; behavioral; manual; review",
        ]
        if not traceability_complete:
            evidence.append("Traceability defect: criterion AC-4 has no authoritative source link or owner")
        if ambiguous:
            evidence.append('Unresolved ambiguity: "fast" has no measurable threshold or audience context; clarification owner is missing')
        else:
            evidence.append("Ambiguity audit: no unresolved terms or materially different interpretations")
        if contradictory:
            evidence.append("Unresolved contradiction: source-register-001 requires PASS while approved-brief-r4 requires BLOCKED; no precedence decision")
        else:
            evidence.append("Contradiction audit: competing sources agree or precedence decision is recorded")
        return new_review_round(self.case_root, "specification", "request read-only specification-domain specialists", evidence)

    def start_next_round(self) -> Path:
        return new_review_next_round(self.case_root, "specification", "recheck stable specification findings", [
            "Scope: same frozen specification target; next bounded round",
            "Profile: specification",
            "Authority and Charter revision unchanged: approved-specification-r4",
            "Evidence labels: structural; source; review",
            "Traceability and acceptance matrix rechecked against the same source",
        ])

    def write_specialist_report(self, *, disposition: str = "confirmed", finding_id: str = "F-001", severity: str = "High", axis: str = "criteria and acceptance traceability", source_reference: str = "SP-AXIS-001", specialist_verdict: str = "PASS") -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("specification specialist report requires CRITIC state")
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        (round_path / "specification-specialist.md").write_text("\n".join([
            "# Specification Specialist Report",
            "- Artifact: acceptance.md",
            "- Profile: specification",
            f"- Axis: {axis}",
            f"- Source finding reference: {source_reference}",
            f"- Stable candidate ID: {finding_id}",
            f"- Severity: {severity}",
            f"- Disposition candidate: {disposition}",
            f"- Specialist verdict: {specialist_verdict}",
            "- Evidence: authoritative source, scope map, acceptance matrix, and ambiguity/contradiction register",
            "- Evidence label: review",
        ]) + "\n", encoding="utf-8")

    def ingest_finding(self, *, disposition: str = "confirmed", finding_id: str = "F-001", source_reference: str = "SP-AXIS-001", severity: str = "High") -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("specification finding ingestion requires CRITIC state")
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        report = (round_path / "specification-specialist.md").read_text(encoding="utf-8")
        if f"Stable candidate ID: {finding_id}" not in report or "Evidence label: review" not in report:
            raise ValueError("specialist report lost stable ID or evidence class")
        add_review_finding(self.case_root, finding_id, "specification specialist", "specification contract", source_reference, severity, disposition, "review")
        if disposition == "confirmed":
            self.set_state("REPAIR", state.round, "direct bounded specification repair to Producer", last_completed_action="validated specification candidate finding")
        else:
            self.set_state("EVALUATE", state.round, "request fresh Evaluator", last_completed_action="rejected specification candidate")

    def apply_repair(self, in_scope: bool) -> None:
        state = self.state()
        if state.status != "REPAIR":
            raise ValueError("Specification repair requires REPAIR state")
        if not in_scope:
            self.set_state("FAIL", state.round, "scope-changing specification repair rejected", last_completed_action="rejected out-of-scope Producer repair")
            return
        ids = get_confirmed_review_finding_ids(self.case_root)
        if not ids:
            raise ValueError("Specification repair requires a confirmed finding")
        write_review_repair_evidence(self.case_root, state.round, ids, [
            "Producer repair evidence: bounded and in-scope",
            "Changed scope: existing acceptance contract only; no new requirement or authority",
            "Validation: authority, scope map, acceptance matrix, terminology and contradiction checks",
            "Evidence label: structural",
            "Evidence label: source",
        ])
        self.set_state("EVALUATE", state.round, "request fresh Evaluator", last_completed_action="bounded specification Producer repair")

    def write_evaluator(self, outcome: str, context_identity: str, traceability_outcome: str = "", ambiguity_outcome: str = "", contradiction_outcome: str = "") -> None:
        if not traceability_outcome:
            traceability_outcome = outcome
        if not ambiguity_outcome:
            ambiguity_outcome = outcome
        if not contradiction_outcome:
            contradiction_outcome = outcome
        state = self.state()
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        records = [
            f"# Evaluator Verdict - Round {state.round:02d}",
            f"Context identity: {context_identity}",
            f"Charter revision: {state.charter_revision}; Profile: specification",
            f"Criterion AC-1 (authority and baseline integrity): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: source | Outcome: {outcome}",
            f"Criterion AC-2 (scope and target traceability): {traceability_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: {traceability_outcome}",
            f"Criterion AC-3 (criteria and acceptance traceability): {traceability_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: {traceability_outcome}",
            f"Criterion AC-4 (terminology and ambiguity control): {ambiguity_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: {ambiguity_outcome}",
            f"Criterion AC-5 (contradiction and decision coherence): {contradiction_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: {contradiction_outcome}",
            f"Criterion AC-6 (testability and evidence design): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: {outcome}",
            f"Criterion AC-7 (version, change, and hand-off integrity): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: {outcome}",
        ]
        for finding_id in get_review_finding_ids(self.case_root):
            repair_name = f"repair-evidence-{finding_id}.md"
            if (round_path / repair_name).is_file():
                records.append(f"- [{repair_name}]({repair_name}) | Label: structural")
        records += ["Open blocking findings: none", f"Outcome: {outcome}", f"Verdict recommendation: {outcome}"]
        (round_path / "evaluator-verdict.md").write_text("\n".join(records) + "\n", encoding="utf-8")

    def evaluate(self, c: Checks, *, passed: bool, independent_context: bool, maximum_round: int = 3) -> None:
        state = self.state()
        if state.status != "EVALUATE":
            raise ValueError("Specification evaluation requires EVALUATE state")
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        producer = (round_path / "producer-evidence.md").read_text(encoding="utf-8")
        if not independent_context:
            self.write_evaluator("BLOCKED", "unavailable independent read-only Evaluator", "BLOCKED", "BLOCKED", "BLOCKED")
            self.set_state("BLOCKED", state.round, "obtain independent Evaluator context", last_completed_action="independent context check", blocker="independent context unavailable")
            return
        if "Traceability defect:" in producer:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED", "BLOCKED", "BLOCKED")
            self.set_state("BLOCKED", state.round, "link every criterion to an authoritative source and owner", last_completed_action="scope and criteria traceability check", blocker="untraceable requirement or acceptance criterion")
            return
        if "Unresolved ambiguity:" in producer or "Unresolved contradiction:" in producer:
            ambiguity = "BLOCKED" if "Unresolved ambiguity:" in producer else "PASS"
            contradiction = "BLOCKED" if "Unresolved contradiction:" in producer else "PASS"
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED", ambiguity, contradiction)
            self.set_state("BLOCKED", state.round, "record authority decision or clarify ambiguous requirement", last_completed_action="authority and ambiguity boundary check", blocker="unresolved specification authority boundary")
            return
        if passed:
            registry = self.case_root / ".project-review" / "findings.md"
            for finding_id in get_confirmed_review_finding_ids(self.case_root):
                repair = round_path / f"repair-evidence-{finding_id}.md"
                if not repair.is_file():
                    raise ValueError(f"Missing repair evidence for {finding_id}")
                with registry.open("a", encoding="utf-8") as fh:
                    fh.write("\n".join([
                        f"Finding {finding_id}: Status: resolved",
                        "Resolution evidence: fresh independent Evaluator",
                        f"Repair evidence: rounds/round-{state.round:02d}/repair-evidence-{finding_id}.md",
                    ]) + "\n")
            self.write_evaluator("PASS", "fresh independent read-only Evaluator")
            verdict = self.case_root / ".project-review" / "verdict.md"
            verdict.write_text("\n".join([
                "# Review Loop Verdict",
                "Verdict: PASS",
                "Issued by: project-review Core",
                "Evaluator: fresh independent read-only context",
                "Specialist input: specification authority, traceability, ambiguity, and contradiction evidence",
            ]) + "\n", encoding="utf-8")
            self.set_state("PASS", state.round, "preserve Core verdict", last_completed_action="fresh specification Evaluator PASS")
        elif state.round < maximum_round:
            self.write_evaluator("FAIL", "fresh independent read-only Evaluator", "FAIL", "FAIL", "FAIL")
            self.set_state("FAIL", state.round, "CRITIC (next round); bounded specification repair remains", last_completed_action="fresh specification Evaluator FAIL")
        else:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED", "BLOCKED", "BLOCKED")
            self.set_state("BLOCKED", state.round, "repair limit reached", last_completed_action="repair limit check", blocker="maximum rounds or no permitted repair")


def assert_specification_evaluator_record(c: Checks, text: str, *, overall_outcome: str, traceability_outcome: str = "", ambiguity_outcome: str = "", contradiction_outcome: str = "", name: str) -> None:
    if not traceability_outcome:
        traceability_outcome = overall_outcome
    if not ambiguity_outcome:
        ambiguity_outcome = overall_outcome
    if not contradiction_outcome:
        contradiction_outcome = overall_outcome
    expected = {
        1: ("source", overall_outcome),
        2: ("structural", traceability_outcome),
        3: ("structural", traceability_outcome),
        4: ("review", ambiguity_outcome),
        5: ("review", contradiction_outcome),
        6: ("behavioral", overall_outcome),
        7: ("structural", overall_outcome),
    }
    missing = []
    for criterion, (label, outcome) in expected.items():
        line = re.search(rf"(?m)^Criterion AC-{criterion} \([^\r\n]+\): {outcome} - Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: ([a-z]+) \| Outcome: {outcome}\r?$", text)
        if not line:
            missing.append(f"AC-{criterion} missing outcome/evidence/link")
            continue
        if line.group(1) != label:
            missing.append(f"AC-{criterion} expected label {label}, observed {line.group(1)}")
        if line.group(1) not in PRIMARY_LABELS:
            missing.append(f"AC-{criterion} uses unsupported primary label")
    if not re.search(rf"(?m)^Outcome: {overall_outcome}\r?$", text):
        missing.append(f"overall outcome {overall_outcome} missing")
    c.check(len(missing) == 0, f"{name} (AC-1..AC-7, links, labels, and outcomes)")


class SpecificationProfileBehaviorTest(unittest.TestCase):
    def test_specification_profile_behavior(self) -> None:
        c = Checks()
        with tempfile.TemporaryDirectory(prefix="review-loop-specification-") as tmp:
            root = Path(tmp)
            installed = root / "installed-review-loop"
            shutil.copytree(ROOT, installed)
            c.check((installed / "references/profiles/specification.md").is_file(), "fresh install includes specification Profile")

            case_root = new_review_case(root, "integration", "specification")
            scenario = SpecificationScenario(case_root)
            acceptance = case_root / "acceptance.md"
            acceptance.write_text("Approved Spec revision 4; source register entry 001 is authoritative", encoding="utf-8")
            scenario.initialize(acceptance)
            c.check(scenario.state().profile == "specification" and scenario.state().charter_revision == "approved-specification-r4" and "Verdict owner: project-review Core" in scenario.state().raw, "init freezes authoritative source, Profile, revision, and Core ownership")
            scenario.start_round()
            producer = (case_root / ".project-review/rounds/round-01/producer-evidence.md").read_text(encoding="utf-8")
            c.check("Authority:" in producer and "Scope map:" in producer and "Acceptance matrix:" in producer and "Evidence labels: source; structural; behavioral; manual; review" in producer, "Producer evidence records authority and requirement traceability")
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-001", specialist_verdict="PASS")
            c.check(scenario.state().status == "CRITIC", "specialist PASS remains a candidate while Core is in CRITIC")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-001")
            c.check(scenario.state().status == "REPAIR", "confirmed specification finding enters generic REPAIR lifecycle")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=True, independent_context=True)
            evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            verdict = (case_root / ".project-review/verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, evaluator, overall_outcome="PASS", name="fresh Evaluator records all specification criteria with linked evidence")
            registry = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "PASS" and "Issued by: project-review Core" in verdict and "Finding F-001: Status: resolved" in registry and "Resolution evidence: fresh independent Evaluator" in registry, "Core owns final PASS and preserves stable finding resolution")

            case_root = new_review_case(root, "missing-source", "specification")
            scenario = SpecificationScenario(case_root)
            scenario.initialize(case_root / "missing-acceptance.md")
            c.check(scenario.state().status == "BLOCKED" and "missing approved authoritative Spec/brief/ticket" in scenario.state().raw, "missing authoritative source blocks initialization")

            case_root = new_review_case(root, "ambiguous", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(ambiguous=True)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-002", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-002")
            scenario.evaluate(c, passed=True, independent_context=True)
            ambiguous_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, ambiguous_evaluator, overall_outcome="BLOCKED", traceability_outcome="BLOCKED", ambiguity_outcome="BLOCKED", contradiction_outcome="PASS", name="ambiguous requirement blocks with criterion-linked evidence")
            c.check(scenario.state().status == "BLOCKED" and "unresolved specification authority boundary" in scenario.state().raw, "unresolved ambiguity returns Core BLOCKED")

            case_root = new_review_case(root, "contradiction", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(contradictory=True)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-003", axis="contradiction and decision coherence", source_reference="SP-CONTRADICTION-001")
            scenario.ingest_finding(disposition="rejected", finding_id="F-003")
            scenario.evaluate(c, passed=True, independent_context=True)
            contradiction_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, contradiction_evaluator, overall_outcome="BLOCKED", traceability_outcome="BLOCKED", ambiguity_outcome="PASS", contradiction_outcome="BLOCKED", name="contradictory authority blocks with criterion-linked evidence")
            c.check(scenario.state().status == "BLOCKED" and "unresolved specification authority boundary" in scenario.state().raw, "unresolved contradiction returns Core BLOCKED")

            case_root = new_review_case(root, "traceability-boundary", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(traceability_complete=False)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-008", axis="criteria and acceptance traceability", source_reference="SP-TRACEABILITY-001")
            scenario.ingest_finding(disposition="rejected", finding_id="F-008")
            scenario.evaluate(c, passed=True, independent_context=True)
            traceability_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, traceability_evaluator, overall_outcome="BLOCKED", traceability_outcome="BLOCKED", ambiguity_outcome="BLOCKED", contradiction_outcome="BLOCKED", name="untraceable criterion blocks AC-2 and AC-3 before PASS")
            c.check(scenario.state().status == "BLOCKED" and "untraceable requirement or acceptance criterion" in scenario.state().raw and "authoritative source and owner" in scenario.state().next, "untraceable criterion returns Core BLOCKED with smallest unblock")

            case_root = new_review_case(root, "bounded-repair", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-004", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-004")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True)
            failed_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, failed_evaluator, overall_outcome="FAIL", name="failed specification evaluation preserves all criterion evidence")
            revision = scenario.state().charter_revision
            c.check(scenario.state().status == "FAIL" and revision == "approved-specification-r4" and "next round" in scenario.state().next, "failed specification round retains frozen revision and bounded next round")
            scenario.start_next_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-004", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-004")
            scenario.evaluate(c, passed=True, independent_context=True)
            recheck_evaluator = (case_root / ".project-review/rounds/round-02/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, recheck_evaluator, overall_outcome="PASS", name="rechecked specification finding reaches Core PASS")
            recheck_registry = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "PASS" and len(re.findall(r"(?:Finding|Re-observed) F-004", recheck_registry)) == 2 and "Disposition: rejected" in recheck_registry, "stable specification finding ID survives bounded recheck")

            case_root = new_review_case(root, "scope-change", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(traceability_complete=False)
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-005", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-005")
            scenario.apply_repair(False)
            c.check(scenario.state().status == "FAIL" and "scope-changing" in scenario.state().next and not (case_root / ".project-review/rounds/round-01/repair-evidence-F-005.md").is_file(), "scope-changing specification repair is rejected without Producer edit")

            case_root = new_review_case(root, "independence-block", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-006")
            scenario.ingest_finding(disposition="rejected", finding_id="F-006")
            scenario.evaluate(c, passed=True, independent_context=False)
            independence_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, independence_evaluator, overall_outcome="BLOCKED", name="missing independent context blocks Core verdict")
            c.check(scenario.state().status == "BLOCKED" and "independent Evaluator" in scenario.state().next, "missing independent Evaluator context returns BLOCKED")

            case_root = new_review_case(root, "maximum-round", "specification")
            scenario = SpecificationScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved Spec revision 4", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-007", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-007")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, maximum_round=1)
            limit_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_specification_evaluator_record(c, limit_evaluator, overall_outcome="BLOCKED", name="maximum-round stop records Core BLOCKED evidence")
            c.check(scenario.state().status == "BLOCKED" and "maximum rounds" in scenario.state().raw, "maximum repair round returns generic BLOCKED")

        self.assertGreater(c.assertions, 0)
        self.assertFalse(c.failures, f"specification-profile behavior failed: {c.failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
