"""Port of skills/review-loop/tests/generic-profile-behavior-tests.ps1."""

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
    get_review_state,
    new_review_case,
    new_review_next_round,
    new_review_round,
    set_review_state,
)


class GenericScenario:
    def __init__(self, case_root: Path) -> None:
        self.case_root = case_root

    def state(self):
        return get_review_state(self.case_root)

    def set_state(self, target: str, round_no: int, next_action: str, charter_revision: str = "") -> None:
        current = self.state()
        if not charter_revision:
            charter_revision = current.charter_revision
        if not charter_revision:
            charter_revision = "fixture-1"
        blocker = next_action if target == "BLOCKED" else "none"
        set_review_state(self.case_root, target, round_no, next_action, "generic", charter_revision, "", "protocol transition", blocker)

    def initialize(self, acceptance_source: Path) -> None:
        if not acceptance_source.is_file():
            self.set_state("BLOCKED", 0, "record missing acceptance source")
            return
        self.set_state("READY", 0, "collect Producer evidence")

    def resume_source_blocked(self) -> None:
        state = self.state()
        if state.status != "BLOCKED":
            raise ValueError("Resume-Blocked requires BLOCKED state")
        if not re.search(r"missing acceptance source", state.next):
            raise ValueError("Resume-SourceBlocked requires a source blocker")
        self.set_state("READY", state.round, "collect Producer evidence")

    def start_round(self) -> Path:
        return new_review_round(self.case_root, "generic", "request read-only Critic", [
            "Scope: disposable fixture acceptance target",
            "Evidence class: executable protocol scenario",
            "Inputs: approved acceptance source and fixture artifact",
        ])

    def record_candidate(self, finding_id: str, disposition: str) -> None:
        if self.state().status != "CRITIC":
            raise ValueError("Candidates require CRITIC state")
        if not re.match(r"^F-\d{3}$", finding_id):
            raise ValueError(f"Invalid finding ID: {finding_id}")
        path = self.case_root / ".project-review" / "findings.md"
        records = [
            f"Finding {finding_id}",
            f"Disposition: {disposition}",
            "Evidence: executable protocol scenario",
        ]
        if path.is_file():
            existing = path.read_text(encoding="utf-8", errors="replace")
            if f"Finding {finding_id}" in existing:
                records = [
                    f"Re-observed {finding_id} in round {self.state().round}",
                    f"Disposition: {disposition}",
                    "Evidence: executable protocol scenario",
                ]
                with path.open("a", encoding="utf-8") as fh:
                    fh.write("\n".join(records) + "\n")
            else:
                with path.open("a", encoding="utf-8") as fh:
                    fh.write("\n".join(records) + "\n")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(records) + "\n", encoding="utf-8")
        if disposition == "confirmed":
            self.set_state("REPAIR", self.state().round, "direct bounded repair to Producer")
        else:
            self.set_state("EVALUATE", self.state().round, "fresh Evaluator")

    def apply_repair(self, in_scope: bool) -> None:
        if self.state().status != "REPAIR":
            raise ValueError("Repairs require REPAIR state")
        round_path = self.case_root / f".project-review/rounds/round-{self.state().round:02d}"
        if not in_scope:
            self.set_state("FAIL", self.state().round, "scope-changing repair rejected")
            return
        finding_id = re.search(r"Finding (F-\d{3})", (self.case_root / ".project-review/findings.md").read_text(encoding="utf-8")).group(1)
        round_path.mkdir(parents=True, exist_ok=True)
        (round_path / "repair-evidence.md").write_text("\n".join([
            f"Finding: {finding_id}",
            "Producer repair evidence: bounded and in-scope",
            "Validation: focused executable protocol scenario",
        ]) + "\n", encoding="utf-8")
        self.set_state("EVALUATE", self.state().round, "request fresh Evaluator")

    def evaluate(self, c: Checks, *, passed: bool, independent_context: bool, repair_available: bool, maximum_round: int) -> None:
        if self.state().status != "EVALUATE":
            raise ValueError("Evaluation requires EVALUATE state")
        state = self.state()
        if not independent_context:
            self.set_state("BLOCKED", state.round, "obtain independent Evaluator context")
            return
        if passed:
            path = self.case_root / ".project-review" / "findings.md"
            if path.is_file():
                with path.open("a", encoding="utf-8") as fh:
                    fh.write("Status: resolved; Resolution evidence: fresh Evaluator\n")
            round_path = self.case_root / f".project-review/rounds/round-{state.round:02d}"
            round_path.mkdir(parents=True, exist_ok=True)
            (round_path / "evaluator-verdict.md").write_text("\n".join([
                f"# Evaluator Verdict - Round {state.round:02d}",
                "Context: fresh independent read-only Evaluator",
                "Criterion AC-1 (frozen acceptance source): PASS - source and fixture evidence retained",
                "Criterion AC-2 (generic lifecycle): PASS - findings and bounded repair evidence retained",
                "Open blocking findings: none",
                "Verdict recommendation: PASS",
            ]) + "\n", encoding="utf-8")
            self.set_state("PASS", state.round, "preserve verdict")
            return
        if repair_available and state.round < maximum_round:
            self.set_state("FAIL", state.round, "CRITIC (next round); bounded repair remains")
        else:
            self.set_state("BLOCKED", state.round, "repair limit reached")

    def resume_next_round(self) -> None:
        new_review_next_round(self.case_root, "generic", "validate existing Finding ID", [
            "Scope: disposable fixture acceptance target; next round",
            "Evidence class: executable protocol scenario",
        ])


