"""Unit and integration tests for agent-config abstract task profiling and topology selection."""

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

from agent_config_models import (
    AbstractTaskProfile,
    AgentConfigResult,
    ExecutionConfig,
    HostCapabilities,
    TaskCharacteristics,
)
from harness_adapter import (
    determine_topology,
    discover_valid_candidates,
    resolve_reasoning_effort,
)
from abstract_profiler import (
    build_deterministic_profile,
    extract_abstract_task_profile,
)
from candidate_selector import select_configuration
from agent_config import agent_config_recommend


class AgentConfigSemanticTest(unittest.TestCase):
    def test_effort_resolution_safety(self) -> None:
        """Verify effort policy resolves strictly to host-supported values and never literal 'max'."""
        host_with_efforts = HostCapabilities(
            supported_effort=["low", "medium", "high"],
        )
        host_without_efforts = HostCapabilities(
            supported_effort=[],
        )

        # 1. highest-supported mapping
        self.assertEqual(resolve_reasoning_effort(host_with_efforts, "highest-supported"), "high")

        # 2. minimal mapping
        self.assertEqual(resolve_reasoning_effort(host_with_efforts, "minimal"), "low")

        # 3. standard mapping
        self.assertEqual(resolve_reasoning_effort(host_with_efforts, "standard"), "medium")

        # 4. host without efforts safely returns None
        self.assertIsNone(resolve_reasoning_effort(host_without_efforts, "highest-supported"))

        # 5. unverified literal 'max' is not emitted unless explicitly supported by host
        self.assertEqual(resolve_reasoning_effort(host_with_efforts, "max"), "high")

    def test_discover_valid_candidates(self) -> None:
        """Verify candidates are strictly intersected with confirmed profile tiers."""
        # Fixed host
        fixed_host = HostCapabilities(
            has_model_selector=False,
            active_model="claude-3-5-sonnet",
        )
        self.assertEqual(discover_valid_candidates(fixed_host), ["claude-3-5-sonnet"])

        # Multi-model host
        multi_host = HostCapabilities(
            has_model_selector=True,
            active_model="gpt-4o",
            available_models=["gpt-4o", "gpt-4o-mini", "o3-mini"],
            profile_tiers={"routine": "gpt-4o-mini", "standard": "gpt-4o", "high": "o3-mini"},
        )
        valid = discover_valid_candidates(multi_host)
        self.assertIn("gpt-4o-mini", valid)
        self.assertIn("gpt-4o", valid)
        self.assertIn("o3-mini", valid)

    def test_setup_gate_and_ticket_gates(self) -> None:
        """Verify explicit setup intent and decomposed without tickets gate."""
        host = HostCapabilities()
        profile = AbstractTaskProfile()

        # Gate 1: Setup intent
        res_setup = select_configuration(host, TaskCharacteristics(), profile, setup_intent=True)
        self.assertEqual(res_setup.readiness, "READY")
        self.assertEqual(res_setup.handoff, "setup")
        self.assertIsNone(res_setup.execution_config)

        # Gate 2: Decomposed without formal tickets
        task_decomposed_no_tickets = TaskCharacteristics(
            shape="decomposed",
            formal_tickets_exist=False,
        )
        res_tickets = select_configuration(host, task_decomposed_no_tickets, profile)
        self.assertEqual(res_tickets.readiness, "NEED_PROJECT_TICKETS")
        self.assertEqual(res_tickets.handoff, "project-tickets")
        self.assertIsNone(res_tickets.execution_config)

    def test_user_preview_rejection_safety(self) -> None:
        """Verify user declining preview falls back to active model without failure."""
        host = HostCapabilities(
            has_model_selector=True,
            active_model="active-default",
            available_models=["active-default", "tier-high"],
            profile_tiers={"high": "tier-high"},
        )
        profile = AbstractTaskProfile(recommended_tier="high")
        task = TaskCharacteristics(difficulty="high")

        res = select_configuration(host, task, profile, approved_preview=False)
        self.assertEqual(res.readiness, "READY")
        self.assertEqual(res.execution_config.model, "active-default")
        self.assertTrue(res.fallback_used)
        self.assertIn("User rejected", res.fallback_reason)

    def test_peer_topologies_cases_a_b_c_d(self) -> None:
        """Verify generation of Case A, Case B, Case C, and Case D peer topologies."""
        profile = AbstractTaskProfile(recommended_tier="high")

        # Case A: Fixed single model, single pass
        host_a = HostCapabilities(has_model_selector=False, active_model="sonnet")
        task_a = TaskCharacteristics(shape="single-pass")
        res_a = select_configuration(host_a, task_a, profile)
        self.assertEqual(res_a.execution_config.topology, "Case A")
        self.assertEqual(res_a.execution_config.model, "sonnet")

        # Case B: Fixed single model, decomposed
        task_b = TaskCharacteristics(shape="decomposed", formal_tickets_exist=True)
        res_b = select_configuration(host_a, task_b, profile)
        self.assertEqual(res_b.execution_config.topology, "Case B")
        self.assertEqual(res_b.execution_config.model, "sonnet")

        # Case C: Tiered multi-model, single pass
        host_c = HostCapabilities(
            has_model_selector=True,
            active_model="gpt-4o",
            available_models=["gpt-4o", "o3-mini"],
            profile_tiers={"routine": "gpt-4o", "high": "o3-mini"},
        )
        res_c = select_configuration(host_c, task_a, profile)
        self.assertEqual(res_c.execution_config.topology, "Case C")
        self.assertEqual(res_c.execution_config.model, "o3-mini")

        # Case D: Tiered multi-model, decomposed
        host_d = HostCapabilities(
            has_model_selector=True,
            per_agent_config=True,
            active_model="gpt-4o",
            available_models=["gpt-4o", "o3-mini"],
            profile_tiers={"routine": "gpt-4o", "high": "o3-mini"},
        )
        res_d = select_configuration(host_d, task_b, profile)
        self.assertEqual(res_d.execution_config.topology, "Case D")
        self.assertEqual(res_d.execution_config.model, "o3-mini")

    def test_abstract_task_profile_deterministic_fallback(self) -> None:
        """Verify deterministic profiling maps task characteristics properly."""
        task_routine = TaskCharacteristics(difficulty="routine", cost_sensitive=True)
        prof_routine = build_deterministic_profile(task_routine)
        self.assertEqual(prof_routine.recommended_tier, "routine")
        self.assertEqual(prof_routine.reasoning_need, "low")

        task_high = TaskCharacteristics(difficulty="high")
        prof_high = build_deterministic_profile(task_high)
        self.assertEqual(prof_high.recommended_tier, "high")
        self.assertEqual(prof_high.reasoning_need, "high")

    def test_mock_jev_abstract_profiler(self) -> None:
        """Verify abstract task profiling via mock Jev System One."""
        mock_choice_tier = MagicMock()
        mock_choice_tier.choice = "high"
        mock_choice_tier.confidence = 0.92

        mock_choice_reasoning = MagicMock()
        mock_choice_reasoning.choice = "high"
        mock_choice_reasoning.confidence = 0.88

        mock_resp = MagicMock()
        mock_resp.choices = {
            "recommended_tier": mock_choice_tier,
            "reasoning_need": mock_choice_reasoning,
        }

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(title="Complex refactor", description="Deep concurrency rework", difficulty="high")

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)
                self.assertEqual(prof.recommended_tier, "high")
                self.assertEqual(prof.reasoning_need, "high")
                self.assertEqual(conf, 0.92)
                self.assertFalse(fallback)


if __name__ == "__main__":
    unittest.main()
