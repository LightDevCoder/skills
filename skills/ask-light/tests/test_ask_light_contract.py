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
        self.assertEqual(len(names), 34)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(data["skillFamilies"]), set(names))
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

    def test_public_entry_points_to_all_routing_layers(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "discovery-contract.md").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: ask-light$")
        self.assertIn("references/light-skill-map.json", skill)
        self.assertIn("Layer 0", contract)
        self.assertIn("Layer A", contract)
        self.assertIn("Layer B", contract)
        self.assertIn("generic host Skill root is not provenance", contract)
        self.assertIn("optional UI metadata", contract)
        self.assertIn("approval", contract)

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
        self.assertTrue(re.search(r'choices=\("next",\s*"workflow",\s*"navigate"', python))
        self.assertIn("LIGHT_SKILL_ROOTS", python)
        self.assertIn("discover_roots", python)
        self.assertIn("recommendation phase was read-only", python + powershell + skill)

    def test_skill_contract_enforces_model_led_hybrid_advisor_boundaries(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "discovery-contract.md").read_text(encoding="utf-8")
        combined = skill + "\n" + contract

        # 1. Python is evidence/validation authority, not semantic recommendation authority
        self.assertIn("Code establishes trustworthy facts", combined)
        self.assertIn("Model understands the situation", combined)
        self.assertIn("Model chooses the workflow action", combined)
        self.assertIn("Code validates that choice", combined)
        self.assertIn("Python is the evidence/validation authority", skill)

        # 2. Model reads relevant candidate contracts
        self.assertIn("shortlist from the catalog", " ".join(skill.lower().split()))
        self.assertIn("read their `skill.md` contracts before selecting", " ".join(skill.lower().split()))

        # 3. Current conversation is first-class evidence
        self.assertIn("conversation is first-class evidence", combined)

        # 4. Hard evidence is scoped to the request being answered
        self.assertIn("Hard constraints are scoped", combined)
        self.assertIn("current-workflow", combined)

        # 5. Final semantic selection must be validated
        self.assertIn("Validate the selection", skill)
        self.assertIn("validate_recommendation", combined)

        # 6. RECOMMEND cannot contain empty Skill
        self.assertIn("never expose an empty `skill:` inside a `recommend` result", " ".join(skill.lower().split()))
        self.assertIn("empty `skill:` inside `recommend` is a contract violation", " ".join(contract.lower().split()))

        # 7. Regex ranking is not final authority
        self.assertIn("candidate hints only", combined)
        self.assertIn("regex ranking is not the routing authority", " ".join(contract.lower().split()))

        # 8. Workflow mode is model-led
        self.assertIn("Model-led", skill)
        self.assertIn("anchor the entry point at the user's actual current state", skill)

        # 9. Approval transition is host-aware
        self.assertIn("Revalidate before transition", skill)
        self.assertIn("host-aware", combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
