"""End-to-end integration tests connecting ask-light and agent-config.

Verifies:
  1. ask-light recommends implement on ticket frontier -> agent-config configures execution.
  2. Fail-closed invariants in ask-light prevent agent-config invocation.
  3. Decomposition gate in agent-config hands off to project-tickets.
  4. Graceful degradation when Jev or API keys are unavailable.
"""

from __future__ import annotations

import sys
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "productivity" / "ask-light" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "engineering" / "agent-config" / "scripts"))

from advisor import ask_light_semantic_recommend
from agent_config import agent_config_recommend
from ask_light_models import CompactProjectState as AskLightState
from harness_adapter import determine_topology
from agent_config_models import HostCapabilities


def canonical_host_and_profile(mode: str = "multi") -> tuple[dict, dict]:
    fixtures = ROOT / "skills/engineering/agent-config/tests/fixtures"
    host_name = "case-c-fixed-single-pass.json" if mode == "single" else "case-a-tiered-single-pass.json"
    host = json.loads((fixtures / host_name).read_text())
    profile = json.loads((fixtures / f"profile-{mode}-model.json").read_text())
    now = datetime.now(timezone.utc).isoformat()
    host["observed_at"] = now
    host["workspace"] = profile["scope"]["workspace"]
    for model in host["available_models"]:
        model["evidence"]["observed_at"] = now
    for capability in host["capabilities"].values():
        if "evidence" in capability:
            capability["evidence"]["observed_at"] = now
    return host, profile


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
        host_capabilities, confirmed_profile = canonical_host_and_profile()
        task_chars = {
            "title": "Implement issue 01",
            "description": "Implement the core tracer bullet",
            "shape": "single-pass",
            "formal_tickets_exist": True,
            "difficulty": "standard",
            "reasoning_policy": "standard",
        }
        cfg_res = agent_config_recommend(host_capabilities, task_chars, profile=confirmed_profile, use_jev=False)
        self.assertEqual(cfg_res.readiness, "READY")
        self.assertEqual(cfg_res.execution_config.topology, "Case C")
        self.assertEqual(cfg_res.execution_config.model, "model-beta")
        self.assertEqual(cfg_res.execution_config.resolved_effort, "medium")

    def test_canonical_host_rejects_synthetic_and_unconfirmed_effort_evidence(self) -> None:
        task = {"title": "Review implementation", "shape": "single-pass", "reasoning_policy": "highest-supported"}
        host, profile = canonical_host_and_profile()
        for model in host["available_models"]:
            model["evidence"]["kind"] = "fallback-default"
        for capability in host["capabilities"].values():
            if "evidence" in capability:
                capability["evidence"]["kind"] = "fallback-default"
        self.assertEqual(agent_config_recommend(host, task, profile=profile, use_jev=False).readiness, "NEED_INPUT")

        host, profile = canonical_host_and_profile()
        host["capabilities"]["reasoning"]["state"] = "unknown"
        result = agent_config_recommend(host, task, profile=profile, use_jev=False)
        self.assertEqual(result.readiness, "NEED_INPUT")
        self.assertIsNone(result.execution_config)

    def test_unsupported_effort_and_unconfirmed_current_model_stop(self) -> None:
        host, profile = canonical_host_and_profile()
        result = agent_config_recommend(
            host, {"shape": "single-pass", "reasoning_policy": "ultra"},
            profile=profile, use_jev=False,
        )
        self.assertEqual(result.readiness, "NEED_INPUT")
        self.assertIsNone(result.execution_config)

        single_host, single_profile = canonical_host_and_profile("single")
        single_host["capabilities"]["model_selection"]["state"] = "available"
        self.assertEqual(
            agent_config_recommend(single_host, {"shape": "single-pass"},
                                   profile=single_profile, use_jev=False).readiness,
            "NEED_INPUT",
        )
        approved = agent_config_recommend(
            single_host, {"shape": "single-pass"}, profile=single_profile,
            approval="approved", use_jev=False,
        )
        self.assertEqual(approved.readiness, "NEED_INPUT")
        self.assertIsNone(approved.execution_config)
        active_session = {
            "host_id": single_host["host_id"], "adapter_id": single_host["adapter_id"],
            "workspace": single_host["workspace"], "model": "model-alpha",
            "observed_at": single_host["observed_at"],
            "evidence": {"kind": "host-runtime", "locator": "current session model", "observed_at": single_host["observed_at"]},
        }
        verified = agent_config_recommend(
            single_host, {"shape": "single-pass"}, profile=single_profile,
            active_session=active_session, use_jev=False,
        )
        self.assertEqual(verified.readiness, "READY")
        self.assertEqual(verified.execution_config.topology, "Case A")
        wrong_session = {**active_session, "adapter_id": "other-adapter"}
        self.assertEqual(agent_config_recommend(
            single_host, {"shape": "single-pass"}, profile=single_profile,
            active_session=wrong_session, use_jev=False,
        ).readiness, "NEED_INPUT")
        stale_session = {**active_session, "observed_at": "2026-01-01T00:00:00Z"}
        self.assertEqual(agent_config_recommend(
            single_host, {"shape": "single-pass"}, profile=single_profile,
            active_session=stale_session, use_jev=False,
        ).readiness, "NEED_INPUT")
        single_host["capabilities"]["model_selection"]["scopes"] = ["new-session"]
        self.assertEqual(agent_config_recommend(
            single_host, {"shape": "single-pass"}, profile=single_profile,
            approval="approved", use_jev=False,
        ).readiness, "NEED_INPUT")
        single_host["capabilities"]["model_selection"]["state"] = "unavailable"
        extra = json.loads(json.dumps(single_host["available_models"][0]))
        extra["id"] = "model-beta"
        single_host["available_models"].append(extra)
        self.assertEqual(
            agent_config_recommend(single_host, {"shape": "single-pass"},
                                   profile=single_profile, use_jev=False).readiness,
            "NEED_INPUT",
        )

    def test_malformed_canonical_host_or_profile_stops_cleanly(self) -> None:
        host, profile = canonical_host_and_profile()
        host["capabilities"] = []
        self.assertEqual(agent_config_recommend(host, {}, profile=profile, use_jev=False).readiness, "NEED_INPUT")
        host, profile = canonical_host_and_profile()
        profile["host"] = []
        self.assertEqual(agent_config_recommend(host, {}, profile=profile, use_jev=False).readiness, "NEED_INPUT")
        host, profile = canonical_host_and_profile()
        del profile["profile_version"]
        self.assertEqual(agent_config_recommend(host, {}, profile=profile, use_jev=False).readiness, "NEED_INPUT")
        host, profile = canonical_host_and_profile()
        self.assertEqual(agent_config_recommend(
            host, {"reasoning_policy": ["high"]}, profile=profile, use_jev=False,
        ).readiness, "NEED_INPUT")

    def test_custom_effort_requires_value_and_host_literal_is_preserved(self) -> None:
        host, profile = canonical_host_and_profile()
        profile["tiers"]["standard"]["effort"] = {"policy": "custom"}
        self.assertEqual(agent_config_recommend(host, {}, profile=profile, use_jev=False).readiness, "NEED_INPUT")
        host, profile = canonical_host_and_profile()
        host["supported_effort_values"] = ["Low", "Deep"]
        result = agent_config_recommend(host, {"reasoning_policy": "Deep"}, profile=profile, use_jev=False)
        self.assertEqual(result.readiness, "READY")
        self.assertEqual(result.execution_config.resolved_effort, "Deep")
        host, profile = canonical_host_and_profile()
        profile["tiers"]["standard"]["effort"] = {"policy": "custom", "value": ""}
        self.assertEqual(agent_config_recommend(host, {}, profile=profile, use_jev=False).readiness, "NEED_INPUT")

    def test_new_session_only_selector_cannot_claim_current_session_ready(self) -> None:
        host, profile = canonical_host_and_profile()
        host["capabilities"]["model_selection"]["scopes"] = ["new-session"]
        result = agent_config_recommend(host, {"shape": "single-pass"}, profile=profile, use_jev=False)
        self.assertEqual(result.readiness, "NEED_INPUT")
        self.assertIsNone(result.execution_config)

    def test_multi_profile_remains_case_c_when_current_model_matches_target(self) -> None:
        host, profile = canonical_host_and_profile()
        active_session = {
            "host_id": host["host_id"], "adapter_id": host["adapter_id"],
            "workspace": host["workspace"], "model": "model-beta",
            "observed_at": host["observed_at"],
            "evidence": {"kind": "host-runtime", "locator": "current session model", "observed_at": host["observed_at"]},
        }
        result = agent_config_recommend(host, {"shape": "single-pass"},
                                        profile=profile, active_session=active_session,
                                        use_jev=False)
        self.assertEqual(result.readiness, "READY")
        self.assertEqual(result.execution_config.topology, "Case C")

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
        host_capabilities, confirmed_profile = canonical_host_and_profile("single")
        task_chars = {
            "title": "Decomposed feature",
            "description": "Multi-component feature",
            "shape": "decomposed",
            "formal_tickets_exist": False,
        }
        cfg_res = agent_config_recommend(host_capabilities, task_chars, profile=confirmed_profile, use_jev=False)
        self.assertEqual(cfg_res.readiness, "NEED_PROJECT_TICKETS")
        self.assertEqual(cfg_res.handoff, "project-tickets")
        self.assertIsNone(cfg_res.execution_config)

    def test_agent_config_rejects_missing_stale_or_mismatched_evidence(self) -> None:
        host, profile = canonical_host_and_profile()
        self.assertEqual(agent_config_recommend({}, {}, use_jev=False).readiness, "NEED_INPUT")
        self.assertEqual(agent_config_recommend(HostCapabilities(active_model="model-alpha", available_models=["model-alpha"], profile_tiers={"high": "model-alpha"}), {}, use_jev=False).readiness, "NEED_INPUT")
        self.assertEqual(agent_config_recommend(host, {}, use_jev=False).readiness, "NEED_INPUT")
        stale = {**host, "observed_at": "2020-01-01T00:00:00Z"}
        self.assertEqual(agent_config_recommend(stale, {}, profile=profile, use_jev=False).readiness, "NEED_INPUT")
        wrong = json.loads(json.dumps(profile))
        wrong["host"]["adapter"] = "other-adapter"
        self.assertEqual(agent_config_recommend(host, {}, profile=wrong, use_jev=False).readiness, "NEED_INPUT")

    def test_high_tier_never_falls_back_to_lower_model(self) -> None:
        host, profile = canonical_host_and_profile()
        host["available_models"] = [model for model in host["available_models"] if model["id"] != "model-gamma"]
        result = agent_config_recommend(host, {"difficulty": "critical", "difficulty_source": "explicit-user"}, profile=profile, use_jev=False)
        self.assertEqual(result.readiness, "NEED_INPUT")
        self.assertIsNone(result.execution_config)


if __name__ == "__main__":
    unittest.main()
