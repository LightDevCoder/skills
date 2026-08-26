"""Behavior checks for socratic convergence and routing."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def skill_text() -> str:
    return (ROOT / "SKILL.md").read_text(encoding="utf-8")


def routing_text() -> str:
    return (ROOT / "references" / "ROUTING.md").read_text(encoding="utf-8")


class SocraticBehaviorTest(unittest.TestCase):
    def test_convergence_marks_resolved_decisions_and_recomputes_the_frontier(self) -> None:
        skill = skill_text()
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + "\n" + workflow

        self.assertIn("newly resolved", skill.lower())
        self.assertIn("recompute", skill.lower() + workflow.lower())
        self.assertIn("dynamic follow-up", skill.lower())
        self.assertIn("fixed questionnaire", skill.lower())

    def test_fact_gaps_block_downstream_decisions(self) -> None:
        skill = skill_text()
        routing = routing_text()

        # dependency blocks frontier
        self.assertIn("downstream", skill)
        self.assertIn("out of the frontier", skill)
        # unknown routing
        for line in ("user must decide", "external fact", "needs experiment", "held by another"):
            self.assertIn(line, routing.lower() if line in routing.lower() else skill.lower() + routing.lower())

    def test_missing_capability_reports_gap_without_chaining(self) -> None:
        skill = skill_text()
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + "\n" + workflow

        self.assertIn("not callable", skill.lower())
        self.assertIn("missing capability", skill.lower())
        self.assertIn("retain the fact as unresolved", combined.lower())

    def test_engine_returns_state_and_stops_for_the_calling_wrapper(self) -> None:
        skill = skill_text()

        self.assertIn("return the state update and stop", skill.lower())
        self.assertIn("calling wrapper authorizes", skill.lower())
        # The engine's output is a state update, not automatic execution.
        self.assertIn("Next step", skill)


if __name__ == "__main__":
    unittest.main(verbosity=2)