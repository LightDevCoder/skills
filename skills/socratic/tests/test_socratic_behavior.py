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
    def test_convergence_does_not_repeat_resolved_decisions(self) -> None:
        skill = skill_text()
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + "\n" + workflow

        # Treat answer as evidence, mark newly resolved, recompute frontier
        self.assertIn("Do not repeat", skill)
        self.assertIn("newly resolved", skill.lower())
        self.assertIn("recompute", skill.lower() + workflow.lower())
        # dynamic follow-up, not fixed questionnaire
        self.assertRegex(skill, r"(?is)dynamic.*follow|expand along.*answer")
        self.assertRegex(combined, r"(?is)do not manufacture.*fixed.*question|prewritten questionnaire|fixed questionnaire")

    def test_fact_gaps_block_downstream_decisions(self) -> None:
        skill = skill_text()
        routing = routing_text()

        # dependency blocks frontier
        self.assertIn("downstream", skill)
        self.assertIn("not part of the frontier", skill)
        # unknown routing
        for line in ("user must decide", "external fact", "needs experiment", "held by another"):
            self.assertIn(line, routing.lower() if line in routing.lower() else skill.lower() + routing.lower())

    def test_missing_capability_reports_gap_without_chaining(self) -> None:
        skill = skill_text()
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + "\n" + workflow

        self.assertIn("not callable", skill.lower())
        self.assertIn("retain the fact as unresolved", skill.lower() if "retain the fact as unresolved" in skill.lower() else skill)
        self.assertIn("missing capability", skill.lower())
        self.assertRegex(combined, r"(?is)do not invent.*(answer|work)|do not.{0,50}convert.{0,50}decision")

    def test_engine_does_not_auto_chain_user_skills(self) -> None:
        skill = skill_text()

        self.assertIn("does not automatically invoke another user-invoked Skill", skill)
        self.assertIn("does not automatically", skill)
        self.assertIn("formal SPEC", skill)


if __name__ == "__main__":
    unittest.main(verbosity=2)
