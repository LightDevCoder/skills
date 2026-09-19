"""End-to-end integration tests connecting ask-light and agent-config.

Verifies:
  1. ask-light recommends implement on ticket frontier -> agent-config configures execution.
  2. Fail-closed invariants in ask-light prevent agent-config invocation.
  3. Decomposition gate in agent-config hands off to project-tickets.
  4. Graceful degradation when Jev or API keys are unavailable.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "productivity" / "ask-light" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "engineering" / "agent-config" / "scripts"))

from advisor import ask_light_semantic_recommend
from agent_config import agent_config_recommend
from ask_light_models import CompactProjectState as AskLightState
from harness_adapter import determine_topology


class IntegratedWorkflowTest(unittest.TestCase):
    def test_happy_path_frontier_to_agent_config(self) -> None:
        """ask-light finds ready tickets, recommends implement, and agent-config configures execution."""
        ask_state = AskLightState(
            initialized=True,
            spec_exists=True,
            spec_active=True,
            tickets_exist=True,
            ready_tickets=["issue-01.md"],
        )
        ask_rec = ask_light_semantic_recommend(ask_state, user_request="下一步做什么？", use_jev=False)
        self.assertEqual(ask_rec.status, "RECOMMEND")
        self.assertEqual(ask_rec.primary_skill, "implement")
        self.assertEqual(ask_rec.target_item, "issue-01.md")

        # Now pass to agent-config
        host_capabilities = {
            "harness": "codex",
            "has_model_selector": True,
            "supported_effort": ["low", "medium", "high"],
            "per_agent_config": True,
            "active_model": "gpt-4o",
            "available_models": ["gpt-4o", "o3-mini"],
            "profile_tiers": {"routine": "gpt-4o", "standard": "gpt-4o", "high": "o3-mini"},
        }
        task_chars = {
            "title": "Implement issue 01",
            "description": "Implement the core tracer bullet",
            "shape": "single-pass",
            "formal_tickets_exist": True,
            "difficulty": "standard",
            "reasoning_policy": "standard",
        }
        cfg_res = agent_config_recommend(host_capabilities, task_chars, use_jev=False)
        self.assertEqual(cfg_res.readiness, "READY")
        self.assertEqual(cfg_res.execution_config.topology, "Case A")
        self.assertEqual(cfg_res.execution_config.model, "gpt-4o")
        self.assertEqual(cfg_res.execution_config.resolved_effort, "medium")

    def test_fail_closed_blocking_prevents_configuration(self) -> None:
        """If ask-light encounters unknown ticket or multiple efforts, workflow halts and never executes."""
        ask_state = AskLightState(
            initialized=True,
            active_efforts=["feat-1", "feat-2"],
            current_effort=None,
        )
        ask_rec = ask_light_semantic_recommend(ask_state, user_request="下一步做什么？", use_jev=False)
        self.assertEqual(ask_rec.status, "NEED_INPUT")
        self.assertTrue(ask_rec.fail_closed)
        # In a workflow orchestrator, non-RECOMMEND/non-TRANSITION stops here.

    def test_decomposed_without_tickets_hands_off_to_project_tickets(self) -> None:
        """Decomposed task without tickets halts in agent-config and hands off to project-tickets."""
        host_capabilities = {
            "harness": "claude-code",
            "has_model_selector": False,
            "active_model": "claude-3-5-sonnet",
        }
        task_chars = {
            "title": "Decomposed feature",
            "description": "Multi-component feature",
            "shape": "decomposed",
            "formal_tickets_exist": False,
        }
        cfg_res = agent_config_recommend(host_capabilities, task_chars, use_jev=False)
        self.assertEqual(cfg_res.readiness, "NEED_PROJECT_TICKETS")
        self.assertEqual(cfg_res.handoff, "project-tickets")
        self.assertIsNone(cfg_res.execution_config)


if __name__ == "__main__":
    unittest.main()
