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
    policy: Optional[str],
) -> Optional[str]:
    """Resolve abstract reasoning policy strictly to verified host-supported strings.
    
    Invariant: NEVER emit unverified literal 'max'.
    If the harness does not support reasoning controls, returns None safely.
    """
    if not host.supported_effort:
        return None

    if not policy:
        return None

    efforts = [e.lower() for e in host.supported_effort]

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
