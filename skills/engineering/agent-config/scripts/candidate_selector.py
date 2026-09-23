"""Candidate configuration selector and gatekeeper for agent-config.

Combines host capabilities, task shape, and abstract profile into canonical AgentConfigResult.
"""

from __future__ import annotations

from typing import Optional, Union

try:
    from .harness_adapter import (
        determine_topology,
        discover_valid_candidates,
        resolve_reasoning_effort,
    )
    from .agent_config_models import (
        AbstractTaskProfile,
        AgentConfigResult,
        ExecutionConfig,
        HostCapabilities,
        TaskCharacteristics,
    )
except ImportError:
    from harness_adapter import (
        determine_topology,
        discover_valid_candidates,
        resolve_reasoning_effort,
    )
    from agent_config_models import (
        AbstractTaskProfile,
        AgentConfigResult,
        ExecutionConfig,
        HostCapabilities,
        TaskCharacteristics,
    )


def select_configuration(
    host: HostCapabilities,
    task: TaskCharacteristics,
    profile: AbstractTaskProfile,
    approval: Optional[Union[str, bool]] = None,
    approved_preview: Optional[bool] = None,
    setup_intent: bool = False,
    jev_confidence: Optional[float] = None,
    fallback_used: bool = False,
    fallback_reason: Optional[str] = None,
) -> AgentConfigResult:
    """Combine host capabilities, task shape, and abstract profile into AgentConfigResult.

    Enforces:
      - Dimension-aware effort resolution (explicit policy > profile reasoning_need > host bounds).
      - Strict candidate containment (selected_model must be in valid_candidates).
      - Explicit approval tracking (unknown, approved, declined).
      - Cost sensitivity does not downgrade capability tier.
    """
    # Normalize approval
    if approval is not None:
        norm_approval = ("approved" if approval else "declined") if isinstance(approval, bool) else str(approval).lower()
    elif approved_preview is not None:
        norm_approval = "approved" if approved_preview else "declined"
    else:
        norm_approval = "unknown"

    # Gate 1: Explicit setup intent
    if setup_intent:
        return AgentConfigResult(
            readiness="NEED_INPUT",
            mode="plan-only",
            approval=norm_approval,
            setup_state={"companion": host.companion_status, "profile": host.profile_status},
            handoff="setup",
            execution_config=None,
            justification="Setup intent detected; preparing host environment without task planning.",
            abstract_profile=profile,
        )

    # Gate 2: Decomposition gate
    if task.shape == "decomposed" and not task.formal_tickets_exist:
        return AgentConfigResult(
            readiness="NEED_PROJECT_TICKETS",
            mode="plan-only",
            approval=norm_approval,
            setup_state={"companion": host.companion_status, "profile": host.profile_status},
            handoff="project-tickets",
            execution_config=None,
            justification="Task classified as decomposed but formal tickets do not exist. Ticketing required.",
            abstract_profile=profile,
        )

    # Gate 3: Host without model selector
    if not host.has_model_selector:
        if not host.active_model or host.active_model not in host.available_models:
            return AgentConfigResult(
                readiness="NEED_INPUT", mode="plan-only", approval=norm_approval,
                setup_state={"companion": host.companion_status, "profile": host.profile_status},
                justification="Fixed Host active model has no confirmed availability evidence.",
                abstract_profile=profile,
            )
        topology = "Case B" if task.shape == "decomposed" else "Case A"
        effort = resolve_reasoning_effort(host, task.reasoning_policy, profile.reasoning_need)
        return AgentConfigResult(
            readiness="READY",
            mode="plan-only",
            approval=norm_approval,
            setup_state={"companion": host.companion_status, "profile": host.profile_status},
            handoff="implement",
            execution_config=ExecutionConfig(
                model=host.active_model,
                resolved_effort=effort,
                topology=topology,
            ),
            justification=f"Harness lacks dynamic model selector; gracefully preserved active model {host.active_model} ({topology}).",
            abstract_profile=profile,
            jev_confidence=jev_confidence,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
        )

    # Gate 4: User rejected configuration preview
    if norm_approval == "declined":
        if not host.active_model or host.active_model not in host.available_models:
            return AgentConfigResult(
                readiness="NEED_INPUT", mode="plan-only", approval="declined",
                setup_state={"companion": host.companion_status, "profile": host.profile_status},
                justification="Current active model is not evidenced; cannot fall back after preview rejection.",
                abstract_profile=profile,
            )
        topology = "Case B" if task.shape == "decomposed" else "Case A"
        return AgentConfigResult(
            readiness="READY",
            mode="plan-only",
            approval="declined",
            setup_state={"companion": host.companion_status, "profile": host.profile_status},
            handoff="implement",
            execution_config=ExecutionConfig(
                model=host.active_model,
                resolved_effort=None,
                topology=topology,
            ),
            justification="User declined configuration mutation; falling back safely to active model in main session.",
            abstract_profile=profile,
            jev_confidence=jev_confidence,
            fallback_used=True,
            fallback_reason="User rejected configuration change preview.",
        )

    # Normal selection flow
    valid_candidates = discover_valid_candidates(host)
    tier = profile.recommended_tier

    # Resolve target model from profile tiers
    target_model = host.profile_tiers.get(tier)

    # A tier is a user-confirmed capability choice, not permission to downgrade.
    if not target_model or target_model not in valid_candidates:
        return AgentConfigResult(
            readiness="NEED_INPUT",
            mode="plan-only",
            approval=norm_approval,
            setup_state={"companion": host.companion_status, "profile": host.profile_status},
            justification=f"No confirmed, available model for {tier} tier; refresh Host evidence or confirm the Profile.",
            abstract_profile=profile,
        )
    if target_model != host.active_model and "current-session" not in host.selector_scopes and host.profile_mode:
        return AgentConfigResult(
            readiness="NEED_INPUT", mode="plan-only", approval=norm_approval,
            setup_state={"companion": host.companion_status, "profile": host.profile_status},
            justification="Host cannot select the target model in the current session, and the current model is unverified or different.",
            abstract_profile=profile,
        )

    # Resolve reasoning effort (explicit policy > Jev profile.reasoning_need > host bounds)
    effort = resolve_reasoning_effort(host, task.reasoning_policy, profile.reasoning_need)

    # Determine topology
    if task.shape == "decomposed":
        topology = "Case B" if host.profile_mode == "single" else ("Case D" if (host.per_agent_config and len(valid_candidates) > 1) else "Case B")
    else:
        topology = "Case A" if host.profile_mode == "single" else ("Case C" if host.profile_mode == "multi" or (target_model != host.active_model and host.has_model_selector) else "Case A")

    cost_note = ""
    if task.cost_sensitive:
        cost_note = " (Cost sensitivity recorded; no host cost metadata available for tie-breaking within valid candidates)"

    justification_msg = (
        f"Selected {target_model} for {tier} tier (topology: {topology}, effort: {effort or 'default'}).{cost_note}"
    )
    if fallback_used:
        justification_msg += f" (Fallback: {fallback_reason})"

    return AgentConfigResult(
        readiness="READY",
        mode="plan-only",
        approval=norm_approval,
        setup_state={"companion": host.companion_status, "profile": host.profile_status},
        handoff="implement",
        execution_config=ExecutionConfig(
            model=target_model,
            resolved_effort=effort,
            topology=topology,
        ),
        justification=justification_msg,
        abstract_profile=profile,
        jev_confidence=jev_confidence,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )
