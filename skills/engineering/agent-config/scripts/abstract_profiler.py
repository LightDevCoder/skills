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


def build_deterministic_profile(task: TaskCharacteristics) -> AbstractTaskProfile:
    """Deterministic fallback mapping of task characteristics to abstract profile.

    Separates capability requirement from cost preference:
    Difficulty maps directly to capability tier and reasoning need;
    cost sensitivity does NOT downgrade capability tier or reasoning need.
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

    prov = {
        "complexity": DimensionProvenance(
            dimension="complexity",
            value=task.difficulty,
            source="deterministic-fallback",
            fallback_used=True,
            fallback_reason="Deterministic fallback baseline",
        ),
        "reasoning": DimensionProvenance(
            dimension="reasoning",
            value=reasoning,
            source="deterministic-fallback",
            fallback_used=True,
            fallback_reason="Deterministic fallback baseline",
        ),
        "tier": DimensionProvenance(
            dimension="tier",
            value=rec_tier,
            source="deterministic-fallback",
            fallback_used=True,
            fallback_reason="Deterministic fallback baseline",
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
    Returns:
      (profile, overall_confidence, fallback_used, fallback_reason)
    """
    api_key, _ = resolve_typesafe_key(project_root)
    if not use_jev or not TYPESAFE_AVAILABLE or not api_key:
        return build_deterministic_profile(task), None, True, "Jev disabled or API key unavailable"

    state = {
        "task_title": task.title,
        "task_description": task.description,
        "cost_sensitive": task.cost_sensitive,
        "latency_sensitive": task.latency_sensitive,
        "declared_difficulty": task.difficulty,
    }

    questions = {
        "task_complexity": Score(
            instructions="How complex is the implementation work described in this task?",
            criteria=[
                "Routine: Simple typos, formatting, minor documentation, or repetitive low-risk edits",
                "Standard: Standard feature implementation, UI Polish, or typical application logic",
                "Complex: Multi-module coordination, complex state management, or algorithmic work",
                "Critical: System-wide architectural overhaul, security-critical paths, or high-concurrency invariants",
            ],
        ),
        "reasoning_need": Score(
            instructions="What level of reasoning effort is required for this task?",
            criteria=[
                "Low: Minimal reasoning, straightforward coding, or template filling",
                "Medium: Standard programming reasoning, trade-off evaluation, and component composition",
                "High: Deep architectural analysis, multi-system coordination, or subtle edge case handling",
            ],
        ),
    }

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

        if comp_conf is None and reas_conf is None:
            raise ValueError("Incomplete answers received from Jev")

        prov: Dict[str, DimensionProvenance] = {}
        fallback_dims: List[str] = []

        # True per-dimension fallback for complexity dimension:
        # Score Discretization Mapping:
        #   [0.0, 0.5) -> routine (rec_tier: routine)
        #   [0.5, 1.5) -> standard (rec_tier: standard)
        #   [1.5, 2.5) -> high (rec_tier: high)
        #   [2.5, 3.0] -> critical (rec_tier: high)
        comp_fallback = False
        if comp_conf is not None and comp_conf >= 0.50 and comp_score_val is not None:
            if comp_score_val < 0.5:
                comp_level = "routine"
                rec_tier = "routine"
            elif comp_score_val < 1.5:
                comp_level = "standard"
                rec_tier = "standard"
            elif comp_score_val < 2.5:
                comp_level = "high"
                rec_tier = "high"
            else:
                comp_level = "critical"
                rec_tier = "high"
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
            det_base = build_deterministic_profile(task)
            comp_level = det_base.complexity_level
            rec_tier = det_base.recommended_tier
            reason_msg = f"Jev confidence {comp_conf:.2f} < 0.50" if comp_conf is not None else "Jev score missing"
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

        # True per-dimension fallback for reasoning dimension:
        # Score Discretization Mapping:
        #   [0.0, 0.5) -> low
        #   [0.5, 1.5) -> medium
        #   [1.5, 2.0] -> high
        reas_fallback = False
        if reas_conf is not None and reas_conf >= 0.50 and reas_score_val is not None:
            if reas_score_val < 0.5:
                reasoning_need = "low"
            elif reas_score_val < 1.5:
                reasoning_need = "medium"
            else:
                reasoning_need = "high"
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

        reported_confs = [c for c in (comp_conf, reas_conf) if c is not None]
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
        fallback_profile = build_deterministic_profile(task)
        return fallback_profile, None, True, f"Jev call failed ({type(exc).__name__}: {exc})"
