"""Public-contract checks for the explicit standalone clarification entry."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_public_contract(root: Path = ROOT) -> tuple[str, str]:
    return (
        (root / "SKILL.md").read_text(encoding="utf-8"),
        (root / "agents" / "openai.yaml").read_text(encoding="utf-8"),
    )


class ClarifyPublicContractTest(unittest.TestCase):
    def test_explicit_entry_uses_the_model_engine_and_returns_a_summary(self) -> None:
        skill, metadata = read_public_contract()

        self.assertRegex(skill, r"(?m)^name: clarify$")
        self.assertRegex(skill, r"(?m)^disable-model-invocation: true$")
        self.assertRegex(metadata, r"(?m)^\s*allow_implicit_invocation: false$")
        self.assertRegex(skill, r"(?is)explicit.*\$clarify.{0,220}socratic")
        for result_field in ("Current understanding", "Resolved decisions", "Still unresolved decisions"):
            self.assertIn(result_field, skill)
        self.assertRegex(skill, r"(?is)(stop|return).{0,160}user")

    def test_missing_dependency_is_reported_as_a_gap_not_a_fabricated_answer(self) -> None:
        skill, _ = read_public_contract()
        attribution = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")

        self.assertIn("fact-finding gap", skill)
        # The composition surface names the fact capabilities without claiming
        # to execute them itself.
        for capability in ("research", "prototype", "to-questionnaire"):
            self.assertIn(capability, skill)
        self.assertRegex(skill, r"(?is)invent an answer|do not\s+invent")
        self.assertIn("mattpocock/skills", attribution)
        self.assertIn("skills/productivity/grill-me/", attribution)
        self.assertIn("v1.2.3", attribution)
        self.assertIn("Copyright (c) 2026 Matt Pocock", attribution)

    def test_composition_before_duplication(self) -> None:
        skill, _ = read_public_contract()
        # must compose via socratic, not copy its state definition
        self.assertIn("clarify → socratic", skill)
        self.assertIn("does not reimplement", skill)
        self.assertIn("references/WORKFLOW.md", skill)
        self.assertIn("references/EXAMPLES.md", skill)

    def test_supporting_files_resolve(self) -> None:
        for name in ("references/WORKFLOW.md", "references/EXAMPLES.md", "references/ROUTING.md"):
            self.assertTrue((ROOT / name).is_file(), f"missing {name}")
        wf = (ROOT / "references/WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("socratic", wf.lower())
        self.assertIn("$clarify", wf)


if __name__ == "__main__":
    unittest.main(verbosity=2)