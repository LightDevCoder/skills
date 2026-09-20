"""Bounded Jev multi-primitive semantic router for ask-light.

Connects TypeSafe Jev System One judgments with deterministic fallbacks:
  1. Choice: Constrained strictly to code-computed legal candidates when >1 candidate exists.
  2. Noul: Execution intent calibration (advisory only; never grants transition authority) & ambiguity detection.
  3. Conditional query planning: Skips Choice for singleton candidate sets; tracks query reasons.
  4. Defense-in-depth: Unauthorized selections rejected; fails closed on hard bounds.
  5. Soft dependency: Graceful fallback when typesafe-sdk is not installed or TYPESAFE_API_KEY is unset.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

def resolve_typesafe_key(project_root: Optional[Path] = None) -> tuple[Optional[str], str]:
    """Canonical credential resolution for TypeSafe API key.

    Order:
      1. Current process environment: os.environ["TYPESAFE_API_KEY"]
      2. Explicit active project .env (parsed line-by-line, no python-dotenv dependency)
      3. Unavailable (None, "missing")

    Never scans arbitrary parents or unrelated current-working-directory .env files.
    """
    env_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if env_key:
        return env_key, "os.environ"

    if project_root is not None:
        env_path = project_root / ".env"
        if env_path.is_file():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() == "TYPESAFE_API_KEY":
                        clean_v = v.strip().strip("'\"")
                        if clean_v:
                            return clean_v, ".env"
            except Exception:
                pass

    return None, "missing"


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
    from .ask_light_models import (
        AskLightRecommendation,
        JevPolicy,
        LegalActionsResult,
        SemanticJudgments,
    )
except ImportError:
    from compact_state_builder import build_compact_jev_state
    from ask_light_models import (
        AskLightRecommendation,
        JevPolicy,
        LegalActionsResult,
        SemanticJudgments,
    )

DEFAULT_POLICY = JevPolicy()


def plan_semantic_queries(
    legal_result: LegalActionsResult,
    user_request: str,
    enable_expanded_judgments: bool = True,
) -> tuple[Dict[str, Any], List[str], Dict[str, str]]:
    """Plan minimal necessary Jev questions based on deterministic facts and request phrasing.

    Invariants:
      1. Non-executable queries (BLOCKED, NEED_INPUT, EXPLAIN) send 0 questions.
      2. Choice is sent ONLY when len(allowed_actions) > 1.
      3. Ambiguity Noul is sent ONLY when clarify is legal or user phrasing contains ambiguity signals.
      4. Escalation Noul is sent ONLY when implement is legal and task complexity warrants agent-config.
      5. Execution intent Noul is sent ONLY when presentation wording benefits from advisory intent.
    """
    questions: Dict[str, Any] = {}
    questions_sent: List[str] = []
    reasons_needed: Dict[str, str] = {}

    req_lower = user_request.lower()

    # 1. Choice: Multiple legal alternatives
    if len(legal_result.allowed_actions) > 1:
        criteria = {
            action: legal_result.candidate_descriptions.get(action, f"Execute {action} workflow step")
            for action in legal_result.allowed_actions
        }
        questions["next_action"] = Choice(
            instructions="Which legal workflow action best matches the user intent and project evidence?",
            criteria=criteria,
        )
        questions_sent.append("next_action")
        reasons_needed["next_action"] = "Multiple legal candidate actions available; semantic preference needed."

    if not enable_expanded_judgments:
        return questions, questions_sent, reasons_needed

    # 2. Material Ambiguity
    ambiguity_keywords = ["maybe", "perhaps", " or ", "not sure", "whether", "should we", "tradeoff", "redesign", "unclear", "ambiguous", "confused"]
    has_ambiguity_phrasing = any(kw in req_lower for kw in ambiguity_keywords)
    clarify_relevant = "project-clarify" in legal_result.allowed_actions
    if clarify_relevant or has_ambiguity_phrasing:
        questions["has_material_ambiguity"] = Noul(
            instructions="Does the request or project state have material ambiguity or unsettled decisions requiring clarification?",
        )
        questions_sent.append("has_material_ambiguity")
        reasons_needed["has_material_ambiguity"] = "Detect semantic ambiguity or conflicting requirements requiring clarification."

    # 3. Deep Reasoning Escalation
    complexity_keywords = [
        "architecture", "overhaul", "distributed", "consensus", "raft", "concurrency",
        "lock-free", "refactor", "security", "cryptographic", "rework", "performance",
    ]
    has_complexity_phrasing = any(kw in req_lower for kw in complexity_keywords)
    implement_relevant = "implement" in legal_result.allowed_actions
    if implement_relevant and has_complexity_phrasing:
        questions["needs_deep_reasoning_escalation"] = Noul(
            instructions="Does this request involve high architectural complexity or conflicting requirements requiring deep reasoning escalation rather than fast routing?",
        )
        questions_sent.append("needs_deep_reasoning_escalation")
        reasons_needed["needs_deep_reasoning_escalation"] = "Assess whether implementation task warrants reasoning escalation to agent-config."

    # 4. Immediate Execution Intent
    if legal_result.status == "RECOMMEND":
        exec_keywords = ["start", "go ahead", "run", "do it", "execute", "implement", "now", "开始", "执行", "should we"]
        if any(kw in req_lower for kw in exec_keywords):
            questions["wants_immediate_execution"] = Noul(
                instructions=(
                    "Does the user request command or authorize immediate execution right now "
                    "(e.g. '立刻开始', 'go ahead and run it', 'start executing now'), "
                    "as opposed to asking a question, asking for advice, or asking for confirmation "
                    "(e.g. '现在开始做吗？', '下一步做什么？', 'what should I do next?')?"
                ),
            )
            questions_sent.append("wants_immediate_execution")
            reasons_needed["wants_immediate_execution"] = "Assess user execution intent probability for advisory presentation."

    return questions, questions_sent, reasons_needed


def route_with_jev(
    legal_result: LegalActionsResult,
    user_request: str,
    client: Optional[Any] = None,
    confidence_threshold: Optional[float] = None,
    policy: Optional[JevPolicy] = None,
    enable_expanded_judgments: bool = True,
    shadow_mode: bool = False,
    project_root: Optional[Path] = None,
) -> AskLightRecommendation:
    """Judge legal candidate actions using bounded Jev semantic primitives with calibrated fallback.

    Invariants:
      1. Never called if legal_result is BLOCKED, NEED_INPUT, or EXPLAIN.
      2. Choice is invoked ONLY when len(allowed_actions) > 1. Singleton candidates skip Choice.
      3. Jev output CANNOT grant transition authority (final_status remains legal_result.status).
      4. Degrades gracefully to explicit fallback_action on error, low confidence, or missing credentials.
      5. Calibrated uncertainty policy governs escalation and fallbacks.
    """
    effective_policy = policy or DEFAULT_POLICY
    min_choice_conf = confidence_threshold if confidence_threshold is not None else effective_policy.action_choice_min_confidence

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

    # Baseline deterministic action (explicit fallback_action preferred over list order)
    baseline_skill = legal_result.fallback_action or legal_result.allowed_actions[0]
    baseline_justification = f"Deterministic baseline selected {baseline_skill} from legal candidates."

    # If TypeSafe is not installed or no API key, fall back immediately
    api_key, _ = resolve_typesafe_key(project_root)
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

    # Query planning: Only ask what is needed
    questions, questions_sent, reasons_needed = plan_semantic_queries(
        legal_result,
        user_request,
        enable_expanded_judgments=enable_expanded_judgments,
    )
    need_choice = "next_action" in questions

    # If query planning determined zero semantic questions needed, return deterministic baseline
    if not questions:
        return AskLightRecommendation(
            status=legal_result.status,
            primary_skill=baseline_skill,
            alternative_skill=None,
            target_item=legal_result.target_item,
            confidence=1.0,
            probabilities={baseline_skill: 1.0},
            semantic_judgments=SemanticJudgments(
                action_choice=None,
                action_confidence=None,
                action_probabilities={},
                questions_sent=[],
                reason_each_question_needed={},
            ),
            fallback_used=False,
            fallback_reason=None,
            fail_closed=legal_result.fail_closed,
            justification=f"Deterministic action {baseline_skill} selected; query planner determined zero semantic queries needed.",
        )

    try:
        ts_client = client or TypeSafeClient(api_key=api_key)
        response = ts_client.system_one(state=compact_state, questions=questions)

        if need_choice:
            choice_ans = response.choices.get("next_action")
            if not choice_ans:
                raise ValueError("Choice answer 'next_action' missing from Jev response")
            selected_skill = choice_ans.choice
            confidence = choice_ans.confidence
            probabilities = dict(choice_ans.probabilities)
        else:
            selected_skill = baseline_skill
            confidence = 1.0
            probabilities = {baseline_skill: 1.0}

        wants_exec_prob = 0.0
        ambiguity_prob = 0.0
        escalation_prob = 0.0

        if enable_expanded_judgments and hasattr(response, "nouls") and response.nouls:
            noul_exec = response.nouls.get("wants_immediate_execution")
            noul_ambig = response.nouls.get("has_material_ambiguity")
            noul_escala = response.nouls.get("needs_deep_reasoning_escalation")

            if noul_exec and hasattr(noul_exec, "noul") and isinstance(noul_exec.noul, (int, float)):
                wants_exec_prob = float(noul_exec.noul)
            if noul_ambig and hasattr(noul_ambig, "noul") and isinstance(noul_ambig.noul, (int, float)):
                ambiguity_prob = float(noul_ambig.noul)
            if noul_escala and hasattr(noul_escala, "noul") and isinstance(noul_escala.noul, (int, float)):
                escalation_prob = float(noul_escala.noul)

        semantic_judgments = SemanticJudgments(
            action_choice=selected_skill if need_choice else None,
            action_confidence=confidence if need_choice else None,
            action_probabilities=probabilities if need_choice else {},
            execution_intent_probability=wants_exec_prob,
            ambiguity_probability=ambiguity_prob,
            escalation_probability=escalation_prob,
            questions_sent=questions_sent,
            reason_each_question_needed=reasons_needed,
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

        # Escalation policy check: high complexity/escalation signal
        escalated = False
        escalation_reason = None
        alternative_skill = None
        if escalation_prob >= effective_policy.escalation_threshold:
            escalated = True
            escalation_reason = f"High reasoning escalation need detected (p={escalation_prob:.2f})."
            if selected_skill == "implement":
                alternative_skill = "agent-config"

        # Material ambiguity routing: if high ambiguity detected and clarify is an option
        if ambiguity_prob >= effective_policy.ambiguity_threshold and "project-clarify" in legal_result.allowed_actions:
            selected_skill = "project-clarify"

        # HARD INVARIANT (Section 12): Jev output cannot grant TRANSITION authority!
        # Transition authority requires deterministic authorization (e.g. explicit command).
        final_status = legal_result.status
        intent_note = ""
        if wants_exec_prob >= effective_policy.execution_intent_threshold and legal_result.status == "RECOMMEND":
            intent_note = f" (Execution intent noted p={wants_exec_prob:.2f}; awaiting explicit command or confirmed approval)."

        # Shadow mode evaluation: record judgments, return deterministic baseline
        if shadow_mode:
            return AskLightRecommendation(
                status=legal_result.status,
                primary_skill=baseline_skill,
                alternative_skill=alternative_skill,
                target_item=legal_result.target_item,
                confidence=confidence,
                probabilities=probabilities,
                semantic_judgments=semantic_judgments,
                fallback_used=False,
                fallback_reason="Shadow mode: deterministic baseline returned; Jev judgments recorded.",
                escalated=escalated,
                escalation_reason=escalation_reason,
                fail_closed=legal_result.fail_closed,
                justification=f"Shadow mode active: baseline {baseline_skill} retained (Jev judged {selected_skill}).",
            )

        # Calibrated uncertainty threshold policy check for Choice
        if need_choice and confidence < min_choice_conf:
            return AskLightRecommendation(
                status=final_status,
                primary_skill=baseline_skill,
                alternative_skill=selected_skill if selected_skill != baseline_skill else None,
                target_item=legal_result.target_item,
                confidence=confidence,
                probabilities=probabilities,
                semantic_judgments=semantic_judgments,
                fallback_used=True,
                fallback_reason=f"Jev confidence {confidence:.2f} below threshold {min_choice_conf:.2f}.",
                escalated=escalated,
                escalation_reason=escalation_reason,
                fail_closed=legal_result.fail_closed,
                justification=f"Borderline Jev confidence ({confidence:.2f}); safely preserved baseline {baseline_skill}.{intent_note}",
            )

        # Success: Bounded Jev judgment accepted
        if need_choice:
            justification_msg = f"Jev selected {selected_skill} (confidence {confidence:.2f}) from legal candidates.{intent_note}"
        else:
            justification_msg = f"Deterministic action {selected_skill} selected (single legal candidate).{intent_note}"

        if escalated:
            justification_msg += f" Note: Escalation recommended ({escalation_reason}); recommend higher reasoning effort or agent-config."

        return AskLightRecommendation(
            status=final_status,
            primary_skill=selected_skill,
            alternative_skill=alternative_skill,
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