class GenericProfileBehaviorTest(unittest.TestCase):
    def test_generic_profile_behavior(self) -> None:
        c = Checks()
        with tempfile.TemporaryDirectory(prefix="review-loop-behavior-") as tmp:
            root = Path(tmp)
            install_root = root / "installed-review-loop"
            shutil.copytree(ROOT, install_root)
            c.check((install_root / "SKILL.md").is_file(), "fresh-install discovers SKILL.md")
            c.check((install_root / "agents/openai.yaml").is_file(), "fresh-install discovers metadata")
            skill_text = (install_root / "SKILL.md").read_text(encoding="utf-8")
            stopping_text = (install_root / "references/stopping-rules.md").read_text(encoding="utf-8")
            c.check(bool(re.search(r"(?i)model-invoked and may also be manually invoked", skill_text)), "invocation contract is model/manual")
            state_section = stopping_text.split("Record the Charter")[0]
            c.check(bool(re.search(r"(?s)FAIL.*CRITIC \(next round\)", stopping_text)) and "SKIPPED" not in state_section, "state machine documents bounded next round")

            case_root = new_review_case(root, "missing-source", "generic")
            scenario = GenericScenario(case_root)
            missing = case_root / "acceptance.md"
            scenario.initialize(missing)
            c.check(scenario.state().status == "BLOCKED", "missing acceptance source blocks init")
            missing.write_text("Approved acceptance source", encoding="utf-8")
            scenario.resume_source_blocked()
            c.check(scenario.state().status == "READY", "resume after source unblock reaches READY")

            case_root = new_review_case(root, "bounded-repair", "generic")
            scenario = GenericScenario(case_root)
            acceptance = case_root / "acceptance.md"
            acceptance.write_text("Approved acceptance source", encoding="utf-8")
            scenario.initialize(acceptance)
            scenario.start_round()
            scenario.record_candidate("F-001", "confirmed")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, repair_available=True, maximum_round=3)
            c.check(scenario.state().status == "FAIL" and "next round" in scenario.state().next, "failed round preserves bounded repair path")
            scenario.resume_next_round()
            scenario.record_candidate("F-001", "confirmed")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=True, independent_context=True, repair_available=True, maximum_round=3)
            finding = (case_root / ".project-review/findings.md").read_text(encoding="utf-8")
            repair_evidence = (case_root / ".project-review/rounds/round-02/repair-evidence.md").read_text(encoding="utf-8")
            producer_evidence = (case_root / ".project-review/rounds/round-01/producer-evidence.md").read_text(encoding="utf-8")
            evaluator_verdict = (case_root / ".project-review/rounds/round-02/evaluator-verdict.md").read_text(encoding="utf-8")
            c.check(
                scenario.state().status == "PASS" and "F-001" in finding and "Status: resolved" in finding
                and "Finding: F-001" in repair_evidence and "Validation:" in repair_evidence
                and "Evidence class:" in producer_evidence
                and bool(re.search(r"Criterion AC-1.*PASS", evaluator_verdict)),
                "bounded repair reaches PASS with stable resolved ID",
            )

            case_root = new_review_case(root, "rejected-candidate", "generic")
            scenario = GenericScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved acceptance source", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.record_candidate("F-002", "rejected")
            scenario.evaluate(c, passed=True, independent_context=True, repair_available=False, maximum_round=3)
            c.check(scenario.state().status == "PASS" and not (case_root / ".project-review/rounds/round-01/repair-evidence.md").is_file(), "rejected candidate bypasses Producer repair")

            case_root = new_review_case(root, "scope-change", "generic")
            scenario = GenericScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved acceptance source", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.record_candidate("F-003", "confirmed")
            scenario.apply_repair(False)
            c.check(scenario.state().status == "FAIL" and "scope-changing" in scenario.state().next, "scope-changing repair returns FAIL")

            case_root = new_review_case(root, "missing-context", "generic")
            scenario = GenericScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved acceptance source", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.record_candidate("F-004", "rejected")
            scenario.evaluate(c, passed=False, independent_context=False, repair_available=False, maximum_round=3)
            c.check(scenario.state().status == "BLOCKED", "missing independent context returns BLOCKED")

            case_root = new_review_case(root, "maximum-round", "generic")
            scenario = GenericScenario(case_root)
            (case_root / "acceptance.md").write_text("Approved acceptance source", encoding="utf-8")
            scenario.initialize(case_root / "acceptance.md")
            scenario.start_round()
            scenario.record_candidate("F-005", "confirmed")
            scenario.apply_repair(True)
            scenario.evaluate(c, passed=False, independent_context=True, repair_available=True, maximum_round=1)
            c.check(scenario.state().status == "BLOCKED" and "repair limit" in scenario.state().next, "maximum-round stop returns BLOCKED")

        self.assertGreater(c.assertions, 0)
        self.assertFalse(c.failures, f"generic-profile behavior failed: {c.failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
