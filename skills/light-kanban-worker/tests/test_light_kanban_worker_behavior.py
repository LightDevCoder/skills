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

try:  # repository harness (source checkout)
    from check_helpers import Checks, read  # noqa: E402
except ImportError:  # installed package copy without the repository harness
    from worker_checks import Checks, read  # noqa: E402
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


def _find_ci(text: str, needle: str) -> int:
    """Case-insensitive index of needle in text."""
    return text.lower().find(needle.lower())


def scenario_g_guard(fixture: str) -> bool:
    """Scenario G must pin the same-agent concurrent-wake boundary: run #1
    active -> run #2 scheduled -> must not start; the guard is the scheduler
    (`max concurrent runs = 1`), and the fixture records that Light-Kanban
    itself provides no run lease."""
    markers = ["run #1", "active", "run #2", "must not start"]
    position = -1
    for marker in markers:
        index = _find_ci(fixture, marker)
        if index == -1 or index < position:
            return False
        position = index
    return (
        "max concurrent runs = 1" in fixture
        and "Verification boundary" in fixture
        and "no run lease" in fixture
    )


def scenario_h_identity(fixture: str) -> bool:
    """Scenario H must pin the fresh-identity-without-avatar boundary: missing
    avatar -> identity configuration missing -> no claim, no mutation -> a
    legal avatar -> registration -> claim succeeds."""
    no_avatar = fixture.find("no avatar")
    missing = fixture.find("identity configuration missing")
    no_claim = fixture.find("No task claimed, no task mutated")
    avatar_ok = fixture.find("provides a legal avatar")
    registration = fixture.find("Registration succeeds")
    claim_ok = fixture.find("claim succeeds")
    return (
        -1 < no_avatar < missing < no_claim < avatar_ok < registration < claim_ok
        and "POST /api/avatars" in fixture
        and "Verification boundary" in fixture
    )


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

    # --- v0.1.5 scenario G: same-agent concurrent wake boundary ---
    scenario_g = read(root, "tests/fixtures/scenario-g-scheduler-guard.md")
    c.check(bool(scenario_g.strip()), "scenario G fixture is empty")
    c.check(scenario_g_guard(scenario_g), "scenario G must pin the same-agent overlap skip boundary")

    # --- v0.1.5 scenario H: fresh identity without avatar ---
    scenario_h = read(root, "tests/fixtures/scenario-h-fresh-identity-no-avatar.md")
    c.check(bool(scenario_h.strip()), "scenario H fixture is empty")
    c.check(scenario_h_identity(scenario_h), "scenario H must pin the missing-avatar no-mutation boundary")

    # --- the SKILL.md itself must carry both boundaries ---
    c.check(
        bool(re.search(r"must\s+skip", skill, re.IGNORECASE)),
        "a same-agent wake while a previous run is active must skip",
    )
    c.check(
        "Avatar is required for first registration" in skill,
        "avatar must be required for first registration only",
    )

    return c.assertions, c.failures


class LightKanbanWorkerBehaviorTest(unittest.TestCase):
    def test_worker_behavior(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LIGHT_KANBAN_WORKER_BEHAVIOR=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
