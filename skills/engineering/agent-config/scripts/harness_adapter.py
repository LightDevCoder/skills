"""Deterministic harness capability adapter for agent-config.

Enforces deterministic capability discovery and effort resolution:
  - NEVER emit unverified literal 'max'.
  - Support hosts without model selector gracefully (single-model peer mode).
  - Four peer topologies: Case A, Case B, Case C, Case D.
"""

from __future__ import annotations

from typing import List, Optional

try:
    from .agent_config_models import HostCapabilities, TaskCharacteristics
except ImportError:
    from agent_config_models import HostCapabilities, TaskCharacteristics


def resolve_reasoning_effort(
    host: HostCapabilities,
    policy: Optional[str] = None,
    profile_reasoning_need: Optional[str] = None,
) -> Optional[str]:
    """Resolve reasoning effort strictly to verified host-supported strings.

    Precedence:
      1. Host capability constraints: if host does not support reasoning controls, returns None.
      2. Explicit user reasoning policy / profile policy: authoritative; Jev cannot lower or override.
      3. Jev reasoning judgment (profile_reasoning_need): maps to nearest verified supported value.
      4. Deterministic fallback: None.

    Invariants:
      - NEVER emit unverified literal 'max'.
      - Host-supported effort strictly bounds output (Jev cannot invent unsupported effort).
    """
    if not host.supported_effort:
        return None

    efforts = [e.lower() for e in host.supported_effort]
    def exact_host_value(value: str) -> str:
        return host.supported_effort[efforts.index(value)]

    # Precedence 1: Explicit user reasoning policy
    if policy:
        if policy == "highest-supported":
            # The host's ordered inventory is authoritative, including xhigh/max.
            return host.supported_effort[-1]

        if policy in ("lowest-supported", "minimal"):
            return host.supported_effort[0]

        if policy == "default":
            return host.default_effort if host.default_effort in host.supported_effort else None

        if policy == "standard":
            if "medium" in efforts:
                return exact_host_value("medium")
            if "standard" in efforts:
                return exact_host_value("standard")
            return host.supported_effort[0]

        # If policy matches an exact host effort string
        if policy.lower() in efforts:
            return exact_host_value(policy.lower())

        # Unknown explicit values require confirmation at the public entry point.
        return None

    # Precedence 2: Jev semantic reasoning judgment
    if profile_reasoning_need:
        need = profile_reasoning_need.lower()
        if need == "high":
            if "high" in efforts:
                return exact_host_value("high")
            if "medium" in efforts:
                return exact_host_value("medium")
            return host.supported_effort[-1]
        elif need == "medium":
            if "medium" in efforts:
                return exact_host_value("medium")
            if "standard" in efforts:
                return exact_host_value("standard")
            if "low" in efforts:
                return exact_host_value("low")
            return host.supported_effort[0]
        elif need == "low":
            if "low" in efforts:
                return exact_host_value("low")
            if "minimal" in efforts:
                return exact_host_value("minimal")
            return host.supported_effort[0]

    return None


def discover_valid_candidates(host: HostCapabilities) -> List[str]:
    """Return strictly legal candidate models supported by this harness and confirmed in profile."""
    if not host.has_model_selector:
        return [host.active_model] if host.active_model in host.available_models else []

    valid: List[str] = []
    # Intersect available models with confirmed profile tiers
    for tier, model in host.profile_tiers.items():
        if model in host.available_models and model not in valid:
            valid.append(model)

    if not valid and host.active_model in host.available_models:
        valid.append(host.active_model)

    return valid


def determine_topology(
    host: HostCapabilities,
    task: TaskCharacteristics,
    is_multi_model: bool,
) -> str:
    """Determine one of the 4 peer execution modes (Cases A, B, C, D)."""
    if task.shape == "decomposed":
        if is_multi_model and host.per_agent_config:
            return "Case D"
        return "Case B"
    else:
        if is_multi_model and host.has_model_selector and len(host.profile_tiers) > 1:
            return "Case C"
        return "Case A"
