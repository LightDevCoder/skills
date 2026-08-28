"""Contract simulation / behavior model tests for implement decision rules (SPEC §11).

Validates the decision logic and behavioral model of implement when
interacting with agent-config, user intent, and host model-selection limits
using test-local simulation.
"""

from __future__ import annotations

import unittest
from typing import Any


class ImplementDecisionEngine:
    """Deterministic model of implement's routing evaluation and execution dispatch."""

    @staticmethod
    def evaluate_routing_need(task: dict[str, Any]) -> bool:
        """Determines if routing/orchestration would materially help the task."""
        units_count = len(task.get("change_units", []))
        files_count = len(task.get("files", []))
        requires_role_split = bool(task.get("requires_role_split", False))
        requires_reviewer_isolation = bool(task.get("requires_reviewer_isolation", False))
        is_solo = bool(task.get("is_solo_bounded", False))

        if is_solo and units_count <= 1 and files_count <= 2 and not requires_reviewer_isolation:
            return False

        return (
            units_count > 1
            or files_count > 3
            or requires_role_split
            or requires_reviewer_isolation
        )

    @classmethod
    def decide_action(
        cls,
        task: dict[str, Any],
        user_intent: str | None = None,
        user_choice_response: str | None = None,
        host_capabilities: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Simulates implement's decision process for a given task and environment."""
        host_caps = host_capabilities or {}
        has_model_selector = host_caps.get("model_selection") == "available"
        has_executable_model = host_caps.get("has_executable_model", True)

        if not has_executable_model:
            return {
                "action": "BLOCKED",
                "offered_agent_config": False,
                "invoked_agent_config": False,
                "reason": "no executable model available",
            }

        # Case E & F: Explicit user intent overrides
        if user_intent == "explicit_enable":
            return {
                "action": "execute_with_agent_config",
                "offered_agent_config": False,
                "invoked_agent_config": True,
                "reason": "explicit user request to use routing",
            }
        if user_intent == "explicit_disable":
            return {
                "action": "execute_direct",
                "offered_agent_config": False,
                "invoked_agent_config": False,
                "reason": "explicit user request to skip routing",
            }

        materially_helpful = cls.evaluate_routing_need(task)

        # Case A: Simple bounded solo task
        if not materially_helpful:
            return {
                "action": "execute_direct",
                "offered_agent_config": False,
                "invoked_agent_config": False,
                "reason": "bounded solo task does not require routing offer",
            }

        # Case B: Complex task with routing value -> offer agent-config
        if user_choice_response is None:
            return {
                "action": "await_user_choice",
                "offered_agent_config": True,
                "invoked_agent_config": False,
                "reason": "offering agent-config for user opt-in",
            }

        # Case C: User accepts
        if user_choice_response == "accept":
            return {
                "action": "execute_with_agent_config",
                "offered_agent_config": True,
                "invoked_agent_config": True,
                "reason": "user accepted agent-config routing",
            }

        # Case D: User declines
        if user_choice_response == "decline":
            return {
                "action": "execute_direct",
                "offered_agent_config": True,
                "invoked_agent_config": False,
                "reason": "user declined agent-config routing; direct execution proceeds",
            }

        return {
            "action": "execute_direct",
            "offered_agent_config": True,
            "invoked_agent_config": False,
            "reason": "fallback to direct execution",
        }


class ImplementBehaviorTest(unittest.TestCase):
    def test_case_a_simple_bounded_solo_task(self) -> None:
        """Case A: Simple bounded solo task -> no offer, direct implementation."""
        task = {
            "name": "fix typo in README",
            "is_solo_bounded": True,
            "files": ["README.md"],
            "change_units": ["doc-fix"],
        }
        result = ImplementDecisionEngine.decide_action(task)
        self.assertEqual(result["action"], "execute_direct")
        self.assertFalse(result["offered_agent_config"])
        self.assertFalse(result["invoked_agent_config"])

    def test_case_b_complex_task_with_routing_value_offers_choice(self) -> None:
        """Case B: Complex task with routing value -> offer agent-config, do not invoke before choice."""
        task = {
            "name": "multi-backend storage implementation",
            "is_solo_bounded": False,
            "files": ["driver.ts", "memory.ts", "file.ts", "test_harness.ts"],
            "change_units": ["driver", "memory", "file"],
        }
        result = ImplementDecisionEngine.decide_action(task, user_choice_response=None)
        self.assertEqual(result["action"], "await_user_choice")
        self.assertTrue(result["offered_agent_config"])
        self.assertFalse(result["invoked_agent_config"])

    def test_case_c_user_accepts_routing_offer(self) -> None:
        """Case C: User accepts -> agent-config invoked."""
        task = {
            "name": "multi-backend storage implementation",
            "files": ["driver.ts", "memory.ts", "file.ts", "test_harness.ts"],
            "change_units": ["driver", "memory", "file"],
        }
        result = ImplementDecisionEngine.decide_action(task, user_choice_response="accept")
        self.assertEqual(result["action"], "execute_with_agent_config")
        self.assertTrue(result["offered_agent_config"])
        self.assertTrue(result["invoked_agent_config"])

    def test_case_d_user_declines_routing_offer(self) -> None:
        """Case D: User declines -> agent-config not invoked, implementation continues directly."""
        task = {
            "name": "multi-backend storage implementation",
            "files": ["driver.ts", "memory.ts", "file.ts", "test_harness.ts"],
            "change_units": ["driver", "memory", "file"],
        }
        result = ImplementDecisionEngine.decide_action(task, user_choice_response="decline")
        self.assertEqual(result["action"], "execute_direct")
        self.assertTrue(result["offered_agent_config"])
        self.assertFalse(result["invoked_agent_config"])
        self.assertNotEqual(result["action"], "BLOCKED")

    def test_case_e_explicit_user_request_for_agent_config(self) -> None:
        """Case E: User explicitly requests agent-config -> invoke directly without redundant prompt."""
        task = {
            "name": "refactor subsystem",
            "files": ["a.ts", "b.ts"],
            "change_units": ["a", "b"],
        }
        result = ImplementDecisionEngine.decide_action(task, user_intent="explicit_enable")
        self.assertEqual(result["action"], "execute_with_agent_config")
        self.assertFalse(result["offered_agent_config"])
        self.assertTrue(result["invoked_agent_config"])

    def test_case_f_explicit_user_disable_for_agent_config(self) -> None:
        """Case F: User explicitly disables agent-config -> do not offer, do not invoke, continue."""
        task = {
            "name": "refactor subsystem",
            "files": ["a.ts", "b.ts", "c.ts", "d.ts"],
            "change_units": ["a", "b", "c"],
        }
        result = ImplementDecisionEngine.decide_action(task, user_intent="explicit_disable")
        self.assertEqual(result["action"], "execute_direct")
        self.assertFalse(result["offered_agent_config"])
        self.assertFalse(result["invoked_agent_config"])

    def test_case_g_host_lacks_model_selector(self) -> None:
        """Case G: Host lacks model selector -> implement remains usable, no automatic BLOCKED."""
        task = {
            "name": "implement payment webhook",
            "files": ["webhook.ts", "test_webhook.ts"],
            "change_units": ["webhook"],
        }
        host_caps = {"model_selection": "unavailable", "has_executable_model": True}
        result = ImplementDecisionEngine.decide_action(
            task, user_choice_response="decline", host_capabilities=host_caps
        )
        self.assertEqual(result["action"], "execute_direct")
        self.assertNotEqual(result["action"], "BLOCKED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
