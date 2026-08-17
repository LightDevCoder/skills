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

try:  # repository harness (source checkout)
    from check_helpers import Checks, read  # noqa: E402
except ImportError:  # installed package copy without the repository harness
    from worker_checks import Checks, read  # noqa: E402
from worker_checks import (  # noqa: E402
    api_fields_documented,
    api_reference_linked,
    atomic_claim_boundary,
    different_agents_concurrent,
    existing_agent_reuses_identity,
    existing_work_before_new_work,
    first_registration_requires_identity,
    frontmatter_is_yaml_safe,
    has_frontmatter_name,
    human_only_review,
    is_model_invoked,
    local_avatar_upload,
    metadata_matches_skill,
    missing_identity_no_mutation,
    no_avatar_optional_first_registration,
    no_daemon_or_polling,
    no_resident_lock_service,
    no_same_agent_overlap,
    one_task_per_run,
    review_feedback_first,
    same_agent_overlap_rule,
    scheduler_owns_concurrency,
)

REQUIRED_SECTIONS = [
    "Responsibility and boundaries",
    "One task per run",
    "Non-overlapping runs",
    "Why this is required",
    "Scheduler responsibility",
    "Unsupported schedulers",
    "Different agents may run concurrently",
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
    "tests/fixtures/overlap-allowed-variant.md",
    "tests/fixtures/avatar-optional-first-registration.md",
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
    c.check(
        bool(re.search(r'default_prompt:.*Use light-kanban-worker to process one task from http://127\.0\.0\.1:8641\.', metadata, re.DOTALL)),
        "openai.yaml default_prompt must be the first-run-capable one-shot form",
    )
    c.check("Agent ID: codex-main" in metadata, "openai.yaml default_prompt must name the Agent ID")
    c.check("Agent Name: Codex" in metadata, "openai.yaml default_prompt must name the Agent Name")
    c.check("Agent Avatar: /path/to/codex-icon.png" in metadata, "openai.yaml default_prompt must include the Agent Avatar")
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

    # --- v0.1.5 scheduling boundary (positive fixture) ---
    c.check(same_agent_overlap_rule(skill), "same-agent non-overlap rule is missing or weakened")
    c.check(no_same_agent_overlap(skill), "same-agent overlap must never be presented as allowed")
    c.check(different_agents_concurrent(skill), "different-agent concurrency must remain explicitly allowed")
    c.check(atomic_claim_boundary(skill), "atomic claim must not be described as a same-agent concurrency lock")
    c.check(scheduler_owns_concurrency(skill), "concurrency control must belong to the scheduler / agent runtime")
    c.check(no_resident_lock_service(skill), "worker must add no lock process, heartbeat, or lease service")
    c.check(first_registration_requires_identity(skill), "first registration must require ID + name + avatar")
    c.check(existing_agent_reuses_identity(skill), "an existing agent must reuse the server's stored name/avatar")
    c.check(missing_identity_no_mutation(skill), "missing first-registration identity must not claim or mutate tasks")
    c.check(local_avatar_upload(skill, api_doc), "local avatar upload path must remain correct")

    # --- negative fixtures: mutations of the positive content must flip checkers ---
    mutated = skill.replace("never archives", "archives the task when done")
    c.check(not human_only_review(mutated), "archive mutation must be rejected")
    mutated = skill.replace("at most one task", "every available task").replace(
        "One task per run", "All tasks per run"
    )
    c.check(not one_task_per_run(mutated), "multi-task mutation must be rejected")
    mutated = skill + "\nStart a background daemon to keep working.\n"
    c.check(not no_daemon_or_polling(mutated), "daemon mutation must be rejected")
    mutated = skill.replace("must not overlap", "may overlap")
    c.check(not same_agent_overlap_rule(mutated), "same-agent overlap-rule mutation must be rejected")
    mutated = skill + "\nThe worker may claim a new identity without an avatar.\n"
    c.check(not no_avatar_optional_first_registration(mutated), "avatar-optional first-registration mutation must be rejected")
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
    # one rule each; the target checker must fail while the other rule
    # checkers must still pass ---
    all_checkers = [
        existing_work_before_new_work,
        no_daemon_or_polling,
        human_only_review,
        one_task_per_run,
        no_same_agent_overlap,
        no_avatar_optional_first_registration,
    ]
    fixture_targets = [
        ("tests/fixtures/todo-first-variant.md", existing_work_before_new_work),
        ("tests/fixtures/daemon-variant.md", no_daemon_or_polling),
        ("tests/fixtures/archive-variant.md", human_only_review),
        ("tests/fixtures/multi-task-variant.md", one_task_per_run),
        ("tests/fixtures/overlap-allowed-variant.md", no_same_agent_overlap),
        ("tests/fixtures/avatar-optional-first-registration.md", no_avatar_optional_first_registration),
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
