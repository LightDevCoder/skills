"""Shared rule checkers for the light-kanban-worker package tests.

Each checker reads SKILL.md / agents/openai.yaml / references/api.md text and
returns a single boolean for one rule of the worker contract. The positive
fixture is the real package content; negative fixtures are mutated variants
that must flip at least one checker.
"""

from __future__ import annotations

import re

API_ENDPOINTS = [
    "GET /api/agents",
    "GET /api/tasks?status=in_progress",
    "GET /api/tasks?status=todo",
    "POST /api/tasks/:id/claim",
    "POST /api/tasks/:id/block",
    "POST /api/tasks/:id/complete",
    "POST /api/avatars",
]

API_FIELDS = ["reviewFeedback", "claimedBy", "workspacePath", "blockReason"]


def has_frontmatter_name(text: str, name: str = "light-kanban-worker") -> bool:
    return bool(re.search(rf"(?m)^name:\s*{re.escape(name)}\s*$", text))


def frontmatter_is_yaml_safe(skill: str) -> bool:
    """The Skills CLI parses the SKILL.md frontmatter as YAML. A plain
    (unquoted) scalar that contains a colon followed by a space — e.g.
    "work: resume" inside a description — is read as a nested mapping and
    the whole package is skipped at install time. Gate both with PyYAML
    when available and with a conservative unquoted-colon-space scan."""
    match = re.search(r"(?ms)^---\r?\n(?P<fm>.*?)\r?\n---\s*$", skill)
    if not match:
        return False
    frontmatter = match.group("fm")
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        value = value.strip()
        if not value:
            continue
        if value.startswith(('"', "'")):
            continue
        # unquoted plain scalar: any word-colon-space inside it is a nested
        # mapping for the YAML parser
        if re.search(r"\w:\s", value):
            return False
    try:
        import yaml  # optional strict gate when the dependency exists
    except Exception:
        # CI has no PyYAML: the conservative scan above is the fallback gate
        return True
    data = yaml.safe_load(frontmatter)
    return isinstance(data, dict) and data.get("name") == "light-kanban-worker"


def is_model_invoked(skill: str) -> bool:
    """The skill must never disable model invocation."""
    return not bool(re.search(r"(?m)^disable-model-invocation:\s*true\s*$", skill))


def allows_implicit_invocation(metadata: str) -> bool:
    return bool(re.search(r"allow_implicit_invocation:\s*true", metadata))


def metadata_matches_skill(skill: str, metadata: str) -> bool:
    """openai.yaml must agree with the SKILL.md invocation declaration."""
    return is_model_invoked(skill) == allows_implicit_invocation(metadata)


def existing_work_before_new_work(skill: str) -> bool:
    """The in-progress check must come before the todo check."""
    in_progress = skill.find("status=in_progress")
    todo = skill.find("status=todo")
    return in_progress != -1 and todo != -1 and in_progress < todo


def review_feedback_first(skill: str) -> bool:
    return (
        "reviewFeedback" in skill
        and "Request Changes" in skill
        and bool(re.search(r"outranks|highest priority|priority", skill, re.IGNORECASE))
    )


def one_task_per_run(skill: str) -> bool:
    return bool(
        re.search(r"at most one task|exactly one task|one task per run", skill, re.IGNORECASE)
    ) and not bool(re.search(r"process (all|multiple|several) tasks", skill, re.IGNORECASE))


CANONICAL_REVIEW_BOUNDARY = (
    r"never\s+archives?\b.*?never\s+accepts?\b.*?never\s+deletes?\b"
    r".*?never\s+recycles?\b.*?never\s+unblocks?\b"
)


def human_only_review(skill: str) -> bool:
    """The worker must never archive/accept/delete/recycle or unblock.

    Two gates: the canonical boundary sentence must appear (whitespace- and
    rewrap-tolerant), and each forbidden verb must have a "never" within a
    bounded distance (catches a truncated or reworded prompt that keeps only
    part of the sentence).
    """
    if not re.search(CANONICAL_REVIEW_BOUNDARY, skill, re.IGNORECASE | re.DOTALL):
        return False
    for verb in ("archive", "accept", "delete", "recycle", "unblock"):
        if not re.search(rf"never.{{0,150}}{verb}", skill, re.IGNORECASE | re.DOTALL):
            return False
    return True


def blocks_on_workspace_failure(skill: str) -> bool:
    return (
        "Workspace path is not accessible from this agent host." in skill
        and bool(re.search(r"\bblock\b", skill, re.IGNORECASE))
    )


def no_daemon_or_polling(skill: str) -> bool:
    return not re.search(
        r"\bdaemon\b|while\s+true|infinite\s+loop|\bsleep\b|background\s+service|polling\s+loop",
        skill,
        re.IGNORECASE,
    )


def api_reference_linked(skill: str, api_doc: str) -> bool:
    return "references/api.md" in skill and all(ep in api_doc for ep in API_ENDPOINTS)


def api_fields_documented(api_doc: str) -> bool:
    return all(field in api_doc for field in API_FIELDS)
