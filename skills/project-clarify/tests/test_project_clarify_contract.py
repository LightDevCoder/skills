"""Contract checks for the explicit evidence-first project clarification stage."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_contract(root: Path = ROOT) -> tuple[str, str, str]:
    return tuple(
        path.read_text(encoding="utf-8")
        for path in (
            root / "SKILL.md",
            root / "agents" / "openai.yaml",
            root / "references" / "project-clarification-contract.md",
        )
    )


class ProjectClarifyContractTest(unittest.TestCase):
    def test_explicit_entry_inspects_facts_before_socratic_questions(self) -> None:
        skill, metadata, contract = read_contract()

        self.assertRegex(skill, r"(?m)^name: project-clarify$")
        self.assertRegex(skill, r"(?m)^disable-model-invocation: true$")
        self.assertRegex(metadata, r"(?m)^\s*allow_implicit_invocation: false$")
        self.assertLess(skill.index("Inspect project facts before asking"), skill.index("Maintain user decisions with `socratic`"))
        # must list project-aware sources
        combined = skill + "\n" + contract
        for marker in ("README", "AGENTS.md", "CONTEXT.md", "docs/adr", "docs/agents/light-project.md"):
            self.assertIn(marker, combined)
        # socratic is the decision engine and questions stay frontier-scoped
        self.assertIn("socratic", skill)
        self.assertIn("unblocked, user-owned frontier", skill)

    def test_invocation_boundaries_and_no_implicit_write_are_explicit(self) -> None:
        skill, metadata, _ = read_contract()

        self.assertRegex(skill, r"(?is)only\s+after.*\$project-clarify|explicit.*\$project-clarify")
        self.assertIn("$project-clarify", skill)
        self.assertIn("Return the handoff in memory by default", skill)
        self.assertIn("separately names a writable destination", skill)
        self.assertNotIn("grill-with-docs", skill + metadata)

    def test_optional_capability_calls_have_read_and_failure_boundaries(self) -> None:
        skill, _, reference = read_contract()
        combined = skill + reference

        self.assertIn("research", combined)
        self.assertIn("prototype", combined)
        self.assertIn("Capability call: socratic | research | prototype", combined)
        for status in ("not-authorized", "unavailable", "result-read"):
            self.assertIn(status, combined)
        self.assertIn("Never record `result-read`", combined)
        self.assertIn("actually read", combined)
        self.assertIn("missing capability", combined)

    def test_transformed_first_party_provenance_is_inspectable(self) -> None:
        attribution = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")

        for marker in (
            "mattpocock/skills",
            "skills/engineering/grill-with-docs/",
            "v1.2.3",
            "6acc160e4e0cd062dbbbd7a1b26ae92855edf07e",
            "Copyright (c) 2026 Matt Pocock",
            "First-party transformation",
        ):
            self.assertIn(marker, attribution)

    def test_supporting_files_and_handoff_shape(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/project-clarification-contract.md", skill)
        self.assertIn("references/EXAMPLES.md", skill)
        self.assertIn("Project clarification handoff", skill)
        self.assertIn("Recommended next explicit invocation:", skill)
        # upgrade path to decision-map
        self.assertIn("decision-map", skill.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
