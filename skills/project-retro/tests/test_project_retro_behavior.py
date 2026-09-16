"""Behavioral checks for project-retro evaluation logic and heuristics."""

from __future__ import annotations

import unittest
from typing import NamedTuple


class FrictionEvent(NamedTuple):
    category: str
    description: str
    weight: str  # "High", "Moderate", "Low"


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


class ProjectRetroBehaviorTest(unittest.TestCase):
    def test_smooth_session_skips_retro(self) -> None:
        """A session with no friction events must skip project-retro."""
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
