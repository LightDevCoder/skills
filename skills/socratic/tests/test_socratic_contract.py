from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SocraticPublicContractTest(unittest.TestCase):
    def test_engine_contract_and_supporting_files_resolve(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("name: socratic", skill)
        self.assertIn("model-invoked", skill + metadata)
        for name in ("WORKFLOW.md", "ROUTING.md", "EXAMPLES.md", "conversation-contract.json"):
            self.assertTrue((ROOT / "references" / name).is_file())
            self.assertIn(f"references/{name}", skill)

    def test_durable_state_remains_owned_by_decision_map(self) -> None:
        contract = json.loads((ROOT / "references" / "conversation-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["persistenceOwner"], "decision-map")


if __name__ == "__main__":
    unittest.main(verbosity=2)
