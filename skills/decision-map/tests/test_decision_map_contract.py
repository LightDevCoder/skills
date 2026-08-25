"""Contract checks for the decision-map stage."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_contract(root: Path = ROOT) -> tuple[str, str, str, str]:
    return tuple(
        path.read_text(encoding="utf-8")
        for path in (
            root / "SKILL.md",
            root / "agents" / "openai.yaml",
            root / "references" / "MAP-CONTRACT.md",
            root / "references" / "WORKFLOW.md",
        )
    )


class DecisionMapContractTest(unittest.TestCase):
    def test_explicit_entry_maps_large_effort_to_a_persistent_map(self) -> None:
        skill, metadata, _, _ = read_contract()

        self.assertRegex(skill, r"(?m)^name: decision-map$")
        self.assertRegex(skill, r"(?m)^disable-model-invocation: true$")
        self.assertRegex(metadata, r"(?m)^\s*allow_implicit_invocation: false$")
        self.assertIn("$decision-map", skill)
        self.assertRegex(skill, r"(?is)large.*multi-session|multi-session.*large")
        self.assertIn(".scratch/<effort>/map.md", skill)

    def test_tracker_ops_match_issue_tracker_wayfinding(self) -> None:
        skill, _, map_contract, workflow = read_contract()
        combined = skill + map_contract + workflow

        # local-markdown tracker ops
        for token in (
            ".scratch/<effort>/map.md",
            ".scratch/<effort>/issues/NN-<slug>.md",
            "Type:",
            "Status: claimed",
            "Status: resolved",
            "Blocked by:",
            "Frontier",
            "Claim",
            "Resolve",
        ):
            self.assertIn(token, combined)
        # must reference the tracker doc
        self.assertIn("docs/agents/issue-tracker.md", skill)
        self.assertRegex(map_contract, r"(?s)## Destination.*## Notes.*## Decisions so far.*## Not yet specified.*## Out of scope")

    def test_composition_uses_four_capabilities_without_duplication(self) -> None:
        skill, _, _, _ = read_contract()

        for cap in ("research", "prototype", "socratic", "to-questionnaire"):
            self.assertIn(cap, skill)
        # composition before duplication
        self.assertRegex(skill, r"(?is)do not copy.*capabilit|call (them|it)")
        self.assertIn("research", skill.lower())
        # at most one ticket per session (except parallel research)
        self.assertRegex(skill, r"(?is)at most one ticket|never resolve more than one ticket")

    def test_handoff_to_project_spec_and_no_autochain(self) -> None:
        skill, _, _, workflow = read_contract()
        combined = skill + workflow

        self.assertIn("decision-map → project-spec", skill)
        self.assertIn("project-spec", combined)
        self.assertRegex(skill, r"(?is)do not auto-chain")
        self.assertIn("fog", skill.lower())
        self.assertIn("fog is empty", combined.lower() if "fog is empty" in combined.lower() else combined)

    def test_provenance_is_transformed_wayfinder(self) -> None:
        attribution = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")
        for marker in (
            "mattpocock/skills",
            "skills/engineering/wayfinder/",
            "v1.2.3",
            "6acc160e4e0cd062dbbbd7a1b26ae92855edf07e",
            "Copyright (c) 2026 Matt Pocock",
            "First-party transformation",
        ):
            self.assertIn(marker, attribution)

    def test_supporting_files_resolve(self) -> None:
        for name in (
            "references/MAP-CONTRACT.md",
            "references/WORKFLOW.md",
            "references/EXAMPLES.md",
        ):
            self.assertTrue((ROOT / name).is_file(), f"missing {name}")
        # references must be reachable from SKILL.md
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/MAP-CONTRACT.md", skill)
        self.assertIn("references/WORKFLOW.md", skill)
        self.assertIn("references/EXAMPLES.md", skill)


if __name__ == "__main__":
    unittest.main(verbosity=2)
