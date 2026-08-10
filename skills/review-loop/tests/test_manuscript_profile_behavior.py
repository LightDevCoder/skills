"""Port of skills/review-loop/tests/manuscript-profile-behavior-tests.ps1."""

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


class ManuscriptScenario:
    def __init__(self, case_root: Path) -> None:
        self.case_root = case_root

    def state(self):
        return get_review_state(self.case_root)

    def set_state(self, status: str, round_no: int, next_action: str, *, charter_revision: str = "", last_completed_action: str = "protocol transition", blocker: str = "none") -> None:
        current = self.state()
        if not charter_revision:
            charter_revision = current.charter_revision
        set_review_state(self.case_root, status, round_no, next_action, "manuscript", charter_revision, "review-loop Core", last_completed_action, blocker)

    def initialize(self, acceptance_source: Path) -> None:
        if not acceptance_source.is_file():
            self.set_state("BLOCKED", 0, "record missing acceptance source", charter_revision="manuscript-fixture-1", last_completed_action="manuscript source check", blocker="missing approved Brief/Charter")
            return
        charter = self.case_root / ".review-loop" / "charter.md"
        charter.parent.mkdir(parents=True, exist_ok=True)
        charter.write_text("\n".join([
            "# Acceptance Charter",
            "- Approval state: approved",
            "- Profile: manuscript",
            "- Charter revision: approved-manuscript-brief-r3",
            "- Artifact snapshot: manuscript/frozen.md sha256: fixture-artifact-hash",
            "- Source register: .manuscript-ops/sources/source-register.tsv",
            "- Review matrix captured_at: 2026-07-22T00:00:00Z",
            "- Acceptance source: acceptance.md",
        ]) + "\n", encoding="utf-8")
        set_review_state(self.case_root, "READY", 0, "collect Producer evidence", "manuscript", "approved-manuscript-brief-r3", "review-loop Core", "manuscript Charter freeze")

    def start_round(self, *, image_triggered: bool = False, image_evidence: bool = True) -> Path:
        evidence = [
            "Scope: frozen manuscript candidate and declared deliverables",
            "Profile: manuscript",
            "Artifact: manuscript/frozen.md; SHA-256: fixture-artifact-hash",
            "Brief/Charter: approved-manuscript-brief-r3",
            "Source register: authoritative source-001; use=factual; exclusions=none",
            "Lifecycle/batch: candidate batch-01; prerequisite outline accepted",
            "Locked source: manuscript/locked.md; SHA-256: fixture-locked-hash",
            "Terminology: glossary reviewed for language en-US",
            "Format evidence: DOCX structural, renderer runtime, manual visual, semantic and round-trip observations",
            "Generation: fixture renderer v1, locked input and output hashes retained",
            "Gate receipt: final-approved-fixture receipt retained",
            "Evidence label: structural; Evidence label: source; Evidence label: runtime; Evidence label: manual; Evidence label: review",
        ]
        if image_triggered and image_evidence:
            evidence.append("Image axis: triggered by registered PPTX/image source; source/rights/placement/caption/annotation/alt-text evidence recorded; Evidence label: manual")
        elif image_triggered:
            evidence.append("Image axis: triggered by registered PPTX/image source; required source/rights/placement/caption/alt-text evidence missing")
        else:
            evidence.append("Image axis: not applicable; no registered image/PPTX/active-batch trigger; negative audit recorded; Evidence label: structural")
        return new_review_round(self.case_root, "manuscript", "request read-only manuscript-domain specialists", evidence)

    def start_next_round(self) -> Path:
        return new_review_next_round(self.case_root, "manuscript", "recheck stable manuscript findings", [
            "Scope: same frozen manuscript target; next round",
            "Profile: manuscript",
            "Evidence label: structural",
            "Evidence label: runtime",
            "Evidence label: manual",
        ])

    def write_specialist_report(self, *, disposition: str = "confirmed", finding_id: str = "F-001", severity: str = "High", source_reference: str = "MS-AXIS-SOURCE-001", specialist_verdict: str = "PASS") -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("manuscript specialist report requires CRITIC state")
        round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        (round_path / "manuscript-specialist.md").write_text("\n".join([
            "# Manuscript Specialist Report",
            "- Artifact: manuscript/frozen.md",
            "- Profile: manuscript",
            "- Axis: Source authority, provenance, factual claims, citations, numbers, and units",
            f"- Source finding reference: {source_reference}",
            f"- Stable candidate ID: {finding_id}",
            f"- Severity: {severity}",
            f"- Disposition candidate: {disposition}",
            f"- Specialist verdict: {specialist_verdict}",
            "- Evidence: source register, locked-source hash, and artifact observation",
            "- Evidence label: review",
        ]) + "\n", encoding="utf-8")

    def ingest_finding(self, *, disposition: str = "confirmed", finding_id: str = "F-001", source_reference: str = "MS-AXIS-SOURCE-001") -> None:
        state = self.state()
        if state.status != "CRITIC":
            raise ValueError("manuscript finding ingestion requires CRITIC state")
        round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
        report = (round_path / "manuscript-specialist.md").read_text(encoding="utf-8")
        if "Axis: Source authority" not in report or f"Stable candidate ID: {finding_id}" not in report or "Evidence label: review" not in report:
            raise ValueError("specialist report lost axis, stable ID, or evidence class")
        add_review_finding(self.case_root, finding_id, "manuscript specialist", "source authority", source_reference, "High", disposition, "review")
        if disposition == "confirmed":
            self.set_state("REPAIR", state.round, "direct bounded repair to Producer", last_completed_action="validated manuscript candidate finding")
        else:
            self.set_state("EVALUATE", state.round, "request fresh Evaluator", last_completed_action="rejected manuscript candidate")

    def apply_repair(self, in_scope: bool) -> None:
        state = self.state()
        if state.status != "REPAIR":
            raise ValueError("Manuscript repair requires REPAIR state")
        if not in_scope:
            self.set_state("FAIL", state.round, "scope-changing manuscript repair rejected", last_completed_action="rejected out-of-scope Producer repair")
            return
        ids = get_confirmed_review_finding_ids(self.case_root)
        if not ids:
            raise ValueError("Manuscript repair requires a confirmed finding")
        write_review_repair_evidence(self.case_root, state.round, ids, [
            "Producer repair evidence: bounded and in-scope",
            "Changed scope: existing manuscript artifact only",
            "Validation: source, runtime renderer, manual visual, semantic and terminology checks",
            "Evidence label: runtime",
            "Evidence label: manual",
        ])
        self.set_state("EVALUATE", state.round, "request fresh Evaluator", last_completed_action="bounded manuscript Producer repair")

    def write_evaluator(self, outcome: str, context_identity: str, format_outcome: str = "PASS") -> None:
        state = self.state()
        round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
        round_path.mkdir(parents=True, exist_ok=True)
        producer = (round_path / "producer-evidence.md").read_text(encoding="utf-8")
        image_label = "manual" if "Image axis: triggered" in producer else "structural"
        records = [
            f"# Evaluator Verdict - Round {state.round:02d}",
            f"Context identity: {context_identity}",
            f"Charter revision: {state.charter_revision}; Profile: manuscript",
            f"Criterion AC-1 (reader task and structure): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: {outcome}",
            f"Criterion AC-2 (source authority and factual fidelity): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: source | Outcome: {outcome}",
            f"Criterion AC-3 (terminology and localization): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: {outcome}",
            f"Criterion AC-4 (reader fit and accessibility): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: {outcome}",
            f"Criterion AC-5 (safety, privacy and metadata): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: {outcome}",
            f"Criterion AC-6 (format, rendering and visual QA): {format_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: runtime | Outcome: {format_outcome}",
            f"Criterion AC-7 (images and figures applicability): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: {image_label} | Outcome: {outcome}",
            f"Criterion AC-8 (lifecycle, batches, gates and locked source): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: source | Outcome: {outcome}",
            f"Criterion AC-9 (reproducibility and artifact evidence): {outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: {outcome}",
            f"Criterion AC-10 (compatibility and round-trip): {format_outcome} - Evidence: [producer-evidence.md](producer-evidence.md) | Label: runtime | Outcome: {format_outcome}",
        ]
        for finding_id in get_review_finding_ids(self.case_root):
            repair_name = f"repair-evidence-{finding_id}.md"
            if (round_path / repair_name).is_file():
                records.append(f"- [{repair_name}]({repair_name}) | Label: runtime")
        records += ["Open blocking findings: none", f"Outcome: {outcome}", f"Verdict recommendation: {outcome}"]
        (round_path / "evaluator-verdict.md").write_text("\n".join(records) + "\n", encoding="utf-8")

    def evaluate(self, c: Checks, *, passed: bool, independent_context: bool, format_evidence: bool = True, maximum_round: int = 3) -> None:
        state = self.state()
        if state.status != "EVALUATE":
            raise ValueError("Manuscript evaluation requires EVALUATE state")
        if not independent_context:
            self.write_evaluator("BLOCKED", "unavailable independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "obtain independent Evaluator context", last_completed_action="independent context check", blocker="independent context unavailable")
            return
        producer_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}/producer-evidence.md"
        producer = producer_path.read_text(encoding="utf-8")
        if "Image axis: triggered" in producer and "source/rights/placement/caption/annotation/alt-text evidence recorded" not in producer:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "obtain required image source and visual evidence", last_completed_action="image applicability check", blocker="triggered image axis evidence unavailable")
            return
        if not format_evidence:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "obtain required render/visual/round-trip evidence", last_completed_action="format evidence check", blocker="blocking format QA unavailable")
            return
        if passed:
            round_path = self.case_root / f".review-loop/rounds/round-{state.round:02d}"
            registry = self.case_root / ".review-loop" / "findings.md"
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
            self.write_evaluator("PASS", "fresh independent read-only Evaluator", "PASS")
            verdict = self.case_root / ".review-loop" / "verdict.md"
            verdict.write_text("\n".join([
                "# Review Loop Verdict",
                "Verdict: PASS",
                "Issued by: review-loop Core",
                "Evaluator: fresh independent read-only context",
                "Specialist input: manuscript-domain source, editorial, and format evidence",
            ]) + "\n", encoding="utf-8")
            self.set_state("PASS", state.round, "preserve Core verdict", last_completed_action="fresh manuscript Evaluator PASS")
        elif not passed and state.round < maximum_round:
            self.write_evaluator("FAIL", "fresh independent read-only Evaluator", "PASS")
            self.set_state("FAIL", state.round, "CRITIC (next round); bounded manuscript repair remains", last_completed_action="fresh manuscript Evaluator FAIL")
        else:
            self.write_evaluator("BLOCKED", "fresh independent read-only Evaluator", "BLOCKED")
            self.set_state("BLOCKED", state.round, "repair limit reached", last_completed_action="repair limit check", blocker="maximum rounds or no permitted repair")


