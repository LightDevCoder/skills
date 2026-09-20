"""Abstract task profiler extracting configuration intent without hardcoding model names.

Profiles work items into abstract tiers (routine, standard, high) and reasoning needs (low, medium, high).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Tuple

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
    from .agent_config_models import AbstractTaskProfile, DimensionProvenance, TaskCharacteristics
except ImportError:
    from agent_config_models import AbstractTaskProfile, DimensionProvenance, TaskCharacteristics

# Semantic Acceptance and Downgrade Policy (PROVISIONAL)
# Capability tier ranks for direction evaluation
TIER_RANKS: Dict[str, int] = {"routine": 1, "standard": 2, "high": 3}
REASONING_RANKS: Dict[str, int] = {"low": 1, "medium": 2, "high": 3}

# Upgrades allocate more capability/safety (safe failure direction) -> standard threshold
UPGRADE_CONFIDENCE_THRESHOLD: float = 0.50
# Holds preserve heuristic baseline -> standard threshold
HOLD_CONFIDENCE_THRESHOLD: float = 0.50
# Downgrades reduce capability tier below baseline (unsafe failure direction) -> requires stronger evidence
DOWNGRADE_CONFIDENCE_THRESHOLD: float = 0.75
# Downgrades must not hover on the tier discretization boundary unless confidence is very high (>= 0.85)
DOWNGRADE_MARGIN: float = 0.15


def build_deterministic_profile(task: TaskCharacteristics) -> AbstractTaskProfile:
    """Deterministic fallback mapping of task characteristics to abstract profile.

    Separates capability requirement from cost preference:
    Difficulty maps directly to capability tier and reasoning need;
    cost sensitivity does NOT downgrade capability tier or reasoning need.
    Preserves authoritative provenance for explicit user, verified ticket, or policy inputs.
    """
    if task.difficulty in ["high", "critical"]:
        rec_tier = "high"
        reasoning = "high"
    elif task.difficulty == "routine":
        rec_tier = "routine"
        reasoning = "low"
    else:
        rec_tier = "standard"
        reasoning = "medium"

    lat_sens = "high" if task.latency_sensitive else "medium"
    cost_sens = "high" if task.cost_sensitive else "medium"

    is_comp_auth = task.difficulty_source not in ("unknown", "heuristic") and bool(task.difficulty)
    comp_src = task.difficulty_source if is_comp_auth else "deterministic-fallback"
    comp_fallback = not is_comp_auth

    is_reas_auth = bool(task.reasoning_policy)
    if is_reas_auth:
        if task.reasoning_policy in ("highest-supported", "high"):
            reasoning = "high"
        elif task.reasoning_policy in ("minimal", "low"):
            reasoning = "low"
        else:
            reasoning = "medium"
        reas_src = "explicit-policy"
        reas_fallback = False
    else:
        reas_src = "deterministic-fallback"
        reas_fallback = True

    prov = {
        "complexity": DimensionProvenance(
            dimension="complexity",
            value=task.difficulty,
            source=comp_src,
            fallback_used=comp_fallback,
            fallback_reason=None if is_comp_auth else "Deterministic fallback baseline",
        ),
        "reasoning": DimensionProvenance(
            dimension="reasoning",
            value=reasoning,
            source=reas_src,
            fallback_used=reas_fallback,
            fallback_reason=None if is_reas_auth else "Deterministic fallback baseline",
        ),
        "tier": DimensionProvenance(
            dimension="tier",
            value=rec_tier,
            source=comp_src,
            fallback_used=comp_fallback,
            fallback_reason=None if is_comp_auth else "Deterministic fallback baseline",
        ),
    }

    return AbstractTaskProfile(
        complexity_level=task.difficulty,
        reasoning_need=reasoning,
        latency_sensitivity=lat_sens,
        cost_sensitivity=cost_sens,
        recommended_tier=rec_tier,
        dimension_provenance=prov,
    )


def extract_abstract_task_profile(
    task: TaskCharacteristics,
    client: Optional[Any] = None,
    use_jev: bool = True,
    project_root: Optional[Path] = None,
) -> Tuple[AbstractTaskProfile, Optional[float], bool, Optional[str]]:
    """Extract abstract configuration intent using Jev Score with true per-dimension fallback.

    Uses Score primitive for ordered dimensions (complexity and reasoning_need).
    Enforces independent per-dimension confidence evaluation and preserves provenance.

    Core responsibility boundary:
      - If task.difficulty is authoritative (source != 'unknown'), complexity is owned by code.
        Do NOT send task_complexity to Jev; Jev state never contains declared_difficulty.
      - If task.reasoning_policy is explicit, reasoning is owned by code/policy.
        Do NOT send reasoning_need to Jev.
      - If both are authoritative, return immediately without Jev invocation.

    Returns:
      (profile, overall_confidence, fallback_used, fallback_reason)
    """
    is_complexity_authoritative = (
        task.difficulty_source not in ("unknown", "heuristic")
        and bool(task.difficulty)
    )
    is_reasoning_authoritative = bool(task.reasoning_policy)

    # 1. If both dimensions are authoritative, deterministic code handles everything with 0 Jev calls
    if is_complexity_authoritative and is_reasoning_authoritative:
        det_prof = build_deterministic_profile(task)
        return det_prof, None, False, None

    # 2. Check Jev prerequisites
    api_key, _ = resolve_typesafe_key(project_root)
    if not use_jev or not TYPESAFE_AVAILABLE or not api_key:
        det_prof = build_deterministic_profile(task)
        return det_prof, None, True, "Jev disabled or API key unavailable"

    # 3. Construct label-clean Jev state (NO declared_difficulty, NO ground truth labels!)
    state = {
        "task_title": task.title,
        "task_description": task.description,
        "cost_sensitive": task.cost_sensitive,
        "latency_sensitive": task.latency_sensitive,
    }

    # 4. Construct questions only for dimensions needing semantic evaluation
    questions: Dict[str, Score] = {}
    if not is_complexity_authoritative:
        questions["task_complexity"] = Score(
            instructions="How complex is the implementation work described in this task?",
            criteria=[
                "Routine: Simple typos, formatting, minor documentation, or repetitive low-risk edits",
                "Standard: Standard feature implementation, UI Polish, or typical application logic",
                "Complex: Multi-module coordination, complex state management, or algorithmic work",
                "Critical: System-wide architectural overhaul, security-critical paths, or high-concurrency invariants",
            ],
        )
    if not is_reasoning_authoritative:
        questions["reasoning_need"] = Score(
            instructions="What level of reasoning effort is required for this task?",
            criteria=[
                "Low: Minimal reasoning, straightforward coding, or template filling",
                "Medium: Standard programming reasoning, trade-off evaluation, and component composition",
                "High: Deep architectural analysis, multi-system coordination, or subtle edge case handling",
            ],
        )

    try:
        ts_client = client or TypeSafeClient(api_key=api_key)
        response = ts_client.system_one(state=state, questions=questions)

        comp_score_val: Optional[float] = None
        comp_conf: Optional[float] = None
        reas_score_val: Optional[float] = None
        reas_conf: Optional[float] = None

        # Check for Score answers
        scores_dict = getattr(response, "scores", None)
        choices_dict = getattr(response, "choices", None)

        if isinstance(scores_dict, dict) and scores_dict:
            score_comp = scores_dict.get("task_complexity")
            score_reas = scores_dict.get("reasoning_need")

            if score_comp and hasattr(score_comp, "score") and isinstance(score_comp.score, (int, float)):
                comp_score_val = float(score_comp.score)
                comp_conf = float(score_comp.confidence) if hasattr(score_comp, "confidence") and isinstance(score_comp.confidence, (int, float)) else 1.0

            if score_reas and hasattr(score_reas, "score") and isinstance(score_reas.score, (int, float)):
                reas_score_val = float(score_reas.score)
                reas_conf = float(score_reas.confidence) if hasattr(score_reas, "confidence") and isinstance(score_reas.confidence, (int, float)) else 1.0

        # Backwards compatibility check for Choice answers if provided by older mocks
        elif isinstance(choices_dict, dict) and choices_dict:
            tier_ans = choices_dict.get("task_complexity") or choices_dict.get("recommended_tier")
            reasoning_ans = choices_dict.get("reasoning_need")
            if tier_ans and hasattr(tier_ans, "choice"):
                comp_score_val = 0.0 if tier_ans.choice == "routine" else (1.0 if tier_ans.choice == "standard" else 2.0)
                comp_conf = float(tier_ans.confidence) if hasattr(tier_ans, "confidence") and isinstance(tier_ans.confidence, (int, float)) else 1.0
            if reasoning_ans and hasattr(reasoning_ans, "choice"):
                reas_score_val = 0.0 if reasoning_ans.choice == "low" else (1.0 if reasoning_ans.choice == "medium" else 2.0)
                reas_conf = float(reasoning_ans.confidence) if hasattr(reasoning_ans, "confidence") and isinstance(reasoning_ans.confidence, (int, float)) else 1.0

        prov: Dict[str, DimensionProvenance] = {}
        fallback_dims: List[str] = []
        reported_confs: List[float] = []

        # Process Complexity dimension:
        # Discretization Mapping:
        #   [0.0, 0.5) -> routine (rec_tier: routine)
        #   [0.5, 1.5) -> standard (rec_tier: standard)
        #   [1.5, 2.5) -> high (rec_tier: high)
        #   [2.5, 3.0] -> critical (rec_tier: high)
        comp_fallback = False
        if is_complexity_authoritative:
            comp_level = task.difficulty
            rec_tier = "high" if comp_level in ("high", "critical") else ("routine" if comp_level == "routine" else "standard")
            prov["complexity"] = DimensionProvenance(
                dimension="complexity",
                value=comp_level,
                confidence=None,
                source=task.difficulty_source,
                fallback_used=False,
            )
            prov["tier"] = DimensionProvenance(
                dimension="tier",
                value=rec_tier,
                confidence=None,
                source=task.difficulty_source,
                fallback_used=False,
            )
        else:
            det_base = build_deterministic_profile(task)
            baseline_tier = det_base.recommended_tier
            baseline_level = det_base.complexity_level

            if comp_score_val is not None and comp_conf is not None:
                # 1. Discretization mapping
                if comp_score_val < 0.5:
                    cand_level = "routine"
                    cand_tier = "routine"
                    boundary_dist = 0.5 - comp_score_val
                elif comp_score_val < 1.5:
                    cand_level = "standard"
                    cand_tier = "standard"
                    boundary_dist = min(comp_score_val - 0.5, 1.5 - comp_score_val)
                elif comp_score_val < 2.5:
                    cand_level = "high"
                    cand_tier = "high"
                    boundary_dist = min(comp_score_val - 1.5, 2.5 - comp_score_val)
                else:
                    cand_level = "critical"
                    cand_tier = "high"
                    boundary_dist = comp_score_val - 2.5

                # 2. Evaluate direction relative to baseline: UPGRADE, HOLD, or DOWNGRADE
                cand_rank = TIER_RANKS[cand_tier]
                base_rank = TIER_RANKS[baseline_tier]

                if cand_rank > base_rank:
                    # UPGRADE: allocating higher capability tier (safe failure direction)
                    accepted = comp_conf >= UPGRADE_CONFIDENCE_THRESHOLD
                    rejection_reason = f"Upgrade to {cand_tier} rejected: confidence {comp_conf:.2f} < {UPGRADE_CONFIDENCE_THRESHOLD:.2f}"
                elif cand_rank == base_rank:
                    # HOLD: preserving baseline capability tier
                    accepted = comp_conf >= HOLD_CONFIDENCE_THRESHOLD
                    rejection_reason = f"Hold at {cand_tier} rejected: confidence {comp_conf:.2f} < {HOLD_CONFIDENCE_THRESHOLD:.2f}"
                else:
                    # DOWNGRADE: reducing capability tier below baseline (unsafe failure direction)
                    # Downgrade policy (PROVISIONAL): Requires stronger evidence to prevent under-powering tasks.
                    strong_confidence = comp_conf >= DOWNGRADE_CONFIDENCE_THRESHOLD
                    strong_margin = (boundary_dist >= DOWNGRADE_MARGIN) or (comp_conf >= 0.85)
                    accepted = strong_confidence and strong_margin
                    rejection_reason = (
                        f"Downgrade from {baseline_tier} to {cand_tier} rejected: "
                        f"confidence {comp_conf:.2f} < {DOWNGRADE_CONFIDENCE_THRESHOLD:.2f} or "
                        f"boundary margin {boundary_dist:.2f} < {DOWNGRADE_MARGIN:.2f} (policy: PROVISIONAL)"
                    )

                if accepted:
                    reported_confs.append(comp_conf)
                    comp_level = cand_level
                    rec_tier = cand_tier
                    prov["complexity"] = DimensionProvenance(
                        dimension="complexity",
                        value=comp_level,
                        confidence=comp_conf,
                        source="jev",
                        fallback_used=False,
                    )
                    prov["tier"] = DimensionProvenance(
                        dimension="tier",
                        value=rec_tier,
                        confidence=comp_conf,
                        source="jev",
                        fallback_used=False,
                    )
                else:
                    comp_fallback = True
                    fallback_dims.append("complexity")
                    comp_level = baseline_level
                    rec_tier = baseline_tier
                    prov["complexity"] = DimensionProvenance(
                        dimension="complexity",
                        value=comp_level,
                        confidence=comp_conf,
                        source="deterministic-fallback",
                        fallback_used=True,
                        fallback_reason=rejection_reason,
                    )
                    prov["tier"] = DimensionProvenance(
                        dimension="tier",
                        value=rec_tier,
                        confidence=comp_conf,
                        source="deterministic-fallback",
                        fallback_used=True,
                        fallback_reason=rejection_reason,
                    )
            else:
                comp_fallback = True
                fallback_dims.append("complexity")
                comp_level = baseline_level
                rec_tier = baseline_tier
                reason_msg = "Jev score or confidence missing"
                prov["complexity"] = DimensionProvenance(
                    dimension="complexity",
                    value=comp_level,
                    confidence=comp_conf,
                    source="deterministic-fallback",
                    fallback_used=True,
                    fallback_reason=reason_msg,
                )
                prov["tier"] = DimensionProvenance(
                    dimension="tier",
                    value=rec_tier,
                    confidence=comp_conf,
                    source="deterministic-fallback",
                    fallback_used=True,
                    fallback_reason=reason_msg,
                )

        # Process Reasoning dimension:
        # Discretization Mapping:
        #   [0.0, 0.5) -> low
        #   [0.5, 1.5) -> medium
        #   [1.5, 2.0] -> high
        reas_fallback = False
        if is_reasoning_authoritative:
            if task.reasoning_policy in ("highest-supported", "high"):
                reasoning_need = "high"
            elif task.reasoning_policy in ("minimal", "low"):
                reasoning_need = "low"
            else:
                reasoning_need = "medium"
            prov["reasoning"] = DimensionProvenance(
                dimension="reasoning",
                value=reasoning_need,
                confidence=None,
                source="explicit-policy",
                fallback_used=False,
            )
        else:
            det_base_reas = build_deterministic_profile(task)
            baseline_reas = det_base_reas.reasoning_need

            if reas_conf is not None and reas_score_val is not None:
                if reas_score_val < 0.5:
                    cand_reas = "low"
                    boundary_dist_reas = 0.5 - reas_score_val
                elif reas_score_val < 1.5:
                    cand_reas = "medium"
                    boundary_dist_reas = min(reas_score_val - 0.5, 1.5 - reas_score_val)
                else:
                    cand_reas = "high"
                    boundary_dist_reas = reas_score_val - 1.5

                cand_rank_reas = REASONING_RANKS[cand_reas]
                base_rank_reas = REASONING_RANKS[baseline_reas]

                if cand_rank_reas > base_rank_reas:
                    accepted_reas = reas_conf >= UPGRADE_CONFIDENCE_THRESHOLD
                    rejection_reason_reas = f"Upgrade reasoning to {cand_reas} rejected: confidence {reas_conf:.2f} < {UPGRADE_CONFIDENCE_THRESHOLD:.2f}"
                elif cand_rank_reas == base_rank_reas:
                    accepted_reas = reas_conf >= HOLD_CONFIDENCE_THRESHOLD
                    rejection_reason_reas = f"Hold reasoning at {cand_reas} rejected: confidence {reas_conf:.2f} < {HOLD_CONFIDENCE_THRESHOLD:.2f}"
                else:
                    strong_confidence_reas = reas_conf >= DOWNGRADE_CONFIDENCE_THRESHOLD
                    strong_margin_reas = (boundary_dist_reas >= DOWNGRADE_MARGIN) or (reas_conf >= 0.85)
                    accepted_reas = strong_confidence_reas and strong_margin_reas
                    rejection_reason_reas = (
                        f"Downgrade reasoning from {baseline_reas} to {cand_reas} rejected: "
                        f"confidence {reas_conf:.2f} < {DOWNGRADE_CONFIDENCE_THRESHOLD:.2f} or "
                        f"boundary margin {boundary_dist_reas:.2f} < {DOWNGRADE_MARGIN:.2f} (policy: PROVISIONAL)"
                    )

                if accepted_reas:
                    reported_confs.append(reas_conf)
                    reasoning_need = cand_reas
                    prov["reasoning"] = DimensionProvenance(
                        dimension="reasoning",
                        value=reasoning_need,
                        confidence=reas_conf,
                        source="jev",
                        fallback_used=False,
                    )
                else:
                    reas_fallback = True
                    fallback_dims.append("reasoning")
                    reasoning_need = baseline_reas
                    prov["reasoning"] = DimensionProvenance(
                        dimension="reasoning",
                        value=reasoning_need,
                        confidence=reas_conf,
                        source="deterministic-fallback",
                        fallback_used=True,
                        fallback_reason=rejection_reason_reas,
                    )
            else:
                reas_fallback = True
                fallback_dims.append("reasoning")
                det_base = build_deterministic_profile(task)
                reasoning_need = det_base.reasoning_need
                reason_msg = f"Jev confidence {reas_conf:.2f} < 0.50" if reas_conf is not None else "Jev score missing"
                prov["reasoning"] = DimensionProvenance(
                    dimension="reasoning",
                    value=reasoning_need,
                    confidence=reas_conf,
                    source="deterministic-fallback",
                    fallback_used=True,
                    fallback_reason=reason_msg,
                )

        any_fallback = comp_fallback or reas_fallback
        fallback_reason = f"Per-dimension fallback on: {', '.join(fallback_dims)}" if any_fallback else None
        overall_conf = min(reported_confs) if reported_confs else None

        profile = AbstractTaskProfile(
            complexity_level=comp_level,
            complexity_score=comp_score_val,
            complexity_confidence=comp_conf,
            reasoning_need=reasoning_need,
            reasoning_score=reas_score_val,
            reasoning_confidence=reas_conf,
            latency_sensitivity="high" if task.latency_sensitive else "medium",
            cost_sensitivity="high" if task.cost_sensitive else "medium",
            recommended_tier=rec_tier,
            dimension_provenance=prov,
        )
        return profile, overall_conf, any_fallback, fallback_reason

    except Exception as exc:
        det_prof = build_deterministic_profile(task)
        prov = det_prof.dimension_provenance
        if not is_complexity_authoritative:
            prov["complexity"].fallback_reason = f"Jev call failed ({type(exc).__name__}: {exc})"
            prov["tier"].fallback_reason = f"Jev call failed ({type(exc).__name__}: {exc})"
        if not is_reasoning_authoritative:
            prov["reasoning"].fallback_reason = f"Jev call failed ({type(exc).__name__}: {exc})"
        return det_prof, None, True, f"Jev call failed ({type(exc).__name__}: {exc})"
