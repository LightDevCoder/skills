"""Contract tests for the first-party light-kanban-worker Skill.

Verifies SKILL.md metadata, invocation type, required workflow sections,
metadata consistency, and API reference links. Positive fixtures are the real
package files; negative fixtures (mutations and adversarial fixture files)
must be rejected by the same checkers.
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
    api_fields_documented,
    api_reference_linked,
    existing_work_before_new_work,
    frontmatter_is_yaml_safe,
    has_frontmatter_name,
    human_only_review,
    is_model_invoked,
    metadata_matches_skill,
    no_daemon_or_polling,
    one_task_per_run,
    review_feedback_first,
)

REQUIRED_SECTIONS = [
    "Responsibility and boundaries",
    "One task per run",
    "Configuration",
    "Agent identity",
    "Golden flow",
    "Existing work before new work",
    "Review feedback first",
    "Claiming new work",
    "No work available",
    "Workspace validation",
    "Read the task context",
    "Execute",
    "Complete the task",
    "Human review boundary",
    "Blocked work",
    "Failures before and after claim",
    "Network boundary",
]

NEGATIVE_FIXTURES = [
    "tests/fixtures/todo-first-variant.md",
    "tests/fixtures/daemon-variant.md",
    "tests/fixtures/archive-variant.md",
    "tests/fixtures/multi-task-variant.md",
]


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill = read(root, "SKILL.md")
    metadata = read(root, "agents/openai.yaml")
    api_doc = read(root, "references/api.md")

    # --- metadata and invocation type ---
    c.check(has_frontmatter_name(skill), "SKILL.md frontmatter name must be light-kanban-worker")
    c.check("description:" in skill, "SKILL.md frontmatter must declare a description")
    c.check(frontmatter_is_yaml_safe(skill), "SKILL.md frontmatter must parse as YAML (Skills CLI install gate)")
    c.check(is_model_invoked(skill), "SKILL.md must not disable model invocation")
    c.check(bool(re.search(r'display_name:\s*"Light Kanban Worker"', metadata)), "openai.yaml display_name is incorrect")
    c.check(bool(re.search(r'short_description:\s*"Pick up and execute work from Light-Kanban"', metadata)), "openai.yaml short_description is incorrect")
    c.check(bool(re.search(r'default_prompt:\s*"Use light-kanban-worker to process one Light-Kanban task\.",?', metadata)), "openai.yaml default_prompt is incorrect")
    c.check(re.search(r"allow_implicit_invocation:\s*true", metadata), "openai.yaml must allow implicit invocation")
    c.check(metadata_matches_skill(skill, metadata), "openai.yaml invocation policy disagrees with SKILL.md")

    # --- required workflow sections ---
    for section in REQUIRED_SECTIONS:
        c.check(
            bool(re.search(rf"(?m)^#{{1,3}}\s+{re.escape(section)}\s*$", skill)),
            f"SKILL.md is missing required workflow section: {section}",
        )

    # --- behavior rules (positive fixture) ---
    c.check(existing_work_before_new_work(skill), "existing-work-first rule is violated")
    c.check(review_feedback_first(skill), "reviewFeedback priority rule is missing")
    c.check(one_task_per_run(skill), "one-task-per-run rule is missing or contradicted")
    c.check(human_only_review(skill), "human-only review boundary is violated")
    c.check(api_reference_linked(skill, api_doc), "API reference links are incomplete")
    c.check(api_fields_documented(api_doc), "API reference is missing key fields")

    # --- negative fixtures: mutations of the positive content must flip checkers ---
    mutated = skill.replace("never archives", "archives the task when done")
    c.check(not human_only_review(mutated), "archive mutation must be rejected")
    mutated = skill.replace("at most one task", "every available task").replace(
        "One task per run", "All tasks per run"
    )
    c.check(not one_task_per_run(mutated), "multi-task mutation must be rejected")
    mutated = skill + "\nStart a background daemon to keep working.\n"
    c.check(not no_daemon_or_polling(mutated), "daemon mutation must be rejected")
    mutated_metadata = metadata.replace(
        "allow_implicit_invocation: true", "allow_implicit_invocation: false"
    )
    c.check(
        not metadata_matches_skill(skill, mutated_metadata),
        "invocation-policy mutation must be rejected",
    )
    mutated_api = api_doc.replace("POST /api/tasks/:id/claim", "")
    c.check(
        not api_reference_linked(skill, mutated_api),
        "removing a claim endpoint from the API reference must be rejected",
    )
    mutated_frontmatter = skill.replace('description: "', "description: ").replace(
        "work — resume", "work: resume"
    )
    c.check(
        not frontmatter_is_yaml_safe(mutated_frontmatter),
        "unquoted colon-space frontmatter mutation must be rejected",
    )

    # --- negative fixture files: adversarial protocols that violate exactly
    # one rule each; the target checker must fail while the other three rule
    # checkers must still pass ---
    all_checkers = [
        existing_work_before_new_work,
        no_daemon_or_polling,
        human_only_review,
        one_task_per_run,
    ]
    fixture_targets = [
        ("tests/fixtures/todo-first-variant.md", existing_work_before_new_work),
        ("tests/fixtures/daemon-variant.md", no_daemon_or_polling),
        ("tests/fixtures/archive-variant.md", human_only_review),
        ("tests/fixtures/multi-task-variant.md", one_task_per_run),
    ]
    for path, checker in fixture_targets:
        fixture = read(root, path)
        c.check(bool(fixture.strip()), f"negative fixture is empty: {path}")
        c.check(not checker(fixture), f"negative fixture must be rejected: {path}")
        for other in all_checkers:
            if other is not checker:
                c.check(
                    other(fixture),
                    f"negative fixture violates a second rule ({other.__name__}): {path}",
                )

    return c.assertions, c.failures


class LightKanbanWorkerContractTest(unittest.TestCase):
    def test_worker_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LIGHT_KANBAN_WORKER_CONTRACT=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
