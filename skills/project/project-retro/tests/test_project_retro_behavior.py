"""Behavioral checks for project-retro evaluation logic, heuristics, and deduplication."""

from __future__ import annotations

import unittest
from typing import NamedTuple, Literal


FindingStatus = Literal["CLOSED", "PARTIAL", "OPEN"]
RetroState = Literal["GATHERING", "EVALUATING", "AWAITING_SELECTION", "APPROVED_ACTION"]


class RecommendationLifecycle:
    def __init__(self, findings: list[RetroFinding]) -> None:
        self.findings = findings
        self.state: RetroState = "GATHERING"
        self.suggested_actions: list[str] = []
        self.approved_action: str | None = None

    def present_findings(self) -> None:
        """Present findings and transition retrospective to AWAITING_SELECTION."""
        self.suggested_actions = filter_suggested_actions(self.findings)
        self.state = "AWAITING_SELECTION"

    def select_action(self, action: str) -> None:
        """Transition selected item to APPROVED_ACTION upon human selection."""
        if self.state != "AWAITING_SELECTION":
            raise ValueError(f"Cannot select action while in state {self.state}")
        if action not in self.suggested_actions:
            raise ValueError(f"Action '{action}' is not in suggested actions: {self.suggested_actions}")
        self.approved_action = action
        self.state = "APPROVED_ACTION"



class FrictionEvent(NamedTuple):
    category: str
    description: str
    weight: str  # "High", "Moderate", "Low"


class RetroFinding(NamedTuple):
    category: str
    title: str
    severity: str  # "High", "Medium", "Low"
    status: FindingStatus
    has_durable_guardrail_at_head: bool
    proposed_action: str | None


def evaluate_retro_trigger(events: list[FrictionEvent]) -> tuple[bool, str]:
    """Evaluate whether the agent should invoke project-retro based on session friction."""
    high_count = sum(1 for e in events if e.weight == "High")
    mod_count = sum(1 for e in events if e.weight == "Moderate")

    if high_count >= 1:
        return True, f"Trigger: {high_count} high-severity friction event(s) detected."
    if mod_count >= 2:
        return True, f"Trigger: {mod_count} moderate friction event(s) detected."
    return False, "Skip: Clean session with minimal or no friction."


