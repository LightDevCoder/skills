"""Public entry point and CLI for agent-config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from .abstract_profiler import extract_abstract_task_profile
    from .candidate_selector import select_configuration
    from .agent_config_models import (
        AgentConfigResult,
        HostCapabilities,
        TaskCharacteristics,
    )
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from abstract_profiler import extract_abstract_task_profile
    from candidate_selector import select_configuration
    from agent_config_models import (
        AgentConfigResult,
        HostCapabilities,
        TaskCharacteristics,
    )


def agent_config_recommend(
    host: Union[HostCapabilities, Dict[str, Any]],
    task: Union[TaskCharacteristics, Dict[str, Any]],
    approved_preview: bool = True,
    setup_intent: bool = False,
    client: Optional[Any] = None,
    use_jev: bool = True,
) -> AgentConfigResult:
    """Recommend right-sized topology, model, and effort for task on current host."""
    host_obj = HostCapabilities.from_dict(host) if isinstance(host, dict) else host
    task_obj = TaskCharacteristics.from_dict(task) if isinstance(task, dict) else task

    profile, confidence, fallback_used, fallback_reason = extract_abstract_task_profile(
        task=task_obj,
        client=client,
        use_jev=use_jev,
    )

    return select_configuration(
        host=host_obj,
        task=task_obj,
        profile=profile,
        approved_preview=approved_preview,
        setup_intent=setup_intent,
        jev_confidence=confidence,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Config execution configurator")
    parser.add_argument("--host-json", default="{}", help="Host capabilities JSON")
    parser.add_argument("--task-json", default="{}", help="Task characteristics JSON")
    parser.add_argument("--setup", action="store_true", help="Explicit setup intent")
    parser.add_argument("--no-preview-approval", action="store_true", help="Simulate user declining preview")
    parser.add_argument("--no-jev", action="store_true", help="Disable Jev System One judgments")

    args = parser.parse_args()
    host_data = json.loads(args.host_json)
    task_data = json.loads(args.task_json)

    result = agent_config_recommend(
        host=host_data,
        task=task_data,
        approved_preview=not args.no_preview_approval,
        setup_intent=args.setup,
        use_jev=not args.no_jev,
    )

    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
