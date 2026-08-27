from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectInitContractTest(unittest.TestCase):
    def test_public_contract_names_stable_output_and_ambiguity_gate(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        presets = (ROOT / "references" / "presets.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "initialization-contract.md").read_text(encoding="utf-8")
        self.assertIn("docs/agents/light-project.md", skill + contract)
        self.assertIn("docs/agents/issue-tracker.md", skill + contract)
        self.assertIn("When two", skill)
        self.assertIn("recommend", skill.lower())
        self.assertIn("Managed markers", contract)
        self.assertIn("Do not create\n`triage-labels.md`", contract)
        self.assertIn("Python 3.9", skill + contract)
        for consumer in ("project-clarify", "decision-map", "project-spec", "project-tickets", "implement", "project-review"):
            self.assertIn(consumer, contract)
        for preset in ("generic", "software", "manuscript", "skill-development", "research", "knowledge-base", "data-analysis"):
            self.assertIn(f"| {preset} |", presets)

    def test_helper_is_syntax_valid_and_has_no_external_execution(self) -> None:
        script = (ROOT / "scripts" / "bootstrap.py").read_text(encoding="utf-8")
        ast.parse(script)
        for forbidden in ("subprocess", "requests", "urlopen", "shutil.rmtree", "unlink("):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
