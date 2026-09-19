"""Public entry point for ask-light semantic workflow advisor."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

try:
    from .ask_light_models import AskLightRecommendation, CompactProjectState
    from .semantic_router import route_with_jev
    from .state_extractor import compute_legal_actions, extract_compact_state_from_dict
except ImportError:
    from ask_light_models import AskLightRecommendation, CompactProjectState
    from semantic_router import route_with_jev
    from state_extractor import compute_legal_actions, extract_compact_state_from_dict


def ask_light_semantic_recommend(
    state: Union[Dict[str, Any], CompactProjectState],
    user_request: str = "下一步做什么？",
    scope: str = "current-workflow",
    explicit_target: Optional[str] = None,
    client: Optional[Any] = None,
    use_jev: bool = True,
    shadow_mode: bool = False,
) -> AskLightRecommendation:
    """Recommend the next workflow action combining deterministic pre-checks and bounded Jev reasoning."""
    if isinstance(state, dict):
        compact_state = extract_compact_state_from_dict(state)
    else:
        compact_state = state

    legal_result = compute_legal_actions(
        state=compact_state,
        user_request=user_request,
        scope=scope,
        explicit_target=explicit_target,
    )

    if not use_jev:
        if legal_result.allowed_actions:
            baseline_skill = legal_result.fallback_action or legal_result.allowed_actions[0]
            return AskLightRecommendation(
                status=legal_result.status,
                primary_skill=baseline_skill,
                alternative_skill=None,
                target_item=legal_result.target_item,
                confidence=None,
                probabilities={baseline_skill: 1.0},
                fallback_used=True,
                fallback_reason="use_jev=False specified; deterministic baseline applied.",
                fail_closed=legal_result.fail_closed,
                justification=f"Deterministic baseline selected {baseline_skill}.",
            )
        else:
            return AskLightRecommendation(
                status=legal_result.status,
                primary_skill=None,
                alternative_skill=None,
                target_item=legal_result.target_item,
                confidence=None,
                probabilities={},
                fallback_used=False,
                fallback_reason=None,
                fail_closed=legal_result.fail_closed,
                justification=legal_result.blocked_reason or "Non-executable query resolved deterministically.",
            )

    return route_with_jev(
        legal_result=legal_result,
        user_request=user_request,
        client=client,
        shadow_mode=shadow_mode,
    )
