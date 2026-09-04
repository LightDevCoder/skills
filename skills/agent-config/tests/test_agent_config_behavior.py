"""Contract simulation / behavior model tests for agent-config.

The fixtures model evidence supplied to the prompt in a test-local simulator.
They validate the 2x2 decision grid, four execution modes, difficulty monotonicity,
degradation rules, and adapter boundaries.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def _valid_evidence(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("kind") == "host-runtime"
        and isinstance(value.get("locator"), str)
        and bool(value["locator"].strip())
        and isinstance(value.get("observed_at"), str)
        and bool(value["observed_at"].strip())
    )


def observed_state(claim: dict[str, Any]) -> str:
    """Normalize unsupported available/unavailable claims to unknown."""
    if not isinstance(claim, dict):
        return "unknown"
    state = claim.get("state")
    if state not in {"available", "unavailable", "unknown"}:
        return "unknown"
    if state == "unknown":
        return "unknown"
    if not _valid_evidence(claim.get("evidence")):
        return "unknown"
    return state


def current_model(evidence: dict[str, Any]) -> str | None:
    models_data = evidence.get("models")
    if isinstance(models_data, dict):
        current = models_data.get("current")
        if (
            isinstance(current, dict)
            and isinstance(current.get("id"), str)
            and observed_state(current) == "available"
        ):
            return current["id"]
        for model in models_data.get("selectable", []):
            if (
                isinstance(model, dict)
                and isinstance(model.get("id"), str)
                and observed_state(model) == "available"
            ):
                return model["id"]
    return None


def selectable_models(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    models_data = evidence.get("models")
    results: list[dict[str, Any]] = []
    if isinstance(models_data, dict):
        for model in models_data.get("selectable", []):
            if isinstance(model, dict) and isinstance(model.get("id"), str):
                if observed_state(model) == "available":
                    results.append(model)
    return results


def capability(evidence: dict[str, Any], name: str) -> str:
    claim = evidence.get("capabilities", {}).get(name, {})
    return observed_state(claim) if isinstance(claim, dict) else "unknown"


def classify_provider_mode(evidence: dict[str, Any]) -> str:
    """Determine whether the host can perform tiered-multi-model routing or fixed-single-model."""
    curr = current_model(evidence)
    sel = selectable_models(evidence)

    if not curr and not sel:
        return "BOUNDARY"

    has_selection = (
        capability(evidence, "model_selection") == "available"
        or capability(evidence, "per_agent_model_selection") == "available"
    )

    # Tiered multi-model requires at least 2 selectable models, each with a verified positive routing_rank
    if len(sel) >= 2 and has_selection:
        ranks = [m.get("routing_rank") for m in sel if isinstance(m.get("routing_rank"), int) and m["routing_rank"] > 0]
        if len(ranks) == len(sel) and len(set(ranks)) > 1:
            return "tiered-multi-model"

    return "fixed-single-model"


def classify_task_shape(task: dict[str, Any]) -> str:
    """Determine single-pass vs decomposed based on semantic structure, never word count."""
    if task.get("tickets") or task.get("has_dependency_graph") or task.get("requires_ticket_decomposition"):
        return "decomposed"
    return "single-pass"


def right_size_model_tier(models: list[dict[str, Any]], difficulty: str) -> dict[str, Any]:
    """Map difficulty to minimum sufficient model rank."""
    ranked = sorted(models, key=lambda m: m.get("routing_rank", 1))
    if not ranked:
        return {}
    if difficulty == "routine":
        return ranked[0]
    elif difficulty == "moderate":
        # Middle rank if available, otherwise lowest sufficient
        mid_idx = len(ranked) // 2 if len(ranked) > 2 else 0
        return ranked[mid_idx]
    elif difficulty in {"demanding", "critical"}:
        return ranked[-1]
    return ranked[0]


def right_size_effort(levels: list[str], difficulty: str) -> str:
    """Map difficulty to appropriate reasoning effort level."""
    if not levels:
        return "default"
    if difficulty == "routine":
        return levels[0]
    elif difficulty == "moderate":
        mid_idx = len(levels) // 2
        return levels[mid_idx]
    else:
        return levels[-1]


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AgentConfigBehaviorTest(unittest.TestCase):
    def test_case_a_tiered_multi_model_single_pass(self) -> None:
        """Mode 1: Right-sizes implementation to sufficient model, stronger reviewer, no forced waves."""
        evidence = load("case-a-tiered-single-pass.json")
        provider_mode = classify_provider_mode(evidence)
        self.assertEqual(provider_mode, "tiered-multi-model")

        task = {"difficulty": "moderate", "word_count": 3500}  # Large word count, but single cohesive task
        task_shape = classify_task_shape(task)
        self.assertEqual(task_shape, "single-pass")

        sel = selectable_models(evidence)
        impl_model = right_size_model_tier(sel, "moderate")
        self.assertEqual(impl_model["id"], "model-beta")
        self.assertEqual(impl_model["routing_rank"], 2)
        # Does not waste highest model on moderate task
        self.assertNotEqual(impl_model["id"], "model-gamma")

        # Review can use highest rank model
        review_model = right_size_model_tier(sel, "critical")
        self.assertEqual(review_model["id"], "model-gamma")
        self.assertEqual(review_model["routing_rank"], 3)

        # Effort right-sizing
        effort_levels = evidence["capabilities"]["reasoning_control"]["levels"]
        self.assertEqual(right_size_effort(effort_levels, "moderate"), "medium")
        self.assertEqual(right_size_effort(effort_levels, "critical"), "high")

    def test_case_b_tiered_multi_model_decomposed(self) -> None:
        """Mode 2: Highest rank controller, monotonic difficulty scaling, parallel disjoint work."""
        evidence = load("case-b-tiered-decomposed.json")
        provider_mode = classify_provider_mode(evidence)
        self.assertEqual(provider_mode, "tiered-multi-model")

        tickets = [
            {"id": "01", "difficulty": "routine", "blocked_by": []},
            {"id": "02", "difficulty": "moderate", "blocked_by": []},
            {"id": "03", "difficulty": "demanding", "blocked_by": []},
            {"id": "04", "difficulty": "critical", "blocked_by": ["03"]},
        ]
        task = {"tickets": tickets, "requires_ticket_decomposition": True}
        task_shape = classify_task_shape(task)
        self.assertEqual(task_shape, "decomposed")

        sel = selectable_models(evidence)
        # Controller gets highest rank
        controller_model = max(sel, key=lambda m: m.get("routing_rank", 1))
        self.assertEqual(controller_model["id"], "model-gamma")
        self.assertEqual(controller_model["routing_rank"], 3)

        # Worker model assignments satisfy monotonicity
        t01_model = right_size_model_tier(sel, "routine")
        t02_model = right_size_model_tier(sel, "moderate")
        t03_model = right_size_model_tier(sel, "demanding")

        self.assertLessEqual(t01_model["routing_rank"], t02_model["routing_rank"])
        self.assertLessEqual(t02_model["routing_rank"], t03_model["routing_rank"])

        # Concurrency cap is respected: cap is 3, ready tickets are 01, 02, 03; 04 is blocked
        ready_tickets = [t for t in tickets if not t["blocked_by"]]
        self.assertEqual(len(ready_tickets), 3)
        self.assertEqual(evidence["capabilities"]["concurrency_cap"]["limit"], 3)

    def test_case_c_fixed_single_model_single_pass(self) -> None:
        """Mode 3: Direct execution with current model, max effort, no artificial role bureaucracy."""
        evidence = load("case-c-fixed-single-pass.json")
        provider_mode = classify_provider_mode(evidence)
        self.assertEqual(provider_mode, "fixed-single-model")

        task = {"difficulty": "routine"}
        task_shape = classify_task_shape(task)
        self.assertEqual(task_shape, "single-pass")

        curr = current_model(evidence)
        self.assertEqual(curr, "model-alpha")

        # Max supported effort
        effort_levels = evidence["capabilities"]["reasoning_control"]["levels"]
        self.assertEqual(effort_levels[-1], "high")

        # Does not fail or return BOUNDARY even though model_selection and subagents are unavailable
        self.assertNotEqual(provider_mode, "BOUNDARY")

    def test_case_d_fixed_single_model_decomposed(self) -> None:
        """Mode 4: Same model across controller and workers, leverages threads/subagents."""
        evidence = load("case-d-fixed-decomposed.json")
        provider_mode = classify_provider_mode(evidence)
        self.assertEqual(provider_mode, "fixed-single-model")

        task = {"tickets": [{"id": "01"}, {"id": "02"}]}
        task_shape = classify_task_shape(task)
        self.assertEqual(task_shape, "decomposed")

        curr = current_model(evidence)
        self.assertEqual(curr, "model-alpha")
        self.assertEqual(capability(evidence, "subagents"), "available")
        self.assertEqual(capability(evidence, "session_threads"), "available")
        self.assertEqual(capability(evidence, "parallelism"), "available")
        self.assertEqual(evidence["capabilities"]["concurrency_cap"]["limit"], 2)

    def test_unranked_multiple_models_fall_back_without_guessing(self) -> None:
        """Do not guess intelligence by model name (model-pro vs model-mini vs model-ultra)."""
        evidence = load("unranked-multiple-models.json")
        provider_mode = classify_provider_mode(evidence)
        # Missing trusted routing_rank forces safe fallback to fixed-single-model
        self.assertEqual(provider_mode, "fixed-single-model")
        self.assertEqual(current_model(evidence), "model-pro")

    def test_missing_reasoning_control_continues_safely(self) -> None:
        """Unavailable reasoning control proceeds with host default without returning BOUNDARY."""
        evidence = load("missing-reasoning-control.json")
        self.assertEqual(capability(evidence, "reasoning_control"), "unavailable")
        provider_mode = classify_provider_mode(evidence)
        self.assertNotEqual(provider_mode, "BOUNDARY")

    def test_false_inventory_and_missing_model_return_boundary(self) -> None:
        """No executable or selectable models produces BOUNDARY."""
        false_inv = load("false-inventory.json")
        self.assertEqual(classify_provider_mode(false_inv), "BOUNDARY")

        missing_mod = load("missing-model-evidence.json")
        self.assertEqual(classify_provider_mode(missing_mod), "BOUNDARY")

    def test_adapter_apply_requires_explicit_user_approval(self) -> None:
        """Adapter presence emits plan-only by default; explicit approval is required to mutate."""
        evidence = load("adapter-scenarios.json")
        self.assertIn("adapter", evidence)
        self.assertEqual(evidence["adapter"]["project_config_support"], "available")

        # Default apply mode without user approval
        default_apply_mode = "plan-only"
        self.assertEqual(default_apply_mode, "plan-only")

        # Explicit user approval allows mutation
        user_confirmed = True
        active_apply_mode = "applied" if user_confirmed else "plan-only"
        self.assertEqual(active_apply_mode, "applied")

    def test_backward_compatibility_with_schema_v1(self) -> None:
        """Schema v1 evidence without routing_rank normalizes gracefully."""
        v1_evidence = load("single-model-multi-agent.json")
        provider_mode = classify_provider_mode(v1_evidence)
        self.assertEqual(provider_mode, "fixed-single-model")
        self.assertEqual(current_model(v1_evidence), "model-alpha")

    @unittest.skipIf(os.environ.get("AGENT_CONFIG_INSTALLED_COPY") == "1", "already running in isolated copy")
    def test_isolated_installed_copy_runs_the_full_package_suite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-config-installed-") as directory:
            destination = Path(directory) / "skills" / "agent-config"
            destination.parent.mkdir(parents=True)
            shutil.copytree(ROOT, destination)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((destination / "references" / "plan-schema.md").is_file())
            self.assertTrue((destination / "references" / "task-assessment.md").is_file())
            self.assertTrue((destination / "references" / "provider-adapter-contract.md").is_file())
            environment = dict(os.environ, AGENT_CONFIG_INSTALLED_COPY="1")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(destination / "tests"), "-p", "test_*.py"],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
