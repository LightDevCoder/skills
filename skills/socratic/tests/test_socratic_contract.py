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
            self.assertIn(state_field, skill)
        # dynamic follow-up and frontier recomputation
        self.assertRegex(skill, r"(?is)answers?.{0,180}(recompute|adjust).{0,180}frontier")
        # must avoid fixed questionnaire
        self.assertRegex(skill, r"(?is)fixed questionnaire|avoid.*questionnaire|not.*fixed.*questionnaire")
        # must distinguish fact vs decision
        self.assertRegex(skill, r"(?is)distinguish.*fact.*decision|fact.*decision")

    def test_fact_dependency_is_not_reframed_as_a_user_choice(self) -> None:
        skill, _ = read_public_contract()
        attribution = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")
        workflow = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
        combined = skill + "\n" + workflow

        # Failure/missing-dependency fixture: source facts need a capability
        # that is unavailable. The public contract must preserve the blocked
        # fact and report the gap instead of claiming a fabricated result.
        self.assertRegex(skill, r"(?is)not callable.{0,160}unresolved.{0,160}missing")
        self.assertRegex(combined, r"(?is)Do not claim.{0,160}started or completed")
        self.assertRegex(combined, r"(?is)Do not.{0,100}convert.{0,100}dependency.{0,100}decision")
        self.assertIn("formal SPEC", skill)
        self.assertIn("mattpocock/skills", attribution)
        self.assertIn("v1.2.3", attribution)
        self.assertIn("Copyright (c) 2026 Matt Pocock", attribution)

    def test_unknown_routing_declares_composition_without_reimplementing(self) -> None:
        skill, _ = read_public_contract()
        self.assertIn("Unknown", skill)
        for target in ("research", "prototype", "to-questionnaire"):
            self.assertIn(target, skill)
        # must declare routing not reimplement
        self.assertRegex(skill, r"(?is)do not reimplement|only declare.*routing|declare.*next step")
        # supporting docs must be referenced
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
