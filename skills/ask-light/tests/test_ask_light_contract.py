from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AskLightContractTest(unittest.TestCase):
    def test_router_has_one_machine_readable_light_map(self) -> None:
        data = json.loads((ROOT / "references" / "light-skill-map.json").read_text(encoding="utf-8"))
        names = [entry["name"] for entry in data["skills"]]
        self.assertEqual(len(names), 33)
        self.assertEqual(len(names), len(set(names)))
        for name in ("eli5", "recap", "project-init", "project-review", "socratic", "ask-light"):
            self.assertIn(name, names)

    def test_map_keeps_only_routing_and_recipe_data(self) -> None:
        data = json.loads((ROOT / "references" / "light-skill-map.json").read_text(encoding="utf-8"))
        for entry in data["skills"]:
            self.assertTrue(set(entry).issubset({"name", "patterns", "precedencePatterns"}), entry["name"])
            self.assertFalse({"category", "role", "invocation"}.intersection(entry), entry["name"])
        for recipe in data["workflows"]:
            for step in recipe["steps"]:
                self.assertTrue({"skill", "expectedInput", "expectedOutput", "handoffArtifact", "stopCondition"}.issubset(step))

    def test_public_entry_points_to_both_routing_layers(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "discovery-contract.md").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: ask-light$")
        self.assertIn("references/light-skill-map.json", skill)
        self.assertIn("Layer A", contract)
        self.assertIn("Layer B", contract)
        self.assertIn("generic host Skill root is not trusted", contract)
        self.assertIn("optional UI metadata", contract)

    def test_scripts_are_read_only_and_compatibility_launcher_is_thin(self) -> None:
        python = (ROOT / "scripts" / "ask_light.py").read_text(encoding="utf-8")
        powershell = (ROOT / "scripts" / "ask-light.ps1").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "discovery-contract.md").read_text(encoding="utf-8")
        for forbidden in ("unlink(", "rmtree", "Invoke-RestMethod", "Install-Module", "Start-Process"):
            self.assertNotIn(forbidden, python + powershell)
        self.assertIn("ask_light.py", powershell)
        self.assertIn("Python 3.9", powershell + skill + contract)
        self.assertIn("sys.version_info >= (3, 9)", powershell)
        self.assertIn("$LASTEXITCODE -eq 0", powershell)
        self.assertIn("manually", skill + contract)
        self.assertIn("status = 'BLOCKED'", powershell)
        self.assertTrue(re.search(r"choices=\(\"next\", \"workflow\"\)", python))


if __name__ == "__main__":
    unittest.main(verbosity=2)
