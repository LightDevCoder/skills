from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "references" / "conversation-contract.json").read_text(encoding="utf-8"))


class SocraticBehaviorTest(unittest.TestCase):
    def test_internal_state_and_user_projection_are_separate(self) -> None:
        self.assertEqual(CONTRACT["schemaVersion"], 1)
        self.assertEqual(CONTRACT["projection"]["frontierDecisionLimit"], 1)
        self.assertTrue(CONTRACT["projection"]["acknowledgeLatestEvidence"])
        self.assertTrue(CONTRACT["projection"]["showMeaningfulTradeoffs"])
        self.assertIn("frontier", CONTRACT["internalState"])

    def test_recommendation_preserves_user_decision(self) -> None:
        self.assertTrue(CONTRACT["projection"]["recommendWhenSupported"])
        self.assertTrue(CONTRACT["projection"]["preserveUserDecision"])

    def test_completion_requires_confirmation_and_correction_recomputes(self) -> None:
        completion = CONTRACT["completion"]
        self.assertTrue(completion["requiresSharedUnderstandingConfirmation"])
        self.assertEqual(completion["confirmationState"], "done")
        self.assertEqual(completion["correctionState"], "active")

    def test_fact_routing_remains_engine_owned(self) -> None:
        self.assertEqual(CONTRACT["factRoutes"], {
            "externalFact": "research",
            "needsExperiment": "prototype",
            "heldByAnotherPerson": "to-questionnaire",
        })


if __name__ == "__main__":
    unittest.main(verbosity=2)
