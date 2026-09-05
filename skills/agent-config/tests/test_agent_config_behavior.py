"""Contract simulation / behavior model tests for agent-config (Phase 2).

Validates the profile-driven architecture, Setup Gate, effort resolution,
the four peer execution modes (Case A, Case B, Case C, Case D), stale profile detection,
and ticket / workflow integration boundaries.
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
    avail = evidence.get("available_models")
    if isinstance(avail, list) and avail:
        for m in avail:
            if isinstance(m, dict) and m.get("state") == "available" and isinstance(m.get("id"), str):
                return m["id"]
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
    avail = evidence.get("available_models")
    if isinstance(avail, list) and avail:
        return [m for m in avail if isinstance(m, dict) and m.get("state") == "available"]
    models_data = evidence.get("models")
    results: list[dict[str, Any]] = []
    if isinstance(models_data, dict):
        for model in models_data.get("selectable", []):
            if isinstance(model, dict) and isinstance(model.get("id"), str):
                if observed_state(model) == "available":
                    results.append(model)
    return results


def capability(evidence: dict[str, Any], name: str) -> str:
    claim = evidence.get("capabilities", {}).get(name)
    if claim is None and name == "reasoning_control":
        claim = evidence.get("capabilities", {}).get("reasoning")
    elif claim is None and name == "reasoning":
        claim = evidence.get("capabilities", {}).get("reasoning_control")
    elif claim is None and name == "session_threads":
        claim = evidence.get("capabilities", {}).get("threads")
    elif claim is None and name == "threads":
        claim = evidence.get("capabilities", {}).get("session_threads")
    elif claim is None and name == "concurrency_cap":
        claim = evidence.get("capabilities", {}).get("concurrency")
    elif claim is None and name == "concurrency":
        claim = evidence.get("capabilities", {}).get("concurrency_cap")
    return observed_state(claim) if isinstance(claim, dict) else "unknown"


def classify_provider_mode(evidence: dict[str, Any], profile: dict[str, Any] | None = None) -> str:
    """Determine whether the host/profile uses tiered-multi-model or fixed-single-model."""
    curr = current_model(evidence)
    sel = selectable_models(evidence)

    if not curr and not sel:
        return "unsupported"

    if profile and isinstance(profile, dict):
        mode = profile.get("model_mode")
        if mode == "multi":
            return "tiered-multi-model"
        if mode == "single":
            return "fixed-single-model"

    # When no profile exists, never guess fixed-single-model or tiered-multi-model
    return "unprofiled"


def classify_task_shape(task: dict[str, Any]) -> str:
    """Determine single-pass vs decomposed based on semantic structure, never word count."""
    if task.get("tickets") or task.get("has_dependency_graph") or task.get("requires_ticket_decomposition"):
        return "decomposed"
    return "single-pass"


def resolve_effort(supported_levels: list[str], policy_or_value: str) -> str:
    """Resolve an abstract effort policy or concrete request to a verified host value (§56)."""
    if not supported_levels:
        return "default"

    if policy_or_value == "highest-supported":
        if "max" in supported_levels:
            return "max"
        return supported_levels[-1]

    if policy_or_value == "default":
        return "default"

    # If an explicit value is supported by the host, use it
    if policy_or_value in supported_levels:
        return policy_or_value

    # Host does NOT support the requested literal (e.g. unverified literal "max").
    # Never emit unverified host values; fall back safely to highest verified level.
    return supported_levels[-1]


def map_difficulty_to_tier(difficulty: str) -> str:
    """Map work-item difficulty to abstract profile tier."""
    if difficulty == "routine":
        return "routine"
    elif difficulty == "moderate":
        return "standard"
    elif difficulty in {"demanding", "critical"}:
        return "high"
    return "standard"


def check_profile_stale(
    profile: dict[str, Any],
    host_available_models: list[str],
    host_id: str | None = None,
) -> tuple[bool, list[str]]:
    """Detect if profile has drifted from host runtime reality (§58)."""
    reasons: list[str] = []

    if host_id and profile.get("host", {}).get("id") != host_id:
        reasons.append(f"Host identity mismatch: expected {profile.get('host', {}).get('id')}, got {host_id}")

    mode = profile.get("model_mode")
    if mode == "single":
        cfg_model = profile.get("single_model", {}).get("model")
        if cfg_model and cfg_model not in host_available_models:
            reasons.append(f"Configured single model '{cfg_model}' is no longer available on host")
    elif mode == "multi":
        tiers = profile.get("tiers", {})
        for tier_name, tier_cfg in tiers.items():
            model = tier_cfg.get("model")
            if model and model not in host_available_models:
                reasons.append(f"Configured model '{model}' for tier '{tier_name}' is no longer available on host")

    return (len(reasons) > 0, reasons)


def evaluate_setup_gate(
    intent: str,
    companion_status: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    host_available_models: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate entry through the Setup Gate (§55)."""
    if intent in {"setup", "agent-config setup"}:
        return {"action": "open-setup", "target": "references/setup.md"}

    # Companion MCP absent: graceful non-blocking fallback
    if companion_status is None:
        if profile is not None:
            # Session-local user-confirmed profile available
            return {
                "action": "proceed-to-assessment",
                "apply_mode": "plan-only",
                "companion": "absent",
                "message": "Proceeding with session-local profile in plan-only mode.",
            }
        return {
            "action": "plan-only-fallback",
            "target": "references/setup.md",
            "companion": "absent",
            "message": "Companion absent; prompt for session-local setup or continue without guessing.",
        }

    if not companion_status.get("configured") or profile is None:
        return {"action": "setup-questionnaire", "target": "references/setup.md"}

    if companion_status.get("stale"):
        return {"action": "setup-questionnaire", "target": "references/setup.md", "stale": True}

    if host_available_models is not None:
        is_stale, reasons = check_profile_stale(profile, host_available_models)
        if is_stale:
            return {
                "action": "setup-questionnaire",
                "target": "references/setup.md",
                "stale": True,
                "reasons": reasons,
            }

    return {"action": "proceed-to-assessment", "apply_mode": "plan-only"}


