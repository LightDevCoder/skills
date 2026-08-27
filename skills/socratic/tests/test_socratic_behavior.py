from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "references" / "conversation-contract.json").read_text(encoding="utf-8"))
SPEC = importlib.util.spec_from_file_location("socratic_frontier", ROOT / "scripts" / "frontier.py")
assert SPEC and SPEC.loader
FRONTIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FRONTIER)


def sample_decisions() -> list[FRONTIER.Decision]:
    return [
        FRONTIER.Decision("D1", "Output format?", options=[{"label": "A", "text": "Keep structure"}, {"label": "B", "text": "Flatten"}], recommended="A"),
        FRONTIER.Decision("D2", "Conflict strategy?", options=[{"label": "A", "text": "Overwrite"}, {"label": "B", "text": "Skip"}, {"label": "C", "text": "Prompt"}], recommended="C", depends_on=["D1"]),
        FRONTIER.Decision("D3", "First platform?", options=[{"label": "A", "text": "macOS"}, {"label": "B", "text": "Cross-platform"}], recommended="A"),
    ]


class SocraticBehaviorTest(unittest.TestCase):
    def test_internal_state_and_user_projection_are_separate(self) -> None:
        self.assertEqual(CONTRACT["schemaVersion"], 2)
        self.assertTrue(CONTRACT["projection"]["frontierAsRound"])
        self.assertTrue(CONTRACT["projection"]["multipleIndependentQuestions"])
        self.assertTrue(CONTRACT["projection"]["batchRepliesSupported"])
        self.assertNotIn("frontierDecisionLimit", CONTRACT["projection"])
        self.assertTrue(CONTRACT["projection"]["acknowledgeLatestEvidence"])
        self.assertTrue(CONTRACT["projection"]["showMeaningfulTradeoffs"])
        self.assertIn("frontier", CONTRACT["internalState"])

    def test_recommendation_preserves_user_decision(self) -> None:
        self.assertTrue(CONTRACT["projection"]["recommendWhenSupported"])
        self.assertTrue(CONTRACT["projection"]["preserveUserDecision"])
        self.assertTrue(CONTRACT["projection"]["allowFreeTextAnswers"])

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

    def test_multiple_question_frontier_asks_all_independent_decisions(self) -> None:
        decisions = sample_decisions()
        frontier = FRONTIER.compute_frontier(decisions)
        self.assertEqual([item.id for item in frontier], ["D1", "D3"])

    def test_dependency_gating_keeps_dependent_question_out_of_first_round(self) -> None:
        decisions = sample_decisions()
        self.assertNotIn("D2", [item.id for item in FRONTIER.compute_frontier(decisions)])
        FRONTIER.apply_answers(decisions, {"D1": "A"})
        self.assertEqual([item.id for item in FRONTIER.compute_frontier(decisions)], ["D2", "D3"])

    def test_choices_and_recommendation_are_available_in_round_items(self) -> None:
        items = FRONTIER.round_items(sample_decisions())
        first = items[0]
        self.assertEqual(first["options"][0]["label"], "A")
        self.assertTrue(first["recommended"])

    def test_colon_and_q_colon_batch_response_parsing(self) -> None:
        decisions = sample_decisions()
        decisions[1].depends_on = []  # make all three independent for parsing
        frontier = FRONTIER.compute_frontier(decisions)
        for response in ("1: B\n2: A\n3: C", "Q1: B\nQ2: A\nQ3: C", "1: B, 2: A, 3: C"):
            with self.subTest(response=response):
                self.assertEqual(FRONTIER.parse_batch_response(response, frontier), {"D1": "B", "D2": "A", "D3": "C"})

    def test_qualified_colon_answers_preserve_qualifiers(self) -> None:
        decisions = sample_decisions()
        decisions[1].depends_on = []  # make all three independent for parsing
        frontier = FRONTIER.compute_frontier(decisions)
        answers = FRONTIER.parse_batch_response("Q1: B\nQ2: B, but only locally\nQ3: A", frontier)
        self.assertEqual(answers["D1"], "B")
        self.assertIn("but only locally", answers["D2"])
        self.assertEqual(answers["D3"], "A")

    def test_partial_answer_without_qualifier_keeps_unanswered_open(self) -> None:
        decisions = sample_decisions()
        decisions[1].depends_on = []  # make all three independent for parsing
        frontier = FRONTIER.compute_frontier(decisions)
        answers = FRONTIER.parse_batch_response("1B, 3C", frontier)
        self.assertEqual(answers, {"D1": "B", "D3": "C"})
        FRONTIER.apply_answers(decisions, answers)
        self.assertFalse(next(item for item in decisions if item.id == "D2").resolved)
        self.assertEqual(FRONTIER.next_step(decisions), "ask-round")


    def test_compact_batch_response_parsing(self) -> None:
        frontier = FRONTIER.compute_frontier(sample_decisions())
        answers = FRONTIER.parse_batch_response("1B, 2A", frontier)
        self.assertEqual(answers, {"D1": "B", "D3": "A"})

    def test_mixed_free_text_batch_response_parsing(self) -> None:
        frontier = FRONTIER.compute_frontier(sample_decisions())
        answers = FRONTIER.parse_batch_response("1B\n2A, but only locally", frontier)
        self.assertEqual(answers["D1"], "B")
        self.assertIn("but only locally", answers["D3"])

    def test_partial_response_leaves_unanswered_questions_open(self) -> None:
        decisions = sample_decisions()
        frontier = FRONTIER.compute_frontier(decisions)
        answers = FRONTIER.parse_batch_response("1A", frontier)
        FRONTIER.apply_answers(decisions, answers)
        self.assertTrue(next(item for item in decisions if item.id == "D1").resolved)
        self.assertFalse(next(item for item in decisions if item.id == "D3").resolved)
        self.assertEqual([item.id for item in FRONTIER.compute_frontier(decisions)], ["D2", "D3"])

    def test_single_free_text_answer_assigns_to_only_frontier_question(self) -> None:
        decisions = sample_decisions()
        FRONTIER.apply_answers(decisions, {"D1": "A", "D3": "B"})
        frontier = FRONTIER.compute_frontier(decisions)
        self.assertEqual([item.id for item in frontier], ["D2"])
        answers = FRONTIER.parse_batch_response("Prompt on collisions, please", frontier)
        self.assertEqual(answers, {"D2": "Prompt on collisions, please"})

    def test_continuous_session_and_final_confirmation_path(self) -> None:
        decisions = sample_decisions()
        # Round 1
        answers = FRONTIER.parse_batch_response("1A, 2B", FRONTIER.compute_frontier(decisions))
        FRONTIER.apply_answers(decisions, answers)
        # Round 2
        answers = FRONTIER.parse_batch_response("2C", FRONTIER.compute_frontier(decisions))
        FRONTIER.apply_answers(decisions, answers)
        self.assertEqual(FRONTIER.next_step(decisions), "synthesize")


if __name__ == "__main__":
    unittest.main(verbosity=2)