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
    def consume_agent_config_result(
        cls,
        agent_config_result: dict[str, Any],
        user_setup_response: str | None = None,
    ) -> dict[str, Any]:
        """Consumes AgentConfigResult according to implement consumption rules."""
        readiness = agent_config_result.get("readiness")

        if readiness == "READY":
            exec_cfg = agent_config_result.get("execution_config")
            if exec_cfg is None:
                return {
                    "action": "BLOCKED",
                    "halted": True,
                    "reason": "invariant violation: execution_config must not be null when readiness is READY",
                }
            return {
                "action": "execute_with_agent_config",
                "execution_config": exec_cfg,
                "handoff": agent_config_result.get("handoff", "implement"),
                "reason": "consumed execution_config and executing bounded slice",
            }

        if readiness == "NEED_INPUT":
            setup_state = agent_config_result.get("setup_state", {})
            profile_state = setup_state.get("profile")
            if user_setup_response == "decline":
                return {
                    "action": "execute_direct",
                    "reason": "user declined setup; fallback safely to direct single-agent execution",
                }
            if user_setup_response == "accept":
                return {
                    "action": "handoff_to_setup",
                    "handoff": "setup",
                    "reason": "user accepted setup; handing off to setup",
                }
            return {
                "action": "offer_setup",
                "handoff": agent_config_result.get("handoff", "setup"),
                "profile_state": profile_state,
                "reason": "profile missing or setup needed; offer setup or fallback",
            }

        if readiness == "NEED_PROJECT_TICKETS":
            return {
                "action": "handoff_to_project_tickets",
                "handoff": "project-tickets",
                "halted": True,
                "reason": "decomposed task without tickets requires formal tickets; halting implementation",
            }

        if readiness in {"BLOCKED", "UNSUPPORTED"}:
            return {
                "action": readiness,
                "halted": True,
                "reason": agent_config_result.get("reason", f"core rejection: {readiness}"),
                "diagnostics": agent_config_result.get("diagnostics", []),
            }

        return {
            "action": "BLOCKED",
            "halted": True,
            "reason": f"unknown readiness state: {readiness}",
        }

    @classmethod
    def decide_action(
        cls,
        task: dict[str, Any],
        user_intent: str | None = None,
        user_choice_response: str | None = None,
        host_capabilities: dict[str, Any] | None = None,
        agent_config_result: dict[str, Any] | None = None,
        user_setup_response: str | None = None,
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
            if agent_config_result is not None:
                consumption = cls.consume_agent_config_result(
                    agent_config_result, user_setup_response=user_setup_response
                )
                return {
                    **consumption,
                    "offered_agent_config": False,
                    "invoked_agent_config": True,
                }
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
            if agent_config_result is not None:
                consumption = cls.consume_agent_config_result(
                    agent_config_result, user_setup_response=user_setup_response
                )
                return {
                    **consumption,
                    "offered_agent_config": True,
                    "invoked_agent_config": True,
                }
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

    def test_happy_path_ticket_offer_accept_ready_consumes(self) -> None:
        """Happy path: Ticket item -> offer -> accept -> agent-config returns READY with execution_config -> implement consumes."""
        task = {
            "name": "implement user authentication token",
            "files": ["auth.ts", "session.ts", "token.ts", "test_auth.ts"],
            "change_units": ["auth", "token"],
            "ticket": ".scratch/auth-feature/issues/01-auth-token.md",
        }
        agent_config_result = {
            "readiness": "READY",
            "mode": "persisted",
            "setup_state": {"companion": "ready", "profile": "persisted"},
            "handoff": "implement",
            "execution_config": {
                "task_shape": "single-pass",
                "model_mode": "single",
                "topology": {"type": "single-pass", "mode": "single-model"},
                "execution": {
                    "model": "claude-sonnet-4",
                    "effort": "high",
                    "reasoning": {
                        "state": "supported",
                        "policy": "highest-supported",
                        "resolved": {"host_field": "effort", "host_value": "high"},
                    },
                    "context": "current-session",
                },
                "review": {
                    "type": "Self-check",
                    "model": "claude-sonnet-4",
                },
            },
            "reason": "Single-pass execution ready with persisted profile",
        }

        # User accepts offer
        result = ImplementDecisionEngine.decide_action(
            task,
            user_choice_response="accept",
            agent_config_result=agent_config_result,
        )

        self.assertEqual(result["action"], "execute_with_agent_config")
        self.assertTrue(result["offered_agent_config"])
        self.assertTrue(result["invoked_agent_config"])
        self.assertIsNotNone(result.get("execution_config"))
        self.assertEqual(
            result["execution_config"]["execution"]["model"],
            "claude-sonnet-4",
        )
        self.assertEqual(
            result["execution_config"]["execution"]["reasoning"]["resolved"]["host_value"],
            "high",
        )
        self.assertEqual(result.get("handoff"), "implement")

    def test_failure_path_missing_profile_need_input_setup_offer_and_fallback(self) -> None:
        """Failure path 1: Missing profile -> agent-config returns NEED_INPUT (profile missing, handoff setup) -> implement offers setup / fallback."""
        task = {
            "name": "large refactor",
            "files": ["a.ts", "b.ts", "c.ts", "d.ts"],
            "change_units": ["a", "b", "c"],
        }
        agent_config_result = {
            "readiness": "NEED_INPUT",
            "mode": "plan-only",
            "setup_state": {"companion": "ready", "profile": "missing"},
            "handoff": "setup",
            "execution_config": None,
            "reason": "Host environment has no user-confirmed profile configured",
        }

        # Step 1: When user accepted routing, agent-config returns NEED_INPUT -> implement offers setup
        result = ImplementDecisionEngine.decide_action(
            task,
            user_choice_response="accept",
            agent_config_result=agent_config_result,
        )
        self.assertEqual(result["action"], "offer_setup")
        self.assertEqual(result["handoff"], "setup")
        self.assertEqual(result.get("profile_state"), "missing")

        # Step 2: User accepts setup -> handoff to setup
        result_accept_setup = ImplementDecisionEngine.decide_action(
            task,
            user_choice_response="accept",
            agent_config_result=agent_config_result,
            user_setup_response="accept",
        )
        self.assertEqual(result_accept_setup["action"], "handoff_to_setup")
        self.assertEqual(result_accept_setup["handoff"], "setup")

        # Step 3: User declines setup -> safe fallback to direct single-agent execution without blocking
        result_decline_setup = ImplementDecisionEngine.decide_action(
            task,
            user_choice_response="accept",
            agent_config_result=agent_config_result,
            user_setup_response="decline",
        )
        self.assertEqual(result_decline_setup["action"], "execute_direct")
        self.assertNotEqual(result_decline_setup["action"], "BLOCKED")

    def test_failure_path_decomposed_without_tickets_halts_and_hands_off(self) -> None:
        """Failure path 2: Decomposed without tickets -> agent-config returns NEED_PROJECT_TICKETS -> implement halts and hands off."""
        task = {
            "name": "entire payment architecture overhaul",
            "files": ["gateway.ts", "webhook.ts", "ledger.ts", "retry.ts", "crypto.ts"],
            "change_units": ["gateway", "webhook", "ledger"],
            "requires_ticket_decomposition": True,
        }
        agent_config_result = {
            "readiness": "NEED_PROJECT_TICKETS",
            "mode": "persisted",
            "setup_state": {"companion": "ready", "profile": "persisted"},
            "handoff": "project-tickets",
            "execution_config": None,
            "reason": "Decomposed task requires formal tickets before implementation can proceed",
        }

        result = ImplementDecisionEngine.decide_action(
            task,
            user_choice_response="accept",
            agent_config_result=agent_config_result,
        )

        self.assertEqual(result["action"], "handoff_to_project_tickets")
        self.assertEqual(result["handoff"], "project-tickets")
        self.assertTrue(result["halted"])
        self.assertIn("formal tickets", result["reason"])

    def test_failure_path_unauthorized_model_or_unknown_capability_halts(self) -> None:
        """Failure path 3: Unauthorized model / unknown capability -> agent-config returns BLOCKED / UNSUPPORTED -> implement halts."""
        task = {
            "name": "isolated algorithm implementation",
            "files": ["algo.ts", "test_algo.ts"],
            "change_units": ["algo"],
        }
        # BLOCKED case: unauthorized model
        blocked_result = {
            "readiness": "BLOCKED",
            "mode": "persisted",
            "setup_state": {"companion": "ready", "profile": "persisted"},
            "handoff": None,
            "execution_config": None,
            "reason": "Selected model 'unauthorized-gpt-5' is not authorized in user profile",
            "diagnostics": ["Model not in single_model or tiers"],
        }
        result_blocked = ImplementDecisionEngine.decide_action(
            task,
            user_intent="explicit_enable",
            agent_config_result=blocked_result,
        )
        self.assertEqual(result_blocked["action"], "BLOCKED")
        self.assertTrue(result_blocked["halted"])
        self.assertIn("not authorized", result_blocked["reason"])
        self.assertIn("Model not in single_model or tiers", result_blocked["diagnostics"])

        # UNSUPPORTED case: unknown capability
        unsupported_result = {
            "readiness": "UNSUPPORTED",
            "mode": "persisted",
            "setup_state": {"companion": "ready", "profile": "persisted"},
            "handoff": None,
            "execution_config": None,
            "reason": "Host runtime does not support required capability 'subagents'",
            "diagnostics": ["capabilities.subagents is false or unknown"],
        }
        result_unsupported = ImplementDecisionEngine.decide_action(
            task,
            user_intent="explicit_enable",
            agent_config_result=unsupported_result,
        )
        self.assertEqual(result_unsupported["action"], "UNSUPPORTED")
        self.assertTrue(result_unsupported["halted"])
        self.assertIn("capability 'subagents'", result_unsupported["reason"])



if __name__ == "__main__":
    unittest.main(verbosity=2)
