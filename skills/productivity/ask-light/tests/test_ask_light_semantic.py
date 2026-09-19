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
        """Verify multi-primitive Jev judgments: Choice, Noul (execution & ambiguity), Score, Escalation."""
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

        mock_score = MagicMock()
        mock_score.score = 2.0
        mock_score.confidence = 0.90

        mock_resp = MagicMock()
        mock_resp.choices = {"next_action": mock_choice}
        mock_resp.nouls = {
            "wants_immediate_execution": mock_noul_exec,
            "has_material_ambiguity": mock_noul_ambig,
            "needs_deep_reasoning_escalation": mock_noul_escala,
        }
        mock_resp.scores = {"readiness_score": mock_score}

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "Go ahead and implement", client=mock_client)
                self.assertEqual(rec.primary_skill, "implement")
                self.assertFalse(rec.fallback_used)
                self.assertEqual(rec.status, "TRANSITION")  # Upgraded by wants_immediate_execution >= 0.80
                self.assertTrue(rec.escalated)  # Escalation detected
                self.assertIsNotNone(rec.semantic_judgments)
                self.assertEqual(rec.semantic_judgments.readiness_score, 2.0)

    def test_defense_in_depth_unauthorized_action_rejected(self) -> None:
        """Verify that if Jev hallucinates or selects an unauthorized action, it is blocked and falls back."""
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

        state = CompactProjectState(initialized=True, spec_exists=True, spec_active=True, tickets_exist=True, ready_tickets=["01.md"])
        legal = compute_legal_actions(state)

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("semantic_router.TYPESAFE_AVAILABLE", True):
                rec = route_with_jev(legal, "What next?", client=mock_client)
                self.assertTrue(rec.fallback_used)
                self.assertEqual(rec.primary_skill, "implement")  # Baseline preserved
                self.assertIn("unauthorized", rec.fallback_reason.lower())

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


if __name__ == "__main__":
    unittest.main()
