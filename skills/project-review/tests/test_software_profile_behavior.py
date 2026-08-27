"""Port of skills/review-loop/tests/software-profile-behavior-tests.ps1.

Executable protocol scenarios in fresh disposable fixtures, asserting the
software Profile's review-loop semantics: specialist evidence, generic
lifecycle transitions, bounded repair, independence blocking, rechecks, and
maximum-round stops.
"""

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

STATUSES = ("INIT", "READY", "CRITIC", "REPAIR", "EVALUATE", "PASS", "FAIL", "BLOCKED")


class SoftwareScenario:
    def __init__(self, case_root: Path) -> None:
        self.case_root = case_root

    def state(self):
        return get_review_state(self.case_root)

    def set_state(self, status: str, round_no: int, next_action: str, blocker: str = "none", charter_revision: str = "") -> None:
        current = self.state()
        if not charter_revision:
            charter_revision = current.charter_revision
        if not charter_revision:
            charter_revision = "software-fixture-1"
        set_review_state(self.case_root, status, round_no, next_action, "software", charter_revision, "project-review Core", "executable software protocol scenario", blocker)

    def initialize(self, acceptance_source: Path) -> None:
        if not acceptance_source.is_file():
            self.set_state("BLOCKED", 0, "record missing acceptance source", "missing acceptance source")
            return
        charter = self.case_root / ".project-review" / "charter.md"
        charter.parent.mkdir(parents=True, exist_ok=True)
        charter.write_text("\n".join([
            "# Acceptance Charter",
            "- Approval state: approved",
            "- Profile: software",
            "- Charter revision: approved-software-spec-r7",
            "- Fixed point: abc1234",
            "- Source: acceptance.md",
            "- Source revision or identity: fixed point abc1234",
        ]) + "\n", encoding="utf-8")
        self.set_state("READY", 0, "collect Producer evidence", "none", "approved-software-spec-r7")

    def start_round(self) -> Path:
        return new_review_round(self.case_root, "software", "request read-only Critic and code-review specialist", [
            "Scope: disposable software fixture acceptance target",
            "Profile: software",
            "Fixed point: abc1234",
            "Evidence label: behavioral",
            "Focused test: fixture assertions",
        ])

    def start_next_round(self) -> Path:
        return new_review_next_round(self.case_root, "software", "validate existing Finding ID and request code-review recheck", [
            "Scope: same frozen software target; next round",
            "Evidence label: behavioral",
            "Focused test: fixture assertions after bounded repair",
        ])

    def write_code_review_report(
        self, *, disposition: str = "confirmed", standards_finding_id: str = "F-001", spec_finding_id: str = "F-002",
        standards_severity: str = "High", spec_severity: str = "Medium",
        standards_source_finding_reference: str = "CR-STD-001", spec_source_finding_reference: str = "CR-SPEC-001",
        specialist_verdict: str = "PASS",
    ) -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("code-review report requires CRITIC state")
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        (round_path / "code-review-standards.md").write_text("\n".join([
            "# code-review Standards report",
            "- Fixed point: abc1234",
            "- Axis: Standards",
            f"- Source finding reference: {standards_source_finding_reference}",
            f"- Stable candidate ID: {standards_finding_id}",
            f"- Severity: {standards_severity}",
            f"- Disposition candidate: {disposition}",
            f"- Specialist verdict: {specialist_verdict}",
            "- Evidence label: review",
        ]) + "\n", encoding="utf-8")
        (round_path / "code-review-spec.md").write_text("\n".join([
            "# code-review Spec report",
            "- Fixed point: abc1234",
            "- Axis: Spec",
            f"- Source finding reference: {spec_source_finding_reference}",
            f"- Stable candidate ID: {spec_finding_id}",
            f"- Severity: {spec_severity}",
            f"- Disposition candidate: {disposition}",
            f"- Specialist verdict: {specialist_verdict}",
            "- Evidence label: review",
        ]) + "\n", encoding="utf-8")

    def ingest_code_review_findings(
        self, *, standards_disposition: str = "confirmed", spec_disposition: str = "confirmed",
        standards_finding_id: str = "F-001", spec_finding_id: str = "F-002",
        standards_severity: str = "", spec_severity: str = "",
        standards_source_finding_reference: str = "CR-STD-001", spec_source_finding_reference: str = "CR-SPEC-001",
    ) -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("Finding ingestion requires CRITIC state")
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        standards_report = (round_path / "code-review-standards.md").read_text(encoding="utf-8")
        spec_report = (round_path / "code-review-spec.md").read_text(encoding="utf-8")
        if "Axis: Standards" not in standards_report or "Axis: Spec" not in spec_report:
            raise ValueError("code-review must retain separate Standards and Spec reports")
        parsed_standards_severity = re.search(r"(?m)^- Severity: (Critical|High|Medium|Low)", standards_report).group(1)
        parsed_spec_severity = re.search(r"(?m)^- Severity: (Critical|High|Medium|Low)", spec_report).group(1)
        if not parsed_standards_severity or not parsed_spec_severity:
            raise ValueError("code-review reports must retain severity metadata")
        if (standards_severity and standards_severity != parsed_standards_severity) or (spec_severity and spec_severity != parsed_spec_severity):
            raise ValueError("provided severity expectations do not match code-review reports")
        if f"Stable candidate ID: {standards_finding_id}" not in standards_report or f"Stable candidate ID: {spec_finding_id}" not in spec_report or f"Source finding reference: {standards_source_finding_reference}" not in standards_report or f"Source finding reference: {spec_source_finding_reference}" not in spec_report:
            raise ValueError("code-review reports must retain stable candidate IDs")
        registry = self.case_root / ".project-review" / "findings.md"
        records = [
            f"Re-observed {standards_finding_id} in round {state.round}",
            f"Source: code-review; Axis: Standards; Source finding reference: {standards_source_finding_reference}",
            f"Severity: {parsed_standards_severity}",
            f"Disposition: {standards_disposition}",
            f"Re-observed {spec_finding_id} in round {state.round}",
            f"Source: code-review; Axis: Spec; Source finding reference: {spec_source_finding_reference}",
            f"Severity: {parsed_spec_severity}",
            f"Disposition: {spec_disposition}",
            "Evidence label: review",
        ]
        if registry.is_file():
            with registry.open("a", encoding="utf-8") as fh:
                fh.write("\n".join(records) + "\n")
        else:
            registry.parent.mkdir(parents=True, exist_ok=True)
            registry.write_text("\n".join(["# Finding Registry"] + [
                f"Finding {standards_finding_id}",
                f"Source: code-review; Axis: Standards; Source finding reference: {standards_source_finding_reference}",
                f"Severity: {parsed_standards_severity}",
                f"Disposition: {standards_disposition}",
                f"Finding {spec_finding_id}",
                f"Source: code-review; Axis: Spec; Source finding reference: {spec_source_finding_reference}",
                f"Severity: {parsed_spec_severity}",
                f"Disposition: {spec_disposition}",
                "Evidence label: review",
                "Resolution evidence: pending fresh Evaluator",
            ]) + "\n", encoding="utf-8")
        if standards_disposition == "confirmed" or spec_disposition == "confirmed":
            self.set_state("REPAIR", state.round, "direct bounded repair to Producer")
        else:
            self.set_state("EVALUATE", state.round, "request fresh Evaluator")

    def all_finding_ids(self) -> list[str]:
        return get_review_finding_ids(self.case_root)

    def confirmed_finding_ids(self) -> list[str]:
        return get_confirmed_review_finding_ids(self.case_root)

    def apply_repair(self, in_scope: bool) -> None:
        state = self.state()
        if state.status != "REPAIR":
            raise ValueError("Repair requires REPAIR state")
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        if not in_scope:
            self.set_state("FAIL", state.round, "scope-changing repair rejected")
            return
        finding_ids = self.confirmed_finding_ids()
        if not finding_ids:
            raise ValueError("Repair requires at least one confirmed finding")
        write_review_repair_evidence(self.case_root, state.round, finding_ids, [
            "Producer repair evidence: bounded and in-scope",
            "Changed scope: existing implementation only",
            "Validation: focused behavioral and negative fixture scenarios",
            "Evidence label: behavioral",
        ])
        self.set_state("EVALUATE", state.round, "request fresh Evaluator")

    def write_evaluator_verdict(self, outcome: str, context_identity: str, standards_outcome: str, spec_outcome: str, behavior_outcome: str, safety_outcome: str, blocking_findings: str) -> Path:
        state = self.state()
        round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
        records = [
            f"# Evaluator Verdict - Round {state.round:02d}",
            f"Context identity: {context_identity}",
            f"Charter revision: {state.charter_revision}; Profile: software",
            f"Criterion AC-1 (Standards): {standards_outcome} - Evidence: [code-review-standards.md](code-review-standards.md) | Label: review | Outcome: {standards_outcome}",
            f"Criterion AC-2 (Spec fidelity): {spec_outcome} - Evidence: [code-review-spec.md](code-review-spec.md) | Label: review | Outcome: {spec_outcome}",
            f"Criterion AC-3 (behavioral correctness): {behavior_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: {behavior_outcome}",
            f"Criterion AC-4 (operational safety): {safety_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: {safety_outcome}",
            "Evidence links and labels:",
            "- [code-review-standards.md](code-review-standards.md) | Label: review",
            "- [code-review-spec.md](code-review-spec.md) | Label: review",
            "- [producer-evidence.md](producer-evidence.md) | Label: behavioral",
        ]
        for finding_id in self.all_finding_ids():
            repair_name = f"repair-evidence-{finding_id}.md"
            if (round_path / repair_name).is_file():
                records.append(f"- [{repair_name}]({repair_name}) | Label: behavioral")
        records += [
            f"Open blocking findings: {blocking_findings}",
            f"Outcome: {outcome}",
            f"Verdict recommendation: {outcome}",
        ]
        path = round_path / "evaluator-verdict.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(records) + "\n", encoding="utf-8")
        return path

    def evaluate(self, c: Checks, *, passed: bool, independent_context: bool, repair_available: bool, maximum_round: int = 3) -> None:
        state = self.state()
        if state.status != "EVALUATE":
            raise ValueError("Evaluation requires EVALUATE state")
        if not independent_context:
            self.write_evaluator_verdict("BLOCKED", "unavailable independent read-only Evaluator", "BLOCKED", "BLOCKED", "BLOCKED", "BLOCKED", "independent context unavailable")
            self.set_state("BLOCKED", state.round, "obtain independent Evaluator context", "independent context unavailable")
            return
        if passed:
            finding_ids = self.confirmed_finding_ids()
            round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
            finding_path = self.case_root / ".project-review" / "findings.md"
            for finding_id in finding_ids:
                repair_name = f"repair-evidence-{finding_id}.md"
                if not (round_path / repair_name).is_file():
                    raise ValueError(f"Missing per-finding repair evidence: {repair_name}")
                with finding_path.open("a", encoding="utf-8") as fh:
                    fh.write("\n".join([
                        f"Finding {finding_id}: Status: resolved",
                        "Resolution evidence: fresh independent Evaluator",
                        f"Repair evidence: rounds/round-{state.round:02d}/{repair_name}",
                    ]) + "\n")
            self.write_evaluator_verdict("PASS", "fresh independent read-only Evaluator", "PASS", "PASS", "PASS", "PASS", "none")
            evaluator_verdict = (round_path / "evaluator-verdict.md").read_text(encoding="utf-8")
            if not all(pattern in evaluator_verdict for pattern in (
                "Criterion AC-1 (Standards): PASS", "Criterion AC-2 (Spec fidelity): PASS",
                "Criterion AC-3 (behavioral correctness): PASS", "Criterion AC-4 (operational safety): PASS",
            )):
                raise ValueError("Evaluator verdict must record criterion-by-criterion software judgments before Core PASS")
            verdict = self.case_root / ".project-review" / "verdict.md"
            verdict.write_text("\n".join([
                "# Review Loop Verdict",
                "Verdict: PASS",
                "Issued by: project-review Core",
                "Evaluator: fresh independent read-only context",
                "Specialist input: code-review Standards + Spec findings",
            ]) + "\n", encoding="utf-8")
            self.set_state("PASS", state.round, "preserve Core verdict")
            return
        if repair_available and state.round < maximum_round:
            self.write_evaluator_verdict("FAIL", "fresh independent read-only Evaluator", "FAIL", "FAIL", "PASS", "PASS", "confirmed code-review findings")
            self.set_state("FAIL", state.round, "CRITIC (next round); bounded repair remains")
        else:
            self.write_evaluator_verdict("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED", "BLOCKED", "BLOCKED", "BLOCKED", "repair limit reached")
            self.set_state("BLOCKED", state.round, "repair limit reached", "maximum rounds or no permitted repair")


