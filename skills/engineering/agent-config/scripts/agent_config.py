"""Public entry point and CLI for agent-config."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from .abstract_profiler import extract_abstract_task_profile
    from .candidate_selector import select_configuration
    from .agent_config_models import (
        AgentConfigResult,
        HostCapabilities,
        TaskCharacteristics,
    )
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from abstract_profiler import extract_abstract_task_profile
    from candidate_selector import select_configuration
    from agent_config_models import (
        AgentConfigResult,
        HostCapabilities,
        TaskCharacteristics,
    )


def agent_config_recommend(
    host: Union[HostCapabilities, Dict[str, Any]],
    task: Union[TaskCharacteristics, Dict[str, Any]],
    approval: Optional[Union[str, bool]] = None,
    approved_preview: Optional[bool] = None,
    setup_intent: bool = False,
    client: Optional[Any] = None,
    use_jev: bool = True,
    profile: Optional[Dict[str, Any]] = None,
    active_session: Optional[Dict[str, Any]] = None,
) -> AgentConfigResult:
    """Recommend right-sized topology, model, and effort for task on current host."""
    if setup_intent:
        return AgentConfigResult(
            readiness="NEED_INPUT", mode="plan-only", handoff="setup",
            setup_state={"companion": "missing", "profile": "missing"},
            justification="Explicit setup intent; use the setup workflow before execution planning.",
        )
    try:
        if isinstance(host, dict):
            host_obj = _host_from_canonical_evidence(host, profile, active_session)
        else:
            raise ValueError("canonical HostCapabilities and Profile dictionaries are required")
    except (TypeError, ValueError, KeyError, AttributeError) as exc:
        return AgentConfigResult(
            readiness="NEED_INPUT", mode="plan-only",
            setup_state={"companion": "missing", "profile": "missing"},
            justification=f"Cannot plan execution from unconfirmed Host/Profile evidence: {exc}",
        )
    if not isinstance(task, (dict, TaskCharacteristics)):
        return AgentConfigResult(readiness="NEED_INPUT", mode="plan-only",
                                 justification="Task characteristics must be an object.")
    task_obj = TaskCharacteristics.from_dict(task) if isinstance(task, dict) else task
    if task_obj.reasoning_policy is not None and not isinstance(task_obj.reasoning_policy, str):
        return AgentConfigResult(readiness="NEED_INPUT", mode="plan-only",
                                 justification="Task reasoning policy must be a string.")

    abstract_profile, confidence, fallback_used, fallback_reason = extract_abstract_task_profile(
        task=task_obj,
        client=client,
        use_jev=use_jev,
    )
    if not task_obj.reasoning_policy and isinstance(profile, dict):
        try:
            if profile.get("model_mode") == "multi":
                effort = profile["tiers"][abstract_profile.recommended_tier].get("effort", {})
            else:
                key = "review_effort" if abstract_profile.recommended_tier == "review" else "execution_effort"
                effort = profile["single_model"].get(key, {})
            if not isinstance(effort, dict):
                raise ValueError("Profile effort policy must be an object")
            if effort.get("policy") == "custom" and (not isinstance(effort.get("value"), str) or not effort["value"]):
                raise ValueError("Custom Profile effort policy needs a concrete Host-supported value")
            task_obj.reasoning_policy = (effort.get("value") if effort.get("policy") == "custom"
                                         else effort.get("policy") or effort.get("value"))
        except (TypeError, KeyError, AttributeError, ValueError) as exc:
            return AgentConfigResult(readiness="NEED_INPUT", mode="plan-only",
                                     justification=f"Profile effort policy is invalid: {exc}")
    if task_obj.reasoning_policy and task_obj.reasoning_policy != "default" and not host_obj.supported_effort:
        return AgentConfigResult(
            readiness="NEED_INPUT", mode="plan-only",
            setup_state={"companion": "missing", "profile": "session-local"},
            justification="Requested reasoning effort has no confirmed Host capability or supported values.",
        )
    supported_policies = {"highest-supported", "lowest-supported", "minimal", "default", "standard"}
    if (task_obj.reasoning_policy and task_obj.reasoning_policy not in supported_policies
            and task_obj.reasoning_policy not in host_obj.supported_effort):
        return AgentConfigResult(
            readiness="NEED_INPUT", mode="plan-only", execution_config=None,
            justification=f"Requested reasoning effort {task_obj.reasoning_policy!r} is not supported by this Host.",
        )
    if host_obj.profile_mode == "single" and host_obj.has_model_selector:
        if host_obj.active_model != host_obj.profile_tiers["standard"]:
            return AgentConfigResult(
                readiness="NEED_INPUT", mode="plan-only", execution_config=None,
                justification="Single-model Profile target is available, but the current session has not been verified to use it; select and validate the model before execution.",
            )
    return select_configuration(
        host=host_obj, task=task_obj, profile=abstract_profile,
        approval=approval, approved_preview=approved_preview,
        setup_intent=setup_intent, jev_confidence=confidence,
        fallback_used=fallback_used, fallback_reason=fallback_reason,
    )


def _host_from_canonical_evidence(host: Dict[str, Any], profile: Optional[Dict[str, Any]], active_session: Optional[Dict[str, Any]] = None) -> HostCapabilities:
    """Translate the companion's HostCapabilities/Profile, never inventing models."""
    if not isinstance(profile, dict):
        raise ValueError("canonical user-confirmed Profile is missing")
    if profile.get("profile_version") != 1:
        raise ValueError("canonical Profile version is missing or unsupported")
    for key in ("host", "scope"):
        if not isinstance(profile.get(key), dict):
            raise ValueError(f"Profile {key} must be an object")
    host_id, adapter_id = host.get("host_id"), host.get("adapter_id")
    if not host_id or not adapter_id or profile.get("host", {}).get("id") != host_id or profile.get("host", {}).get("adapter") != adapter_id:
        raise ValueError("Host and Profile identity differ")
    observed = datetime.fromisoformat(str(host["observed_at"]).replace("Z", "+00:00"))
    if observed.tzinfo is None or not datetime.now(timezone.utc) - timedelta(hours=24) <= observed <= datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError("Host evidence is stale or has an invalid timestamp")
    def fresh_evidence(evidence: object) -> bool:
        verified_kinds = {"host-runtime", "host-config", "host-schema", "adapter-probe", "user-confirmed"}
        if not isinstance(evidence, dict) or evidence.get("kind") not in verified_kinds or not evidence.get("locator"):
            return False
        if not evidence.get("observed_at"):
            return True  # The enclosing Host snapshot supplies the timestamp.
        stamp = datetime.fromisoformat(str(evidence["observed_at"]).replace("Z", "+00:00"))
        return stamp.tzinfo is not None and datetime.now(timezone.utc) - timedelta(hours=24) <= stamp <= datetime.now(timezone.utc) + timedelta(minutes=5)
    workspace = host.get("workspace")
    scope = profile.get("scope", {})
    if scope.get("type") == "project" and (not workspace or workspace != scope.get("workspace")):
        raise ValueError("Profile workspace does not match inspected Host workspace")
    if scope.get("type") not in ("project", "global"):
        raise ValueError("Profile scope is unconfirmed")
    available = []
    for item in host.get("available_models", []):
        evidence = item.get("evidence") if isinstance(item, dict) else None
        if isinstance(item, dict) and item.get("state") == "available" and fresh_evidence(evidence) and item.get("id"):
            available.append(item["id"])
    if not available:
        raise ValueError("no evidenced available models")
    verified_active = ""
    if active_session is not None:
        if not isinstance(active_session, dict) or active_session.get("host_id") != host_id or active_session.get("adapter_id") != adapter_id:
            raise ValueError("current session identity does not match Host evidence")
        active_evidence = active_session.get("evidence")
        if (not isinstance(active_evidence, dict) or active_evidence.get("kind") not in ("host-runtime", "adapter-probe")
                or not active_evidence.get("observed_at") or not fresh_evidence(active_evidence)
                or not active_session.get("observed_at")):
            raise ValueError("current session model lacks fresh runtime evidence")
        active_stamp = datetime.fromisoformat(str(active_session["observed_at"]).replace("Z", "+00:00"))
        evidence_stamp = datetime.fromisoformat(str(active_evidence["observed_at"]).replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if (active_stamp.tzinfo is None or evidence_stamp.tzinfo is None
                or not now - timedelta(minutes=5) <= active_stamp <= now + timedelta(minutes=5)
                or not now - timedelta(minutes=5) <= evidence_stamp <= now + timedelta(minutes=5)):
            raise ValueError("current session model evidence is stale")
        if scope.get("type") == "project" and active_session.get("workspace") != workspace:
            raise ValueError("current session workspace differs from Host evidence")
        verified_active = active_session.get("model", "")
        if verified_active not in available:
            raise ValueError("current session model is not in verified Host inventory")
    capabilities = host.get("capabilities", {})
    if not isinstance(capabilities, dict):
        raise ValueError("Host capabilities must be an object")
    reasoning = capabilities.get("reasoning", {})
    effort_values = host.get("supported_effort_values", [])
    if not isinstance(effort_values, list) or any(not isinstance(value, str) or not value for value in effort_values):
        raise ValueError("Host effort inventory is invalid")
    if effort_values and (reasoning.get("state") != "available" or not fresh_evidence(reasoning.get("evidence"))):
        raise ValueError("Host effort inventory lacks confirmed reasoning capability")
    selector = capabilities.get("model_selection", {})
    if selector.get("state") not in ("available", "unavailable") or not fresh_evidence(selector.get("evidence")):
        raise ValueError("model selection capability is unconfirmed")
    if not isinstance(selector.get("scopes", []), list):
        raise ValueError("model selection scopes must be a list")
    mode = profile.get("model_mode")
    if mode == "single":
        single = profile.get("single_model")
        if not isinstance(single, dict):
            raise ValueError("Profile single_model must be an object")
        target_model = single.get("model")
        tiers = {tier: target_model for tier in ("routine", "standard", "high", "review")}
        # The canonical Host inventory does not identify the active session model.
        # A fixed-model Host is safe only when its evidenced inventory is unique.
        if selector["state"] == "unavailable" and len(available) != 1:
            raise ValueError("single-model Profile lacks confirmed current Host model")
        active = verified_active or (available[0] if selector["state"] == "unavailable" else "")
    elif mode == "multi" and selector["state"] == "available":
        tiers = {}
        if not isinstance(profile.get("tiers"), dict):
            raise ValueError("Profile tiers must be an object")
        for tier in ("routine", "standard", "high", "review"):
            entry = profile.get("tiers", {}).get(tier, {})
            if not isinstance(entry, dict):
                raise ValueError(f"{tier} tier must be an object")
            if entry.get("source") != "user-confirmed" or not entry.get("model"):
                raise ValueError(f"{tier} tier lacks user confirmation")
            tiers[tier] = entry["model"]
        active = verified_active  # Canonical HostCapabilities does not report the current model.
    else:
        raise ValueError("Profile mode conflicts with Host model selection capability")
    if any(model not in available for model in tiers.values()):
        raise ValueError("Profile refers to unavailable or unconfirmed model")
    return HostCapabilities(
        harness=host_id, has_model_selector=selector["state"] == "available",
        selector_scopes=list(selector.get("scopes", [])),
        supported_effort=list(effort_values),
        default_effort=host.get("default_effort_value"),
        per_agent_config=(
            (capabilities.get("per_agent_model_selection", {}).get("state") == "available"
             and fresh_evidence(capabilities.get("per_agent_model_selection", {}).get("evidence")))
            or ("per-agent" in selector.get("scopes", [])
                and capabilities.get("subagents", {}).get("state") == "available"
                and fresh_evidence(capabilities.get("subagents", {}).get("evidence")))
        ),
        active_model=active, available_models=available, profile_tiers=tiers,
        profile_mode=mode,
        companion_status="missing", profile_status="session-local",
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Config execution configurator")
    parser.add_argument("--host-json", default="{}", help="Host capabilities JSON")
    parser.add_argument("--task-json", default="{}", help="Task characteristics JSON")
    parser.add_argument("--profile-json", default="{}", help="Canonical user-confirmed Profile JSON")
    parser.add_argument("--active-session-json", default="null", help="Optional fresh current-session model evidence JSON")
    parser.add_argument("--setup", action="store_true", help="Explicit setup intent")
    parser.add_argument("--approval", choices=["unknown", "approved", "declined"], default=None, help="Explicit preview approval state")
    parser.add_argument("--no-preview-approval", action="store_true", help="Simulate user declining preview")
    parser.add_argument("--no-jev", action="store_true", help="Disable Jev System One judgments")

    args = parser.parse_args()
    host_data = json.loads(args.host_json)
    task_data = json.loads(args.task_json)

    approval_arg = args.approval
    if approval_arg is None and args.no_preview_approval:
        approval_arg = "declined"

    result = agent_config_recommend(
        host=host_data,
        task=task_data,
        profile=json.loads(args.profile_json),
        active_session=json.loads(args.active_session_json),
        approval=approval_arg,
        setup_intent=args.setup,
        use_jev=not args.no_jev,
    )

    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