def sort_findings_by_severity(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    """Sort retrospective findings by severity: High > Medium > Low."""
    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(findings, key=lambda f: severity_order.get(f.get("severity", "Low"), 3))


def filter_suggested_actions(findings: list[RetroFinding], limit: int = 3) -> list[str]:
    """Extract bounded suggested actions from OPEN and PARTIAL findings only.

    CLOSED findings already have verified durable guardrails and must NOT generate
    duplicate suggested action items.
    """
    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    actionable = [f for f in findings if f.status in ("OPEN", "PARTIAL") and f.proposed_action]
    sorted_actionable = sorted(actionable, key=lambda f: severity_order.get(f.severity, 3))
    return [f.proposed_action for f in sorted_actionable if f.proposed_action][:limit]


class ProjectRetroBehaviorTest(unittest.TestCase):
    def test_smooth_session_skips_retro(self) -> None:
        """Scenario 1: A session with no friction events must skip project-retro."""
        events: list[FrictionEvent] = []
        should_trigger, reason = evaluate_retro_trigger(events)
        self.assertFalse(should_trigger)
        self.assertIn("Skip", reason)

    def test_single_low_or_moderate_friction_skips_retro(self) -> None:
        """Isolated minor friction does not warrant full retrospective overhead."""
        events = [
            FrictionEvent(
                category="Tool Economy",
                description="Read one 60KB file once",
                weight="Low",
            )
        ]
        should_trigger, reason = evaluate_retro_trigger(events)
        self.assertFalse(should_trigger)
        self.assertIn("Skip", reason)

        events = [
            FrictionEvent(
                category="Navigation",
                description="Took 2 searches to find test file",
                weight="Moderate",
            )
        ]
        should_trigger, reason = evaluate_retro_trigger(events)
        self.assertFalse(should_trigger)
        self.assertIn("Skip", reason)

    def test_high_weight_friction_triggers_retro(self) -> None:
        """Missing automated guardrail or unwired CI triggers project-retro."""
        events = [
            FrictionEvent(
                category="Guardrails",
                description="Syntax error escaped to review because no pre-commit linter existed",
                weight="High",
            )
        ]
        should_trigger, reason = evaluate_retro_trigger(events)
        self.assertTrue(should_trigger)
        self.assertIn("Trigger", reason)

    def test_multiple_moderate_frictions_trigger_retro(self) -> None:
        """Accumulated moderate friction (navigation + reviewer gap) triggers retro."""
        events = [
            FrictionEvent(
                category="Navigation",
                description="Repeatedly searched for unindexed dependency",
                weight="Moderate",
            ),
            FrictionEvent(
                category="Standards",
                description="Reviewer missed mechanical naming violation",
                weight="Moderate",
            ),
        ]
        should_trigger, reason = evaluate_retro_trigger(events)
        self.assertTrue(should_trigger)
        self.assertIn("Trigger", reason)

    def test_findings_ordered_by_severity(self) -> None:
        """Findings must be ordered by severity High -> Medium -> Low."""
        raw_findings = [
            {"title": "Unindexed docs", "severity": "Low", "category": "Navigation"},
            {"title": "Missing CI pre-commit hook", "severity": "High", "category": "Automated checks"},
            {"title": "Bloated AGENTS.md instructions", "severity": "Medium", "category": "Steering economy"},
        ]
        sorted_findings = sort_findings_by_severity(raw_findings)
        self.assertEqual(sorted_findings[0]["severity"], "High")
        self.assertEqual(sorted_findings[1]["severity"], "Medium")
        self.assertEqual(sorted_findings[2]["severity"], "Low")
        self.assertEqual(sorted_findings[0]["title"], "Missing CI pre-commit hook")

    def test_scenario_2_historical_problem_closed_generates_no_duplicate_action(self) -> None:
        """Scenario 2: A historical problem verified closed at HEAD generates no suggested action."""
        findings = [
            RetroFinding(
                category="Automated checks",
                title="Evaluation fixture label leakage",
                severity="High",
                status="CLOSED",
                has_durable_guardrail_at_head=True,
                proposed_action="Add fixture isolation test",  # should be ignored because status is CLOSED
            ),
            RetroFinding(
                category="Automated checks",
                title="Missing release tag immutability guard",
                severity="High",
                status="OPEN",
                has_durable_guardrail_at_head=False,
                proposed_action="Add scripts/verify_release_integrity.py",
            ),
        ]
        actions = filter_suggested_actions(findings)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], "Add scripts/verify_release_integrity.py")
        self.assertNotIn("Add fixture isolation test", actions)

    def test_scenario_3_and_4_and_5_bounded_top_actions(self) -> None:
        """Scenarios 3, 4, 5: Bounded top-3 actions from multiple OPEN/PARTIAL findings."""
        findings = [
            RetroFinding(
                category="Automated checks",
                title="Release tag retargeting",
                severity="High",
                status="OPEN",
                has_durable_guardrail_at_head=False,
                proposed_action="1. Add scripts/verify_release_integrity.py",
            ),
            RetroFinding(
                category="Information access",
                title="Official CLI conventions unreferenced",
                severity="Medium",
                status="OPEN",
                has_durable_guardrail_at_head=False,
                proposed_action="2. Document canonical Skills CLI conventions in references/",
            ),
            RetroFinding(
                category="Test architecture",
                title="Cross-repo sibling dependency coupling",
                severity="Medium",
                status="PARTIAL",
                has_durable_guardrail_at_head=False,
                proposed_action="3. Establish Layer 1 hermetic schema snapshot and Layer 2 drift test",
            ),
            RetroFinding(
                category="Steering economy",
                title="Stale workspace pointer in AGENTS.md",
                severity="Low",
                status="OPEN",
                has_durable_guardrail_at_head=False,
                proposed_action="4. Update AGENTS.md with dynamic wayfinding rule",
            ),
        ]
        actions = filter_suggested_actions(findings, limit=3)
        self.assertEqual(len(actions), 3)
        self.assertIn("1. Add scripts/verify_release_integrity.py", actions)
        self.assertIn("2. Document canonical Skills CLI conventions in references/", actions)
        self.assertIn("3. Establish Layer 1 hermetic schema snapshot and Layer 2 drift test", actions)
        self.assertNotIn("4. Update AGENTS.md with dynamic wayfinding rule", actions)

    def test_recommendation_lifecycle_state_transitions(self) -> None:
        """Retrospective findings transition to AWAITING_SELECTION, then APPROVED_ACTION upon human selection."""
        findings = [
            RetroFinding(
                category="Automated checks",
                title="Tag immutability guard",
                severity="High",
                status="OPEN",
                has_durable_guardrail_at_head=False,
                proposed_action="Add verify_release_integrity.py to CI",
            ),
            RetroFinding(
                category="Automated checks",
                title="Historical label leak",
                severity="High",
                status="CLOSED",
                has_durable_guardrail_at_head=True,
                proposed_action="Add fixture test",
            ),
        ]
        lifecycle = RecommendationLifecycle(findings)
        self.assertEqual(lifecycle.state, "GATHERING")

        lifecycle.present_findings()
        self.assertEqual(lifecycle.state, "AWAITING_SELECTION")
        self.assertEqual(lifecycle.suggested_actions, ["Add verify_release_integrity.py to CI"])
        self.assertIsNone(lifecycle.approved_action)

        lifecycle.select_action("Add verify_release_integrity.py to CI")
        self.assertEqual(lifecycle.state, "APPROVED_ACTION")
        self.assertEqual(lifecycle.approved_action, "Add verify_release_integrity.py to CI")

    def test_selection_fails_if_not_awaiting_selection(self) -> None:
        """Cannot transition to APPROVED_ACTION before findings are presented."""
        lifecycle = RecommendationLifecycle([])
        with self.assertRaises(ValueError):
            lifecycle.select_action("Some action")



if __name__ == "__main__":
    unittest.main(verbosity=2)
