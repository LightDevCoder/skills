"""Public-contract checks for the model-invoked clarification engine.

These are deterministic contract tests, not a claim that a host ran a live
model conversation. The scenarios pin the observable rules a host must load
from the package instructions.
"""

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


class SocraticPublicContractTest(unittest.TestCase):
    def test_model_engine_keeps_a_dynamic_decision_frontier(self) -> None:
        skill, metadata = read_public_contract()
        joined = skill + "\n" + metadata

        self.assertRegex(skill, r"(?m)^name: socratic$")
        self.assertIn("model-invoked", joined)
        for state_field in (
            "current understanding",
            "open decisions",
            "dependencies",
            "frontier",
            "newly resolved decisions",
        ):
            self.assertIn(state_field, skill.lower())
        self.assertRegex(skill, r"(?is)(recompute|update).{0,120}frontier")
        self.assertIn("fixed questionnaire", skill)
        self.assertRegex(skill, r"(?is)fact.*decision|facts are not user decisions")

    def test_missing_capability_is_reported_as_a_gap_not_a_fabricated_answer(self) -> None:
        skill, _ = read_public_contract()
        attribution = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + "\n" + workflow

        self.assertIn("not callable", skill.lower())
        self.assertIn("missing capability", skill.lower())
        self.assertIn("unresolved", combined.lower())
        self.assertRegex(skill, r"(?is)not callable|missing capability")
        self.assertIn("mattpocock/skills", attribution)
        self.assertIn("v1.2.3", attribution)
        self.assertIn("Copyright (c) 2026 Matt Pocock", attribution)

    def test_unknown_routing_declares_composition_without_reimplementing(self) -> None:
        skill, _ = read_public_contract()
        self.assertIn("Unknown", skill)
        for target in ("research", "prototype", "to-questionnaire"):
            self.assertIn(target, skill)
        self.assertIn("calling wrapper authorizes", skill)
        self.assertIn("references/WORKFLOW.md", skill)
        self.assertIn("references/ROUTING.md", skill)

    def test_supporting_files_resolve(self) -> None:
        for name in ("references/WORKFLOW.md", "references/EXAMPLES.md", "references/ROUTING.md"):
            self.assertTrue((ROOT / name).is_file(), f"missing {name}")
        workflow = (ROOT / "references/WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("frontier", workflow.lower())
        self.assertIn("Decision ownership", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)