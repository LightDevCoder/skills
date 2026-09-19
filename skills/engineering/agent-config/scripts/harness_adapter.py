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

    # Precedence 1: Explicit user reasoning policy
    if policy:
        if policy == "highest-supported":
            for preferred in ["high", "medium", "low"]:
                if preferred in efforts:
                    return preferred
            return host.supported_effort[-1]

        if policy == "minimal":
            for preferred in ["low", "minimal", "medium"]:
                if preferred in efforts:
                    return preferred
            return host.supported_effort[0]

        if policy == "standard":
            if "medium" in efforts:
                return "medium"
            if "standard" in efforts:
                return "standard"
            return host.supported_effort[0]

        # If policy matches an exact host effort string
        if policy.lower() in efforts:
            return policy.lower()

        # If policy requested 'max' or unsupported literal, never emit unverified literal 'max';
        # fall back safely to highest verified level.
        for preferred in ["high", "medium", "low"]:
            if preferred in efforts:
                return preferred
        return host.supported_effort[-1]

    # Precedence 2: Jev semantic reasoning judgment
    if profile_reasoning_need:
        need = profile_reasoning_need.lower()
        if need == "high":
            if "high" in efforts:
                return "high"
            if "medium" in efforts:
                return "medium"
            return host.supported_effort[-1]
        elif need == "medium":
            if "medium" in efforts:
                return "medium"
            if "standard" in efforts:
                return "standard"
            if "low" in efforts:
                return "low"
            return host.supported_effort[0]
        elif need == "low":
            if "low" in efforts:
                return "low"
            if "minimal" in efforts:
                return "minimal"
            return host.supported_effort[0]

    return None


def discover_valid_candidates(host: HostCapabilities) -> List[str]:
    """Return strictly legal candidate models supported by this harness and confirmed in profile."""
    if not host.has_model_selector:
        return [host.active_model]

    valid: List[str] = []
    # Intersect available models with confirmed profile tiers
    for tier, model in host.profile_tiers.items():
        if model in host.available_models and model not in valid:
            valid.append(model)

    if not valid and host.active_model:
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
