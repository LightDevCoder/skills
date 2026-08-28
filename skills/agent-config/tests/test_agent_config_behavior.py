"""Contract simulation / behavior model tests for agent-config.

The fixtures model evidence supplied to the prompt in a test-local simulator.
They validate the declared decision table and contract rules, not a live host
query or live multi-agent execution.
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
    elif isinstance(models_data, list):
        for model in models_data:
            if isinstance(model, dict) and isinstance(model.get("id"), str):
                sel = model.get("selectable", {})
                if observed_state(sel) == "available":
                    return model["id"]
    return None


def selectable_models(evidence: dict[str, Any]) -> list[str]:
    models_data = evidence.get("models")
    results: list[str] = []
    if isinstance(models_data, dict):
        for model in models_data.get("selectable", []):
            if isinstance(model, dict) and isinstance(model.get("id"), str):
                if observed_state(model) == "available":
                    results.append(model["id"])
    elif isinstance(models_data, list):
        for model in models_data:
            if isinstance(model, dict) and isinstance(model.get("id"), str):
                sel = model.get("selectable", {})
                if observed_state(sel) == "available":
                    results.append(model["id"])
    return results


def executable_models(evidence: dict[str, Any]) -> list[str]:
    curr = current_model(evidence)
    sel = selectable_models(evidence)
    combined: list[str] = []
    if curr and curr not in combined:
        combined.append(curr)
    for m in sel:
        if m not in combined:
            combined.append(m)
    return combined


def capability(evidence: dict[str, Any], name: str) -> str:
    claim = evidence.get("capabilities", {}).get(name, {})
    return observed_state(claim) if isinstance(claim, dict) else "unknown"


def select_route(evidence: dict[str, Any]) -> str:
    """The finite route table the Skill requires a plan to follow."""
    selectable = selectable_models(evidence)
    executable = executable_models(evidence)
    subagents = capability(evidence, "subagents") == "available"
    sessions = capability(evidence, "session_threads") == "available"
    parallel = capability(evidence, "parallelism") == "available"
    per_agent_model = capability(evidence, "per_agent_model_selection") == "available"

    # Route A: Multi-model, multi-agent
    if len(selectable) >= 2 and subagents and sessions and parallel and per_agent_model:
        return "multi-model-multi-agent"

    # Route B: Fixed-model / single-model, multi-agent
    if len(executable) >= 1 and subagents and sessions:
        return "single-model-multi-agent"

    # Route C: Fixed-model / single-model, single-agent
    if len(executable) >= 1:
        return "single-model-single-agent"

    # Route D: Boundary
    return "BOUNDARY"


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AgentConfigBehaviorTest(unittest.TestCase):
    def test_verified_multi_model_capabilities_select_role_clear_parallel_route(self) -> None:
        evidence = load("multi-model.json")
        self.assertEqual(select_route(evidence), "multi-model-multi-agent")
        self.assertEqual(selectable_models(evidence), ["model-alpha", "model-beta"])
        self.assertEqual(capability(evidence, "worktrees"), "available")
        cap = evidence["capabilities"]["concurrency_cap"]
        self.assertEqual(observed_state(cap), "available")
        self.assertEqual(cap["limit"], 3)

    def test_single_model_multi_agent_route_keeps_reviewer_separate_without_worktrees(self) -> None:
        evidence = load("single-model-multi-agent.json")
        self.assertEqual(select_route(evidence), "single-model-multi-agent")
        self.assertEqual(current_model(evidence), "model-alpha")
        self.assertEqual(capability(evidence, "model_selection"), "unavailable")
        self.assertEqual(capability(evidence, "per_agent_model_selection"), "unavailable")
        self.assertEqual(capability(evidence, "worktrees"), "unavailable")
        self.assertEqual(evidence["capabilities"]["concurrency_cap"]["limit"], 2)
        self.assertEqual(capability(evidence, "session_threads"), "available")
        self.assertNotEqual(select_route(evidence), "BOUNDARY")

    def test_single_agent_fallback_keeps_independent_review_gate_blocked(self) -> None:
        evidence = load("single-agent.json")
        self.assertEqual(select_route(evidence), "single-model-single-agent")
        self.assertEqual(current_model(evidence), "model-alpha")
        self.assertEqual(capability(evidence, "subagents"), "unavailable")
        self.assertEqual(capability(evidence, "session_threads"), "unavailable")
        self.assertEqual(capability(evidence, "parallelism"), "unavailable")
        self.assertEqual(capability(evidence, "model_selection"), "unavailable")
        self.assertEqual(evidence["capabilities"]["concurrency_cap"]["limit"], None)
        self.assertNotEqual(select_route(evidence), "BOUNDARY")

    def test_false_inventory_is_normalized_and_cannot_create_a_lane(self) -> None:
        evidence = load("false-inventory.json")
        self.assertIsNone(current_model(evidence))
        self.assertEqual(selectable_models(evidence), [])
        self.assertEqual(executable_models(evidence), [])
        self.assertEqual(capability(evidence, "subagents"), "unknown")
        self.assertEqual(capability(evidence, "parallelism"), "unknown")
        self.assertEqual(select_route(evidence), "BOUNDARY")

    def test_missing_model_evidence_returns_boundary(self) -> None:
        evidence = load("missing-model-evidence.json")
        self.assertIsNone(current_model(evidence))
        self.assertEqual(selectable_models(evidence), [])
        self.assertEqual(executable_models(evidence), [])
        self.assertEqual(select_route(evidence), "BOUNDARY")

    @unittest.skipIf(os.environ.get("AGENT_CONFIG_INSTALLED_COPY") == "1", "already running in isolated copy")
    def test_isolated_installed_copy_runs_the_full_package_suite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-config-installed-") as directory:
            destination = Path(directory) / "skills" / "agent-config"
            destination.parent.mkdir(parents=True)
            shutil.copytree(ROOT, destination)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((destination / "references" / "plan-schema.md").is_file())
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
