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
        """Verify abstract task profiling via mock Jev System One Score primitives."""
        mock_score_comp = MagicMock()
        mock_score_comp.score = 2.2  # maps to high / critical
        mock_score_comp.confidence = 0.92

        mock_score_reas = MagicMock()
        mock_score_reas.score = 1.9  # maps to high
        mock_score_reas.confidence = 0.88

        mock_resp = MagicMock()
        mock_resp.scores = {
            "task_complexity": mock_score_comp,
            "reasoning_need": mock_score_reas,
        }

        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(title="Complex refactor", description="Deep concurrency rework", difficulty="high")

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)
                self.assertEqual(prof.recommended_tier, "high")
                self.assertEqual(prof.reasoning_need, "high")
                self.assertEqual(prof.complexity_confidence, 0.92)
                self.assertEqual(prof.reasoning_confidence, 0.88)
                self.assertEqual(conf, 0.88)  # Dimension-aware: min(0.92, 0.88)
                self.assertFalse(fallback)

    def test_jev_reasoning_need_influences_effort_when_no_explicit_policy(self) -> None:
        """P0 (Section 22): Jev reasoning_need influences resolved effort when user policy is None."""
        host = HostCapabilities(
            has_model_selector=True,
            active_model="gpt-4o",
            available_models=["gpt-4o", "o3-mini"],
            supported_effort=["low", "medium", "high"],
            profile_tiers={"routine": "gpt-4o", "high": "o3-mini"},
        )
        task = TaskCharacteristics(shape="single-pass", reasoning_policy=None)
        profile = AbstractTaskProfile(recommended_tier="high", reasoning_need="high")

        res = select_configuration(host, task, profile)
        self.assertEqual(res.execution_config.resolved_effort, "high")

    def test_explicit_user_effort_overrides_jev(self) -> None:
        """Section 22 & 25: Explicit user effort policy takes strict precedence over Jev."""
        host = HostCapabilities(
            supported_effort=["low", "medium", "high"],
            profile_tiers={"high": "o3-mini"},
        )
        # User explicitly requested minimal effort; Jev says high
        task = TaskCharacteristics(shape="single-pass", reasoning_policy="minimal")
        profile = AbstractTaskProfile(recommended_tier="high", reasoning_need="high")

        res = select_configuration(host, task, profile)
        self.assertEqual(res.execution_config.resolved_effort, "low")  # User policy wins

    def test_host_supported_effort_bounds_jev_output(self) -> None:
        """Section 22 & 30: Host supported effort strictly bounds Jev output; never invents unsupported values."""
        host = HostCapabilities(
            supported_effort=["low", "medium"],  # No 'high' supported
            profile_tiers={"high": "model-tier"},
        )
        task = TaskCharacteristics(reasoning_policy=None)
        profile = AbstractTaskProfile(recommended_tier="high", reasoning_need="high")

        res = select_configuration(host, task, profile)
        # Host cannot satisfy 'high', so it gracefully resolves to nearest supported level 'medium'
        self.assertEqual(res.execution_config.resolved_effort, "medium")

    def test_approval_unknown_is_not_treated_as_approved(self) -> None:
        """Section 28: Unknown preview approval is recommendation only (mode='plan-only', approval='unknown')."""
        host = HostCapabilities(
            has_model_selector=True,
            active_model="active-default",
            profile_tiers={"high": "high-model"},
        )
        task = TaskCharacteristics(difficulty="high")
        profile = AbstractTaskProfile(recommended_tier="high")

        res = select_configuration(host, task, profile)  # Default approval is unknown
        self.assertEqual(res.approval, "unknown")
        self.assertEqual(res.mode, "plan-only")

    def test_cost_sensitive_does_not_automatically_downgrade_capability(self) -> None:
        """Section 26: Cost sensitivity does NOT downgrade high complexity work to routine."""
        task = TaskCharacteristics(difficulty="high", cost_sensitive=True)
        prof = build_deterministic_profile(task)
        self.assertEqual(prof.recommended_tier, "high")
        self.assertEqual(prof.cost_sensitivity, "high")

    def test_cost_sensitive_standard_task_does_not_downgrade_to_routine(self) -> None:
        """P1 (Section 24-25): Standard task with cost_sensitive must stay standard, not downgrade to routine."""
        task = TaskCharacteristics(difficulty="standard", cost_sensitive=True)
        prof = build_deterministic_profile(task)
        self.assertEqual(prof.recommended_tier, "standard")
        self.assertEqual(prof.reasoning_need, "medium")

    def test_independent_per_dimension_confidence_fallback(self) -> None:
        """P1 (Sections 27-29): High-confidence complexity is retained when reasoning falls back."""
        mock_score_comp = MagicMock()
        mock_score_comp.score = 2.2  # high
        mock_score_comp.confidence = 0.95  # High confidence -> keep Jev

        mock_score_reas = MagicMock()
        mock_score_reas.score = 1.8
        mock_score_reas.confidence = 0.35  # Low confidence (<0.50) -> fallback reasoning only

        mock_resp = MagicMock()
        mock_resp.scores = {
            "task_complexity": mock_score_comp,
            "reasoning_need": mock_score_reas,
        }
        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(title="Complex feature", description="Refactor with low reasoning certainty", difficulty="standard")

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                # Complexity retained from Jev
                self.assertEqual(prof.recommended_tier, "high")
                self.assertEqual(prof.complexity_level, "high")
                self.assertFalse(prof.dimension_provenance["complexity"].fallback_used)
                self.assertEqual(prof.dimension_provenance["complexity"].source, "jev")

                # Reasoning fell back to deterministic baseline for standard (medium)
                self.assertEqual(prof.reasoning_need, "medium")
                self.assertTrue(prof.dimension_provenance["reasoning"].fallback_used)
                self.assertEqual(prof.dimension_provenance["reasoning"].source, "deterministic-fallback")

                self.assertTrue(fallback)
                self.assertIn("reasoning", reason)

    def test_score_discretization_boundaries(self) -> None:
        """P1 (Section 30): Explicit boundary validation for Score discretization mapping."""
        task = TaskCharacteristics(difficulty="standard")

        def make_mock_client(comp_score: float, reas_score: float):
            resp = MagicMock()
            s_comp = MagicMock(score=comp_score, confidence=0.99)
            s_reas = MagicMock(score=reas_score, confidence=0.99)
            resp.scores = {"task_complexity": s_comp, "reasoning_need": s_reas}
            client = MagicMock()
            client.system_one.return_value = resp
            return client

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                # Boundary 0.49 vs 0.50 for complexity
                p_under, _, _, _ = extract_abstract_task_profile(task, client=make_mock_client(0.49, 0.49))
                self.assertEqual(p_under.complexity_level, "routine")
                self.assertEqual(p_under.reasoning_need, "low")

                p_over, _, _, _ = extract_abstract_task_profile(task, client=make_mock_client(0.50, 0.50))
                self.assertEqual(p_over.complexity_level, "standard")
                self.assertEqual(p_over.reasoning_need, "medium")

                # Boundary 1.49 vs 1.50
                p_under2, _, _, _ = extract_abstract_task_profile(task, client=make_mock_client(1.49, 1.49))
                self.assertEqual(p_under2.complexity_level, "standard")
                self.assertEqual(p_under2.reasoning_need, "medium")

                p_over2, _, _, _ = extract_abstract_task_profile(task, client=make_mock_client(1.50, 1.50))
                self.assertEqual(p_over2.complexity_level, "high")
                self.assertEqual(p_over2.reasoning_need, "high")

                # Boundary 2.49 vs 2.50
                p_under3, _, _, _ = extract_abstract_task_profile(task, client=make_mock_client(2.49, 1.8))
                self.assertEqual(p_under3.complexity_level, "high")

                p_over3, _, _, _ = extract_abstract_task_profile(task, client=make_mock_client(2.50, 1.8))
                self.assertEqual(p_over3.complexity_level, "critical")
                self.assertEqual(p_over3.recommended_tier, "high")

    def test_authoritative_difficulty_skips_jev_complexity(self) -> None:
        """P1 (Section 15, 18, 41): Authoritative difficulty skips Jev complexity query; consumed by code."""
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.scores = {"reasoning_need": MagicMock(score=1.8, confidence=0.95)}
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Refactor distributed consensus",
            description="Replace synchronization logic",
            difficulty="high",
            difficulty_source="explicit-user",  # Authoritative source
            reasoning_policy=None,  # Reasoning still needs Jev
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                # Verified: task_complexity was NOT asked to Jev!
                called_questions = mock_client.system_one.call_args[1]["questions"]
                self.assertNotIn("task_complexity", called_questions)
                self.assertIn("reasoning_need", called_questions)

                # Complexity is code-owned with authoritative provenance
                self.assertEqual(prof.recommended_tier, "high")
                self.assertEqual(prof.complexity_level, "high")
                self.assertEqual(prof.dimension_provenance["complexity"].source, "explicit-user")
                self.assertFalse(prof.dimension_provenance["complexity"].fallback_used)

    def test_unknown_difficulty_invokes_jev_complexity(self) -> None:
        """P1 (Section 17, 41): Unknown difficulty invokes Jev task_complexity query."""
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.scores = {
            "task_complexity": MagicMock(score=2.2, confidence=0.90),
            "reasoning_need": MagicMock(score=1.8, confidence=0.90),
        }
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="New feature exploration",
            description="Implement complex multi-tier algorithm",
            difficulty="standard",
            difficulty_source="unknown",  # Not authoritative -> invokes Jev
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                called_questions = mock_client.system_one.call_args[1]["questions"]
                self.assertIn("task_complexity", called_questions)
                self.assertEqual(prof.dimension_provenance["complexity"].source, "jev")

    def test_serialized_jev_state_does_not_contain_expected_complexity_label(self) -> None:
        """P1 (Section 14, 21, 41): Serialized Jev state contains NO declared_difficulty or answer labels."""
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.scores = {"task_complexity": MagicMock(score=1.0, confidence=0.95)}
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Update API schema documentation",
            description="Fix endpoints documentation",
            difficulty="routine",
            difficulty_source="unknown",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                extract_abstract_task_profile(task, client=mock_client)

                called_state = mock_client.system_one.call_args[1]["state"]
                self.assertNotIn("declared_difficulty", called_state)
                self.assertNotIn("difficulty", called_state)
                self.assertNotIn("expected_tier", called_state)
                self.assertNotIn("expected_complexity", called_state)

    def test_serialized_jev_state_does_not_contain_expected_reasoning_label(self) -> None:
        """P1 (Section 19, 41): Serialized Jev state contains NO reasoning labels or hints."""
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.scores = {"reasoning_need": MagicMock(score=1.0, confidence=0.95)}
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Add retry logic",
            description="Retry transient network errors",
            difficulty_source="unknown",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                extract_abstract_task_profile(task, client=mock_client)

                called_state = mock_client.system_one.call_args[1]["state"]
                self.assertNotIn("reasoning_need", called_state)
                self.assertNotIn("expected_reasoning", called_state)
                self.assertNotIn("expected_level", called_state)

    def test_runtime_fixture_cannot_access_ground_truth_fields(self) -> None:
        """P1 (Section 21, 37, 41): validate_fixture_isolation blocks evaluation if ground truth leaks."""
        eval_candidates = [
            Path(__file__).resolve().parent.parent.parent.parent.parent / "evals" / "jev",
            Path(__file__).resolve().parents[5] / "evals" / "jev" if len(Path(__file__).resolve().parents) > 5 else None,
        ]
        import sys
        found = False
        for c in eval_candidates:
            if c and c.is_dir():
                if str(c) not in sys.path:
                    sys.path.insert(0, str(c))
                found = True
                break

        if not found:
            self.skipTest("evals/jev not present in standalone skill-only environment")

        try:
            from eval_agent_config import validate_fixture_isolation, AgentConfigScenario, AgentConfigExpected
        except ImportError:
            self.skipTest("eval_agent_config not importable in standalone skill-only environment")

        # 1. Real suite must pass isolation validation
        self.assertTrue(validate_fixture_isolation())

        # 2. Synthetic leaking scenario must be detected and blocked
        leaking_task = TaskCharacteristics(title="Leaking task")
        leaking_task.declared_difficulty = "high"  # type: ignore[attr-defined]

        leaking_scenario = AgentConfigScenario(
            id="AC-LEAK",
            name="Leaking test",
            host=HostCapabilities(),
            task=leaking_task,
            approval="approved",
            expected=AgentConfigExpected(
                expected_tier="high",
                expected_model="model-x",
                expected_topology="Case A",
                expected_readiness="READY",
            ),
        )

        with self.assertRaises(RuntimeError) as ctx:
            validate_fixture_isolation([leaking_scenario])
        self.assertIn("FIXTURE LEAKAGE DETECTED", str(ctx.exception))

    def test_explicit_reasoning_policy_skips_jev_reasoning_judgment(self) -> None:
        """P1 (Section 34, 41): Explicit reasoning policy skips Jev reasoning judgment."""
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.scores = {"task_complexity": MagicMock(score=0.2, confidence=0.90)}
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Documentation cleanup",
            description="Fix typos",
            difficulty="routine",
            difficulty_source="unknown",
            reasoning_policy="highest-supported",  # Explicit policy
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                called_questions = mock_client.system_one.call_args[1]["questions"]
                self.assertNotIn("reasoning_need", called_questions)
                self.assertIn("task_complexity", called_questions)
                self.assertEqual(prof.dimension_provenance["reasoning"].source, "explicit-policy")

    def test_semantic_fallback_keeps_workflow_config_functional(self) -> None:
        """P1 (Section 41): When Jev call fails completely, configuration remains fully functional."""
        from agent_config import agent_config_recommend

        failing_client = MagicMock()
        failing_client.system_one.side_effect = RuntimeError("Simulated API failure")

        host = HostCapabilities(
            has_model_selector=True,
            active_model="active-model",
            available_models=["active-model", "tier-high"],
            profile_tiers={"high": "tier-high"},
        )
        task = TaskCharacteristics(
            title="Critical bug",
            description="Fix critical vulnerability",
            difficulty="high",
            difficulty_source="unknown",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                res = agent_config_recommend(
                    host=host,
                    task=task,
                    approval="approved",
                    client=failing_client,
                )
                self.assertEqual(res.readiness, "READY")
                self.assertEqual(res.execution_config.model, "tier-high")
                self.assertTrue(res.fallback_used)

    def test_downgrade_policy_rejects_marginal_confidence_downgrade(self) -> None:
        """Verify downgrade from baseline standard to routine is rejected when evidence is marginal."""
        mock_score_comp = MagicMock()
        mock_score_comp.score = 0.41  # candidate routine
        mock_score_comp.confidence = 0.59  # marginal confidence (<0.75 threshold)

        mock_score_reas = MagicMock()
        mock_score_reas.score = 0.5
        mock_score_reas.confidence = 0.90

        mock_resp = MagicMock()
        mock_resp.scores = {
            "task_complexity": mock_score_comp,
            "reasoning_need": mock_score_reas,
        }
        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Fix off-by-one error in pagination",
            description="Page index starts at 0 instead of 1",
            difficulty="standard",
            difficulty_source="unknown",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                # Downgrade rejected! Retains baseline standard
                self.assertEqual(prof.recommended_tier, "standard")
                self.assertEqual(prof.complexity_level, "standard")
                self.assertTrue(prof.dimension_provenance["complexity"].fallback_used)
                self.assertEqual(prof.dimension_provenance["complexity"].source, "deterministic-fallback")
                self.assertIn("Downgrade from standard to routine rejected", prof.dimension_provenance["complexity"].fallback_reason)

    def test_downgrade_policy_accepts_strong_evidence_downgrade(self) -> None:
        """Verify downgrade from baseline standard to routine is accepted with strong evidence."""
        mock_score_comp = MagicMock()
        mock_score_comp.score = 0.10  # candidate routine, far from 0.5 boundary
        mock_score_comp.confidence = 0.90  # strong confidence (>=0.75 threshold)

        mock_score_reas = MagicMock()
        mock_score_reas.score = 0.2
        mock_score_reas.confidence = 0.90

        mock_resp = MagicMock()
        mock_resp.scores = {
            "task_complexity": mock_score_comp,
            "reasoning_need": mock_score_reas,
        }
        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Fix typo in README header",
            description="Fix spelling error",
            difficulty="standard",
            difficulty_source="unknown",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                # Strong evidence downgrade accepted!
                self.assertEqual(prof.recommended_tier, "routine")
                self.assertEqual(prof.complexity_level, "routine")
                self.assertFalse(prof.dimension_provenance["complexity"].fallback_used)
                self.assertEqual(prof.dimension_provenance["complexity"].source, "jev")

    def test_upgrade_policy_accepts_standard_confidence(self) -> None:
        """Verify upgrade from routine to standard is accepted with standard confidence (>=0.50)."""
        mock_score_comp = MagicMock()
        mock_score_comp.score = 1.0  # candidate standard
        mock_score_comp.confidence = 0.55  # >=0.50 upgrade threshold

        mock_score_reas = MagicMock()
        mock_score_reas.score = 1.0
        mock_score_reas.confidence = 0.90

        mock_resp = MagicMock()
        mock_resp.scores = {
            "task_complexity": mock_score_comp,
            "reasoning_need": mock_score_reas,
        }
        mock_client = MagicMock()
        mock_client.system_one.return_value = mock_resp

        task = TaskCharacteristics(
            title="Implement webhook dispatcher",
            description="Process incoming events",
            difficulty="routine",
            difficulty_source="unknown",
        )

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-key"}):
            with patch("abstract_profiler.TYPESAFE_AVAILABLE", True):
                prof, conf, fallback, reason = extract_abstract_task_profile(task, client=mock_client)

                # Upgrade accepted
                self.assertEqual(prof.recommended_tier, "standard")
                self.assertFalse(prof.dimension_provenance["complexity"].fallback_used)
                self.assertEqual(prof.dimension_provenance["complexity"].source, "jev")


if __name__ == "__main__":
    unittest.main()
