from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FULL = (
    "agent-config", "ask-light", "clarify", "code-review", "decision-map",
    "generic-review", "implement", "project-clarify", "project-init",
    "project-review", "project-spec", "project-tickets", "review-loop", "socratic",
)


class FunctionalClosureBoundaryTest(unittest.TestCase):
    def test_recap_description_matches_the_user_approved_minimal_entry(self) -> None:
        skill = (ROOT / "skills/recap/SKILL.md").read_text(encoding="utf-8")
        description = next(line for line in skill.splitlines() if line.startswith("description: "))
        self.assertEqual(
            description,
            "description: show one concise line about the current session without replacing or compacting conversation history.",
        )
        self.assertEqual(
            skill.splitlines()[6:],
            [
                "# Recap",
                "",
                "After an explicit `$recap` request, output one concise line of at most 400 characters summarizing what happened in the current session so far without clearing, replacing, compacting, or rewriting conversation history, then stop.",
            ],
        )

    def test_recap_output_is_one_unlabeled_line_with_a_400_character_limit(self) -> None:
        def valid(text: str) -> bool:
            return bool(text.strip()) and not re.search(r"[\r\n]", text) and len(text) <= 400

        self.assertTrue(valid("x" * 400))
        self.assertFalse(valid("x" * 401))
        self.assertFalse(valid("first line\nsecond line"))

    def test_frozen_hashes_allow_only_the_recap_skill_entry_amendment(self) -> None:
        baseline = ROOT / ".scratch/light-skills-lean-refactor/frozen-baseline.sha256"
        for line in baseline.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*([0-9a-f]{64})\s+(.+)$", line)
            if not match:
                continue
            expected, relative = match.groups()
            if relative == "skills/recap/SKILL.md":
                continue
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_every_local_markdown_pointer_resolves_without_cross_skill_deep_links(self) -> None:
        for name in FULL:
            package = ROOT / "skills" / name
            for source in package.rglob("*.md"):
                text = source.read_text(encoding="utf-8")
                for raw in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                    link = raw.split("#", 1)[0]
                    if not link or "://" in link:
                        continue
                    target = (source.parent / link).resolve()
                    self.assertTrue(target.exists(), f"broken pointer: {source.relative_to(ROOT)} -> {raw}")
                    if target.is_relative_to(ROOT / "skills"):
                        self.assertTrue(target.is_relative_to(package), f"cross-Skill deep reference: {source.relative_to(ROOT)} -> {raw}")

    def test_repaired_ownership_has_one_runtime_contract(self) -> None:
        self.assertFalse((ROOT / "skills/clarify/references/ROUTING.md").exists())
        self.assertTrue((ROOT / "skills/socratic/references/ROUTING.md").is_file())
        self.assertFalse((ROOT / "skills/project-review/references/reviewer-contract.md").exists())
        self.assertTrue((ROOT / "skills/review-loop/references/reviewer-contract.md").is_file())

    def test_historical_material_is_explicitly_runtime_optional(self) -> None:
        for path in (ROOT / "skills/review-loop/references/migration.md", ROOT / "skills/project-review/references/migration.md"):
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?i)^# Historical migration")
            self.assertIn("not required for current", text)

    def test_light_skill_map_matches_the_actual_collection(self) -> None:
        mapped = {entry["name"] for entry in json.loads((ROOT / "skills/ask-light/references/light-skill-map.json").read_text(encoding="utf-8"))["skills"]}
        actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(mapped, actual)


if __name__ == "__main__":
    unittest.main(verbosity=2)
