"""Abstract task profiler extracting configuration intent without hardcoding model names.

Profiles work items into abstract tiers (routine, standard, high) and reasoning needs (low, medium, high).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Tuple

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
    from typesafe_sdk import Choice, TypeSafeClient
    TYPESAFE_AVAILABLE = True
except ImportError:
    TYPESAFE_AVAILABLE = False
    class Choice:  # type: ignore[no-redef]
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
    """Extract abstract configuration intent using Jev Choice with deterministic fallback.
    
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
        "recommended_tier": Choice(
            instructions="Which abstract capability tier is most appropriate for this task?",
            criteria={
                "routine": "Simple, typo fix, minor documentation, or repetitive low-risk edits",
                "standard": "Standard feature implementation, UI Polish, or typical application logic",
                "high": "Complex architectural overhaul, critical security, high concurrency, or deep algorithmic reasoning",
            },
        ),
        "reasoning_need": Choice(
            instructions="What level of reasoning effort is required for this task?",
            criteria={
                "low": "Minimal reasoning, routine coding or template filling",
                "medium": "Standard programming reasoning and component composition",
                "high": "Deep architectural analysis, multi-system coordination, or subtle edge case handling",
            },
        ),
    }

    try:
        ts_client = client or TypeSafeClient()
        response = ts_client.system_one(state=state, questions=questions)

        tier_ans = response.choices.get("recommended_tier")
        reasoning_ans = response.choices.get("reasoning_need")

        if not tier_ans or not reasoning_ans:
            raise ValueError("Incomplete answers received from Jev")

        rec_tier = tier_ans.choice
        confidence = tier_ans.confidence

        # Calibrated uncertainty threshold: fallback if Jev is uncertain
        if confidence < 0.55:
            fallback_profile = build_deterministic_profile(task)
            return fallback_profile, confidence, True, f"Jev confidence {confidence:.2f} below threshold 0.55."

        # If task is explicitly cost-sensitive, enforce routine tier priority
        if task.cost_sensitive and rec_tier != "high":
            rec_tier = "routine"

        profile = AbstractTaskProfile(
            complexity_level=task.difficulty,
            reasoning_need=reasoning_ans.choice,
            latency_sensitivity="high" if task.latency_sensitive else "medium",
            cost_sensitivity="high" if task.cost_sensitive else "medium",
            recommended_tier=rec_tier,
        )
        return profile, confidence, False, None

    except Exception as exc:
        fallback_profile = build_deterministic_profile(task)
        return fallback_profile, None, True, f"Jev call failed ({type(exc).__name__}: {exc})"
