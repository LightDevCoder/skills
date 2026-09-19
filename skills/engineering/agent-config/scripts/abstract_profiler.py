"""Abstract task profiler extracting configuration intent without hardcoding model names.

Profiles work items into abstract tiers (routine, standard, high) and reasoning needs (low, medium, high).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Tuple

# Load .env safely only if present in explicit project root
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    dotenv_path = project_root / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path)
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
    from .agent_config_models import AbstractTaskProfile, TaskCharacteristics
except ImportError:
    from agent_config_models import AbstractTaskProfile, TaskCharacteristics


def build_deterministic_profile(task: TaskCharacteristics) -> AbstractTaskProfile:
    """Deterministic fallback mapping of task characteristics to abstract profile."""
    if task.cost_sensitive and task.difficulty in ["routine", "standard"]:
        rec_tier = "routine"
        reasoning = "low"
    elif task.difficulty in ["high", "critical"]:
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

    return AbstractTaskProfile(
        complexity_level=task.difficulty,
        reasoning_need=reasoning,
        latency_sensitivity=lat_sens,
        cost_sensitivity=cost_sens,
        recommended_tier=rec_tier,
    )


def extract_abstract_task_profile(
    task: TaskCharacteristics,
    client: Optional[Any] = None,
    use_jev: bool = True,
) -> Tuple[AbstractTaskProfile, Optional[float], bool, Optional[str]]:
    """Extract abstract configuration intent using Jev Score with deterministic fallback.

    Uses Score primitive for ordered dimensions (complexity and reasoning_need).
    Returns:
      (profile, confidence, fallback_used, fallback_reason)
    """
    if not use_jev or not TYPESAFE_AVAILABLE or not os.environ.get("TYPESAFE_API_KEY"):
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
        ts_client = client or TypeSafeClient()
        response = ts_client.system_one(state=state, questions=questions)

        comp_score_val: Optional[float] = None
        comp_conf: Optional[float] = None
        reas_score_val: Optional[float] = None
        reas_conf: Optional[float] = None

        rec_tier = "standard"
        comp_level = task.difficulty
        reasoning_need = "medium"

        # Check for Score answers
        scores_dict = getattr(response, "scores", None)
        choices_dict = getattr(response, "choices", None)

        if isinstance(scores_dict, dict) and scores_dict:
            score_comp = scores_dict.get("task_complexity")
            score_reas = scores_dict.get("reasoning_need")

            if score_comp and hasattr(score_comp, "score") and isinstance(score_comp.score, (int, float)):
                comp_score_val = float(score_comp.score)
                comp_conf = float(score_comp.confidence) if hasattr(score_comp, "confidence") and isinstance(score_comp.confidence, (int, float)) else 1.0

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

            if score_reas and hasattr(score_reas, "score") and isinstance(score_reas.score, (int, float)):
                reas_score_val = float(score_reas.score)
                reas_conf = float(score_reas.confidence) if hasattr(score_reas, "confidence") and isinstance(score_reas.confidence, (int, float)) else 1.0

                if reas_score_val < 0.5:
                    reasoning_need = "low"
                elif reas_score_val < 1.5:
                    reasoning_need = "medium"
                else:
                    reasoning_need = "high"

        # Backwards compatibility check for Choice answers if provided by older mocks
        elif isinstance(choices_dict, dict) and choices_dict:
            tier_ans = choices_dict.get("task_complexity") or choices_dict.get("recommended_tier")
            reasoning_ans = choices_dict.get("reasoning_need")
            if tier_ans and hasattr(tier_ans, "choice"):
                rec_tier = tier_ans.choice
                comp_level = task.difficulty
                comp_conf = float(tier_ans.confidence) if hasattr(tier_ans, "confidence") and isinstance(tier_ans.confidence, (int, float)) else 1.0
            if reasoning_ans and hasattr(reasoning_ans, "choice"):
                reasoning_need = reasoning_ans.choice
                reas_conf = float(reasoning_ans.confidence) if hasattr(reasoning_ans, "confidence") and isinstance(reasoning_ans.confidence, (int, float)) else 1.0

        if comp_conf is None and reas_conf is None:
            raise ValueError("Incomplete answers received from Jev")

        overall_conf = min(
            [c for c in (comp_conf, reas_conf) if c is not None] or [0.0]
        )

        # Dimension-aware uncertainty threshold: fallback if Jev is uncertain
        if overall_conf < 0.50:
            fallback_profile = build_deterministic_profile(task)
            return fallback_profile, overall_conf, True, f"Jev confidence {overall_conf:.2f} below threshold 0.50."

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
        )
        return profile, overall_conf, False, None

    except Exception as exc:
        fallback_profile = build_deterministic_profile(task)
        return fallback_profile, None, True, f"Jev call failed ({type(exc).__name__}: {exc})"