def assert_manuscript_evaluator_record(c: Checks, text: str, *, overall_outcome: str, format_outcome: str = "", image_label: str = "structural", name: str) -> None:
    if not format_outcome:
        format_outcome = overall_outcome
    expected = {
        1: ("structural", overall_outcome),
        2: ("source", overall_outcome),
        3: ("review", overall_outcome),
        4: ("review", overall_outcome),
        5: ("review", overall_outcome),
        6: ("runtime", format_outcome),
        7: (image_label, overall_outcome),
        8: ("source", overall_outcome),
        9: ("structural", overall_outcome),
        10: ("runtime", format_outcome),
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
    c.check(len(missing) == 0, f"{name} (AC-1..AC-10, links, labels, image mapping)")


class ManuscriptProfileBehaviorTest(unittest.TestCase):
    def test_manuscript_profile_behavior(self) -> None:
        c = Checks()
        with tempfile.TemporaryDirectory(prefix="review-loop-manuscript-") as tmp:
            root = Path(tmp)
            installed = root / "installed-review-loop"
            shutil.copytree(ROOT, installed)
            c.check((installed / "references/profiles/manuscript.md").is_file(), "fresh install includes manuscript Profile")

            case_root = new_review_case(root, "integration", "manuscript")
            scenario = ManuscriptScenario(case_root)
            acceptance = case_root / "acceptance.md"
            acceptance.write_text("Approved ManuscriptBrief and final deliverable revision 1", encoding="utf-8")
            scenario.initialize(acceptance)
            c.check(scenario.state().profile == "manuscript" and scenario.state().charter_revision == "approved-manuscript-brief-r3", "manuscript init freezes Profile and Brief revision")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-001", specialist_verdict="PASS")
            c.check(scenario.state().status == "CRITIC", "specialist PASS remains evidence while Core is in CRITIC")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-001")
            c.check(scenario.state().status == "REPAIR", "manuscript finding enters generic REPAIR lifecycle")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=True, independent_context=True)
            evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            verdict = (case_root / ".review-loop/verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, evaluator, overall_outcome="PASS", format_outcome="PASS", image_label="structural", name="fresh Evaluator records non-image manuscript axes and Core owns final PASS")
            c.check(scenario.state().status == "PASS" and "Issued by: review-loop Core" in verdict, "Core verdict record is separate from Evaluator evidence")

            producer = (case_root / ".review-loop/rounds/round-01/producer-evidence.md").read_text(encoding="utf-8")
            c.check("Image axis: not applicable" in producer and "negative audit recorded" in producer, "image axis remains explicit when no image trigger applies")

            case_root = new_review_case(root, "triggered-image", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(image_triggered=True, image_evidence=True)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-007", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-007")
            scenario.evaluate(c, passed=True, independent_context=True)
            image_producer = (case_root / ".review-loop/rounds/round-01/producer-evidence.md").read_text(encoding="utf-8")
            image_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, image_evaluator, overall_outcome="PASS", format_outcome="PASS", image_label="manual", name="triggered image Evaluator maps AC-7 to manual evidence")
            c.check(scenario.state().status == "PASS" and "source/rights/placement/caption/annotation/alt-text evidence recorded" in image_producer, "triggered image axis passes with complete evidence")

            case_root = new_review_case(root, "triggered-image-missing-evidence", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round(image_triggered=True, image_evidence=False)
            scenario.write_specialist_report(disposition="rejected", finding_id="F-008", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-008")
            scenario.evaluate(c, passed=True, independent_context=True)
            missing_image_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, missing_image_evaluator, overall_outcome="BLOCKED", format_outcome="BLOCKED", image_label="manual", name="triggered image Evaluator retains manual AC-7 mapping when blocked")
            c.check(scenario.state().status == "BLOCKED" and "triggered image axis evidence unavailable" in scenario.state().raw, "triggered image axis blocks without complete image evidence")

            case_root = new_review_case(root, "missing-source", "manuscript")
            scenario = ManuscriptScenario(case_root)
            scenario.initialize(case_root / "missing-acceptance.md")
            c.check(scenario.state().status == "BLOCKED" and bool(re.search(r"(?m)^Blocker: missing approved Brief/Charter", scenario.state().raw)), "missing approved manuscript source blocks init")

            case_root = new_review_case(root, "bounded-repair", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-002", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-002")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True)
            failed_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, failed_evaluator, overall_outcome="FAIL", format_outcome="PASS", image_label="structural", name="failed manuscript Evaluator records all axes and valid labels")
            revision = scenario.state().charter_revision
            c.check(scenario.state().status == "FAIL" and revision == "approved-manuscript-brief-r3", "failed manuscript round retains frozen Charter and bounded next round")
            scenario.start_next_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-002", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-002")
            scenario.evaluate(c, passed=True, independent_context=True)
            recheck_evaluator = (case_root / ".review-loop/rounds/round-02/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, recheck_evaluator, overall_outcome="PASS", format_outcome="PASS", image_label="structural", name="rechecked manuscript Evaluator records all axes and valid labels")
            registry = (case_root / ".review-loop/findings.md").read_text(encoding="utf-8")
            c.check(scenario.state().status == "PASS" and len(re.findall(r"(?:Finding|Re-observed) F-002", registry)) == 2 and "Disposition: rejected" in registry, "bounded recheck preserves stable manuscript finding ID")

            case_root = new_review_case(root, "scope-change", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-003", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-003")
            scenario.apply_repair(False)
            c.check(scenario.state().status == "FAIL" and "scope-changing" in scenario.state().next and not (case_root / ".review-loop/rounds/round-01/repair-evidence-F-003.md").is_file(), "scope-changing manuscript repair is rejected without Producer edit")

            case_root = new_review_case(root, "format-evidence-block", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-004", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-004")
            scenario.evaluate(c, passed=True, independent_context=True, format_evidence=False)
            blocked_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, blocked_evaluator, overall_outcome="BLOCKED", format_outcome="BLOCKED", image_label="structural", name="format-blocked manuscript Evaluator records all axes and valid labels")
            c.check(scenario.state().status == "BLOCKED" and bool(re.search(r"(?m)^Blocker: blocking format QA unavailable", scenario.state().raw)), "missing required render/visual evidence blocks manuscript acceptance")

            case_root = new_review_case(root, "independence-block", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="rejected", finding_id="F-005", specialist_verdict="PASS")
            scenario.ingest_finding(disposition="rejected", finding_id="F-005")
            scenario.evaluate(c, passed=True, independent_context=False)
            independence_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, independence_evaluator, overall_outcome="BLOCKED", format_outcome="BLOCKED", image_label="structural", name="independence-blocked manuscript Evaluator records all axes and valid labels")
            c.check(scenario.state().status == "BLOCKED" and "independent Evaluator" in scenario.state().next, "missing independent context blocks manuscript verdict")

            case_root = new_review_case(root, "maximum-round", "manuscript")
            scenario = ManuscriptScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved ManuscriptBrief revision 1", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.write_specialist_report(disposition="confirmed", finding_id="F-006", specialist_verdict="FAIL")
            scenario.ingest_finding(disposition="confirmed", finding_id="F-006")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, format_evidence=True, maximum_round=1)
            limit_evaluator = (case_root / ".review-loop/rounds/round-01/evaluator-verdict.md").read_text(encoding="utf-8")
            assert_manuscript_evaluator_record(c, limit_evaluator, overall_outcome="BLOCKED", format_outcome="BLOCKED", image_label="structural", name="maximum-round manuscript Evaluator records all axes and valid labels")
            c.check(scenario.state().status == "BLOCKED" and bool(re.search(r"(?m)^Blocker: maximum rounds", scenario.state().raw)), "maximum repair round returns generic BLOCKED")

        self.assertFalse(c.failures, f"manuscript-profile behavior failed: {c.failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