def assert_evaluator_record(c: Checks, text: str, *, overall_outcome: str, standards_outcome: str, spec_outcome: str, behavior_outcome: str, safety_outcome: str, name: str) -> None:
    patterns = [
        rf"(?m)^Criterion AC-1 .*Evidence: \[code-review-standards\.md\]\(code-review-standards\.md\) \| Label: review \| Outcome: {standards_outcome}\r?$",
        rf"(?m)^Criterion AC-2 .*Evidence: \[code-review-spec\.md\]\(code-review-spec\.md\) \| Label: review \| Outcome: {spec_outcome}\r?$",
        rf"(?m)^Criterion AC-3 .*Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: behavioral \| Outcome: {behavior_outcome}\r?$",
        rf"(?m)^Criterion AC-4 .*Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: behavioral \| Outcome: {safety_outcome}\r?$",
        rf"(?m)^Outcome: {overall_outcome}\r?$",
    ]
    c.check(all(re.search(p, text) for p in patterns), name)


class SoftwareProfileBehaviorTest(unittest.TestCase):
    def test_software_profile_behavior(self) -> None:
        c = Checks()
        with tempfile.TemporaryDirectory(prefix="review-loop-software-") as tmp:
            root = Path(tmp)
            installed_root = root / "installed-review-loop"
            shutil.copytree(ROOT, installed_root)
            c.check((installed_root / "references/profiles/software.md").is_file(), "fresh install includes software Profile")

            case_root = new_review_case(root, "integration", "software")
            scenario = SoftwareScenario(case_root)
            acceptance = case_root / "acceptance.md"
            acceptance.write_text("Approved software Spec revision 1", encoding="utf-8")
            scenario.initialize(acceptance)
            c.check(scenario.state().charter_revision == "approved-software-spec-r7", "software init freezes approved Charter revision")
            scenario.start_round()
            scenario.write_code_review_report(disposition="confirmed", standards_finding_id="F-001", spec_finding_id="F-002", specialist_verdict="PASS")
            c.check(scenario.state().status == "CRITIC", "code-review specialist PASS does not set final state")
            scenario.ingest_code_review_findings(standards_disposition="confirmed", spec_disposition="confirmed", standards_finding_id="F-001", spec_finding_id="F-002")
            c.check(scenario.state().status == "REPAIR", "code-review findings enter generic REPAIR lifecycle")
            registry = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            standards_report = (case_root / ".project-review/rounds/round-01/code-review-standards.md").read_text(encoding="utf-8")
            spec_report = (case_root / ".project-review/rounds/round-01/code-review-spec.md").read_text(encoding="utf-8")
            c.check(
                "Axis: Standards" in standards_report and "Source finding reference: CR-STD-001" in standards_report
                and "Stable candidate ID: F-001" in standards_report and "Severity: High" in standards_report
                and "Axis: Spec" in spec_report and "Source finding reference: CR-SPEC-001" in spec_report
                and "Stable candidate ID: F-002" in spec_report and "Severity: Medium" in spec_report,
                "separate specialist reports retain axis, source reference, severity, and stable ID",
            )
            c.check(
                "Axis: Standards" in registry and "CR-STD-001" in registry and "Axis: Spec" in registry
                and "CR-SPEC-001" in registry and "Severity: High" in registry and "Severity: Medium" in registry
                and "Evidence label: review" in registry,
                "specialist metadata enters generic finding registry",
            )
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=True, independent_context=True, repair_available=True)
            evaluator_verdict = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            verdict = (case_root / ".project-review/verdict.md").read_text(encoding="utf-8")
            assert_evaluator_record(c, evaluator_verdict, overall_outcome="PASS", standards_outcome="PASS", spec_outcome="PASS", behavior_outcome="PASS", safety_outcome="PASS", name="fresh Evaluator records every criterion with linked evidence, labels, and PASS outcome")
            c.check(scenario.state().status == "PASS" and "Issued by: project-review Core" in verdict and "Issued by: code-review" not in verdict, "Core owns final PASS verdict")

            case_root = new_review_case(root, "bounded-repair", "software")
            scenario = SoftwareScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved software Spec revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            c.check(scenario.state().charter_revision == "approved-software-spec-r7", "bounded repair starts from approved Charter revision")
            scenario.start_round()
            scenario.write_code_review_report(disposition="confirmed", standards_finding_id="F-001", spec_finding_id="F-002", specialist_verdict="FAIL")
            scenario.ingest_code_review_findings(standards_disposition="confirmed", spec_disposition="confirmed", standards_finding_id="F-001", spec_finding_id="F-002")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, repair_available=True)
            charter_revision = scenario.state().charter_revision
            c.check(charter_revision == "approved-software-spec-r7", "failed round retains exact approved Charter revision")
            c.check(scenario.state().status == "FAIL" and "next round" in scenario.state().next, "failed evaluation preserves bounded next-round path")
            scenario.start_next_round()
            c.check(scenario.state().charter_revision == charter_revision and scenario.state().charter_revision == "approved-software-spec-r7", "next round preserves exact frozen Charter revision")
            scenario.write_code_review_report(disposition="confirmed", standards_finding_id="F-001", spec_finding_id="F-002", specialist_verdict="PASS")
            scenario.ingest_code_review_findings(standards_disposition="confirmed", spec_disposition="confirmed", standards_finding_id="F-001", spec_finding_id="F-002")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=True, independent_context=True, repair_available=True)
            registry = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            repair_evidence_standards = (case_root / ".project-review/rounds/round-02/repair-evidence-F-001.md").read_text(encoding="utf-8")
            repair_evidence_spec = (case_root / ".project-review/rounds/round-02/repair-evidence-F-002.md").read_text(encoding="utf-8")
            evaluator_verdict = (case_root / ".project-review/rounds/round-02/evaluator-verdict.md").read_text(encoding="utf-8")
            first_round_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_evaluator_record(c, first_round_evaluator, overall_outcome="FAIL", standards_outcome="FAIL", spec_outcome="FAIL", behavior_outcome="PASS", safety_outcome="PASS", name="failed Evaluator record includes every criterion with linked evidence, labels, and FAIL outcome")
            c.check(
                scenario.state().status == "PASS"
                and len(re.findall(r"(?m)^Finding F-001\r?$", registry)) == 1
                and len(re.findall(r"(?m)^Finding F-002\r?$", registry)) == 1
                and registry.count("CR-STD-001") == 2 and registry.count("CR-SPEC-001") == 2
                and "Re-observed F-001" in registry and "Re-observed F-002" in registry
                and "Finding F-001: Status: resolved" in registry and "Finding F-002: Status: resolved" in registry
                and "Resolution evidence: fresh independent Evaluator" in registry
                and "Finding: F-001" in repair_evidence_standards and "Finding: F-002" in repair_evidence_spec
                and "](repair-evidence-F-001.md)" in evaluator_verdict and "](repair-evidence-F-002.md)" in evaluator_verdict,
                "bounded repair resolves every specialist ID with per-ID evidence and final evaluation",
            )
            assert_evaluator_record(c, evaluator_verdict, overall_outcome="PASS", standards_outcome="PASS", spec_outcome="PASS", behavior_outcome="PASS", safety_outcome="PASS", name="bounded repair final Evaluator record includes every criterion with linked evidence, labels, and PASS outcome")

            case_root = new_review_case(root, "scope-changing-repair", "software")
            scenario = SoftwareScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved software Spec revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_code_review_report(disposition="confirmed", standards_finding_id="F-003", spec_finding_id="F-004", specialist_verdict="FAIL")
            scenario.ingest_code_review_findings(standards_disposition="confirmed", spec_disposition="confirmed", standards_finding_id="F-003", spec_finding_id="F-004")
            scenario.apply_repair(False)
            c.check(scenario.state().status == "FAIL" and "scope-changing" in scenario.state().next and not (case_root / ".project-review/rounds/round-01/repair-evidence.md").is_file(), "scope-changing repair is rejected without Producer edit")

            case_root = new_review_case(root, "independence-block", "software")
            scenario = SoftwareScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved software Spec revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_code_review_report(disposition="rejected", standards_finding_id="F-005", spec_finding_id="F-006", specialist_verdict="PASS")
            scenario.ingest_code_review_findings(standards_disposition="rejected", spec_disposition="rejected", standards_finding_id="F-005", spec_finding_id="F-006")
            scenario.evaluate(c, passed=True, independent_context=False, repair_available=False)
            blocked_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "BLOCKED" and "independent Evaluator" in scenario.state().next, "missing independent context blocks specialist conclusion")
            assert_evaluator_record(c, blocked_evaluator, overall_outcome="BLOCKED", standards_outcome="BLOCKED", spec_outcome="BLOCKED", behavior_outcome="BLOCKED", safety_outcome="BLOCKED", name="independence BLOCKED Evaluator record includes every criterion with linked evidence, labels, and BLOCKED outcome")

            case_root = new_review_case(root, "rejected-recheck", "software")
            scenario = SoftwareScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved software Spec revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_code_review_report(disposition="confirmed", standards_finding_id="F-009", spec_finding_id="F-010", standards_severity="Critical", spec_severity="Low", specialist_verdict="FAIL")
            scenario.ingest_code_review_findings(standards_disposition="confirmed", spec_disposition="confirmed", standards_finding_id="F-009", spec_finding_id="F-010", standards_severity="Critical", spec_severity="Low")
            initial_registry = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            c.check("Finding F-009" in initial_registry and "Severity: Critical" in initial_registry and "Finding F-010" in initial_registry and "Severity: Low" in initial_registry, "specialist Critical and Low severities enter registry exactly")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, repair_available=True)
            scenario.start_next_round()
            scenario.write_code_review_report(disposition="rejected", standards_finding_id="F-009", spec_finding_id="F-010", standards_severity="Critical", spec_severity="Low", specialist_verdict="PASS")
            scenario.ingest_code_review_findings(standards_disposition="rejected", spec_disposition="rejected", standards_finding_id="F-009", spec_finding_id="F-010", standards_severity="Critical", spec_severity="Low")
            c.check(len(scenario.confirmed_finding_ids()) == 0, "rejected recheck removes IDs from confirmed repair set")
            scenario.evaluate(c, passed=True, independent_context=True, repair_available=False)
            recheck_registry = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            recheck_evaluator = (case_root / ".project-review/rounds/round-02/evaluator-verdict.md").read_text(encoding="utf-8")
            c.check(
                scenario.state().status == "PASS" and "Re-observed F-009" in recheck_registry and "Re-observed F-010" in recheck_registry
                and "Disposition: rejected" in recheck_registry
                and recheck_registry.count("Severity: Critical") == 2 and recheck_registry.count("Severity: Low") == 2
                and not (case_root / ".project-review/rounds/round-02/repair-evidence-F-009.md").is_file()
                and not (case_root / ".project-review/rounds/round-02/repair-evidence-F-010.md").is_file(),
                "rejected recheck reaches PASS without stale repair evidence",
            )
            assert_evaluator_record(c, recheck_evaluator, overall_outcome="PASS", standards_outcome="PASS", spec_outcome="PASS", behavior_outcome="PASS", safety_outcome="PASS", name="rejected recheck PASS Evaluator record includes every criterion with linked evidence, labels, and PASS outcome")

            case_root = new_review_case(root, "maximum-round", "software")
            scenario = SoftwareScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved software Spec revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_code_review_report(disposition="confirmed", standards_finding_id="F-007", spec_finding_id="F-008", specialist_verdict="FAIL")
            scenario.ingest_code_review_findings(standards_disposition="confirmed", spec_disposition="confirmed", standards_finding_id="F-007", spec_finding_id="F-008")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, repair_available=True, maximum_round=1)
            limit_evaluator = (case_root / ".project-review/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "BLOCKED", "maximum-round stop returns BLOCKED")
            assert_evaluator_record(c, limit_evaluator, overall_outcome="BLOCKED", standards_outcome="BLOCKED", spec_outcome="BLOCKED", behavior_outcome="BLOCKED", safety_outcome="BLOCKED", name="maximum-round BLOCKED Evaluator record includes every criterion with linked evidence, labels, and BLOCKED outcome")

        self.assertGreater(c.assertions, 0)
        self.assertFalse(c.failures, f"software-profile behavior failed: {c.failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
