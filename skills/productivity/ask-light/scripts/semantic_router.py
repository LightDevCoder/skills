"""Bounded Jev multi-primitive semantic router for ask-light.

Connects TypeSafe Jev System One judgments with deterministic fallbacks:
  1. Choice: Constrained strictly to code-computed legal candidates.
  2. Noul: Execution intent calibration (p >= 0.80) & ambiguity detection (p >= 0.65).
  3. Score: Readiness score (0-3).
  4. Defense-in-depth: Unauthorized selections rejected; fails closed on hard bounds.
  5. Soft dependency: Graceful fallback when typesafe-sdk is not installed or TYPESAFE_API_KEY is unset.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

# Load .env if present
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    dotenv_path = project_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    else:
        load_dotenv()
except ImportError:
    pass

try:
    from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
    TYPESAFE_AVAILABLE = True
except ImportError:
    TYPESAFE_AVAILABLE = False
    class Choice:  # type: ignore[no-redef]
        def __init__(self, instructions: str = "", criteria: Any = None):
            self.instructions = instructions
            self.criteria = criteria
    class Noul:  # type: ignore[no-redef]
        def __init__(self, instructions: str = ""):
            self.instructions = instructions
    class Score:  # type: ignore[no-redef]
        def __init__(self, instructions: str = "", criteria: Any = None):
            self.instructions = instructions
            self.criteria = criteria
    class TypeSafeClient:  # type: ignore[no-redef]
        def __init__(self, api_key: Optional[str] = None):
            self.api_key = api_key
        def system_one(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("TypeSafe SDK is not installed.")

try:
    from .compact_state_builder import build_compact_jev_state
    from .ask_light_models import AskLightRecommendation, LegalActionsResult, SemanticJudgments
except ImportError:
    from compact_state_builder import build_compact_jev_state
    from ask_light_models import AskLightRecommendation, LegalActionsResult, SemanticJudgments

# Calibrated uncertainty thresholds
DEFAULT_CONFIDENCE_THRESHOLD = 0.55
AMBIGUITY_THRESHOLD = 0.65
EXECUTION_INTENT_THRESHOLD = 0.80
ESCALATION_THRESHOLD = 0.60


def route_with_jev(
    legal_result: LegalActionsResult,
    user_request: str,
    client: Optional[Any] = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    enable_expanded_judgments: bool = True,
) -> AskLightRecommendation:
    """Judge legal candidate actions using bounded Jev Choice/Noul/Score with calibrated fallback.
    
    Invariants:
      1. Never called if legal_result is BLOCKED, NEED_INPUT, or EXPLAIN.
      2. Choice is constrained strictly to legal_result.allowed_actions.
      3. Degrades gracefully to deterministic baseline on error or missing credentials.
      4. Calibrated uncertainty policy governs escalation and fallbacks.
    """
    # Guard 1: Non-executable or blocked states return deterministic decision immediately
    if legal_result.status in ["BLOCKED", "NEED_INPUT", "EXPLAIN"]:
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
            justification=legal_result.blocked_reason or "Non-execution query resolved deterministically.",
        )

    # Guard 2: Terminal state for accepted review
    if legal_result.status == "TERMINAL":
        return AskLightRecommendation(
            status="TERMINAL",
            primary_skill=None,
            alternative_skill="release-workflow",
            target_item=None,
            confidence=1.0,
            probabilities={},
            fallback_used=False,
            fail_closed=False,
            justification="Current effort accepted and complete; no mandatory next workflow step.",
        )

    # Guard 3: If no allowed actions exist, halt
    if not legal_result.allowed_actions:
        return AskLightRecommendation(
            status="BLOCKED",
            primary_skill=None,
            target_item=None,
            fallback_used=False,
            fail_closed=True,
            justification="No legal workflow actions available for current project state.",
        )

    # Baseline deterministic default action (first allowed action)
    baseline_skill = legal_result.allowed_actions[0]
    baseline_justification = f"Deterministic baseline selected {baseline_skill} from legal candidates."

    # If TypeSafe is not installed or no API key, fall back immediately
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not TYPESAFE_AVAILABLE or not api_key:
        return AskLightRecommendation(
            status=legal_result.status,
            primary_skill=baseline_skill,
            alternative_skill=None,
            target_item=legal_result.target_item,
            confidence=None,
            probabilities={baseline_skill: 1.0},
            fallback_used=True,
            fallback_reason="TypeSafe SDK or TYPESAFE_API_KEY unavailable; used deterministic baseline.",
            fail_closed=legal_result.fail_closed,
            justification=baseline_justification,
        )

    # Build compact token-efficient state
    compact_state = build_compact_jev_state(legal_result, user_request)

    criteria = {
        action: legal_result.candidate_descriptions.get(action, f"Execute {action} workflow step")
        for action in legal_result.allowed_actions
    }

    questions: Dict[str, Any] = {
        "next_action": Choice(
            instructions="Which legal workflow action best matches the user intent and project evidence?",
            criteria=criteria,
        ),
    }

    if enable_expanded_judgments:
        questions["wants_immediate_execution"] = Noul(
            instructions=(
                "Does the user request command or authorize immediate execution right now "
                "(e.g. '立刻开始', 'go ahead and run it', 'start executing now'), "
                "as opposed to asking a question, asking for advice, or asking for confirmation "
                "(e.g. '现在开始做吗？', '下一步做什么？', 'what should I do next?')?"
            ),
        )
        questions["has_material_ambiguity"] = Noul(
            instructions="Does the request or project state have material ambiguity or unsettled decisions requiring clarification?",
        )
        questions["readiness_score"] = Score(
            instructions="What is the project implementation readiness grade?",
            criteria=[
                "Grade 0: Not ready - uninitialized or missing core requirements/clarification",
                "Grade 1: Partially ready - spec exists but tickets not ready or blocked",
                "Grade 2: Ready - unblocked tickets ready for implementation",
                "Grade 3: Complete - all implementation complete and verified",
            ],
        )
        questions["needs_deep_reasoning_escalation"] = Noul(
            instructions="Does this request involve high architectural complexity or conflicting requirements requiring deep reasoning escalation rather than fast routing?",
        )

    try:
        ts_client = client or TypeSafeClient(api_key=api_key)
        response = ts_client.system_one(state=compact_state, questions=questions)

        choice_ans = response.choices.get("next_action")
        if not choice_ans:
            raise ValueError("Choice answer 'next_action' missing from Jev response")

        selected_skill = choice_ans.choice
        confidence = choice_ans.confidence
        probabilities = dict(choice_ans.probabilities)

        semantic_judgments: Optional[SemanticJudgments] = None
        wants_exec_prob = 0.0
        ambiguity_prob = 0.0
        escalation_prob = 0.0

        if enable_expanded_judgments and hasattr(response, "nouls") and response.nouls:
            noul_exec = response.nouls.get("wants_immediate_execution")
            noul_ambig = response.nouls.get("has_material_ambiguity")
            noul_escala = response.nouls.get("needs_deep_reasoning_escalation")
            score_ready = (
                response.scores.get("readiness_score")
                if hasattr(response, "scores") and response.scores
                else None
            )

            if noul_exec and hasattr(noul_exec, "noul") and isinstance(noul_exec.noul, (int, float)):
                wants_exec_prob = float(noul_exec.noul)
            if noul_ambig and hasattr(noul_ambig, "noul") and isinstance(noul_ambig.noul, (int, float)):
                ambiguity_prob = float(noul_ambig.noul)
            if noul_escala and hasattr(noul_escala, "noul") and isinstance(noul_escala.noul, (int, float)):
                escalation_prob = float(noul_escala.noul)

            readiness_score_val = (
                float(score_ready.score)
                if score_ready and hasattr(score_ready, "score") and isinstance(score_ready.score, (int, float))
                else None
            )
            readiness_conf_val = (
                float(score_ready.confidence)
                if score_ready and hasattr(score_ready, "confidence") and isinstance(score_ready.confidence, (int, float))
                else None
            )

            semantic_judgments = SemanticJudgments(
                action_choice=selected_skill,
                action_confidence=confidence,
                action_probabilities=probabilities,
                wants_immediate_execution_prob=wants_exec_prob,
                has_material_ambiguity_prob=ambiguity_prob,
                readiness_score=readiness_score_val,
                readiness_confidence=readiness_conf_val,
                escalation_prob=escalation_prob,
            )

        # Defense-in-depth: Verify Jev selected strictly from legal allowed_actions
        if selected_skill not in legal_result.allowed_actions:
            return AskLightRecommendation(
                status=legal_result.status,
                primary_skill=baseline_skill,
                alternative_skill=None,
                target_item=legal_result.target_item,
                confidence=None,
                probabilities={},
                semantic_judgments=semantic_judgments,
                fallback_used=True,
                fallback_reason=f"Jev selected unauthorized action '{selected_skill}' not in allowed set.",
                fail_closed=legal_result.fail_closed,
                justification=f"Jev unauthorized action prevented; defaulted to legal action {baseline_skill}.",
            )

        # Escalation policy check: high ambiguity + escalation signal
        escalated = False
        escalation_reason = None
        if escalation_prob >= ESCALATION_THRESHOLD:
            escalated = True
            escalation_reason = f"High reasoning escalation need detected (p={escalation_prob:.2f})."

        # Material ambiguity routing: if high ambiguity detected and clarify is an option
        if ambiguity_prob >= AMBIGUITY_THRESHOLD and "project-clarify" in legal_result.allowed_actions:
            selected_skill = "project-clarify"

        # Execution intent detection: promote status to TRANSITION if user explicitly requested execution
        final_status = legal_result.status
        if wants_exec_prob >= EXECUTION_INTENT_THRESHOLD and legal_result.status == "RECOMMEND":
            final_status = "TRANSITION"

        # Calibrated uncertainty threshold policy check
        if confidence < confidence_threshold:
            return AskLightRecommendation(
                status=final_status,
                primary_skill=baseline_skill,
                alternative_skill=selected_skill if selected_skill != baseline_skill else None,
                target_item=legal_result.target_item,
                confidence=confidence,
                probabilities=probabilities,
                semantic_judgments=semantic_judgments,
                fallback_used=True,
                fallback_reason=f"Jev confidence {confidence:.2f} below threshold {confidence_threshold:.2f}.",
                escalated=escalated,
                escalation_reason=escalation_reason,
                fail_closed=legal_result.fail_closed,
                justification=f"Borderline Jev confidence ({confidence:.2f}); safely preserved baseline {baseline_skill}.",
            )

        # Success: Bounded Jev judgment accepted
        justification_msg = (
            f"Jev selected {selected_skill} (confidence {confidence:.2f}) from legal candidates."
        )
        if escalated:
            justification_msg += f" Note: Escalation recommended ({escalation_reason})."

        return AskLightRecommendation(
            status=final_status,
            primary_skill=selected_skill,
            alternative_skill=None,
            target_item=legal_result.target_item,
            confidence=confidence,
            probabilities=probabilities,
            semantic_judgments=semantic_judgments,
            fallback_used=False,
            fallback_reason=None,
            escalated=escalated,
            escalation_reason=escalation_reason,
            fail_closed=legal_result.fail_closed,
            justification=justification_msg,
        )

    except Exception as exc:
        # Graceful fallback on any API / network / auth failure
        return AskLightRecommendation(
            status=legal_result.status,
            primary_skill=baseline_skill,
            alternative_skill=None,
            target_item=legal_result.target_item,
            confidence=None,
            probabilities={},
            fallback_used=True,
            fallback_reason=f"Jev call failed ({type(exc).__name__}: {exc}); fell back to deterministic baseline.",
            fail_closed=legal_result.fail_closed,
            justification=baseline_justification,
        )
