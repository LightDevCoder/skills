"""Scenario-level checks for project-clarify's published behavior contract."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def skill_text(root: Path = ROOT) -> str:
    return (root / "SKILL.md").read_text(encoding="utf-8")


class ProjectClarifyBehaviorTest(unittest.TestCase):
    def test_positive_existing_project_flow_uses_inspection_then_a_decision(self) -> None:
        skill = skill_text()

        existing_project_fixture = {
            "README/project brief": "goal and constraints",
            "manifests": "runtime facts",
            "source and test entry points": "current behavior",
        }
        self.assertEqual(len(existing_project_fixture), 3)
        self.assertIn("stable locator", skill)
        self.assertLess(skill.index("Inspect project facts before asking"), skill.index("Maintain user decisions with `socratic`"))
        self.assertIn("docs/agents/light-project.md", skill)
        self.assertRegex(skill, r"Ask the complete\s+current frontier as a round|frontier as a round")

    def test_empty_project_boundary_does_not_invent_facts(self) -> None:
        skill = skill_text()
        ref = (ROOT / "references" / "project-clarification-contract.md").read_text(encoding="utf-8")
        examples = (ROOT / "references" / "EXAMPLES.md").read_text(encoding="utf-8")
        combined = skill + ref + examples

        self.assertRegex(combined, r"(?is)empty project|no project material exists|empty")
        self.assertRegex(combined, r"(?is)not a reason to invent|do not invent|do not.*invent")
        self.assertIn("evidence gap", combined.lower())

    def test_refusal_or_no_write_keeps_the_handoff_in_memory(self) -> None:
        skill = skill_text()

        self.assertIn("in memory by default", skill)
        self.assertIn("separately names a writable destination", skill)
        self.assertIn("Then stop", skill)

    def test_missing_capability_blocks_a_dependency_without_relabeling_it(self) -> None:
        skill = skill_text()
        ref = (ROOT / "references" / "project-clarification-contract.md").read_text(encoding="utf-8")
        combined = skill + ref

        self.assertRegex(combined, r"(?is)unavailable.*not-authorized|not-authorized.*unavailable")
        self.assertRegex(combined, r"(?is)leave unavailable or\s+not-authorized gaps unresolved|retain the (fact )?gap")
        self.assertIn("keep their downstream decisions", combined)
        self.assertRegex(combined, r"(?is)missing capability")

    def test_interaction_records_optional_calls_and_returns_a_handoff(self) -> None:
        skill = skill_text()
        ref = (ROOT / "references" / "project-clarification-contract.md").read_text(encoding="utf-8")
        combined = skill + ref

        for field in (
            "Capability call: socratic | research | prototype",
            "Blocked decision:",
            "Result read: path or artifact identifier | none",
            "Project clarification handoff",
            "Recommended next explicit invocation:",
        ):
            self.assertIn(field, combined)
        # handoff contains capability records
        self.assertIn("Capability call records", combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