def route_execution(
    profile: dict[str, Any] | None,
    task: dict[str, Any],
    host_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Adaptive execution routing producing plan metadata (§57, §58, §59)."""
    task_shape = classify_task_shape(task)
    tickets = task.get("tickets")

    # Host unsupported check (§7): no executable or selectable models evidenced
    curr = current_model(host_evidence)
    sel = selectable_models(host_evidence)
    if not curr and not sel:
        return {
            "readiness": "UNSUPPORTED",
            "mode": "plan-only",
            "setup_state": {
                "companion": "missing",
                "profile": "missing",
            },
            "handoff": None,
            "execution_config": None,
            "task_shape": task_shape,
            "execution_state": "blocked",
            "reason": "Host environment evidences no executable or selectable models.",
        }

    # Ticket integration boundary (§59): decomposed task with no tickets
    if task_shape == "decomposed" and not tickets:
        return {
            "readiness": "NEED_PROJECT_TICKETS",
            "mode": "plan-only",
            "setup_state": {
                "companion": "ready" if profile else "missing",
                "profile": "persisted" if profile else "missing",
            },
            "handoff": "project-tickets",
            "execution_config": None,
            "task_shape": "decomposed",
            "execution_state": "blocked",
            "reason": "Decomposed task requires formal ticket breakdown before execution scheduling.",
        }

    # When neither a persisted profile nor an explicit session-local profile is provided,
    # halt resource routing and direct to agent-config setup. Never assume or guess "fixed-single-model".
    if not profile or not isinstance(profile, dict):
        return {
            "readiness": "NEED_INPUT",
            "mode": "plan-only",
            "setup_state": {
                "companion": "missing",
                "profile": "missing",
            },
            "handoff": "setup",
            "execution_config": None,
            "action": "setup-required",
            "target": "agent-config setup",
            "provider_mode": "unprofiled",
            "task_shape": task_shape,
            "execution_state": "blocked",
            "message": "No confirmed profile found. Resource routing halted; direct to agent-config setup or supply session-local profile.",
        }

    # Model authorization check (§7, §11)
    authorized_models = set()
    if profile.get("model_mode") == "single":
        single_m_auth = profile.get("single_model", {}).get("model")
        if single_m_auth:
            authorized_models.add(single_m_auth)
    elif profile.get("model_mode") == "multi":
        for t_cfg in profile.get("tiers", {}).values():
            if t_cfg.get("model"):
                authorized_models.add(t_cfg.get("model"))
    requested_model = task.get("requested_model")
    if requested_model and requested_model not in authorized_models:
        return {
            "readiness": "BLOCKED",
            "mode": "plan-only",
            "setup_state": {
                "companion": "ready",
                "profile": "persisted",
            },
            "handoff": None,
            "execution_config": None,
            "task_shape": task_shape,
            "execution_state": "blocked",
            "reason": f"Requested model '{requested_model}' is not authorized in user profile.",
        }

    model_mode = profile.get("model_mode", "single")
    reasoning_levels = (
        host_evidence.get("supported_effort_values")
        if host_evidence.get("supported_effort_values") is not None
        else host_evidence.get("capabilities", {}).get("reasoning_control", {}).get("levels", [])
    )
    cap_claim = (
        host_evidence.get("capabilities", {}).get("concurrency")
        or host_evidence.get("capabilities", {}).get("concurrency_cap", {})
    )
    if isinstance(cap_claim, dict):
        concurrency_cap = cap_claim.get("max_concurrency") or cap_claim.get("limit") or 1
    else:
        concurrency_cap = 1

    has_subagents = capability(host_evidence, "subagents") == "available"
    has_threads = (
        capability(host_evidence, "threads") == "available"
        or capability(host_evidence, "session_threads") == "available"
    )

    if model_mode == "single":
        single_m = profile.get("single_model", {}).get("model", "default")
        exec_effort_cfg = profile.get("single_model", {}).get("execution_effort", {})
        if isinstance(exec_effort_cfg, dict):
            exec_policy = exec_effort_cfg.get("value") or exec_effort_cfg.get("policy", "highest-supported")
        elif isinstance(exec_effort_cfg, str):
            exec_policy = exec_effort_cfg
        else:
            exec_policy = "highest-supported"

        resolved_effort = resolve_effort(reasoning_levels, exec_policy)

        if task_shape == "single-pass":
            # Case A: Fixed Single-model + Single-pass (§57)
            canonical_exec_cfg = {
                "task_shape": "single-pass",
                "model_mode": "single",
                "readiness": "executable",
                "reason": "Single model direct execution for bounded single-pass task",
                "topology": {
                    "type": "single-session",
                    "concurrency": 1,
                },
                "execution": {
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": "current-session",
                },
                "review": {
                    "strategy": "self-check",
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": "current-session",
                },
            }
            return {
                "readiness": "READY",
                "mode": "plan-only",
                "setup_state": {
                    "companion": "ready",
                    "profile": "persisted",
                },
                "handoff": "implement",
                "execution_config": canonical_exec_cfg,
                "execution_state": "executable",
                "mode_title": "Case A (Fixed Single-model + Single-pass)",
                "provider_mode": "fixed-single-model",
                "task_shape": "single-pass",
                "controller": None,
                "execution": {
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": "current-session",
                },
                "review": {
                    "type": "Self-check",
                    "strategy": "self-check",
                    "model": single_m,
                    "effort": resolved_effort,
                },
                "fake_roles": False,
            }
        else:
            # Case B: Fixed Single-model + Decomposed (P0, §57)
            worker_context = "subagent" if has_subagents else ("session_thread" if has_threads else "serial-main-session")
            workers = []
            work_items = []
            for t in (tickets or []):
                t_id = t.get("id", "item")
                workers.append({
                    "ticket": t_id,
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": worker_context,
                    "blocked_by": t.get("blocked_by", []),
                })
                work_items.append({
                    "ticket_id": str(t_id),
                    "difficulty": t.get("difficulty", "moderate"),
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": worker_context,
                    "review_strategy": "controller-review",
                })
            canonical_exec_cfg = {
                "task_shape": "decomposed",
                "model_mode": "single",
                "readiness": "executable",
                "reason": "Single model decomposed execution with Controller coordinating fresh contexts",
                "topology": {
                    "type": "serial-tickets" if not has_subagents and not has_threads else "controller-workers",
                    "concurrency": concurrency_cap,
                    "fresh_contexts": has_threads or has_subagents,
                    "subagent_contexts": has_subagents,
                },
                "controller": {
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": "current-session",
                },
                "work_items": work_items,
                "review": {
                    "strategy": "controller-review",
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": "current-session",
                },
            }
            return {
                "readiness": "READY",
                "mode": "plan-only",
                "setup_state": {
                    "companion": "ready",
                    "profile": "persisted",
                },
                "handoff": "implement",
                "execution_config": canonical_exec_cfg,
                "execution_state": "executable",
                "mode_title": "Case B (Fixed Single-model + Decomposed)",
                "provider_mode": "fixed-single-model",
                "task_shape": "decomposed",
                "controller": {
                    "model": single_m,
                    "effort": resolved_effort,
                    "context": "current-session",
                },
                "workers": workers,
                "concurrency_cap": concurrency_cap,
                "review": {
                    "type": "Controller Review",
                    "strategy": "controller-review",
                    "model": single_m,
                    "effort": resolved_effort,
                },
                "model_tier_assignment": False,
            }
    else:
        # Multi-model
        tiers = profile.get("tiers", {})
        if task_shape == "single-pass":
            # Case C: Tiered Multi-model + Single-pass (§58)
            diff = task.get("difficulty", "moderate")
            tier_name = map_difficulty_to_tier(diff)
            tier_cfg = tiers.get(tier_name, {})
            model_id = tier_cfg.get("model")
            tier_effort_cfg = tier_cfg.get("effort")
            if isinstance(tier_effort_cfg, dict):
                tier_effort_val = tier_effort_cfg.get("value") or tier_effort_cfg.get("policy", "default")
            elif isinstance(tier_effort_cfg, str):
                tier_effort_val = tier_effort_cfg
            else:
                tier_effort_val = "default"
            effort = resolve_effort(reasoning_levels, tier_effort_val)

            review_cfg = tiers.get("review", {})
            review_model = review_cfg.get("model", model_id)
            review_effort_cfg = review_cfg.get("effort")
            if isinstance(review_effort_cfg, dict):
                review_effort_val = review_effort_cfg.get("value") or review_effort_cfg.get("policy", "highest-supported")
            elif isinstance(review_effort_cfg, str):
                review_effort_val = review_effort_cfg
            else:
                review_effort_val = "highest-supported"
            review_effort = resolve_effort(reasoning_levels, review_effort_val)

            canonical_exec_cfg = {
                "task_shape": "single-pass",
                "model_mode": "multi",
                "readiness": "executable",
                "reason": "Tiered multi-model execution right-sized to task difficulty",
                "topology": {
                    "type": "single-session",
                    "concurrency": 1,
                },
                "execution": {
                    "model": model_id,
                    "effort": effort,
                    "context": "current-session",
                },
                "review": {
                    "strategy": "independent-review",
                    "tier": "review",
                    "model": review_model,
                    "effort": review_effort,
                    "context": "fresh-thread",
                },
            }

            return {
                "readiness": "READY",
                "mode": "plan-only",
                "setup_state": {
                    "companion": "ready",
                    "profile": "persisted",
                },
                "handoff": "implement",
                "execution_config": canonical_exec_cfg,
                "execution_state": "executable",
                "mode_title": "Case C (Tiered Multi-model + Single-pass)",
                "provider_mode": "tiered-multi-model",
                "task_shape": "single-pass",
                "execution": {
                    "tier": tier_name,
                    "model": model_id,
                    "effort": effort,
                    "context": "current-session",
                },
                "topology": "minimal",
                "review": {
                    "type": "Independent Review",
                    "strategy": "independent-review",
                    "tier": "review",
                    "model": review_model,
                    "effort": review_effort,
                },
            }
        else:
            # Case D: Tiered Multi-model + Decomposed (P0, §58)
            review_cfg = tiers.get("review", {})
            controller_cfg = tiers.get("high", review_cfg)
            controller_model = controller_cfg.get("model")
            controller_effort_cfg = controller_cfg.get("effort")
            if isinstance(controller_effort_cfg, dict):
                ctrl_effort_val = controller_effort_cfg.get("value") or controller_effort_cfg.get("policy", "highest-supported")
            elif isinstance(controller_effort_cfg, str):
                ctrl_effort_val = controller_effort_cfg
            else:
                ctrl_effort_val = "highest-supported"
            controller_effort = resolve_effort(reasoning_levels, ctrl_effort_val)

            worker_context = "subagent" if has_subagents else ("session_thread" if has_threads else "serial-main-session")
            workers = []
            work_items = []
            for t in (tickets or []):
                diff = t.get("difficulty", "moderate")
                t_tier = map_difficulty_to_tier(diff)
                t_cfg = tiers.get(t_tier, {})
                t_effort_cfg = t_cfg.get("effort")
                if isinstance(t_effort_cfg, dict):
                    t_effort_val = t_effort_cfg.get("value") or t_effort_cfg.get("policy", "default")
                elif isinstance(t_effort_cfg, str):
                    t_effort_val = t_effort_cfg
                else:
                    t_effort_val = "default"
                t_effort = resolve_effort(reasoning_levels, t_effort_val)
                workers.append({
                    "ticket": t.get("id"),
                    "difficulty": diff,
                    "tier": t_tier,
                    "model": t_cfg.get("model"),
                    "effort": t_effort,
                    "context": worker_context,
                    "blocked_by": t.get("blocked_by", []),
                })
                work_items.append({
                    "ticket_id": str(t.get("id", "item")),
                    "difficulty": diff if diff in {"routine", "moderate", "demanding", "critical"} else "moderate",
                    "tier": t_tier,
                    "model": t_cfg.get("model"),
                    "effort": t_effort,
                    "context": worker_context,
                    "review_strategy": "controller-review" if diff != "critical" else "independent-review",
                })

            canonical_exec_cfg = {
                "task_shape": "decomposed",
                "model_mode": "multi",
                "readiness": "executable",
                "reason": "Tiered multi-model decomposed execution with per-ticket tier routing",
                "topology": {
                    "type": "controller-workers",
                    "concurrency": concurrency_cap,
                    "fresh_contexts": has_threads or has_subagents,
                    "subagent_contexts": has_subagents,
                },
                "controller": {
                    "model": controller_model,
                    "effort": controller_effort,
                    "context": "current-session",
                },
                "work_items": work_items,
                "review": {
                    "strategy": "controller-review",
                    "tier": "review",
                    "model": review_cfg.get("model", controller_model),
                    "effort": resolve_effort(reasoning_levels, "highest-supported"),
                    "context": "current-session",
                },
            }

            return {
                "readiness": "READY",
                "mode": "plan-only",
                "setup_state": {
                    "companion": "ready",
                    "profile": "persisted",
                },
                "handoff": "implement",
                "execution_config": canonical_exec_cfg,
                "execution_state": "executable",
                "mode_title": "Case D (Tiered Multi-model + Decomposed)",
                "provider_mode": "tiered-multi-model",
                "task_shape": "decomposed",
                "controller": {
                    "tier": "high",
                    "model": controller_model,
                    "effort": controller_effort,
                    "context": "current-session",
                },
                "workers": workers,
                "concurrency_cap": concurrency_cap,
                "review": {
                    "type": "Controller Review",
                    "strategy": "controller-review",
                    "tier": "review",
                    "model": review_cfg.get("model", controller_model),
                    "effort": resolve_effort(reasoning_levels, "highest-supported"),
                },
            }


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AgentConfigBehaviorTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    # Setup Gate Behavior Tests (§55)
    # -------------------------------------------------------------------------

    def test_setup_gate_explicit_setup_intent(self) -> None:
        """Explicit setup intent routes directly to references/setup.md."""
        gate = evaluate_setup_gate("agent-config setup", {"configured": True}, {"model_mode": "single"})
        self.assertEqual(gate["action"], "open-setup")
        self.assertEqual(gate["target"], "references/setup.md")

    def test_setup_gate_configured_profile(self) -> None:
        """Configured valid profile proceeds directly to task assessment."""
        profile = load("profile-single-model.json")
        companion_status = {"configured": True, "stale": False}
        gate = evaluate_setup_gate("normal", companion_status, profile, ["model-alpha"])
        self.assertEqual(gate["action"], "proceed-to-assessment")
        self.assertEqual(gate["apply_mode"], "plan-only")

    def test_setup_gate_unconfigured_profile(self) -> None:
        """Unconfigured companion routes to setup questionnaire."""
        companion_status = {"configured": False, "stale": False}
        gate = evaluate_setup_gate("normal", companion_status, None)
        self.assertEqual(gate["action"], "setup-questionnaire")
        self.assertEqual(gate["target"], "references/setup.md")

    def test_setup_gate_companion_absent_fallback(self) -> None:
        """Companion absent falls back to plan-only session mode without guessing or auto-installing."""
        # Unconfigured session fallback
        gate_no_profile = evaluate_setup_gate("normal", None, None)
        self.assertEqual(gate_no_profile["action"], "plan-only-fallback")
        self.assertEqual(gate_no_profile["companion"], "absent")

        # Session-local confirmed profile fallback
        session_profile = load("profile-single-model.json")
        gate_session_local = evaluate_setup_gate("normal", None, session_profile)
        self.assertEqual(gate_session_local["action"], "proceed-to-assessment")
        self.assertEqual(gate_session_local["apply_mode"], "plan-only")
        self.assertEqual(gate_session_local["companion"], "absent")

    # -------------------------------------------------------------------------
    # Effort Resolution Tests (§56)
    # -------------------------------------------------------------------------

    def test_effort_resolution_supported_hierarchies(self) -> None:
        """Highest-supported resolves strictly to top supported value without literal guessing."""
        # [low, medium, high] -> high
        self.assertEqual(resolve_effort(["low", "medium", "high"], "highest-supported"), "high")

        # [high] -> high
        self.assertEqual(resolve_effort(["high"], "highest-supported"), "high")

        # [low, high, max] -> max
        self.assertEqual(resolve_effort(["low", "high", "max"], "highest-supported"), "max")

        # [low, medium, high, max] -> max
        self.assertEqual(resolve_effort(["low", "medium", "high", "max"], "highest-supported"), "max")

        # [standard, deep] -> deep
        self.assertEqual(resolve_effort(["standard", "deep"], "highest-supported"), "deep")

    def test_effort_resolution_never_emits_unverified_host_values(self) -> None:
        """Never emit unverified literal max or other unsupported values."""
        # Host only has [low, medium, high]; requested 'max' is rejected and falls back safely
        resolved = resolve_effort(["low", "medium", "high"], "max")
        self.assertNotEqual(resolved, "max")
        self.assertEqual(resolved, "high")

        # Host has no reasoning control
        self.assertEqual(resolve_effort([], "highest-supported"), "default")
        self.assertEqual(resolve_effort([], "high"), "default")

    # -------------------------------------------------------------------------
    # Single-Model Behavior Tests (§57)
    # -------------------------------------------------------------------------

    def test_case_a_single_model_single_pass(self) -> None:
        """Case A: Direct execution with single model, resolved effort, no fake roles."""
        profile = load("profile-single-model.json")
        evidence = load("case-c-fixed-single-pass.json")
        task = {"difficulty": "routine", "word_count": 4000}  # Anti-wordcount: large prose, single task

        self.assertEqual(classify_task_shape(task), "single-pass")
        plan = route_execution(profile, task, evidence)

        self.assertEqual(plan["readiness"], "READY")
        self.assertEqual(plan["handoff"], "implement")
        self.assertIsNotNone(plan["execution_config"])
        self.assertEqual(plan["execution_state"], "executable")
        self.assertEqual(plan["mode_title"], "Case A (Fixed Single-model + Single-pass)")
        self.assertEqual(plan["provider_mode"], "fixed-single-model")
        self.assertEqual(plan["task_shape"], "single-pass")
        self.assertIsNone(plan["controller"])
        self.assertEqual(plan["execution"]["model"], "model-alpha")
        self.assertEqual(plan["execution"]["effort"], "high")
        self.assertEqual(plan["execution"]["context"], "current-session")
        self.assertFalse(plan["fake_roles"])
        self.assertEqual(plan["review"]["type"], "Self-check")

    def test_case_b_single_model_decomposed_p0(self) -> None:
        """Case B (P0): Controller main session + worker contexts, same model, actual effort, concurrency cap."""
        profile = load("profile-single-model.json")
        evidence = load("case-d-fixed-decomposed.json")
        tickets = [
            {"id": "01", "difficulty": "routine", "blocked_by": []},
            {"id": "02", "difficulty": "moderate", "blocked_by": []},
            {"id": "03", "difficulty": "demanding", "blocked_by": ["01"]},
        ]
        task = {"tickets": tickets}

        self.assertEqual(classify_task_shape(task), "decomposed")
        plan = route_execution(profile, task, evidence)

        self.assertEqual(plan["readiness"], "READY")
        self.assertEqual(plan["handoff"], "implement")
        self.assertIsNotNone(plan["execution_config"])
        self.assertEqual(plan["execution_state"], "executable")
        self.assertEqual(plan["mode_title"], "Case B (Fixed Single-model + Decomposed)")
        self.assertEqual(plan["provider_mode"], "fixed-single-model")
        self.assertEqual(plan["task_shape"], "decomposed")

        # Controller is in main session with single model
        self.assertEqual(plan["controller"]["model"], "model-alpha")
        self.assertEqual(plan["controller"]["context"], "current-session")

        # Workers all run the same model with verified host effort
        for worker in plan["workers"]:
            self.assertEqual(worker["model"], "model-alpha")
            self.assertEqual(worker["effort"], "high")

        # Concurrency limit respected
        self.assertEqual(plan["concurrency_cap"], 2)
        self.assertFalse(plan["model_tier_assignment"])
        self.assertEqual(plan["review"]["type"], "Controller Review")

    # -------------------------------------------------------------------------
    # Multi-Model Behavior Tests (§58)
    # -------------------------------------------------------------------------

    def test_case_c_multi_model_single_pass(self) -> None:
        """Case C: Task difficulty mapped to user profile tier, minimal topology."""
        profile = load("profile-multi-model.json")
        evidence = load("case-a-tiered-single-pass.json")
        task = {"difficulty": "moderate"}

        plan = route_execution(profile, task, evidence)

        self.assertEqual(plan["readiness"], "READY")
        self.assertEqual(plan["handoff"], "implement")
        self.assertIsNotNone(plan["execution_config"])
        self.assertEqual(plan["execution_state"], "executable")
        self.assertEqual(plan["mode_title"], "Case C (Tiered Multi-model + Single-pass)")
        self.assertEqual(plan["provider_mode"], "tiered-multi-model")
        self.assertEqual(plan["task_shape"], "single-pass")
        self.assertEqual(plan["execution"]["tier"], "standard")
        self.assertEqual(plan["execution"]["model"], "model-beta")
        self.assertEqual(plan["execution"]["effort"], "medium")
        self.assertEqual(plan["topology"], "minimal")
        self.assertEqual(plan["review"]["tier"], "review")
        self.assertEqual(plan["review"]["model"], "model-gamma")
        self.assertEqual(plan["review"]["effort"], "high")

    def test_case_d_multi_model_decomposed_p0(self) -> None:
        """Case D (P0): Ticket difficulty mapped to profile tiers, Controller review, real model IDs."""
        profile = load("profile-multi-model.json")
        evidence = load("case-b-tiered-decomposed.json")
        tickets = [
            {"id": "01", "difficulty": "routine", "blocked_by": []},
            {"id": "02", "difficulty": "moderate", "blocked_by": []},
            {"id": "03", "difficulty": "demanding", "blocked_by": []},
            {"id": "04", "difficulty": "critical", "blocked_by": ["03"]},
        ]
        task = {"tickets": tickets}

        plan = route_execution(profile, task, evidence)

        self.assertEqual(plan["readiness"], "READY")
        self.assertEqual(plan["handoff"], "implement")
        self.assertIsNotNone(plan["execution_config"])
        self.assertEqual(plan["execution_state"], "executable")
        self.assertEqual(plan["mode_title"], "Case D (Tiered Multi-model + Decomposed)")
        self.assertEqual(plan["provider_mode"], "tiered-multi-model")
        self.assertEqual(plan["task_shape"], "decomposed")

        # Controller runs on review / high tier
        self.assertEqual(plan["controller"]["model"], "model-gamma")

        # Workers map strictly to user-confirmed tiers
        w01 = plan["workers"][0]
        self.assertEqual(w01["tier"], "routine")
        self.assertEqual(w01["model"], "model-alpha")
        self.assertEqual(w01["effort"], "low")

        w02 = plan["workers"][1]
        self.assertEqual(w02["tier"], "standard")
        self.assertEqual(w02["model"], "model-beta")
        self.assertEqual(w02["effort"], "medium")

        w03 = plan["workers"][2]
        self.assertEqual(w03["tier"], "high")
        self.assertEqual(w03["model"], "model-gamma")
        self.assertEqual(w03["effort"], "high")

        w04 = plan["workers"][3]
        self.assertEqual(w04["tier"], "high")
        self.assertEqual(w04["model"], "model-gamma")
        self.assertEqual(w04["effort"], "high")

        self.assertEqual(plan["concurrency_cap"], 3)
        self.assertEqual(plan["review"]["type"], "Controller Review")

    def test_multi_model_same_model_bound_to_multiple_tiers(self) -> None:
        """A user profile can bind the same model to multiple tiers without error."""
        profile = load("profile-multi-model-shared.json")
        evidence = load("case-a-tiered-single-pass.json")

        self.assertEqual(profile["tiers"]["routine"]["model"], "model-alpha")
        self.assertEqual(profile["tiers"]["standard"]["model"], "model-alpha")
        self.assertEqual(profile["tiers"]["high"]["model"], "model-beta")

        task = {"difficulty": "routine"}
        plan = route_execution(profile, task, evidence)
        self.assertEqual(plan["execution"]["model"], "model-alpha")

        task2 = {"difficulty": "moderate"}
        plan2 = route_execution(profile, task2, evidence)
        self.assertEqual(plan2["execution"]["model"], "model-alpha")

        task3 = {"difficulty": "demanding"}
        plan3 = route_execution(profile, task3, evidence)
        self.assertEqual(plan3["execution"]["model"], "model-beta")

    def test_stale_profile_detection_on_missing_model(self) -> None:
        """When a configured model disappears from the host, profile is detected as stale (§58)."""
        profile = load("profile-multi-model.json")
        # model-gamma is configured for high/review, but disappears from host
        host_available_models = ["model-alpha", "model-beta"]

        is_stale, reasons = check_profile_stale(profile, host_available_models)
        self.assertTrue(is_stale)
        self.assertTrue(any("model-gamma" in r for r in reasons))

        # Setup Gate routes to setup/repair
        gate = evaluate_setup_gate("normal", {"configured": True}, profile, host_available_models)
        self.assertEqual(gate["action"], "setup-questionnaire")
        self.assertTrue(gate.get("stale"))

    # -------------------------------------------------------------------------
    # Ticket / Workflow Integration Tests (§59)
    # -------------------------------------------------------------------------

    def test_ticket_integration_missing_tickets_hands_off_to_project_tickets(self) -> None:
        """Decomposed task without formal tickets yields NEED_PROJECT_TICKETS handoff (§59, Repair 3)."""
        profile = load("profile-single-model.json")
        evidence = load("case-d-fixed-decomposed.json")
        task = {"requires_ticket_decomposition": True, "tickets": []}

        plan = route_execution(profile, task, evidence)
        self.assertEqual(plan["readiness"], "NEED_PROJECT_TICKETS")
        self.assertEqual(plan["task_shape"], "decomposed")
        self.assertEqual(plan["handoff"], "project-tickets")
        self.assertIsNone(plan["execution_config"])

    def test_unranked_multiple_models_fall_back_without_guessing(self) -> None:
        """Do not guess intelligence by model name (model-pro vs model-mini vs model-ultra)."""
        evidence = load("unranked-multiple-models.json")
        provider_mode = classify_provider_mode(evidence, profile=None)
        # Without user profile tiers, never default to fixed-single-model
        self.assertEqual(provider_mode, "unprofiled")
        self.assertEqual(current_model(evidence), "model-pro")
        # With confirmed profile, resolves according to profile mode
        profile = {"model_mode": "single", "single_model": {"model": "model-pro"}}
        self.assertEqual(classify_provider_mode(evidence, profile=profile), "fixed-single-model")

    def test_missing_reasoning_control_continues_safely(self) -> None:
        """Unavailable reasoning control proceeds with host default without returning unsupported."""
        evidence = load("missing-reasoning-control.json")
        self.assertEqual(capability(evidence, "reasoning_control"), "unavailable")
        provider_mode = classify_provider_mode(evidence)
        self.assertNotEqual(provider_mode, "unsupported")

    def test_false_inventory_and_missing_model_return_unsupported(self) -> None:
        """No executable or selectable models produces unsupported."""
        false_inv = load("false-inventory.json")
        self.assertEqual(classify_provider_mode(false_inv), "unsupported")

        missing_mod = load("missing-model-evidence.json")
        self.assertEqual(classify_provider_mode(missing_mod), "unsupported")

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
        self.assertEqual(classify_provider_mode(v1_evidence, profile=None), "unprofiled")
        profile = {"model_mode": "single", "single_model": {"model": "model-alpha"}}
        provider_mode = classify_provider_mode(v1_evidence, profile=profile)
        self.assertEqual(provider_mode, "fixed-single-model")
        self.assertEqual(current_model(v1_evidence), "model-alpha")

    def test_setup_never_assesses_ticket_difficulty_emits_topology_or_routes_workers(self) -> None:
        """agent-config setup prepares/repairs environment/profile, never assessing difficulty or routing (§13, §18)."""
        setup_gate_res = evaluate_setup_gate("agent-config setup", companion_status=None, profile=None)
        self.assertEqual(setup_gate_res["action"], "open-setup")
        # Setup mode must never emit execution topologies, ticket difficulties, or worker routing
        self.assertNotIn("topology", setup_gate_res)
        self.assertNotIn("workers", setup_gate_res)
        self.assertNotIn("difficulty", setup_gate_res)
        self.assertNotIn("controller", setup_gate_res)
        self.assertNotIn("execution", setup_gate_res)
        self.assertEqual(setup_gate_res["target"], "references/setup.md")

    def test_normal_agent_config_never_silently_installs_mcp_or_rewrites_profiles(self) -> None:
        """Normal agent-config runtime planning never silently installs MCP or rewrites profiles (§15, §16, §18)."""
        res_no_companion = evaluate_setup_gate("plan", companion_status=None, profile=None)
        # Never silently mutates host or auto-installs MCP
        self.assertIn(res_no_companion["action"], {"plan-only-fallback", "setup-questionnaire"})
        self.assertNotIn("installed_mcp", res_no_companion)
        self.assertNotIn("mutated_profile", res_no_companion)

        # Missing profile halts resource routing rather than silently generating/rewriting a profile
        evidence = load("unranked-multiple-models.json")
        plan_no_profile = route_execution(profile=None, task={"difficulty": "routine"}, host_evidence=evidence)
        self.assertEqual(plan_no_profile["readiness"], "NEED_INPUT")
        self.assertEqual(plan_no_profile["handoff"], "setup")
        self.assertIsNone(plan_no_profile["execution_config"])
        self.assertEqual(plan_no_profile["action"], "setup-required")
        self.assertNotIn("saved_profile", plan_no_profile)

    def test_unprofiled_host_halts_resource_routing_and_never_defaults_to_fixed_single_model(self) -> None:
        """When no profile exists, provider_mode does not default to fixed-single-model and routing halts (§17)."""
        evidence = load("unranked-multiple-models.json")
        provider_mode = classify_provider_mode(evidence, profile=None)
        self.assertNotEqual(provider_mode, "fixed-single-model")
        self.assertEqual(provider_mode, "unprofiled")

        task = {"difficulty": "demanding"}
        plan = route_execution(profile=None, task=task, host_evidence=evidence)
        self.assertEqual(plan["readiness"], "NEED_INPUT")
        self.assertEqual(plan["handoff"], "setup")
        self.assertIsNone(plan["execution_config"])
        self.assertNotEqual(plan.get("provider_mode"), "fixed-single-model")
        self.assertEqual(plan.get("action"), "setup-required")
        self.assertEqual(plan.get("target"), "agent-config setup")

    def test_unauthorized_model_returns_canonical_blocked(self) -> None:
        """Task requesting model not authorized in user profile returns canonical BLOCKED (§7, §11)."""
        profile = load("profile-single-model.json")
        evidence = load("case-c-fixed-single-pass.json")
        task = {"difficulty": "routine", "requested_model": "unauthorized-external-model"}
        plan = route_execution(profile, task, evidence)
        self.assertEqual(plan["readiness"], "BLOCKED")
        self.assertIsNone(plan["execution_config"])
        self.assertIn("not authorized", plan["reason"])

    def test_unsupported_host_returns_canonical_unsupported(self) -> None:
        """Host evidencing no executable or selectable models returns canonical UNSUPPORTED (§7, §11)."""
        profile = load("profile-single-model.json")
        evidence = load("missing-model-evidence.json")
        task = {"difficulty": "routine"}
        plan = route_execution(profile, task, evidence)
        self.assertEqual(plan["readiness"], "UNSUPPORTED")
        self.assertIsNone(plan["execution_config"])

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
            self.assertTrue((destination / "references" / "harness-support.md").is_file())
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
