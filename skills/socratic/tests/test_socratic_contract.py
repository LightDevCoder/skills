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
        for name in ("WORKFLOW.md", "ROUTING.md", "EXAMPLES.md", "conversation-contract.json", "frontier.py"):
            self.assertTrue((ROOT / "references" / name).is_file() or (ROOT / "scripts" / name).is_file(), f"missing {name}")
            pointer = f"references/{name}" if (ROOT / "references" / name).is_file() else f"scripts/{name}"
            self.assertIn(pointer, skill)

    def test_durable_state_remains_owned_by_decision_map(self) -> None:
        contract = json.loads((ROOT / "references" / "conversation-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["persistenceOwner"], "decision-map")

    def test_frontier_round_contract_replaces_one_question_limit(self) -> None:
        contract = json.loads((ROOT / "references" / "conversation-contract.json").read_text(encoding="utf-8"))
        self.assertNotIn("frontierDecisionLimit", contract["projection"])
        self.assertTrue(contract["projection"]["frontierAsRound"])
        self.assertTrue(contract["projection"]["multipleIndependentQuestions"])
        self.assertTrue(contract["projection"]["batchRepliesSupported"])


if __name__ == "__main__":
    unittest.main(verbosity=2)