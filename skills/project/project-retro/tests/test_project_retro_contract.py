"""Contract checks for the project-retro package."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
ATTRIBUTION = (ROOT / "ATTRIBUTION.md").read_text(encoding="utf-8")
CATEGORIES = (ROOT / "references" / "categories.md").read_text(encoding="utf-8")
HEURISTICS = (ROOT / "references" / "heuristics.md").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "references" / "template.md").read_text(encoding="utf-8")


class ProjectRetroContractTest(unittest.TestCase):
    def test_package_structure_and_files(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "ATTRIBUTION.md").is_file())
        self.assertTrue((ROOT / "references" / "categories.md").is_file())
        self.assertTrue((ROOT / "references" / "heuristics.md").is_file())
        self.assertTrue((ROOT / "references" / "template.md").is_file())

    def test_frontmatter_and_model_invocation_policy(self) -> None:
        self.assertRegex(SKILL, r"(?m)^name:\s*project-retro\s*$")
        self.assertRegex(SKILL, r"(?m)^description:\s*.+")
        # Model-invoked: must NOT disable model invocation
        self.assertIsNone(re.search(r"(?m)^disable-model-invocation:\s*true\s*$", SKILL))
        # openai.yaml must declare allow_implicit_invocation: true
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        self.assertIn("display_name:", METADATA)
        self.assertIn("short_description:", METADATA)
        self.assertIn("default_prompt:", METADATA)

    def test_attribution_integrity(self) -> None:
        self.assertIn("Matt Pocock", ATTRIBUTION)
        self.assertIn("https://github.com/mattpocock/skills", ATTRIBUTION)
        self.assertIn("959a8e9f1edc3adbe2f7e3054bb6fbefa6696260", ATTRIBUTION)
        self.assertIn("MIT", ATTRIBUTION)
        self.assertIn("PORT & LIGHT WORKFLOW ADAPTATION", ATTRIBUTION)

    def test_six_core_categories_covered(self) -> None:
        for cat in (
            "Navigation",
            "Automated checks",
            "Coding standards",
            "Steering economy",
            "Tool economy",
            "Information access",
        ):
            self.assertTrue(
                re.search(re.escape(cat), SKILL, re.IGNORECASE) is not None,
                f"Missing category in SKILL.md: {cat}",
            )
            self.assertTrue(
                re.search(re.escape(cat), CATEGORIES, re.IGNORECASE) is not None,
                f"Missing category in categories.md: {cat}",
            )

    def test_agent_self_evaluation_trigger_documented(self) -> None:
        self.assertIn("Agent self-evaluation trigger", SKILL)
        self.assertIn("Friction signal", SKILL)
        self.assertIn("Skip", SKILL)
        self.assertIn("heuristics.md", SKILL)

    def test_reference_links_resolve(self) -> None:
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", SKILL):
            link = match.group(2).split("#")[0]
            if link.startswith("http"):
                continue
            resolved = ROOT / link
            self.assertTrue(resolved.is_file(), f"Unresolved link in SKILL.md: {link}")

    def test_no_hardcoded_paths_or_external_runtime_dependency(self) -> None:
        full_text = "\n".join((SKILL, METADATA, CATEGORIES, HEURISTICS, TEMPLATE))
        self.assertNotRegex(full_text, r"/Users/|/home/|C:\\")
        self.assertNotIn("install mattpocock/skills", full_text.lower())

    def test_tri_state_deduplication_and_audit_discipline_documented(self) -> None:
        """Verify CLOSED/PARTIAL/OPEN status model and template structure."""
        self.assertIn("[CLOSED]", SKILL)
        self.assertIn("[PARTIAL]", SKILL)
        self.assertIn("[OPEN]", SKILL)
        self.assertIn("Already-Closed Guardrails", TEMPLATE)
        self.assertIn("Remaining Systemic Findings", TEMPLATE)
        self.assertIn("Suggested Actions — Pending Approval", TEMPLATE)
        self.assertIn("Suggested Actions — Pending Approval", SKILL)
        self.assertIn("Useful signals", CATEGORIES)
        self.assertIn("Typical durable improvements", CATEGORIES)
        self.assertIn("Neutral Tone", HEURISTICS)
        self.assertIn("Recommendation Is Not Authorization", HEURISTICS)

    def test_positive_instruction_and_state_transitions(self) -> None:
        """Verify positive instructions, Audit Communication, and state transitions."""
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        heuristics_text = (ROOT / "references" / "heuristics.md").read_text(encoding="utf-8")
        template_text = (ROOT / "references" / "template.md").read_text(encoding="utf-8")

        self.assertIn("Audit Communication", skill_text)
        self.assertIn("AWAITING_SELECTION", skill_text)
        self.assertIn("APPROVED_ACTION", skill_text)
        self.assertRegex(skill_text, r"Routine sessions with no reusable systemic\s+friction")
        self.assertIn("AWAITING_SELECTION", heuristics_text)
        self.assertIn("APPROVED_ACTION", heuristics_text)
        self.assertIn("AWAITING_SELECTION", template_text)
        self.assertIn("APPROVED_ACTION", template_text)



if __name__ == "__main__":
    unittest.main(verbosity=2)
