"""Behavior tests for the first-party light-kanban-worker Skill.

Pins the workflow ordering and the failure-mode rules of the worker contract:
golden-flow order, review-feedback priority, one-task-per-run, human-only
review boundary, workspace-failure blocking, no daemon / infinite polling, and
pre-claim no-mutation behavior.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # skills/light-kanban-worker/
REPO_ROOT = ROOT.parents[1]  # repository root
sys.path.insert(0, str(REPO_ROOT / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_helpers import Checks, read  # noqa: E402
from worker_checks import (  # noqa: E402
    blocks_on_workspace_failure,
    existing_work_before_new_work,
    human_only_review,
    no_daemon_or_polling,
    one_task_per_run,
    review_feedback_first,
)

# The golden flow order: resolve identity -> check owned in-progress -> review
# feedback -> check todo -> claim -> workspace -> complete (or block).
GOLDEN_FLOW_MARKERS = [
    "GET /api/agents",
    "status=in_progress",
    "reviewFeedback",
    "status=todo",
    "/claim",
    "workspacePath",
    "/complete",
]


def golden_flow_ordered(skill: str) -> bool:
    position = -1
    for marker in GOLDEN_FLOW_MARKERS:
        index = skill.find(marker)
        if index == -1 or index < position:
            return False
        position = index
    return True


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill = read(root, "SKILL.md")
    api_doc = read(root, "references/api.md")

    # --- golden flow ordering ---
    c.check(golden_flow_ordered(skill), "golden flow markers are out of order")
    c.check(existing_work_before_new_work(skill), "existing-work-first rule is violated")

    # --- review-feedback priority chain ---
    c.check(review_feedback_first(skill), "reviewFeedback priority is missing")
    c.check(
        "Request Changes" in skill and "reviewFeedback" in skill,
        "request-changes resume chain is not documented",
    )
    c.check(
        bool(re.search(r"1\..{0,200}review", skill, re.IGNORECASE | re.DOTALL)),
        "priority list must rank review-feedback tasks first",
    )

    # --- one task per run ---
    c.check(one_task_per_run(skill), "one-task-per-run rule is violated")

    # --- human-only boundary ---
    c.check(human_only_review(skill), "human-only review boundary is violated")
    c.check(
        "Awaiting Confirmation" in skill and "Accept" in skill,
        "awaiting-confirmation handoff to the human is missing",
    )

    # --- workspace failure blocks ---
    c.check(blocks_on_workspace_failure(skill), "workspace-failure block rule is violated")
    c.check(
        "Workspace path is not accessible from this agent host." in skill,
        "meaningful workspace block reason is missing",
    )

    # --- no daemon / infinite polling ---
    c.check(no_daemon_or_polling(skill), "daemon/polling language must be absent")
    c.check(bool(re.search(r"No task\s+available", skill)), "empty-queue exit message is missing")

    # --- failures ---
    c.check(
        "do not change any task" in skill.lower() or "without changing any task" in skill.lower(),
        "pre-claim failure must leave tasks untouched",
    )
    c.check(
        "block" in skill.lower() and "reason" in skill.lower(),
        "post-claim failure must block with a reason",
    )

    # --- API reference details ---
    for token in ("409", "conflict", "FIFO"):
        c.check(token in api_doc, f"API reference is missing {token!r} semantics")

    return c.assertions, c.failures


class LightKanbanWorkerBehaviorTest(unittest.TestCase):
    def test_worker_behavior(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LIGHT_KANBAN_WORKER_BEHAVIOR=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
