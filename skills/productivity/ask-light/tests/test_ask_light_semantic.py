"""Unit and contract tests for ask-light bounded Jev semantic routing and fail-closed invariants."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
import sys
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ask_light_models import (
    AskLightRecommendation,
    CompactProjectState,
    LegalActionsResult,
    SemanticJudgments,
)
from compact_state_builder import build_compact_jev_state
from state_extractor import (
    CANDIDATE_DESCRIPTIONS,
    compute_legal_actions,
    extract_compact_state_from_dict,
)
from semantic_router import route_with_jev
from advisor import ask_light_semantic_recommend


class AskLightSemanticTest(unittest.TestCase):
    def test_compact_state_builder_privacy_and_compactness(self) -> None:
        """Verify compact state builder never leaks raw files, code, or secrets, and stays <350 bytes."""
        state = CompactProjectState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=[".scratch/feat/issues/01.md"],
            resolved_tickets=[".scratch/feat/issues/00.md"],
        )
        legal = compute_legal_actions(state, "What next?")
        compact = build_compact_jev_state(legal, "What next?")

        self.assertEqual(
            set(compact.keys()),
            {"user_request", "project", "known_blockers", "allowed_candidate_actions"},
        )
        self.assertEqual(compact["user_request"], "What next?")
        self.assertTrue(compact["project"]["initialized"])
        self.assertEqual(compact["project"]["implementation_status"], "partial")
        self.assertEqual(compact["allowed_candidate_actions"], ["implement"])

        dumped = json.dumps(compact)
        self.assertNotIn("issues/01.md", dumped)
        self.assertLess(len(dumped), 350)

    def test_deterministic_pre_checks_happy_paths(self) -> None:
        """Verify canonical progression across standard project lifecycle states."""
        # 1. Uninitialized
        res = compute_legal_actions(CompactProjectState(initialized=False))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-init"])

        # 2. Initialized, no spec
        res = compute_legal_actions(CompactProjectState(initialized=True, spec_exists=False))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-clarify"])

        # 3. Clarification ready
        res = compute_legal_actions(CompactProjectState(initialized=True, spec_exists=False, clarification_ready=True))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-spec"])

        # 4. Active spec, no tickets
        res = compute_legal_actions(CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=False))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-tickets"])

        # 5. Tickets ready
        res = compute_legal_actions(CompactProjectState(
            initialized=True, spec_exists=True, spec_active=True, tickets_exist=True,
            ready_tickets=["issue-01.md"]
        ))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["implement"])
        self.assertEqual(res.target_item, "issue-01.md")

        # 6. All tickets resolved
        res = compute_legal_actions(CompactProjectState(
            initialized=True, spec_exists=True, spec_active=True, tickets_exist=True,
            all_tickets_resolved=True
        ))
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-review"])

        # 7. Review fresh pass
        res = compute_legal_actions(CompactProjectState(
            initialized=True, review_exists=True, review_verdict="PASS", review_freshness="fresh"
        ))
        self.assertEqual(res.status, "TERMINAL")
        self.assertEqual(res.allowed_actions, ["release-workflow"])

    def test_fail_closed_invariants(self) -> None:
        """Verify hard boundaries: unknown tickets, multiple efforts, stale review, dirty tree."""
        # Unknown ticket
        res = compute_legal_actions(
            CompactProjectState(initialized=True),
            user_request="implement ticket 99",
            explicit_target="99",
        )
        self.assertEqual(res.status, "BLOCKED")
        self.assertTrue(res.fail_closed)

        # Multiple active efforts
        res = compute_legal_actions(
            CompactProjectState(initialized=True, active_efforts=["feat-a", "feat-b"], current_effort=None)
        )
        self.assertEqual(res.status, "NEED_INPUT")
        self.assertTrue(res.fail_closed)

        # Stale review
        res = compute_legal_actions(
            CompactProjectState(initialized=True, review_exists=True, review_verdict="PASS", review_freshness="stale")
        )
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-review"])
        self.assertTrue(res.fail_closed)

        # Dirty working tree after review
        res = compute_legal_actions(
            CompactProjectState(initialized=True, review_exists=True, review_verdict="PASS", working_tree_dirty=True)
        )
        self.assertEqual(res.status, "RECOMMEND")
        self.assertEqual(res.allowed_actions, ["project-review"])
        self.assertTrue(res.fail_closed)

    def test_request_intent_detection(self) -> None:
        """Verify question explanation, progress reporting, and explicit execution intent."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])

        # Explanation inquiry
        res_explain = compute_legal_actions(state, user_request="explain the difference between tdd and prototype")
        self.assertEqual(res_explain.status, "EXPLAIN")
        self.assertEqual(res_explain.allowed_actions, [])

        # Progress inquiry
        res_report = compute_legal_actions(state, user_request="汇报当前项目进度")
        self.assertEqual(res_report.status, "EXPLAIN")

        # Explicit execution
        res_exec = compute_legal_actions(state, user_request="立刻开始执行工单")
        self.assertEqual(res_exec.status, "TRANSITION")
        self.assertEqual(res_exec.allowed_actions, ["implement"])

    def test_fallback_when_typesafe_sdk_or_key_unavailable(self) -> None:
        """Verify seamless fallback to deterministic baseline when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            state = CompactProjectState(initialized=True, spec_exists=False)
            legal = compute_legal_actions(state)
            rec = route_with_jev(legal, "What next?")
            self.assertTrue(rec.fallback_used)
            self.assertEqual(rec.primary_skill, "project-clarify")
            self.assertIn("unavailable", rec.fallback_reason.lower())

    def test_mock_jev_system_one_response(self) -> None:
        """Verify multi-primitive Jev judgments: Noul (execution & ambiguity), Escalation."""
        mock_choice = MagicMock()
        mock_choice.choice = "implement"
        mock_choice.confidence = 0.95
        mock_choice.probabilities = {"implement": 0.95}

        mock_noul_exec = MagicMock()
        mock_noul_exec.noul = 0.92

        mock_noul_ambig = MagicMock()
        mock_noul_ambig.noul = 0.10

        mock_noul_escala = MagicMock()
        mock_noul_escala.noul = 0.75

        mock_resp = MagicMock()
        mock_resp.choices = {"next_action": mock_choice}
        mock_resp.nouls = {
            "wants_immediate_execution": mock_noul_exec,
            "has_material_ambiguity": mock_noul_ambig,
            "needs_deep_reasoning_escalation": mock_noul_escala,
        }
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "Should we implement now?", client=mock_client)
                self.assertEqual(rec.primary_skill, "implement")
                self.assertFalse(rec.fallback_used)
                # Hard invariant: Jev execution intent (0.92) does NOT grant TRANSITION authority
                self.assertEqual(rec.status, "RECOMMEND")
                self.assertTrue(rec.escalated)  # Escalation detected
                self.assertIsNotNone(rec.semantic_judgments)
                self.assertEqual(rec.semantic_judgments.execution_intent_probability, 0.92)
                self.assertNotIn("next_action", rec.semantic_judgments.questions_sent)  # singleton candidate skips Choice

    def test_defense_in_depth_unauthorized_action_rejected(self) -> None:
        """Verify that if Jev hallucinates or selects an unauthorized action among multiple choices, it is blocked and falls back."""
        mock_choice = MagicMock()
        mock_choice.choice = "unauthorized-external-skill"
        mock_choice.confidence = 0.99
        mock_choice.probabilities = {"unauthorized-external-skill": 0.99}

        mock_resp = MagicMock()
        mock_resp.choices = {"next_action": mock_choice}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        # Set up a legal result with multiple actions to trigger Choice
        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["implement", "agent-config"],
            fallback_action="implement",
            candidate_descriptions={"implement": "Implement ticket", "agent-config": "Configure agent"},
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "What next?", client=mock_client)
                self.assertTrue(rec.fallback_used)
                self.assertEqual(rec.primary_skill, "implement")  # Baseline fallback preserved
                self.assertIn("unauthorized", rec.fallback_reason.lower())

    def test_jev_cannot_grant_transition_authority(self) -> None:
        """Hard Invariant (Section 12): Jev execution intent = 0.99 cannot change status to TRANSITION."""
        mock_noul_exec = MagicMock()
        mock_noul_exec.noul = 0.99

        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {"wants_immediate_execution": mock_noul_exec}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state, user_request="Advice only, do not run.")
        self.assertEqual(legal.status, "RECOMMEND")

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "Advice only, do not run.", client=mock_client)
                self.assertEqual(rec.status, "RECOMMEND")
                self.assertEqual(rec.semantic_judgments.execution_intent_probability, 0.99)

    def test_single_legal_action_causes_zero_choice_request(self) -> None:
        """Section 13: len(allowed_actions) == 1 must skip Choice."""
        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["implement"],
            fallback_action="implement",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "What next?", client=mock_client)
                self.assertNotIn("next_action", rec.semantic_judgments.questions_sent)
                self.assertEqual(rec.primary_skill, "implement")

    def test_zero_legal_actions_causes_zero_choice_request(self) -> None:
        """Section 13: len(allowed_actions) == 0 returns immediately without calling Jev."""
        mock_client = MagicMock()

        legal = LegalActionsResult(
            status="BLOCKED",
            allowed_actions=[],
            blocked_reason="All tickets blocked",
        )

        rec = route_with_jev(legal, "What next?", client=mock_client)
        self.assertEqual(rec.status, "BLOCKED")
        mock_client.system_one.assert_not_called()

    def test_fallback_action_is_explicit_not_list_order_dependent(self) -> None:
        """Section 15: Fallback action is explicit, not list-order dependent."""
        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["secondary-action", "preferred-fallback"],
            fallback_action="preferred-fallback",
            candidate_descriptions={"secondary-action": "Second", "preferred-fallback": "First"},
        )

        with patch.dict(os.environ, {}, clear=True):
            rec = route_with_jev(legal, "What next?")
            self.assertEqual(rec.primary_skill, "preferred-fallback")
            self.assertTrue(rec.fallback_used)

    def test_unconsumed_semantic_questions_are_not_sent(self) -> None:
        """Section 16: Unconsumed readiness_score is never sent."""
        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "What next?", client=mock_client)
                self.assertNotIn("readiness_score", rec.semantic_judgments.questions_sent)

    def test_shadow_evaluation_mode(self) -> None:
        """Section 37: Shadow mode executes Jev, records judgments, but retains deterministic baseline."""
        mock_choice = MagicMock()
        mock_choice.choice = "agent-config"
        mock_choice.confidence = 0.95
        mock_choice.probabilities = {"agent-config": 0.95}

        mock_resp = MagicMock()
        mock_resp.choices = {"next_action": mock_choice}
        mock_resp.nouls = {}
        mock_resp.scores = {}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        legal = LegalActionsResult(
            status="RECOMMEND",
            allowed_actions=["implement", "agent-config"],
            fallback_action="implement",
            candidate_descriptions={"implement": "Do work", "agent-config": "Config"},
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "What next?", client=mock_client, shadow_mode=True)
                self.assertEqual(rec.primary_skill, "implement")  # Deterministic baseline preserved
                self.assertIn("Shadow mode", rec.justification)
                self.assertEqual(rec.semantic_judgments.action_choice, "agent-config")

    def test_advisor_end_to_end_from_dict(self) -> None:
        """Verify ask_light_semantic_recommend accepting standard evidence dict."""
        evidence = {
            "initialized": True,
            "spec": {"exists": True, "active": True, "paths": ["docs/spec.md"]},
            "tickets": {"exists": True, "ready": [{"path": "01.md"}], "blocked": [], "resolved": []},
            "review": {"exists": False},
        }
        rec = ask_light_semantic_recommend(evidence, user_request="下一步做什么？", use_jev=False)
        self.assertEqual(rec.status, "RECOMMEND")
        self.assertEqual(rec.primary_skill, "implement")
        self.assertEqual(rec.target_item, "01.md")

    def test_query_planner_zero_questions_on_plain_query_and_single_action(self) -> None:
        """P1 (Section 13-15): Standard query with single legal action skips Jev API calls completely."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        mock_client = MagicMock()
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "What should I do next?", client=mock_client)
                self.assertEqual(rec.primary_skill, "implement")
                self.assertEqual(rec.confidence, 1.0)
                # Query planner emitted 0 questions -> system_one was never called!
                mock_client.system_one.assert_not_called()
                self.assertEqual(rec.semantic_judgments.questions_sent, [])

    def test_query_planner_sends_ambiguity_when_ambiguous_phrasing_present(self) -> None:
        """P1 (Section 14): Ambiguous user phrasing triggers ambiguity question."""
        state = CompactProjectState(initialized=True, spec_exists=False)
        legal = compute_legal_actions(state)

        mock_resp = MagicMock()
        mock_resp.choices = {}
        mock_resp.nouls = {"has_material_ambiguity": MagicMock(noul=0.92)}
        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "Maybe we should redesign auth or database first?", client=mock_client)
                self.assertIn("has_material_ambiguity", rec.semantic_judgments.questions_sent)
                self.assertEqual(rec.primary_skill, "project-clarify")

    def test_adversarial_linguistic_cases_distinguish_intent_from_authorization(self) -> None:
        """P1 (Sections 35-37): Natural language adversarial cases separate semantic intent from deterministic authority."""
        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])

        mock_client = MagicMock()
        mock_client.system_one.return_value = MagicMock(
            choices={},
            nouls={"wants_immediate_execution": MagicMock(noul=0.15)}
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                # 1. "Don't implement anything; just tell me what comes next."
                legal_neg = compute_legal_actions(state, user_request="Don't implement anything; just tell me what comes next.")
                rec_neg = route_with_jev(legal_neg, "Don't implement anything; just tell me what comes next.", client=mock_client)
                self.assertEqual(rec_neg.status, "RECOMMEND")
                self.assertEqual(rec_neg.primary_skill, "implement")

                # 2. "Should I implement now?"
                legal_hes = compute_legal_actions(state, user_request="Should I implement now?")
                rec_hes = route_with_jev(legal_hes, "Should I implement now?", client=mock_client)
                self.assertEqual(rec_hes.status, "RECOMMEND")  # Hesitant inquiry cannot grant transition

                # 3. "Implement now."
                legal_cmd = compute_legal_actions(state, user_request="Implement now.")
                self.assertEqual(legal_cmd.status, "TRANSITION")  # Deterministic authorization holds!


if __name__ == "__main__":
    unittest.main()
