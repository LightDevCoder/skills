#!/usr/bin/env python3
"""Deterministic Light evidence service for ask-light.

Architecture (owned by SKILL.md):

    Code establishes trustworthy facts.
    Model understands the situation.
    Model chooses the workflow action.
    Code validates that choice.

This helper is the CODE layer. It collects project evidence, publishes the
Skill catalog and workflow recipes, and validates the model-selected Skill
after the fact. It never owns semantic routing: it returns facts and scoped
hard constraints, not recommendations. The only user-visible RECOMMEND results
are assembled by the ask-light model contract after `validate_recommendation`
accepts the model's choice.

Read-only during the recommendation phase.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

MAP_PATH = Path(__file__).resolve().parents[1] / "references" / "light-skill-map.json"
LIGHT_CATEGORIES = {"first-party", "light-first-party"}
INVOCATION_CONTROLS = {"explicit-only", "model-callable", "either"}
HOST_SKILL_ROOTS = (
    Path.home() / ".agents" / "skills",
    Path.home() / ".codex" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".config" / "skills",
)

EVIDENCE_SCHEMA = "ask-light-evidence/1"
ROUTING_NEEDS_MODEL = "needs-model-judgment"

# Request scopes for post-model selection validation. Only
# "current-workflow" binds the evidence packet's hard constraints; independent
# tasks, new efforts, and standalone requests are validated for availability
# and provenance only.
CONSTRAINT_SCOPES = ("current-workflow", "independent", "standalone")
CONSTRAINT_SCOPE_DEFAULT = "current-workflow"

# Light repo convention: a SPEC is active unless it explicitly says it was
# superseded/obsoleted/archived (or lives in an obvious archive/old segment).
INACTIVE_SPEC_STATUSES = {
    "superseded", "obsolete", "archived", "archive", "deprecated", "retired",
}
INACTIVE_SPEC_PATH_SEGMENTS = {
    "archive", "archived", "obsolete", "old", "superseded", "retired",
    "deprecated", "backup", "bak", "previous", "historical", "past",
    "prior", "completed",
}

# Ticket completion is fail-closed: only explicit resolved vocabulary counts.
TICKET_RESOLVED_STATES = {"resolved", "done", "closed", "complete", "completed", "accepted"}
# Known unresolved vocabulary (producer contract: `ready-for-agent` or `open`
# for map-style scans; `claimed` while worked; `blocked`/waiting states are
# unresolved but not implementable). Anything outside both sets is unknown.
TICKET_READY_STATES = {"open", "ready", "ready-for-agent", "todo"}
TICKET_CLAIMED_STATES = {"claimed", "in-progress", "in_progress"}
TICKET_WAITING_STATES = {"blocked", "awaiting", "awaiting-confirmation", "needs-work"}
TICKET_UNRESOLVED_STATES = TICKET_READY_STATES | TICKET_CLAIMED_STATES | TICKET_WAITING_STATES

# Canonical review evidence is the `project-review` durable state produced by
# skills/project-review (see its references/WORKFLOW.md). The `.review-loop/`
# directory is a documented backwards-compatibility location; it is consumed
# only when no `.project-review/` directory exists. Legacy human-facing paths
# such as docs/agents/acceptance.md are not producer-owned output and never
# establish current acceptance.
PROJECT_REVIEW_DIRNAME = ".project-review"
LEGACY_PROJECT_REVIEW_DIRNAME = ".review-loop"

# Natural-language family navigation is explicit, not token-overlap matching.
FAMILY_ALIASES = {
    "project": ("project", "projects"),
    "review": ("review", "reviews", "acceptance", "verdict"),
    "learning": ("learning", "learn", "study", "teaching"),
    "clarification": ("clarification", "clarify", "clarifying"),
    "implementation": ("implementation", "implement", "building", "coding"),
    "research": ("research", "investigation"),
    "knowledge-work": ("knowledge", "writing", "documentation", "docs"),
    "specialized": ("specialized", "domain"),
    "utility": ("utility", "utilities", "helpers"),
    "internal/reusable": ("internal", "reusable"),
}
FAMILY_INTENT_WORDS = ("skill", "skills", "which", "show", "list", "for", "what", "browse")
DIAGNOSTIC_INTENT_PATTERN = re.compile(r"\b(bug|bugs|debug|debugging|diagnos(?:e|is|ing|tic)?|regression|fix)\b", re.I)
COMPARISON_PATTERN = re.compile(
    r"\b(?:difference|differences|diff)\b.*?\b(?:between|of)\s+([A-Za-z][A-Za-z0-9-]*)\s+and\s+([A-Za-z][A-Za-z0-9-]*)|"
    r"\b([A-Za-z][A-Za-z0-9-]*)\s+vs\.?\s+([A-Za-z][A-Za-z0-9-]*)",
    re.I,
)

# Bounded scan bounds for artifact signal classification.
SIGNAL_SCAN_FILE_LIMIT = 40
SIGNAL_SCAN_MAX_BYTES = 64 * 1024


def load_map(path: Path = MAP_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [item["name"] for item in data["skills"]]
    if len(names) != len(set(names)):
        raise ValueError("Light Skill Map contains duplicate names")
    duplicated_metadata = {"role", "invocation"}
    for item in data["skills"]:
        if duplicated_metadata.intersection(item):
            raise ValueError(f"Light Skill Map duplicates package metadata for {item['name']}")
    required_handoff = {"skill", "expectedInput", "expectedOutput", "handoffArtifact", "stopCondition"}
    for recipe in data["workflows"]:
        for step in recipe["steps"]:
            missing = required_handoff.difference(step)
            if missing:
                raise ValueError(f"workflow {recipe['id']} step is missing handoff fields: {', '.join(sorted(missing))}")
            if step["skill"] not in names:
                raise ValueError(f"workflow {recipe['id']} references an unknown Light Skill: {step['skill']}")
    families = data.get("skillFamilies")
    if families:
        if set(families) != set(names):
            raise ValueError("Light Skill Map families do not match the skill list")
    return data


# ---------------------------------------------------------------------------
# Canonical durable-field parsing (producer owner: skills/project-review).
# These helpers are shared fail-closed grammar; they never salvage values.
# ---------------------------------------------------------------------------

def _small_text(path: Path, max_bytes: int = SIGNAL_SCAN_MAX_BYTES) -> str:
    try:
        if path.is_file() and path.stat().st_size <= max_bytes:
            return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        pass
    return ""


def _has_glob(root: Path, pattern: str) -> bool:
    try:
        return any(root.glob(pattern))
    except OSError:
        return False


def _field_values(text: str, field_names: tuple[str, ...]) -> list[str]:
    """Extract compact status/verdict tokens from markdown field lines.

    Only the first token before a comma/semicolon is returned; trailing prose
    such as `; Resolution evidence: ...` is not treated as a status/verdict
    value.
    """
    # Whitespace inside the field grammar is blank-space-only so a bare
    # heading line (for example `# Verdict`) can never bridge the separator
    # dash/colon of the NEXT list item and fabricate a second field value.
    pattern = re.compile(
        r"(?mi)^[ \t]*(?:[>#-]+[ \t]*)?(?:\*\*)?(?:{})[ \t]*(?:\*\*)?[ \t]*[:=.-][ \t]*(?:\*\*)?[ \t]*(.+)$".format(
            "|".join(re.escape(field) for field in field_names)
        )
    )
    values: list[str] = []
    for match in pattern.finditer(text):
        raw = match.group(1).strip()
        part = re.split(r"[;,]", raw, maxsplit=1)[0].strip().lower()
        if part:
            # Real project-review records wrap values in markdown emphasis
            # (`Verdict: **PASS**`); strip emphasis wrappers, not just parens.
            values.append(part.split()[0].strip("():-*_"))
    return values


def _raw_field_occurrences(text: str, field: str, *, strip_wrappers: bool = True) -> list[str]:
    """Return every canonical field-line value for `field`, in file order.

    Unlike `_field_values`, whole lines are preserved so prose/path-bearing
    fields such as the Charter's `Source:` line stay intact. The lookahead-style
    anchor keeps `Source revision or identity:` separate from `Source:`.
    With ``strip_wrappers=False`` values keep their exact characters —
    required by the strict scope grammar, where wrapper-stripping would
    silently rewrite an invalid literal path (``src/*`` -> ``src/``) into a
    different acceptable one.
    """
    pattern = re.compile(
        r"(?mi)^[ \t]*(?:[>#-]+[ \t]*)?(?:\*\*)?" + re.escape(field) + r"(?:\*\*)?[ \t]*[:=][ \t]*(.+)$"
    )
    values: list[str] = []
    for match in pattern.finditer(text):
        value = match.group(1).strip()
        values.append(value.strip("`*_ \t") if strip_wrappers else value)
    return values


def _singleton_field_value(text: str, field: str, *, strip_wrappers: bool = True) -> tuple[str, str]:
    """Read one producer-owned singleton field, failing closed on cardinality.

    Authoritative durable fields are singleton fields: cardinality is part of
    validity. Returns (value, "") for exactly one canonical occurrence,
    ("", "missing") for zero, and ("", "ambiguous") for more than one — even
    when the duplicated values are identical. A duplicated canonical field
    means the durable record no longer conforms to the producer contract, so
    the consumer never interprets "first value wins".
    """
    occurrences = _raw_field_occurrences(text, field, strip_wrappers=strip_wrappers)
    if not occurrences:
        return "", "missing"
    if len(occurrences) > 1:
        return "", "ambiguous"
    return occurrences[0], ""


def _reviewed_scratch_references(source_value: str) -> list[str]:
    """Extract effort names cited by a Charter Source line.

    Ownership uses this repository's own convention: an effort lives at
    `.scratch/<name>` and is cited by SPEC path. A citation that names no
    `.scratch` target cannot prove which effort was reviewed.
    """
    return re.findall(r"\.scratch[/\\]([A-Za-z0-9._\-]+)", source_value)


def _reviewed_source_paths(source_value: str) -> list[str]:
    """Extract concrete `.scratch` file/dir paths cited by the Charter Source.

    Review freshness is scoped to exactly the reviewed baseline the producer
    recorded — these cited paths — never to unrelated repository activity.
    """
    paths: list[str] = []
    for token in re.findall(r"\.scratch(?:[/\\][A-Za-z0-9._\-]+)+", source_value):
        normalized = token.replace("\\", "/").rstrip("/")
        if normalized and normalized not in paths:
            paths.append(normalized)
    return paths


def _run_git(root: Path, *args: str):
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None


_HEX_REVISION_PATTERN = re.compile(r"\b([0-9a-fA-F]{7,40})\b")


def _resolvable_git_commit(root: Path, revision_token: str, *, peel: bool = True) -> str:
    """Return the full commit SHA a revision resolves to locally, else ""."""
    suffix = "^{commit}" if peel else ""
    resolved = _run_git(root, "rev-parse", "--verify", "--quiet", f"{revision_token}{suffix}")
    if resolved is not None and resolved.returncode == 0 and resolved.stdout.strip():
        return resolved.stdout.strip()
    return ""


def _resolve_recorded_revision(root: Path, revision_value: str) -> tuple[str, str]:
    """Resolve a Charter identity to exactly one locally verifiable Git commit.

    The producer convention freezes repository sources at a Git revision
    (WORKFLOW.md: freeze the source location plus revision / immutable
    identity). The value is usable only when it carries exactly ONE
    commit-like token that resolves locally: multiple commit-like tokens —
    including duplicate SHAs, or an unresolvable token beside a resolvable
    one — leave the frozen identity ambiguous and fail closed instead of
    salvaging one candidate. Version strings, timestamps, or free-form labels
    carry no verifiable token and fail closed rather than being guessed into
    equivalence.
    """
    tokens = _HEX_REVISION_PATTERN.findall(revision_value)
    if not revision_value.strip():
        return "", "missing"
    if len(tokens) != 1:
        return "", "ambiguous" if len(tokens) > 1 else "unresolvable"
    resolved = _resolvable_git_commit(root, tokens[0])
    if not resolved:
        return "", "unresolvable"
    return resolved, ""


def _classify_review_freshness(
    root: Path,
    charter_text: str,
) -> tuple[str, list[str], str]:
    """Decide whether a review verdict still applies to its recorded baseline.

    Returns ("current"|"stale"|"unknown", gaps, baseline_revision). The Charter
    froze both a Source location and a revision identity; freshness holds only
    while every cited source still matches the recorded commit — including
    uncommitted working-tree modifications, which `git diff <rev> -- <path>`
    reports alongside committed ones. When a cited source is a directory, the
    reviewed baseline is that whole directory: files that appear inside it after
    the revision also invalidate freshness, detected with
    `git ls-files --others` (without `--exclude-standard`, so files hidden by
    Git ignore rules still count). Canonical fields are singleton fields: a
    missing or duplicated `Profile:`, `Source:`, or `Source revision or
    identity:` line means the durable record does not conform to the producer
    contract and fails closed. Anything that cannot be proven fresh is
    "unknown"; unknown is fail-closed and never grants acceptance.
    """
    profile, profile_failure = _reviewed_profile_field(charter_text)
    if profile_failure:
        detail = (
            "no canonical `- Profile:` line found"
            if profile_failure == "missing"
            else "more than one canonical `- Profile:` line found"
        )
        return "unknown", [
            f"The Charter's `Profile:` field is {profile_failure} ({detail}), so the "
            "review Profile that selects the freshness contract cannot be "
            "established; ask-light does not fall back to a default Profile and "
            "fails closed."
        ], ""
    revision_value, revision_failure = _singleton_field_value(
        charter_text, "Source revision or identity"
    )
    if revision_failure == "ambiguous":
        return "unknown", [
            "The Charter records more than one canonical `Source revision or "
            "identity:` field line, so the frozen baseline identity is ambiguous; "
            "ask-light does not choose between duplicate canonical fields and "
            "fails closed."
        ], ""
    baseline, failure = _resolve_recorded_revision(root, revision_value)
    if failure == "missing":
        return "unknown", [
            "The Charter records no usable `Source revision or identity`, so the "
            "reviewed baseline cannot be anchored; ask-light does not trust the "
            "verdict for the current state without that frozen baseline."
        ], ""
    inside = _run_git(root, "rev-parse", "--is-inside-work-tree")
    if inside is None or inside.returncode != 0 or inside.stdout.strip() != "true":
        return "unknown", [
            "The project root is not a readable Git work tree, so the recorded "
            "`Source revision or identity` cannot be verified against it; ask-light "
            "fails closed instead of assuming the review is still current."
        ], ""
    if failure == "ambiguous":
        return "unknown", [
            f"The Charter's `Source revision or identity` ('{revision_value}') does not "
            "carry exactly one unambiguous Git commit identity, so the frozen baseline "
            "cannot be verified; ask-light does not salvage one candidate from an "
            "ambiguous value and fails closed."
        ], ""
    if failure == "unresolvable":
        return "unknown", [
            f"The Charter's `Source revision or identity` ('{revision_value}') does not "
            "resolve to a local Git commit, so review freshness cannot be verified; "
            "ask-light fails closed rather than guessing an equivalence."
        ], ""
    source_value, source_failure = _singleton_field_value(charter_text, "Source")
    if source_failure == "ambiguous":
        return "unknown", [
            "The Charter records more than one canonical `Source:` field line, so the "
            "reviewed baseline location is ambiguous; ask-light does not choose one "
            "Source from an ambiguous Charter and fails closed."
        ], baseline
    cited_paths = _reviewed_source_paths(source_value)
    if not cited_paths:
        return "unknown", [
            "The Charter's `Source:` line identifies no concrete `.scratch` path at the "
            "recorded revision, so the reviewed baseline cannot be compared against the "
            "current state; ask-light fails closed."
        ], baseline
    short_baseline = baseline[:12]
    for relative in cited_paths:
        present_at_revision = _run_git(root, "cat-file", "-e", f"{baseline}:{relative}")
        if present_at_revision is None or present_at_revision.returncode != 0:
            return "unknown", [
                f"The cited reviewed source '{relative}' does not exist at the recorded "
                f"revision ({short_baseline}), so verdict freshness cannot be established."
            ], baseline
        if not (root / relative).exists():
            return "stale", [
                f"The reviewed source '{relative}' was removed after the recorded "
                f"revision ({short_baseline}); the frozen baseline no longer exists.",
            ], baseline
        difference = _run_git(root, "diff", "--quiet", baseline, "--", relative)
        if difference is None:
            return "unknown", [
                f"Git could not compare '{relative}' against the recorded revision, so "
                "review freshness is undetermined."
            ], baseline
        if difference.returncode not in (0, 1):
            return "unknown", [
                f"The freshness comparison for '{relative}' failed (git error), so it "
                "cannot be proven that the reviewed baseline is unchanged."
            ], baseline
        if difference.returncode == 1:
            return "stale", [
                f"The reviewed source '{relative}' changed after the recorded revision "
                f"({short_baseline}), including uncommitted working-tree changes.",
            ], baseline
        # A directory baseline covers everything under it, not only the tracked
        # content recorded at the revision. Files that appear inside the reviewed
        # directory afterwards — untracked or ignored alike — change that
        # baseline. `git status` hides ignored files, so completeness is checked
        # with `git ls-files --others` WITHOUT `--exclude-standard` and with
        # literal pathspecs (the cited path is producer-owned, not a glob).
        if (root / relative).is_dir():
            directory_children = _run_git(
                root, "--literal-pathspecs", "ls-files", "--others", "--", relative,
            )
            if directory_children is None:
                return "unknown", [
                    f"Git could not inspect the reviewed directory '{relative}', so it cannot "
                    "be proven free of post-review additions."
                ], baseline
            if directory_children.returncode != 0:
                return "unknown", [
                    f"The completeness check for reviewed directory '{relative}' failed "
                    "(git error), so it cannot be proven unchanged."
                ], baseline
            added = [line for line in directory_children.stdout.splitlines() if line]
            if added:
                names = ", ".join(added[:3])
                extra = "" if len(added) <= 3 else f" (+{len(added) - 3} more)"
                return "stale", [
                    f"New files appeared inside the reviewed directory '{relative}' after the "
                    f"recorded revision ({short_baseline}): {names}{extra} — including files "
                    "Git ignore rules hide from status; the frozen directory baseline "
                    "no longer matches.",
                ], baseline
    return "current", [], baseline


def _reviewed_profile_field(charter_text: str) -> tuple[str, str]:
    """Parse the Charter's singleton `Profile:` field, failing closed.

    Returns (profile, "") or ("", failure) with failure in {"missing",
    "ambiguous"}. The Profile decides which freshness contract a verdict is
    consumed under, so first-match or duplicate-tolerant parsing would let a
    tampered record skip the software baseline checks entirely; the Profile
    must appear exactly once.
    """
    raw, failure = _singleton_field_value(charter_text, "Profile")
    if failure:
        return "", failure
    part = re.split(r"[;,]", raw, maxsplit=1)[0].strip().lower()
    if not part:
        return "", "missing"
    return part.split()[0].strip("():-*_"), ""


# Strict software-baseline grammars (producer owner: skills/project-review).
# The canonical Charter/verdict identity fields carry exactly ONE full
# 40-character commit SHA; the implementation scope carries semicolon-
# separated repository-relative LITERAL paths. Both are fail-closed: there is
# no salvage path that reduces a malformed value into a different valid form.
_EXACT_COMMIT_PATTERN = re.compile(r"[0-9a-fA-F]{40}")
_SCOPE_FORBIDDEN_CHARACTERS = "`\"'*?[]{}\\"


def _parse_exact_commit_token(raw_value: str) -> str:
    """Apply the strict single-commit grammar to one field value.

    After Markdown wrapper trimming the complete value must be exactly one
    full 40-character hexadecimal SHA. Prose, short SHAs, or second endpoints
    are malformed — never partially salvaged or deduplicated.
    """
    token = raw_value.strip().strip("`*_ \t")
    return token if _EXACT_COMMIT_PATTERN.fullmatch(token) else ""


def _parse_exact_commit_field(root: Path, text: str, field: str) -> tuple[str, str]:
    """Resolve a strict identity field to its locally verifiable full commit.

    The field is a producer-owned singleton: returns (full_sha, "") or ("",
    failure) with failure in {"missing", "ambiguous", "malformed",
    "unresolvable"}. A written SHA that resolves to some other object (e.g. an
    annotated tag peeled to another commit) is not the recorded commit identity
    and fails closed instead of being retargeted.
    """
    raw, failure = _singleton_field_value(text, field)
    if failure:
        return "", failure
    token = _parse_exact_commit_token(raw)
    if not token:
        return "", "malformed"
    resolved = _resolvable_git_commit(root, token)
    if not resolved or resolved.lower() != token.lower():
        return "", "unresolvable"
    return resolved, ""


def _parse_implementation_scope(raw_value: str) -> tuple[list[str], str]:
    """Parse the software `Implementation scope:` field, failing closed.

    Returns (entries, "") or ([], error_description). Every semicolon-
    separated entry must be a repository-relative POSIX literal path: no empty
    entries, absolute paths, `..` traversal, Git pathspec magic, wildcard/
    glob/backslash/quoting characters. One invalid entry rejects the WHOLE
    field — valid entries are never partially salvaged.
    """
    entries: list[str] = []
    for part in raw_value.split(";"):
        entry = part.strip()
        if not entry:
            return [], "empty/malformed scope entry between ';' separators"
        if any(character in entry for character in _SCOPE_FORBIDDEN_CHARACTERS):
            return [], f"'{entry}' uses characters outside the literal-path grammar"
        if entry.startswith(":"):
            return [], f"'{entry}' uses Git pathspec magic"
        if entry.startswith("/"):
            return [], f"'{entry}' is absolute instead of repository-relative"
        if ".." in Path(entry).parts:
            return [], f"'{entry}' contains '..' traversal"
        entries.append(entry)
    if not entries:
        return [], "no entries recorded"
    return entries, ""


def _classify_software_implementation_freshness(
    root: Path,
    charter_text: str,
    verdict_text: str,
) -> tuple[str, list[str]]:
    """Verify the software Profile's three-field implementation baseline.

    Returns ("not-applicable"|"current"|"stale"|"unknown", gaps). A software
    verdict binds to THREE produced identities (profiles/software.md):

    - Charter `- Fixed point:` — exactly one full commit SHA, the immutable
      code-review base the review was delimited from;
    - Charter `- Implementation scope:` — the immutable reviewed software
      target as repository-relative literal paths (the machine projection of
      the Charter's approved software `In scope`);
    - verdict `- Reviewed implementation revision:` — exactly one full commit
      SHA, the final candidate the fresh Evaluator judged. It lives on the
      verdict, not the Charter, because authorized bounded repairs may move
      the candidate during review.

    Freshness holds only while, inside the frozen scope, the current tree
    exactly matches the reviewed implementation revision (`git diff <rev> --
    <scope>` covers tracked/committed/staged/unstaged drift) and no new file
    appears inside the scope — detected with `git ls-files --others` WITHOUT
    `--exclude-standard`, so files hidden from `git status` by Git ignore rules
    still count. The base must differ from and delimit the final revision, and
    the B..C review window must contain non-empty in-scope change. All three
    identity fields are producer-owned singletons: missing, duplicated (even
    identically), or ambiguous fields fail closed. Anything that cannot be
    proven is "unknown"; unknown is fail-closed and never grants acceptance.
    """
    profile, profile_failure = _reviewed_profile_field(charter_text)
    if profile_failure:
        detail = (
            "no canonical `- Profile:` line found"
            if profile_failure == "missing"
            else "more than one canonical `- Profile:` line found"
        )
        return "unknown", [
            "The Charter's `Profile:` field is not exactly one canonical value "
            f"({detail}), so the review Profile that selects the freshness "
            "contract cannot be established; ask-light does not silently fall "
            "back to the generic contract and fails closed."
        ]
    if profile != "software":
        return "not-applicable", []

    base_revision, failure = _parse_exact_commit_field(root, charter_text, "Fixed point")
    short_base = base_revision[:12] if base_revision else ""
    if failure == "missing":
        return "unknown", [
            "The Charter records the `software` review Profile but no `- Fixed point:` "
            "identity; a software verdict may only be consumed together with the "
            "immutable code-review base it froze."
        ]
    if failure == "ambiguous":
        return "unknown", [
            "The Charter records more than one canonical `- Fixed point:` field line, "
            "so the immutable review base is ambiguous; duplicate canonical fields "
            "violate the producer singleton contract and ask-light fails closed "
            "instead of selecting one."
        ]
    if failure == "malformed":
        return "unknown", [
            "The Charter's `Fixed point` value is not exactly one full 40-character "
            "commit SHA, so the immutable review base cannot be established; ask-light "
            "does not salvage partial identities and fails closed."
        ]
    if failure == "unresolvable":
        return "unknown", [
            "The Charter's `Fixed point` SHA does not resolve to a local Git commit, so "
            "the immutable review base cannot be verified; ask-light fails closed."
        ]

    scope_raw, scope_cardinality = _singleton_field_value(
        charter_text, "Implementation scope", strip_wrappers=False
    )
    if scope_cardinality == "ambiguous":
        return "unknown", [
            "The Charter records more than one canonical `- Implementation scope:` "
            "field line, so the reviewed software target is ambiguous; duplicate "
            "canonical fields violate the producer singleton contract and ask-light "
            "fails closed instead of selecting one."
        ]
    if not scope_raw.strip():
        return "unknown", [
            "The Charter records the `software` review Profile but no `- Implementation "
            "scope:` target, so the reviewed software component cannot be delimited; "
            "ask-light never infers scope from changed paths and fails closed."
        ]
    scope_entries, scope_error = _parse_implementation_scope(scope_raw)
    if scope_error:
        return "unknown", [
            f"The Charter's `Implementation scope` is unverifiable ({scope_error}), so "
            "the reviewed software target cannot be trusted; the whole field fails "
            "closed rather than partially salvaging valid entries."
        ]

    final_revision, failure = _parse_exact_commit_field(
        root, verdict_text, "Reviewed implementation revision"
    )
    if failure == "missing":
        return "unknown", [
            "The durable verdict records no `- Reviewed implementation revision:`, so the "
            "evaluated implementation candidate cannot be identified; ask-light never "
            "falls back to the fixed-point window's touched paths and fails closed."
        ]
    if failure == "ambiguous":
        return "unknown", [
            "The durable verdict records more than one canonical `- Reviewed "
            "implementation revision:` field line, so the evaluated candidate is "
            "ambiguous; ask-light fails closed instead of selecting one."
        ]
    if failure == "malformed":
        return "unknown", [
            "The verdict's `Reviewed implementation revision` is not exactly one full "
            "40-character commit SHA, so the evaluated candidate cannot be bound; "
            "ask-light fails closed instead of salvaging the value."
        ]
    if failure == "unresolvable":
        return "unknown", [
            "The verdict's `Reviewed implementation revision` SHA does not resolve to a "
            "local Git commit, so the evaluated candidate cannot be compared to the "
            "current state; ask-light fails closed."
        ]
    short_final = final_revision[:12]

    if final_revision == base_revision:
        return "unknown", [
            f"The frozen review base ({short_base}) equals the reviewed implementation "
            "revision, so it cannot delimit any reviewed implementation; ask-light fails "
            "closed instead of inventing a base."
        ]
    ancestor = _run_git(root, "merge-base", "--is-ancestor", base_revision, final_revision)
    if ancestor is None or ancestor.returncode != 0:
        return "unknown", [
            f"The frozen review base ({short_base}) does not delimit the reviewed "
            f"implementation revision ({short_final}); the base/final relationship cannot "
            "be proven, so the verdict fails closed."
        ]

    window = _run_git(
        root, "--literal-pathspecs", "diff", "--name-only", base_revision, final_revision,
        "--", *scope_entries,
    )
    if window is None or window.returncode != 0:
        return "unknown", [
            "Git could not reconstruct the reviewed window behind the frozen base and "
            "final revision, so implementation freshness cannot be proven."
        ]
    if not any(line.strip() for line in window.stdout.splitlines()):
        return "unknown", [
            f"The reviewed window ({short_base}..{short_final}) contains no change inside "
            "the frozen `Implementation scope`, so the software review has no in-scope "
            "content to verify; ask-light does not broaden the scope to manufacture one."
        ]

    drift = _run_git(
        root, "--literal-pathspecs", "diff", "--name-status", final_revision,
        "--", *scope_entries,
    )
    if drift is None or drift.returncode not in (0, 1):
        return "unknown", [
            "The implementation freshness comparison failed (git error), so it cannot be "
            "proven that the reviewed implementation is unchanged."
        ]
    changed = [line for line in drift.stdout.splitlines() if line.strip()]
    if changed:
        names = ", ".join(line.split("\t")[-1] for line in changed[:3])
        extra = "" if len(changed) <= 3 else f" (+{len(changed) - 3} more)"
        return "stale", [
            f"The reviewed implementation changed after the evaluated revision "
            f"({short_final}): {names}{extra} — including uncommitted working-tree "
            "changes; the previous verdict no longer describes the current "
            "implementation inside the frozen scope.",
        ]

    # Scope completeness: any file present inside the frozen scope that is not
    # tracked at the evaluated revision is post-review drift. `git status`
    # hides ignored files, so the check uses `git ls-files --others` WITHOUT
    # `--exclude-standard` (Git ignore controls status presentation, not scope
    # membership) and literal path semantics — scope entries are producer-owned
    # literal paths, never glob patterns. Files added and staged or committed
    # after the revision were already caught by the drift comparison above;
    # anything still listed here is new on disk.
    scope_children = _run_git(
        root, "--literal-pathspecs", "ls-files", "--others", "--", *scope_entries,
    )
    if scope_children is None:
        return "unknown", [
            "Git could not inspect the frozen implementation scope for post-review "
            "additions, so it cannot be proven unchanged."
        ]
    if scope_children.returncode != 0:
        return "unknown", [
            "The implementation scope completeness check failed (git error), so it "
            "cannot be proven free of post-review additions."
        ]
    # A whitespace-only filename is a real entry, so entries are filtered by
    # emptiness only — never by stripping, which would hide such a file.
    added = [line for line in scope_children.stdout.splitlines() if line]
    if added:
        names = ", ".join(added[:3])
        extra = "" if len(added) <= 3 else f" (+{len(added) - 3} more)"
        return "stale", [
            f"A new file appeared inside the frozen implementation scope after the "
            f"evaluated revision ({short_final}): {names}{extra} — including files "
            "Git ignore rules hide from status; the reviewed implementation "
            "baseline no longer matches the current tree.",
        ]
    return "current", []


def _project_review_dir(root: Path) -> Path | None:
    primary = root / PROJECT_REVIEW_DIRNAME
    if primary.is_dir():
        return primary
    legacy = root / LEGACY_PROJECT_REVIEW_DIRNAME
    return legacy if legacy.is_dir() else None


ACTIVE_REVIEW_STATUSES = {"INIT", "READY", "CRITIC", "REPAIR", "EVALUATE"}
TERMINAL_REVIEW_STATUSES = {"PASS", "FAIL", "BLOCKED"}

# Canonical Round grammar (producer owner: skills/project-review).
# Accepts integer (e.g. `1`, `2`, `01`, `02`) or standard round prefix/suffix
# formatting (`round-01`, `round-1`, `round-01 (final)`, `round-01 (closed)`).
# Loose text, multiple tokens, or arbitrary prose fails closed as malformed.
_ROUND_PATTERN = re.compile(
    r"^(?:round-)?0*(\d+)(?:[ \t]+(?:\(final\)|\(closed\)))?$",
    re.IGNORECASE,
)

# Canonical terminal Verdict grammar (producer owner: skills/project-review).
# Accepts exactly PASS, FAIL, or BLOCKED (case-insensitive, formatting wrappers stripped,
# optional `(final)` or `(closed)` suffix).
# Loose text, semantic aliases (e.g. `PASSED`, `FAILED`, `REJECTED`, `INCOMPLETE`,
# `NEEDS-WORK`, `PENDING`, `SUCCESS`, `ACCEPTED`, `DENIED`), or arbitrary prose fail closed.
_TERMINAL_VERDICT_PATTERN = re.compile(
    r"^(?:(?:\*\*|`|__)?)(PASS|FAIL|BLOCKED)(?:(?:\*\*|`|__)?)(?:[ \t]+(?:\(final\)|\(closed\)))?$",
    re.IGNORECASE,
)


def _parse_canonical_round(raw_value: str) -> tuple[int | None, str]:
    """Extract a canonical positive integer round (>= 1) from producer round syntax.

    Accepts forms like `1`, `01`, `round-01`, `round-1`, `round-01 (final)`,
    `round-01 (closed)`. Rejects non-positive rounds (0, 00, round-00), arbitrary
    prose, empty values, or malformed tokens, failing closed as (None, "malformed").
    """
    clean = raw_value.strip().strip("`*_ \t")
    if not clean:
        return None, "malformed"
    match = _ROUND_PATTERN.match(clean)
    if not match:
        return None, "malformed"
    val = int(match.group(1))
    if val < 1:
        return None, "malformed"
    return val, ""


def _parse_canonical_terminal_verdict(raw_value: str) -> tuple[str | None, str]:
    r"""Extract a strict canonical terminal verdict (PASS, FAIL, BLOCKED).

    Accepts `PASS`, `FAIL`, `BLOCKED` (and normalized formatting like `pass`,
    `**PASS**`, `\`PASS\``, `PASS (final)`, `PASS (closed)`).
    Rejects semantic aliases (PASSED, FAILED, REJECTED, INCOMPLETE, NEEDS-WORK,
    PENDING, SUCCESS, ACCEPTED, DENIED) or arbitrary tokens, failing closed as
    (None, "malformed").
    """
    clean = raw_value.strip().strip("`*_ \t")
    if not clean:
        return None, "malformed"
    match = _TERMINAL_VERDICT_PATTERN.match(clean)
    if not match:
        return None, "malformed"
    return match.group(1).upper(), ""


def _singleton_round_field(text: str, field: str = "Round") -> tuple[int | None, str, str]:
    """Parse one producer-owned singleton Round field, failing closed on cardinality.

    Returns (round_int, raw_value, "") for valid singleton, (None, "", "missing")
    for 0 occurrences, (None, "", "ambiguous") for >1 occurrences, or
    (None, raw_value, "malformed") for non-conforming syntax.
    """
    raw, failure = _singleton_field_value(text, field)
    if failure:
        return None, "", failure
    round_no, parse_err = _parse_canonical_round(raw)
    if parse_err:
        return None, raw, parse_err
    return round_no, raw, ""


def _review_record(
    stage: str,
    reason: str,
    *,
    status: str | None = None,
    verdict: str | None = None,
    freshness: str | None = None,
    profile: str | None = None,
    accepted: bool = False,
    paths: list[str] | None = None,
    gaps: list[str] | None = None,
    completed: list[str] | None = None,
    missing: list[str] | None = None,
) -> dict[str, Any]:
    """One classified durable-review record (facts only; no Skill field)."""
    return {
        "stage": stage,
        "status": status,
        "verdict": verdict,
        "freshness": freshness,
        "profile": profile,
        "accepted": accepted,
        "reason": reason,
        "gaps": list(gaps or []),
        "paths": list(paths or []),
        "completed": list(completed if completed is not None else ["Light project contract", "active SPEC", "tickets resolved"]),
        "missing": list(missing or []),
    }


def _classify_review_transaction(
    root: Path,
    review_dir: Path,
    current_effort: str,
) -> dict[str, Any]:
    """Verify the 3-part durable review transaction (Charter + State + Verdict).

    A review verdict is authoritative only when Charter, State, and Verdict form
    one mutually coherent durable transaction. State is authoritative for the
    current review lifecycle state: an active review (INIT, READY, CRITIC,
    REPAIR, EVALUATE) overrides any previous verdict. A terminal state
    (PASS, FAIL, BLOCKED) requires an agreeing verdict on the exact same Charter
    revision, Profile, and Round, plus current Source freshness and software
    implementation freshness. Canonical fields are singletons; missing,
    ambiguous, or conflicting records fail closed.

    Returns a review record: facts about the transaction (stage, status,
    verdict, freshness, profile, accepted, reason, gaps, paths). Which Skill
    should act on these facts is decided by the model, guided by the scoped
    hard constraints the evidence packet derives from the stage.
    """
    charter_path = review_dir / "charter.md"
    charter_text = _small_text(charter_path)
    dir_name = review_dir.name

    charter_rev, charter_rev_fail = _singleton_field_value(charter_text, "Charter revision")
    if charter_rev_fail == "missing":
        reason = (
            f"`{dir_name}/charter.md` records no canonical `Charter revision:` field line; "
            "ask-light cannot verify review revision coherence and fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"canonical Charter revision in {dir_name}/charter.md"])
    if charter_rev_fail == "ambiguous":
        reason = (
            f"`{dir_name}/charter.md` records more than one canonical `Charter revision:` "
            "field line; duplicate canonical fields violate the producer singleton contract "
            "and ask-light fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"unambiguous singleton Charter revision in {dir_name}/charter.md"])

    charter_profile, charter_prof_fail = _reviewed_profile_field(charter_text)
    if charter_prof_fail:
        detail = "no canonical `- Profile:` line found" if charter_prof_fail == "missing" else "more than one canonical `- Profile:` line found"
        reason = (
            f"The Charter's `Profile:` field is {charter_prof_fail} ({detail}), so the review "
            "Profile that selects the freshness contract cannot be established; ask-light fails closed."
        )
        return _review_record("review-freshness-unknown", reason, missing=[f"canonical Profile in {dir_name}/charter.md"])

    state_path = review_dir / "state.md"
    if not state_path.is_file():
        reason = (
            f"A `{dir_name}` durable record exists for the current effort, but `state.md` "
            "is missing or unreadable; ask-light cannot establish the current review "
            "lifecycle state and fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"valid {dir_name}/state.md recording current review state"])

    state_text = _small_text(state_path)
    if not state_text.strip():
        reason = f"`{dir_name}/state.md` is empty or unreadable; ask-light requires valid review state and fails closed."
        return _review_record("review-state-unknown", reason, missing=[f"valid {dir_name}/state.md recording current review state"])

    state_status_raw, status_fail = _singleton_field_value(state_text, "Status")
    if status_fail == "missing":
        reason = f"`{dir_name}/state.md` records no canonical `Status:` field line; ask-light fails closed."
        return _review_record("review-state-unknown", reason, missing=[f"canonical Status in {dir_name}/state.md"])
    if status_fail == "ambiguous":
        reason = (
            f"`{dir_name}/state.md` records more than one canonical `Status:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"unambiguous singleton Status in {dir_name}/state.md"])

    state_rev, state_rev_fail = _singleton_field_value(state_text, "Charter revision")
    if state_rev_fail == "missing":
        reason = f"`{dir_name}/state.md` records no canonical `Charter revision:` field line; ask-light fails closed."
        return _review_record("review-state-unknown", reason, missing=[f"canonical Charter revision in {dir_name}/state.md"])
    if state_rev_fail == "ambiguous":
        reason = (
            f"`{dir_name}/state.md` records more than one canonical `Charter revision:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"unambiguous singleton Charter revision in {dir_name}/state.md"])

    state_prof_raw, state_prof_fail = _singleton_field_value(state_text, "Profile")
    if state_prof_fail == "missing":
        reason = f"`{dir_name}/state.md` records no canonical `Profile:` field line; ask-light fails closed."
        return _review_record("review-state-unknown", reason, missing=[f"canonical Profile in {dir_name}/state.md"])
    if state_prof_fail == "ambiguous":
        reason = (
            f"`{dir_name}/state.md` records more than one canonical `Profile:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"unambiguous singleton Profile in {dir_name}/state.md"])

    state_round, state_round_raw, state_round_fail = _singleton_round_field(state_text, "Round")
    if state_round_fail == "missing":
        reason = f"`{dir_name}/state.md` records no canonical `Round:` field line; ask-light fails closed."
        return _review_record("review-state-unknown", reason, missing=[f"canonical Round in {dir_name}/state.md"])
    if state_round_fail == "ambiguous":
        reason = (
            f"`{dir_name}/state.md` records more than one canonical `Round:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"unambiguous singleton Round in {dir_name}/state.md"])
    if state_round_fail == "malformed":
        reason = (
            f"`{dir_name}/state.md` records an unknown or malformed Round ('{state_round_raw}'); "
            "ask-light requires a canonical review round (e.g. `Round: 1` or `Round: round-01`) and fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"valid canonical Round in {dir_name}/state.md"])

    if state_rev.strip().strip("`*_ \t") != charter_rev.strip().strip("`*_ \t"):
        reason = (
            f"The review state's Charter revision ('{state_rev}') does not match the current "
            f"Charter revision ('{charter_rev}'); the durable review state belongs to a "
            "different Charter revision and is not current."
        )
        return _review_record("review-state-unknown", reason, missing=["synchronized review state matching the current Charter revision"])

    state_prof_norm = re.split(r"[;,]", state_prof_raw, maxsplit=1)[0].strip().lower().split()[0].strip("():-*_")
    if state_prof_norm != charter_profile.lower():
        reason = (
            f"The review state's Profile ('{state_prof_raw}') does not match the Charter's "
            f"Profile ('{charter_profile}'); ask-light cannot determine the authoritative review "
            "profile and fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=["synchronized review state matching the Charter profile"])

    clean_status = state_status_raw.strip().strip("`*_ \t")
    status_token = clean_status.upper()
    if status_token not in (ACTIVE_REVIEW_STATUSES | TERMINAL_REVIEW_STATUSES):
        reason = (
            f"The review state records an unknown or unsupported Status ('{state_status_raw}'); "
            "ask-light requires a canonical project-review Status (INIT, READY, CRITIC, REPAIR, "
            "EVALUATE, PASS, FAIL, BLOCKED) and fails closed."
        )
        return _review_record("review-state-unknown", reason, missing=[f"valid canonical Status in {dir_name}/state.md"])

    if status_token in ACTIVE_REVIEW_STATUSES:
        return _review_record(
            "project-review",
            (
                f"A project-review is currently in progress (Status: {status_token}). "
                "`project-review` owns advancing the active review round to completion."
            ),
            status=status_token,
            profile=charter_profile,
            missing=["completed project-review verdict"],
        )

    # Terminal review status: PASS, FAIL, BLOCKED
    verdict_path = review_dir / "verdict.md"
    verdict_rel = str(verdict_path.relative_to(root))
    if not verdict_path.is_file():
        reason = (
            f"The review state is terminal ({status_token}) but `{dir_name}/verdict.md` is "
            "missing or unreadable; ask-light requires a coherent verdict and fails closed."
        )
        return _review_record("review-state-unknown", reason, status=status_token, profile=charter_profile, missing=[f"valid {dir_name}/verdict.md matching terminal review state"])

    verdict_text = _small_text(verdict_path)
    if not verdict_text.strip():
        reason = f"The review state is terminal ({status_token}) but `{dir_name}/verdict.md` is empty; ask-light fails closed."
        return _review_record("review-state-unknown", reason, status=status_token, profile=charter_profile, missing=[f"valid {dir_name}/verdict.md"])

    v_verdict_raw, v_verdict_fail = _singleton_field_value(verdict_text, "Verdict")
    if v_verdict_fail == "missing":
        reason = (
            f"`{dir_name}/verdict.md` records no canonical `Verdict:` field line; "
            "ask-light requires terminal acceptance verdict identity and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"canonical Verdict in {dir_name}/verdict.md"])
    if v_verdict_fail == "ambiguous":
        reason = (
            f"`{dir_name}/verdict.md` records more than one canonical `Verdict:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"unambiguous singleton Verdict in {dir_name}/verdict.md"])

    verdict_conclusion, v_verdict_parse_err = _parse_canonical_terminal_verdict(v_verdict_raw)
    if v_verdict_parse_err:
        reason = (
            f"`{dir_name}/verdict.md` records an unknown or non-canonical terminal acceptance Verdict ('{v_verdict_raw}'); "
            "ask-light requires a strict canonical terminal conclusion (PASS, FAIL, or BLOCKED) and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"valid canonical terminal Verdict (PASS, FAIL, or BLOCKED) in {dir_name}/verdict.md"])

    v_rev_raw, v_rev_fail = _singleton_field_value(verdict_text, "Charter revision")
    if v_rev_fail == "missing":
        reason = (
            f"`{dir_name}/verdict.md` records no canonical `Charter revision:` field line; "
            "ask-light requires terminal verdict transaction identity and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"canonical Charter revision in {dir_name}/verdict.md"])
    if v_rev_fail == "ambiguous":
        reason = (
            f"`{dir_name}/verdict.md` records more than one canonical `Charter revision:` field "
            "line; duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"unambiguous singleton Charter revision in {dir_name}/verdict.md"])
    if v_rev_raw.strip().strip("`*_ \t") != charter_rev.strip().strip("`*_ \t"):
        reason = (
            f"The verdict's Charter revision ('{v_rev_raw}') does not match the current Charter "
            f"revision ('{charter_rev}'); the verdict belongs to a different Charter revision and "
            "is not current."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=["synchronized verdict matching current Charter revision"])

    v_prof_raw, v_prof_fail = _singleton_field_value(verdict_text, "Profile")
    if v_prof_fail == "missing":
        reason = (
            f"`{dir_name}/verdict.md` records no canonical `Profile:` field line; "
            "ask-light requires terminal verdict transaction identity and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"canonical Profile in {dir_name}/verdict.md"])
    if v_prof_fail == "ambiguous":
        reason = (
            f"`{dir_name}/verdict.md` records more than one canonical `Profile:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"unambiguous singleton Profile in {dir_name}/verdict.md"])
    v_prof_norm = re.split(r"[;,]", v_prof_raw, maxsplit=1)[0].strip().lower().split()[0].strip("():-*_")
    if v_prof_norm != charter_profile.lower():
        reason = (
            f"The verdict's Profile ('{v_prof_raw}') does not match the Charter's Profile "
            f"('{charter_profile}'); ask-light fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=["synchronized verdict matching Charter profile"])

    v_round, v_round_raw, v_round_fail = _singleton_round_field(verdict_text, "Round")
    if v_round_fail == "missing":
        reason = (
            f"`{dir_name}/verdict.md` records no canonical `Round:` field line; "
            "ask-light requires terminal verdict round identity and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"canonical Round in {dir_name}/verdict.md"])
    if v_round_fail == "ambiguous":
        reason = (
            f"`{dir_name}/verdict.md` records more than one canonical `Round:` field line; "
            "duplicate canonical fields violate the producer singleton contract and ask-light "
            "fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"unambiguous singleton Round in {dir_name}/verdict.md"])
    if v_round_fail == "malformed":
        reason = (
            f"`{dir_name}/verdict.md` records an unknown or malformed Round ('{v_round_raw}'); "
            "ask-light requires a canonical review round and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=[f"valid canonical Round in {dir_name}/verdict.md"])
    if v_round != state_round:
        reason = (
            f"The verdict's Round ({v_round}) does not match the current State Round ({state_round}); "
            "the verdict belongs to a different review round and is not current."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, profile=charter_profile, paths=[verdict_rel], missing=["synchronized verdict matching current State round"])

    if status_token != verdict_conclusion:
        reason = (
            f"Durable review state and acceptance verdict conflict: state.md records Status: {status_token} while "
            f"verdict.md records {verdict_conclusion}. ask-light does not resolve conflicting records and fails closed."
        )
        return _review_record("acceptance-unknown", reason, status=status_token, verdict=verdict_conclusion, profile=charter_profile, paths=[verdict_rel], missing=["coherent review state and verdict records"])

    # Freshness verification
    review_freshness, freshness_gaps, _baseline = _classify_review_freshness(root, charter_text)
    if charter_profile.lower() == "software" and review_freshness == "current":
        implementation_state, implementation_gaps = _classify_software_implementation_freshness(
            root, charter_text, verdict_text
        )
        if implementation_state in ("stale", "unknown"):
            review_freshness = implementation_state
            freshness_gaps = implementation_gaps

    if review_freshness == "stale":
        detail = freshness_gaps[0] if freshness_gaps else "the reviewed baseline changed after the recorded revision."
        reason = (
            "The current effort has changed since the recorded project-review baseline. "
            "The previous verdict no longer proves the current state is accepted; run a "
            f"fresh `project-review` for the current baseline. {detail}"
        )
        return _review_record(
            "review-stale",
            reason,
            status=status_token,
            verdict=verdict_conclusion,
            freshness="stale",
            profile=charter_profile,
            paths=[verdict_rel],
            gaps=freshness_gaps,
            missing=["a fresh project-review verdict for the changed baseline"],
            completed=["Light project contract", "active SPEC", "tickets resolved", "recorded project-review baseline exists"],
        )

    if review_freshness == "unknown":
        reason = (
            f"A `{dir_name}` verdict exists for the current effort, but its freshness "
            "cannot be verified against the frozen baseline it recorded (the Charter's "
            "`Source revision or identity`, or for a software Profile also the frozen "
            "`Fixed point` / `Implementation scope` / verdict `- Reviewed implementation "
            "revision` identities), so `ask-light` neither accepts nor reports the old "
            "verdict as current. Fail closed: re-freeze a verifiable baseline with "
            "`project-review`."
        )
        return _review_record(
            "review-freshness-unknown",
            reason,
            status=status_token,
            verdict=verdict_conclusion,
            freshness="unknown",
            profile=charter_profile,
            paths=[verdict_rel],
            gaps=freshness_gaps or [reason],
            missing=["a verifiable frozen baseline behind the recorded review"],
        )

    if status_token == "PASS":
        return _review_record(
            "accepted",
            "The current Light workflow is complete: the project is initialized, has an active SPEC, all implementation tickets are explicitly resolved, and acceptance evidence explicitly passes.",
            status=status_token,
            verdict=verdict_conclusion,
            freshness="current",
            profile=charter_profile,
            accepted=True,
            paths=[verdict_rel],
            completed=[
                "project initialized",
                "SPEC completed",
                "tickets resolved",
                "implementation completed",
                "acceptance passed",
            ],
            missing=[],
        )
    reason = (
        f"Acceptance evidence exists for the current baseline but reports a {status_token} "
        "verdict. This is not a successful acceptance, so `ask-light` does not mark the workflow complete."
    )
    return _review_record(
        "acceptance-not-passed",
        reason,
        status=status_token,
        verdict=verdict_conclusion,
        freshness="current",
        profile=charter_profile,
        paths=[verdict_rel],
        missing=["successful acceptance verdict"],
    )


def _classify_review_ownership(
    review_dir: Path,
    root: Path,
    current_effort: str | None,
) -> tuple[str, list[str]]:
    """Decide whether a durable review record belongs to the current effort.

    Returns ("current"|"historical"|"unresolvable", gaps). A Charter whose
    Source cites exactly the resolved current effort is "current"; one citing
    exactly another named `.scratch` target is "historical"; anything else —
    missing Charter, missing pointer, mixed citations — is unresolvable and
    must fail closed rather than be guessed.
    """
    charter_text = _small_text(review_dir / "charter.md")
    if not charter_text or not current_effort:
        gap = (
            f"`{PROJECT_REVIEW_DIRNAME}/charter.md` is missing or unreadable, so "
            f"the review's ownership cannot be established; ask-light does not "
            f"apply a verdict of unknown ownership to the current effort."
            if not charter_text and review_dir.name == PROJECT_REVIEW_DIRNAME
            else f"The durable `{LEGACY_PROJECT_REVIEW_DIRNAME}/charter.md` record is missing or "
            "unreadable, so the review's ownership cannot be established."
        )
        return "unresolvable", [gap]
    source_value, source_failure = _singleton_field_value(charter_text, "Source")
    if source_failure == "ambiguous":
        gaps = [
            f"`{PROJECT_REVIEW_DIRNAME}/charter.md` records more than one canonical "
            "`Source:` field line, so the reviewed effort is ambiguous; ask-light cannot "
            f"prove it belongs to the current effort '{current_effort}' and fails closed "
            "instead of selecting one Source."
        ]
        if review_dir.name == LEGACY_PROJECT_REVIEW_DIRNAME:
            gaps[0] = gaps[0].replace(PROJECT_REVIEW_DIRNAME, LEGACY_PROJECT_REVIEW_DIRNAME)
        return "unresolvable", gaps
    references = {name for name in _reviewed_scratch_references(source_value)}
    if references == {current_effort}:
        return "current", []
    if len(references) == 1:
        other = next(iter(references))
        return "historical", [
            f"The durable review record cites `.scratch/{other}` as its reviewed source, "
            f"not the resolved current effort '{current_effort}'."
        ]
    gaps = [
        f"`{PROJECT_REVIEW_DIRNAME}/charter.md` records "
        f"'{source_value or '(no Source value)'}' as its acceptance baseline source, "
        f"which does not identify a single reviewed effort; ask-light cannot prove it "
        f"belongs to the current effort '{current_effort}' and fails closed.",
    ]
    if review_dir.name == LEGACY_PROJECT_REVIEW_DIRNAME:
        gaps[0] = gaps[0].replace(PROJECT_REVIEW_DIRNAME, LEGACY_PROJECT_REVIEW_DIRNAME)
    return "unresolvable", gaps


def _spec_status(text: str) -> str:
    values = _field_values(text, ("Status", "State"))
    return values[0] if values else ""


def _in_inactive_spec_segment(path: Path, root: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return any(part.lower() in INACTIVE_SPEC_PATH_SEGMENTS for part in relative.parts[:-1])


def _is_active_spec(path: Path, root: Path) -> bool:
    if not path.is_file():
        return False
    if _in_inactive_spec_segment(path, root):
        return False
    status = _spec_status(_small_text(path)).lower()
    if status and any(token in status for token in INACTIVE_SPEC_STATUSES):
        return False
    return True


# Effort identity comes from Light-owned planning artifacts. Review results do
# not identify an effort; they live in the project-level `.project-review/`
# durable state and are linked back to an effort through the Charter Source.
EFFORT_EVIDENCE_PATTERNS = (
    "spec.md",
    "map.md",
    "issues/*.md",
)


def _effort_has_evidence(path: Path) -> bool:
    if not path.is_dir():
        return False
    return any(_has_glob(path, pattern) for pattern in EFFORT_EVIDENCE_PATTERNS)


def _root_active_spec(root: Path) -> bool:
    root_specs = [
        root / "SPEC.md", root / "spec.md",
        root / "docs" / "SPEC.md", root / "docs" / "spec.md",
    ]
    return any(_is_active_spec(path, root) for path in root_specs)


def _is_historical_effort(path: Path, root: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    if any(part.lower() in INACTIVE_SPEC_PATH_SEGMENTS for part in relative.parts):
        return True
    spec = path / "spec.md"
    return spec.is_file() and not _is_active_spec(spec, root)


def _explicit_effort_references(root: Path) -> set[str]:
    """Read project-level contracts for a concrete effort pointer.

    The bootstrap contract uses `.scratch/<effort>/issues` as a placeholder;
    a concrete path (for example `.scratch/parser-effort/issues`) or a manual
    `Current effort:` line can be a reliable pointer. Nothing is inferred from
    directory ordering or alphabetical names.
    """
    references: set[str] = set()
    effort_field = re.compile(
        r"(?im)^\s*(?:-\s*)?(?:Current effort|Active effort|Effort)\s*[:=]\s*(.+)$"
    )
    tracker_field = re.compile(
        r"(?im)^\s*(?:-\s*)?(?:Issue tracker|Work item location|SPEC location|Ticket location)\s*[:=]\s*(.+)$"
    )
    for relative in ("docs/agents/light-project.md", "docs/agents/issue-tracker.md"):
        path = root / relative
        if not path.is_file():
            continue
        text = _small_text(path)
        for match in effort_field.finditer(text):
            value = match.group(1).strip().strip("`*_")
            if not value or "<effort>" in value or value.lower() in {"none", "none recorded", "?"}:
                continue
            name = value.split()[0].strip("():-")
            if name:
                references.add(name)
        for match in tracker_field.finditer(text):
            value = match.group(1).strip()
            found = re.search(r"\.scratch/([^/\s<>]+)", value)
            if found:
                name = found.group(1).strip("`*_():-")
                if name and name != "<effort>":
                    references.add(name)
    return references


def _resolve_current_effort(root: Path) -> tuple[str | None, str, list[str]]:
    """Resolve the current/active `.scratch` effort before reading tickets.

    Returns (current_effort_name, failure_stage, gaps). `failure_stage` is
    empty on success and otherwise one of the fail-closed stages:
    "ambiguous-current-effort" or "contradictory-current-effort". The resolver
    prefers an explicit project-level pointer, then a single active SPEC
    effort, then a single non-historical effort with evidence. It never
    guesses by directory order, and a pointer that contradicts active SPEC
    evidence fails closed instead of silently picking either side.
    """
    scratch = root / ".scratch"
    if not scratch.is_dir():
        return None, "", []

    efforts = [
        child for child in sorted(scratch.iterdir())
        if child.is_dir() and _effort_has_evidence(child)
    ]
    if not efforts:
        return None, "", []

    explicit = _explicit_effort_references(root)
    if explicit:
        if len(explicit) > 1:
            names = ", ".join(sorted(explicit))
            return None, "ambiguous-current-effort", [
                f"Multiple project-level current-effort pointers were found ({names}); "
                "the current project workflow cannot be established reliably."
            ]
        name = next(iter(explicit))
        candidate = scratch / name
        if not candidate.is_dir() or not _effort_has_evidence(candidate):
            return None, "ambiguous-current-effort", [
                f"Project-level current-effort pointer '{name}' does not match a readable "
                ".scratch effort; the current workflow cannot be established reliably."
            ]
        if _is_historical_effort(candidate, root):
            competing = sorted(
                effort.name for effort in efforts
                if effort.name != name and _is_active_spec(effort / "spec.md", root)
            )
            if competing:
                return None, "contradictory-current-effort", [
                    f"Project-level current-effort pointer '{name}' targets an effort whose SPEC "
                    f"records an inactive/historical state, while these efforts have active SPECS: "
                    f"{', '.join(competing)}. Contradictory current-effort evidence must be resolved "
                    "(update the pointer or the SPEC states); ask-light does not choose between them."
                ]
        return candidate.name, "", []

    active = [effort for effort in efforts if _is_active_spec(effort / "spec.md", root)]
    if active:
        if len(active) > 1:
            names = ", ".join(sorted(effort.name for effort in active))
            return None, "ambiguous-current-effort", [
                f"Multiple active Light efforts were found ({names}). "
                "The current project workflow cannot be determined safely."
            ]
        return active[0].name, "", []

    non_historical = [effort for effort in efforts if not _is_historical_effort(effort, root)]
    if len(non_historical) == 1:
        return non_historical[0].name, "", []

    root_active_spec = _root_active_spec(root)
    if len(non_historical) > 1:
        names = ", ".join(sorted(effort.name for effort in non_historical))
        return None, "ambiguous-current-effort", [
            f"Multiple non-historical Light efforts were found ({names}) without a single "
            "active SPEC. The current project workflow cannot be determined safely."
        ]

    if root_active_spec or len(efforts) > 1:
        if len(efforts) == 1:
            name = efforts[0].name
            return None, "ambiguous-current-effort", [
                f"The only Light effort '{name}' is historical/inactive, so it cannot be "
                "selected as current without a project-level pointer."
            ]
        names = ", ".join(sorted(effort.name for effort in efforts))
        return None, "ambiguous-current-effort", [
            f"Light efforts exist ({names}) but none is active/current and no reliable "
            "project-level pointer identifies the current effort."
        ]

    return None, "", []


def _find_research_artifacts(root: Path) -> list[str]:
    """Return repository-relative paths for research document candidates.

    Presence proves only that an artifact exists — never that it is relevant,
    complete, or that requirements were clarified. These are reasoning inputs.
    """
    research_dir = root / "docs" / "research"
    artifacts: list[str] = []
    if research_dir.is_dir():
        try:
            for path in sorted(research_dir.iterdir()):
                if path.is_file() and path.suffix.lower() in (".md", ".txt"):
                    artifacts.append(str(path.relative_to(root)))
        except OSError:
            pass
    return artifacts


# Clarification handoff classification (producer owner: skills/project-clarify).
# A persisted handoff counts as readiness evidence only when its CONTENT
# resembles the producer contract — never because a filename contains
# "clarif". The producer handoff shape carries the title marker plus
# `Status:` and `Recommended next explicit invocation:` fields.
CLARIFICATION_HANDOFF_MARKER = "project clarification handoff"
CLARIFICATION_STATUS_STATES = {
    "ready-for-next-stage": "ready",
    "waiting-for-user": "waiting",
    "blocked": "blocked",
}
CLARIFICATION_RECOMMENDED_FIELD = "Recommended next explicit invocation"


def _clarification_candidate_files(root: Path, current_effort: str | None) -> list[Path]:
    """Bounded candidate scan for persisted clarification handoffs."""
    directories = [root / "docs" / "agents"]
    if current_effort:
        directories.append(root / ".scratch" / current_effort)
    candidates: list[Path] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        try:
            files = [
                path for path in sorted(directory.iterdir())
                if path.is_file() and path.suffix.lower() in (".md", ".txt")
            ]
        except OSError:
            continue
        candidates.extend(files[:SIGNAL_SCAN_FILE_LIMIT])
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in sorted(candidates):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique[: SIGNAL_SCAN_FILE_LIMIT * 2]


def _classify_clarification_signals(root: Path, current_effort: str | None) -> list[dict[str, Any]]:
    """Classify persisted clarification-handoff records by producer content.

    Returns records for files whose content resembles the project-clarify
    handoff contract: the `Project clarification handoff` marker, or a
    recognized handoff `Status` together with a `Recommended next explicit
    invocation` field. A filename containing "clarif" alone is NOT evidence;
    unrecognized or missing statuses classify as "unknown" (fail-closed —
    never ready).
    """
    records: list[dict[str, Any]] = []
    for path in _clarification_candidate_files(root, current_effort):
        text = _small_text(path)
        if not text.strip():
            continue
        marker = CLARIFICATION_HANDOFF_MARKER in text.lower()
        statuses = _field_values(text, ("Status",))
        recognized = [status for status in statuses if status in CLARIFICATION_STATUS_STATES]
        recommended = _field_values(text, (CLARIFICATION_RECOMMENDED_FIELD,))
        if not marker and not (recognized and recommended):
            continue
        raw_status = recognized[0] if recognized else ""
        state = CLARIFICATION_STATUS_STATES.get(raw_status, "unknown")
        records.append({
            "path": str(path.relative_to(root)),
            "marker": marker,
            "status": raw_status or "unknown",
            "state": state,
            "recommendedNext": recommended[0] if recommended else "",
            "ready": state == "ready",
        })
    return records


def _parse_ticket_blocked_by(text: str) -> tuple[list[str], bool]:
    """Parse a ticket's `Blocked by` edges into normalized ticket numbers.

    Returns (references, parse_ok). `None`-style values produce no references.
    Every other comma-separated part must carry a leading ticket number
    (producer contract: `Blocked by: NN, NN`); a part without one is a
    reference that cannot be proven resolved, so the whole field fails closed
    with parse_ok=False.
    """
    values = _raw_field_occurrences(text, "Blocked by")
    if not values:
        return [], True
    references: list[str] = []
    for value in values:
        if value.strip().lower().startswith("none"):
            continue
        for part in re.split(r"[,;]", value):
            part = part.strip().strip("*`_")
            if not part:
                continue
            match = re.match(r"^(\d{1,4})\b", part)
            if not match:
                return [], False
            number = str(int(match.group(1)))
            if number not in references:
                references.append(number)
    return references, True


def _classify_ticket_frontier(ticket_paths: list[Path], root: Path) -> dict[str, Any]:
    """Classify tickets into the frontier contract buckets (fail-closed).

    Buckets: ready (unblocked implementable frontier), blocked (declared
    blockers outstanding or waiting statuses), claimed/in-progress, resolved,
    unknown (missing/unknown Status vocabulary or unresolvable `Blocked by`
    grammar). A ready frontier exists only when at least one ticket is ready;
    unresolved-but-all-blocked tickets never prove implementation can proceed.
    """
    entries: list[dict[str, Any]] = []
    for path in ticket_paths:
        text = _small_text(path)
        statuses = _field_values(text, ("Status", "State"))
        blocked_by, parse_ok = _parse_ticket_blocked_by(text)
        stem_match = re.match(r"^(\d{1,4})", path.stem)
        entries.append({
            "path": path,
            "statuses": statuses,
            "blockedBy": blocked_by,
            "blockedByParseOk": parse_ok,
            "number": str(int(stem_match.group(1))) if stem_match else "",
        })
    resolved_numbers = {
        entry["number"]
        for entry in entries
        if entry["number"] and entry["statuses"]
        and all(status in TICKET_RESOLVED_STATES for status in entry["statuses"])
    }
    buckets: dict[str, list[dict[str, Any]]] = {
        "ready": [], "blocked": [], "claimed": [], "resolved": [], "unknown": [],
    }
    for entry in entries:
        record: dict[str, Any] = {
            "path": str(entry["path"].relative_to(root)),
            "status": entry["statuses"][0] if entry["statuses"] else "",
            "blockedBy": entry["blockedBy"],
        }
        known_statuses = bool(entry["statuses"]) and all(
            status in TICKET_RESOLVED_STATES or status in TICKET_UNRESOLVED_STATES
            for status in entry["statuses"]
        )
        if not known_statuses:
            record["detail"] = (
                "no canonical Status field"
                if not entry["statuses"]
                else f"unknown ticket status '{entry['statuses'][0]}'"
            )
            buckets["unknown"].append(record)
            continue
        if not entry["blockedByParseOk"]:
            record["detail"] = "'Blocked by' references cannot be resolved to numbered sibling tickets"
            buckets["unknown"].append(record)
            continue
        if any(status in TICKET_CLAIMED_STATES for status in entry["statuses"]):
            buckets["claimed"].append(record)
            continue
        if all(status in TICKET_RESOLVED_STATES for status in entry["statuses"]):
            buckets["resolved"].append(record)
            continue
        outstanding = [ref for ref in entry["blockedBy"] if ref not in resolved_numbers]
        record["outstandingBlockers"] = outstanding
        ready_statuses = all(status in TICKET_READY_STATES for status in entry["statuses"])
        if ready_statuses and not outstanding:
            buckets["ready"].append(record)
        else:
            record["detail"] = (
                "declared blockers outstanding"
                if outstanding
                else f"unresolved waiting state ('{entry['statuses'][0]}')"
            )
            buckets["blocked"].append(record)
    for bucket in buckets.values():
        bucket.sort(key=lambda item: item["path"])
    return {
        "exists": bool(ticket_paths),
        "ready": buckets["ready"],
        "blocked": buckets["blocked"],
        "claimed": buckets["claimed"],
        "resolved": buckets["resolved"],
        "unknown": buckets["unknown"],
        "readyTicketPaths": [record["path"] for record in buckets["ready"]],
        "blockedTicketPaths": [record["path"] for record in buckets["blocked"]],
        "claimedTicketPaths": [record["path"] for record in buckets["claimed"]],
        "resolvedTicketPaths": [record["path"] for record in buckets["resolved"]],
        "unknownTicketPaths": [record["path"] for record in buckets["unknown"]],
        "frontierReady": bool(buckets["ready"]),
        "allResolved": bool(ticket_paths) and not buckets["unknown"] and len(buckets["resolved"]) == len(ticket_paths),
    }


def _constraint(constraint_type: str, owner_skill: str = "", blocking: bool = True, *, detail: str = "") -> dict[str, Any]:
    """One scoped hard fact. Constraints apply to current-workflow
    reasoning only; they never hijack independent tasks or standalone requests."""
    return {
        "type": constraint_type,
        "appliesTo": "current-workflow",
        "ownerSkill": owner_skill,
        "blocking": blocking,
        "detail": detail,
    }


_STAGE_CONSTRAINTS = {
    "uninitialized": ("uninitialized-project", "project-init", True),
    "ambiguous-current-effort": ("ambiguous-current-effort", "", True),
    "contradictory-current-effort": ("contradictory-current-effort", "", True),
    "project-review": ("active-review", "project-review", True),
    "review-stale": ("stale-review", "project-review", True),
    "review-freshness-unknown": ("review-freshness-unknown", "project-review", True),
    "review-state-unknown": ("review-state-unknown", "project-review", True),
    "review-ownership-unknown": ("review-ownership-unknown", "project-review", True),
    "acceptance-unknown": ("acceptance-unknown", "project-review", True),
    "acceptance-not-passed": ("review-verdict-not-passed", "project-review", True),
    "tickets-unknown": ("ticket-state-unknown", "", True),
    "implementation-complete": ("acceptance-pending", "project-review", True),
    "accepted": ("current-effort-accepted", "", False),
}


def _empty_tickets() -> dict[str, Any]:
    return {
        "exists": False,
        "ready": [], "blocked": [], "claimed": [], "resolved": [], "unknown": [],
        "readyTicketPaths": [], "blockedTicketPaths": [], "claimedTicketPaths": [],
        "resolvedTicketPaths": [], "unknownTicketPaths": [],
        "frontierReady": False,
        "allResolved": False,
    }


def _empty_review() -> dict[str, Any]:
    return {
        "exists": False,
        "directory": None,
        "ownership": None,
        "status": None,
        "verdict": None,
        "freshness": None,
        "profile": None,
        "accepted": False,
        "paths": [],
        "gaps": [],
    }


def _empty_evidence(note: str = "no project root was resolved; standalone and semantic routing proceed from the Skill catalog") -> dict[str, Any]:
    return {
        "schema": EVIDENCE_SCHEMA,
        "projectReadable": False,
        "projectRoot": "",
        "initialized": False,
        "projectContract": {},
        "currentEffort": {"name": None, "resolution": "none", "gaps": []},
        "spec": {"exists": False, "active": False, "paths": []},
        "tickets": _empty_tickets(),
        "review": _empty_review(),
        "artifactSignals": {"research": [], "clarification": []},
        "hardConstraints": [],
        "stage": "none",
        "reason": note,
        "completed": [],
        "missing": [],
        "gaps": [],
    }


def _inspect_review_evidence(root: Path, current_effort: str | None) -> dict[str, Any]:
    """Inspect the durable review state at EVERY project stage (fail-closed).

    The canonical software workflow runs project-spec → project-review →
    project-tickets, so a review transaction can be the live workflow state
    before any ticket exists. The record reports ownership, lifecycle status,
    verdict, freshness, and profile as facts; the model determines what the
    review applies to using the producer-owned review contract.
    """
    review_dir = _project_review_dir(root)
    record = _empty_review()
    if review_dir is None:
        return record
    record["exists"] = True
    record["directory"] = review_dir.name
    record["paths"] = [
        str(path.relative_to(root))
        for path in sorted(review_dir.glob("*.md"))
    ]
    ownership, ownership_gaps = _classify_review_ownership(review_dir, root, current_effort)
    record["ownership"] = ownership
    record["gaps"] = list(ownership_gaps)
    if ownership != "current":
        # Without proven ownership the transaction cannot be evaluated for the
        # current effort; the ownership fact and gaps are the evidence.
        return record
    transaction = _classify_review_transaction(root, review_dir, current_effort or "")
    record.update({
        "status": transaction.get("status"),
        "verdict": transaction.get("verdict"),
        "freshness": transaction.get("freshness"),
        "profile": transaction.get("profile"),
        "accepted": transaction.get("accepted", False),
        "reason": transaction.get("reason", ""),
        "gaps": record["gaps"] + list(transaction.get("gaps", [])),
        "stage": transaction.get("stage", ""),
        "completed": transaction.get("completed", []),
        "missing": transaction.get("missing", []),
    })
    return record


def inspect_project_evidence(project_root: Path) -> dict[str, Any]:
    """Inspect a bounded set of real project evidence — facts, not routing.

    Returns an evidence packet: project contract, current effort resolution,
    SPEC activity, ticket frontier, durable review state (at every stage),
    artifact signals, and scoped hard constraints. The packet never names a
    recommended Skill: semantic workflow choice belongs to the model, guided
    by `hardConstraints` (which bind only current-workflow reasoning)
    and validated afterwards by `validate_recommendation`.
    """
    root = Path(project_root).resolve()
    evidence = _empty_evidence()
    evidence["projectRoot"] = str(root)
    if not root.is_dir():
        evidence["stage"] = "unknown"
        evidence["reason"] = "project root is not readable"
        evidence["gaps"] = ["project root is not readable"]
        return evidence
    evidence["projectReadable"] = True

    project_contract = root / "docs/agents/light-project.md"
    evidence["initialized"] = project_contract.is_file()
    if not evidence["initialized"]:
        evidence["stage"] = "uninitialized"
        evidence["reason"] = "No docs/agents/light-project.md exists; the repository has not been initialized for Light Project workflows."
        evidence["completed"] = []
        evidence["missing"] = ["Light project configuration and tracker contract"]
        evidence["review"] = _inspect_review_evidence(root, None)
        evidence["hardConstraints"] = [_constraint(*_STAGE_CONSTRAINTS["uninitialized"], detail=evidence["reason"])]
        return evidence

    # Resolve the current/active effort before reading effort-owned evidence so
    # historical .scratch efforts cannot contaminate the current workflow state.
    current_effort, effort_failure, effort_gaps = _resolve_current_effort(root)
    evidence["currentEffort"] = {
        "name": current_effort,
        "resolution": (
            "current" if current_effort
            else ("ambiguous" if effort_failure == "ambiguous-current-effort"
                  else "contradictory" if effort_failure == "contradictory-current-effort"
                  else "none")
        ),
        "gaps": list(effort_gaps),
    }

    # Active SPEC: a few conventional locations plus the resolved effort root.
    # Inactive/superseded/archived specs are not project evidence.
    spec_candidates = [
        root / "SPEC.md", root / "spec.md",
        root / "docs" / "SPEC.md", root / "docs" / "spec.md",
    ]
    scratch_specs = []
    if current_effort:
        scratch_spec = root / ".scratch" / current_effort / "spec.md"
        if scratch_spec.is_file():
            scratch_specs = [scratch_spec]
    all_spec_candidates = [*spec_candidates, *scratch_specs]
    spec_paths = [path for path in all_spec_candidates if _is_active_spec(path, root)]
    evidence["spec"] = {
        "exists": bool(spec_paths),
        "active": bool(spec_paths),
        "paths": [str(path.relative_to(root)) for path in spec_paths[:10]],
    }

    # Durable review state is inspected at EVERY stage (SPEC review happens
    # before tickets exist in the canonical workflow).
    review_record = _inspect_review_evidence(root, current_effort)
    evidence["review"] = review_record
    if review_record.get("gaps"):
        evidence["gaps"].extend(review_record["gaps"])

    # Tickets: local-markdown issue files only, bounded to the current effort.
    if current_effort:
        issues_dir = root / ".scratch" / current_effort / "issues"
        ticket_paths = sorted(issues_dir.glob("*.md")) if issues_dir.is_dir() else []
    else:
        ticket_paths = []
    ticket_paths = [path for path in ticket_paths if path.is_file()]
    evidence["tickets"] = _classify_ticket_frontier(ticket_paths, root)

    # Artifact signals: candidates, not conclusions.
    evidence["artifactSignals"] = {
        "research": _find_research_artifacts(root),
        "clarification": _classify_clarification_signals(root, current_effort),
    }

    # Effort-level fail-closed facts dominate the stage when present.
    if effort_failure:
        evidence["stage"] = effort_failure
        evidence["reason"] = (
            effort_gaps[0]
            if effort_gaps
            else "The current Light effort cannot be established reliably from repository evidence."
        )
        evidence["completed"] = ["Light project contract present"]
        evidence["missing"] = ["resolve which Light effort is current"]
        evidence["gaps"].extend(effort_gaps)
        evidence["hardConstraints"] = [_constraint(*_STAGE_CONSTRAINTS[effort_failure], detail=evidence["reason"])]
        return evidence

    # An owned review in a live/unknown transaction state owns the current
    # workflow at every ticket stage: an active round must complete, a stale
    # or incoherent verdict must be re-established before anything else.
    review_transaction_stages = {
        "project-review", "review-stale", "review-freshness-unknown",
        "review-state-unknown", "acceptance-unknown",
    }
    if review_record.get("exists") and review_record.get("stage") in review_transaction_stages:
        stage = review_record["stage"]
        evidence["stage"] = stage
        evidence["reason"] = review_record.get("reason", "")
        completed = ["Light project contract"]
        if evidence["spec"]["active"]:
            completed.append("active SPEC")
        if evidence["tickets"]["allResolved"]:
            completed.append("tickets resolved")
        evidence["completed"] = completed
        evidence["missing"] = review_record.get("missing", [])
        evidence["hardConstraints"] = [
            _constraint(*_STAGE_CONSTRAINTS[stage], detail=review_record.get("reason", ""))
        ]
        return evidence

    if not evidence["spec"]["active"]:
        contract_text = _small_text(project_contract)
        has_goal = bool(re.search(r"(?im)^-\s*Goal:\s*(?!\?|\(none recorded\)|$)\S", contract_text))
        has_outputs = bool(re.search(r"(?im)^-\s*Outputs:\s*(?!\(none recorded\)|$)\S", contract_text))
        has_constraints = bool(re.search(r"(?im)^-\s*Constraints:\s*(?!\?|\(none recorded\)|$)\S", contract_text))
        evidence["stage"] = "initialized"
        evidence["reason"] = ""
        evidence["completed"] = ["Light project contract present"]
        evidence["missing"] = ["active SPEC"]
        evidence["projectContract"] = {
            "path": str(project_contract.relative_to(root)),
            "goalRecorded": has_goal,
            "outputsRecorded": has_outputs,
            "constraintsRecorded": has_constraints,
        }
        return evidence

    tickets = evidence["tickets"]
    if tickets["unknown"]:
        evidence["stage"] = "tickets-unknown"
        evidence["reason"] = (
            "Ticket files exist but their completion state cannot be established from repository evidence. "
            "At least one ticket has no Status field or uses a status outside the known resolved/unresolved "
            "vocabulary, so `ask-light` cannot claim implementation is complete."
        )
        evidence["completed"] = ["Light project contract", "active SPEC", "ticket files present"]
        evidence["missing"] = ["reliable ticket completion state"]
        evidence["gaps"].append(evidence["reason"])
        evidence["hardConstraints"] = [
            _constraint(*_STAGE_CONSTRAINTS["tickets-unknown"], detail=evidence["reason"])
        ]
        return evidence

    if not tickets["allResolved"]:
        evidence["stage"] = "work-in-progress"
        evidence["reason"] = (
            "Implementation tickets exist and at least one remains unresolved."
            if tickets["frontierReady"]
            else "Implementation tickets exist and remain unresolved, but no ready unblocked frontier item is present."
        )
        evidence["completed"] = ["Light project contract", "active SPEC", "ticket graph"]
        evidence["missing"] = ["completion of the unresolved ticket(s)"]
        return evidence

    if not tickets["exists"]:
        evidence["stage"] = "spec-no-tickets"
        evidence["reason"] = ""
        evidence["completed"] = ["Light project contract", "active SPEC"]
        evidence["missing"] = ["implementation tickets and unblocked frontier"]
        return evidence

    # All tickets explicitly resolved: acceptance evidence decides the stage.
    if not review_record.get("exists"):
        evidence["stage"] = "implementation-complete"
        evidence["reason"] = (
            "Implementation tickets are resolved but no acceptance/review verdict evidence is present. "
            "`project-review` owns final acceptance against the frozen baseline."
        )
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["missing"] = ["final acceptance/review verdict evidence"]
        evidence["hardConstraints"] = [
            _constraint(*_STAGE_CONSTRAINTS["implementation-complete"], detail=evidence["reason"])
        ]
        return evidence
    if review_record.get("ownership") == "historical":
        evidence["stage"] = "implementation-complete"
        evidence["reason"] = (
            f"Durable review evidence exists but belongs to a historical effort ({review_record['gaps'][0] if review_record['gaps'] else 'another effort'}), "
            "not the current effort. `project-review` owns final acceptance for the current effort."
        )
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["missing"] = ["final acceptance/review verdict evidence for the current effort"]
        evidence["hardConstraints"] = [
            _constraint(*_STAGE_CONSTRAINTS["implementation-complete"], detail=evidence["reason"])
        ]
        return evidence
    if review_record.get("ownership") == "unresolvable":
        reason = (
            f"A `{review_record.get('directory', PROJECT_REVIEW_DIRNAME)}` durable record exists but its ownership cannot be established from the "
            "Charter's `Source:` line, so `ask-light` cannot prove the verdict belongs to the current effort. "
            "Fail closed: link the review by recording the reviewed SPEC path "
            f"(`.scratch/{current_effort or '<effort>'}/spec.md`) in the Charter `Source:`."
        )
        evidence["stage"] = "review-ownership-unknown"
        evidence["reason"] = reason
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["missing"] = ["review ownership proven for the current effort"]
        evidence["gaps"].append(reason)
        evidence["hardConstraints"] = [
            _constraint(*_STAGE_CONSTRAINTS["review-ownership-unknown"], detail=reason)
        ]
        return evidence

    # Proven ownership with a coherent terminal verdict.
    if review_record.get("stage") == "accepted":
        evidence["stage"] = "accepted"
        evidence["reason"] = review_record.get("reason", "")
        evidence["completed"] = review_record.get("completed", [])
        evidence["missing"] = []
        evidence["hardConstraints"] = [
            _constraint(*_STAGE_CONSTRAINTS["accepted"], detail=evidence["reason"])
        ]
        return evidence
    stage = review_record.get("stage") or "acceptance-not-passed"
    evidence["stage"] = stage
    evidence["reason"] = review_record.get("reason", "")
    evidence["completed"] = review_record.get("completed", [])
    evidence["missing"] = review_record.get("missing", [])
    evidence["hardConstraints"] = [
        _constraint(*_STAGE_CONSTRAINTS.get(stage, ("acceptance-unknown", "project-review", True)), detail=evidence["reason"])
    ]
    return evidence


# ---------------------------------------------------------------------------
# Skill catalog, availability, and provenance (deterministic).
# ---------------------------------------------------------------------------

def read_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {}, str(exc)
    if not lines or lines[0] != "---":
        return {}, "SKILL.md has no YAML frontmatter"
    fields: dict[str, str] = {}
    closed = False
    index = 1
    while index < len(lines):
        line = lines[index]
        if line == "---":
            closed = True
            break
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            key, raw = match.group(1), match.group(2).strip()
            if raw in {">", ">-", ">+", "|", "|-", "|+"}:
                continuation: list[str] = []
                index += 1
                while index < len(lines) and (not lines[index] or lines[index][0].isspace()):
                    continuation.append(lines[index].strip())
                    index += 1
                if raw.startswith(">"):
                    paragraphs: list[str] = []
                    paragraph: list[str] = []
                    for value in continuation:
                        if value:
                            paragraph.append(value)
                        elif paragraph:
                            paragraphs.append(" ".join(paragraph))
                            paragraph = []
                    if paragraph:
                        paragraphs.append(" ".join(paragraph))
                    fields[key] = "\n".join(paragraphs)
                else:
                    fields[key] = "\n".join(continuation)
                continue
            fields[key] = raw.strip("\"'")
        index += 1
    if not closed:
        return fields, "SKILL.md frontmatter is not closed"
    if not fields.get("name") or not fields.get("description"):
        return fields, "name and description are required"
    return fields, ""


def availability_policy(context: dict[str, Any], host_name: str) -> dict[str, Any]:
    raw = context.get("availability")
    policy = {"host": host_name, "available": [], "unavailable": [], "readablePaths": []}
    if isinstance(raw, str):
        policy["host"] = raw or host_name
    elif isinstance(raw, dict):
        policy["host"] = raw.get("host") or host_name
        policy["available"] = raw.get("availableSkills", raw.get("available", [])) or []
        policy["unavailable"] = raw.get("unavailableSkills", raw.get("unavailable", [])) or []
        policy["readablePaths"] = raw.get("readablePaths", []) or []
    return policy


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def discover(roots: list[dict[str, Any]], skill_map: dict[str, Any], policy: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], int]:
    known = {item["name"] for item in skill_map["skills"]}
    candidates: list[dict[str, Any]] = []
    gaps: list[str] = []
    metadata_reads = 0
    seen_packages: set[Path] = set()
    for record in roots:
        if str(record.get("category", "")) not in LIGHT_CATEGORIES:
            continue
        raw_path = record.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            gaps.append("Light first-party root requires a non-empty path")
            continue
        root = Path(raw_path)
        if not root.is_dir():
            gaps.append(f"Light first-party root is unreadable: {root}")
            continue
        packages = [root] if (root / "SKILL.md").is_file() else [path.parent for path in root.rglob("SKILL.md")]
        for package in sorted(set(packages)):
            resolved_package = package.resolve()
            if resolved_package in seen_packages:
                continue
            seen_packages.add(resolved_package)
            metadata_reads += 1
            fields, error = read_frontmatter(package / "SKILL.md")
            name = fields.get("name", package.name).lower()
            if name not in known:
                continue
            reasons: list[str] = []
            if error:
                reasons.append(error)
            if policy["available"] and name not in policy["available"]:
                reasons.append("Skill is not in the host available-skill set")
            if name in policy["unavailable"]:
                reasons.append("Skill is listed as unavailable by the active host")
            readable = [Path(value) for value in policy["readablePaths"]]
            if readable and not any(is_under(package, allowed) for allowed in readable):
                reasons.append("package path is outside host readable paths")
            invocation_type = "user-invoked" if fields.get("disable-model-invocation", "").lower() == "true" else "model-invoked"
            candidates.append({
                "name": name,
                "sourceCategory": "first-party",
                "packagePath": str(resolved_package),
                "description": fields.get("description", ""),
                "invocationType": invocation_type,
                "metadataStatus": "unavailable" if error else "available",
                "metadataReadable": not bool(error),
                "metadataError": error,
                "availabilityStatus": "unavailable" if reasons else "available",
                "availabilityError": "; ".join(reasons),
                "readStatus": "not-read",
            })
            if reasons:
                gaps.append(f"{name}: {'; '.join(reasons)}")
    return candidates, gaps, metadata_reads


def _collection_root_candidates(cwd: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    start = Path.cwd() if cwd is None else cwd
    for base in [start, *list(start.parents)[:5]]:
        root = base / "skills"
        if root.is_dir() and (root / "ask-light" / "SKILL.md").is_file() and (root / "socratic" / "SKILL.md").is_file():
            candidates.append(root)
    script_collection = Path(__file__).resolve().parents[2]
    if (script_collection / "ask-light" / "SKILL.md").is_file() and (script_collection / "socratic" / "SKILL.md").is_file():
        candidates.append(script_collection)
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if codex_home:
        codex_root = Path(codex_home) / "skills"
        if codex_root.is_dir() and (codex_root / "ask-light" / "SKILL.md").is_file():
            candidates.append(codex_root)
    for host_root in HOST_SKILL_ROOTS:
        if host_root.is_dir() and (host_root / "ask-light" / "SKILL.md").is_file():
            candidates.append(host_root)
        elif (host_root / "light-skill-map.json").is_file():
            candidates.append(host_root)
    return candidates


def discover_roots(cwd: Path | None = None) -> list[dict[str, Any]]:
    """Discover Light first-party roots without requiring caller-supplied roots."""
    explicit = os.environ.get("LIGHT_SKILL_ROOTS", "").strip()
    roots: list[dict[str, Any]] = []
    if explicit:
        try:
            parsed = json.loads(explicit)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        roots.append(item)
                    elif isinstance(item, str):
                        roots.append({"category": "first-party", "path": item})
        except json.JSONDecodeError:
            # A plain path-separated list is also accepted.
            for item in explicit.split(os.pathsep):
                if item:
                    roots.append({"category": "first-party", "path": item})
    seen: set[Path] = set()
    for candidate in _collection_root_candidates(cwd):
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append({"category": "first-party", "path": str(resolved)})
    return roots


def validate_selected(candidate: dict[str, Any]) -> tuple[int, int, str]:
    package = Path(candidate["packagePath"])
    skill = package / "SKILL.md"
    pending = [skill]
    visited_files: set[Path] = set()
    counted_targets: set[Path] = set()
    reference_reads = 0
    while pending:
        source = pending.pop()
        resolved_source = source.resolve()
        if resolved_source in visited_files:
            continue
        visited_files.add(resolved_source)
        try:
            body = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return 1, reference_reads, f"body/reference unreadable: {source.relative_to(package)}: {exc}"
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
            if link.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link):
                continue
            relative = link.split("#", 1)[0]
            if not relative:
                continue
            target = (source.parent / relative).resolve()
            if not is_under(target, package) or not target.exists():
                return 1, reference_reads, f"body/reference unreadable: {link}"
            if target not in counted_targets:
                counted_targets.add(target)
                reference_reads += 1
            if target.is_file() and target.suffix.lower() in {".md", ".markdown"}:
                pending.append(target)
    return 1, reference_reads, ""


def invocation(name: str, host: str) -> str:
    if host.lower() == "codex":
        return f"${name}"
    if host.lower() in {"claude", "claude-code"}:
        return f"/{name}"
    return f"Skill: {name}"


def invocation_compatible(invocation_type: str, control: str) -> bool:
    return control in {"explicit-only", "either"} or invocation_type == "model-invoked"


def _build_catalog(candidates: list[dict[str, Any]], skill_map: dict[str, Any]) -> list[dict[str, Any]]:
    """Compact catalog metadata for model candidate selection (§17).

    Frontmatter stays authoritative for name/description/invocation type; the
    Light Skill Map stays authoritative for collection membership, families,
    and workflow relationships.
    """
    families = skill_map.get("skillFamilies", {})
    catalog: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda item: item["name"]):
        catalog.append({
            "name": candidate["name"],
            "description": candidate["description"],
            "family": families.get(candidate["name"], ""),
            "invocationType": candidate["invocationType"],
            "availability": candidate["availabilityStatus"],
            "packagePath": candidate["packagePath"],
            "sourceCategory": candidate["sourceCategory"],
        })
    return catalog


# ---------------------------------------------------------------------------
# Mode packets: next (evidence), workflow (recipes), navigate (deterministic).
# Every packet is an evidence/decision input for the model — never a final
# semantic recommendation.
# ---------------------------------------------------------------------------

def next_evidence(roots: list[dict[str, Any]] | None, context: dict[str, Any], host: str = "codex", skill_map: dict[str, Any] | None = None) -> dict[str, Any]:
    """Next-mode packet: project evidence + Skill catalog for model judgment."""
    skill_map = skill_map or load_map()
    if roots is None or not roots:
        roots = discover_roots()
    policy = availability_policy(context, host)
    candidates, gaps, metadata_reads = discover(roots, skill_map, policy)
    project_root_value = context.get("projectRoot") or context.get("cwd")
    if project_root_value and str(project_root_value).strip():
        evidence = inspect_project_evidence(Path(str(project_root_value)))
    else:
        evidence = _empty_evidence()
    catalog = _build_catalog(candidates, skill_map)
    available_names = sorted(item["name"] for item in catalog if item["availability"] == "available")
    return {
        "mode": "next",
        "routingState": ROUTING_NEEDS_MODEL,
        "host": policy["host"],
        "evidence": evidence,
        "catalog": catalog,
        "availableSkills": available_names,
        "gaps": gaps,
        "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0},
        "next": "awaiting-approval",
        "execution": "recommendation phase was read-only; execution begins only after explicit user approval",
    }


def recipes_result(roots: list[dict[str, Any]] | None, context: dict[str, Any], host: str = "codex", skill_map: dict[str, Any] | None = None) -> dict[str, Any]:
    """Workflow-mode packet: canonical recipes + step availability.

    The helper publishes every recipe with per-step availability and handoff
    contracts; it never selects the winning recipe. The model inspects the
    current context, selects the relevant workflow semantically, anchors the
    entry point at the user's actual current state, and preserves each step's
    stopping boundary.
    """
    skill_map = skill_map or load_map()
    if roots is None or not roots:
        roots = discover_roots()
    policy = availability_policy(context, host)
    candidates, gaps, metadata_reads = discover(roots, skill_map, policy)
    available_groups: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        if candidate["availabilityStatus"] == "available":
            available_groups.setdefault(candidate["name"], []).append(candidate)
    recipes: list[dict[str, Any]] = []
    for recipe in skill_map["workflows"]:
        steps: list[dict[str, Any]] = []
        for step in recipe["steps"]:
            group = available_groups.get(step["skill"], [])
            available = len(group) == 1
            ambiguous = len(group) > 1
            steps.append({
                "skill": step["skill"],
                "expectedInput": step["expectedInput"],
                "expectedOutput": step["expectedOutput"],
                "handoffArtifact": step["handoffArtifact"],
                "stopCondition": step["stopCondition"],
                "optional": step.get("optional", False),
                "availability": "ambiguous" if ambiguous else ("available" if available else "unavailable"),
                "invocationType": group[0]["invocationType"] if available else "unknown",
                "invocation": invocation(step["skill"], policy["host"]),
                "missingDependency": step["skill"] if (ambiguous or not available) else "",
            })
        recipes.append({
            "id": recipe["id"],
            "projectTypes": recipe["projectTypes"],
            "taskKinds": recipe["taskKinds"],
            "entryCondition": f"{'/'.join(recipe['projectTypes'])} + {'/'.join(recipe['taskKinds'])}",
            "steps": steps,
            "stoppingBoundary": recipe["stoppingBoundary"],
            "finalAuthority": recipe["finalAuthority"],
        })
    project_root_value = context.get("projectRoot") or context.get("cwd")
    if project_root_value and str(project_root_value).strip():
        evidence = inspect_project_evidence(Path(str(project_root_value)))
    else:
        evidence = _empty_evidence()
    return {
        "mode": "workflow",
        "routingState": ROUTING_NEEDS_MODEL,
        "host": policy["host"],
        "evidence": evidence,
        "recipes": recipes,
        "availableSkills": sorted(available_groups),
        "gaps": gaps,
        "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0},
        "next": "awaiting-approval",
        "execution": "recommendation phase was read-only; execution begins only after explicit user approval",
    }


def navigate_result(skill_map: dict[str, Any], query: str, host: str = "codex") -> dict[str, Any]:
    """Resolve collection-navigation intent with explicit family/skill parsing.

    Deterministic taxonomy lookup stays code-owned (§29): natural-language
    family browsing, diagnostic capability lookup, and exact named comparisons
    resolve without model judgment; the explanation is model-generated.

    Natural-language examples:
      "What project skills do I have?"      -> project family only
      "Show me the review skills"           -> review family only
      "Which skills are for learning?"      -> learning family only
      "What can I use for bugs?"            -> diagnostic capabilities
      "What's the difference between clarify and project-clarify?" -> comparison
    """
    text = query.strip()
    lower = text.lower()
    families = skill_map.get("skillFamilies", {})
    known_names = {entry["name"] for entry in skill_map["skills"]}
    base = {
        "mode": "navigate",
        "status": "RECOMMEND",
        "skill": "",
        "source": "",
        "invocation": "",
        "confidence": "high",
        "alternative": None,
        "gaps": [],
        "reads": {"metadata": 0, "bodies": 0, "references": 0},
        "candidates": [],
        "next": "awaiting-approval",
        "execution": "recommendation phase was read-only; execution begins only after explicit user approval",
        "projectStage": "",
        "completed": [],
        "missing": [],
    }

    def matched(query_match: re.Match[str]) -> list[dict[str, Any]]:
        left, right = query_match.group(1) or query_match.group(3), query_match.group(2) or query_match.group(4)
        left_entry = _known_skill(skill_map, left)
        right_entry = _known_skill(skill_map, right)
        if not left_entry or not right_entry:
            return []
        return [
            {"name": left_entry["name"], "family": families.get(left_entry["name"], ""), "description": left_entry.get("patterns", [])[:1], "invocation": invocation(left_entry["name"], host)},
            {"name": right_entry["name"], "family": families.get(right_entry["name"], ""), "description": right_entry.get("patterns", [])[:1], "invocation": invocation(right_entry["name"], host)},
        ]

    comparison = COMPARISON_PATTERN.search(lower)
    if comparison:
        matches = matched(comparison)
        if matches:
            result = dict(base)
            result.update({
                "skill": "",
                "skills": matches,
                "reason": f"Comparison requested between {matches[0]['name']} and {matches[1]['name']}: use each Skill's package contract for their exact boundaries.",
                "comparison": {
                    "left": matches[0]["name"],
                    "right": matches[1]["name"],
                    "families": [matches[0]["family"], matches[1]["family"]],
                },
            })
            return result

    # Explicit family detection: only when a family word appears together with
    # collection-navigation intent words. This avoids generic-token noise.
    matched_families: list[str] = []
    for family, aliases in FAMILY_ALIASES.items():
        if any(re.search(rf"(?<![A-Za-z0-9-]){re.escape(alias)}(?![A-Za-z0-9-])", lower) for alias in aliases):
            if any(word in lower for word in FAMILY_INTENT_WORDS):
                matched_families.append(family)
    if len(matched_families) == 1:
        family = matched_families[0]
        skills = [
            {"name": entry["name"], "family": family, "description": entry.get("patterns", [])[:1], "invocation": invocation(entry["name"], host)}
            for entry in skill_map["skills"]
            if families.get(entry["name"]) == family
        ]
        if skills:
            result = dict(base)
            result.update({
                "skill": "",
                "skills": skills,
                "reason": f"Light Skill family matched: {family}",
                "family": family,
            })
            return result

    # Diagnostic/bug intent maps to the relevant diagnostic capability.
    if DIAGNOSTIC_INTENT_PATTERN.search(lower):
        diagnostics = sorted(
            [
                {"name": entry["name"], "family": families.get(entry["name"], ""), "description": entry.get("patterns", [])[:1], "invocation": invocation(entry["name"], host)}
                for entry in skill_map["skills"]
                if entry["name"] == "diagnosing-bugs"
            ],
            key=lambda item: item["name"],
        )
        if diagnostics:
            result = dict(base)
            result.update({
                "skill": "diagnosing-bugs" if len(diagnostics) == 1 else "",
                "skills": diagnostics,
                "reason": "Bug/diagnostic intent matched: diagnosing-bugs owns investigating and repairing regressions.",
            })
            return result

    # Exact skill-name lookup (still explicit, not arbitrary token overlap).
    exact = _known_skill(skill_map, lower.strip())
    if exact:
        result = dict(base)
        result.update({
            "skill": exact["name"],
            "skills": [{"name": exact["name"], "family": families.get(exact["name"], ""), "description": exact.get("patterns", [])[:1], "invocation": invocation(exact["name"], host)}],
            "reason": f"Exact Light Skill matched: {exact['name']}",
        })
        return result

    result = dict(base)
    result.update({
        "status": "NEED-INPUT",
        "reason": "",
        "skill": "",
        "skills": [],
        "gaps": [f"No Light Skill family matched: {query}"],
    })
    return result


def _known_skill(skill_map: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((entry for entry in skill_map["skills"] if entry["name"].lower() == name.lower()), None)


# ---------------------------------------------------------------------------
# Post-model selection validation (deterministic; §30).
# ---------------------------------------------------------------------------

def validate_recommendation(
    selected_skill: str,
    *,
    evidence: dict[str, Any] | None = None,
    roots: list[dict[str, Any]] | None = None,
    host: str = "codex",
    skill_map: dict[str, Any] | None = None,
    invocation_control: str = "explicit-only",
    scope: str = CONSTRAINT_SCOPE_DEFAULT,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the model-selected Skill after the choice is made.

    Checks: the Skill is in the Light map, exactly one first-party available
    copy exists, SKILL.md is readable with valid frontmatter, host availability
    permits it, invocation metadata is compatible, package provenance is
    first-party, local pointers resolve, and — for current-workflow scopes —
    that no blocking hard constraint is silently violated.

    The validator NEVER substitutes another Skill. A blocked selection keeps
    its logical recommendation and reports why it cannot proceed.
    """
    skill_map = skill_map or load_map()
    if roots is None or not roots:
        roots = discover_roots()
    context = context or {}
    scope = scope or CONSTRAINT_SCOPE_DEFAULT
    selected = str(selected_skill or "").strip().lower()
    result: dict[str, Any] = {
        "mode": "validate",
        "scope": scope,
        "selectedSkill": selected,
        "status": "VALIDATED",
        "logicalRecommendation": selected,
        "source": "",
        "invocation": "",
        "invocationType": "",
        "provenance": "",
        "checks": {
            "noSkillSelected": False,
            "inLightMap": False,
            "available": False,
            "uniqueCopy": False,
            "metadataReadable": False,
            "hostPermits": False,
            "invocationCompatible": False,
            "provenanceFirstParty": False,
            "localPointersResolve": False,
            "hardConstraintsRespected": False,
        },
        "constraints": list(evidence.get("hardConstraints", [])) if evidence else [],
        "reason": "",
        "gaps": [],
        "reads": {"metadata": 0, "bodies": 0, "references": 0},
        "execution": "validation is read-only; execution begins only after explicit user approval",
    }

    def blocked(reason: str) -> dict[str, Any]:
        result["status"] = "BLOCKED"
        result["reason"] = reason
        result["gaps"].append(reason)
        return result

    if not selected or selected == "none":
        result["selectedSkill"] = ""
        result["logicalRecommendation"] = ""
        result["checks"]["noSkillSelected"] = True
        result["checks"]["hardConstraintsRespected"] = True
        result["reason"] = "no Skill selected; the recommendation is a terminal or needs-input answer"
        return result

    if not any(entry["name"].lower() == selected for entry in skill_map["skills"]):
        return blocked(
            f"logical recommendation '{selected}' is not a Light Skill in the Light Skill Map; "
            "ask-light does not substitute another Skill."
        )
    result["checks"]["inLightMap"] = True

    control = str(context.get("invocationControl", "") or invocation_control)
    if control not in INVOCATION_CONTROLS:
        return blocked(f"invocationControl must be explicit-only, model-callable, or either (got '{control}').")

    policy = availability_policy(context, host)
    candidates, gaps, metadata_reads = discover(roots, skill_map, policy)
    result["gaps"].extend(gaps)
    result["reads"]["metadata"] = metadata_reads
    installed = [
        candidate for candidate in candidates
        if candidate["name"] == selected and candidate["availabilityStatus"] == "available"
    ]
    result["checks"]["available"] = bool(installed)
    result["checks"]["uniqueCopy"] = len(installed) == 1
    if not installed:
        return blocked(
            f"logical recommendation: {selected}; status: BLOCKED; the selected Skill is unavailable "
            "on this host. ask-light does not substitute another Skill."
        )
    if len(installed) > 1:
        return blocked(
            f"logical recommendation: {selected}; status: BLOCKED; multiple available first-party copies "
            "require host precedence evidence. ask-light does not substitute another Skill."
        )
    candidate = installed[0]
    result["checks"]["metadataReadable"] = bool(candidate["metadataReadable"])
    result["checks"]["hostPermits"] = candidate["availabilityStatus"] == "available"
    result["checks"]["provenanceFirstParty"] = candidate.get("sourceCategory") == "first-party"
    result["checks"]["invocationCompatible"] = invocation_compatible(candidate["invocationType"], control)
    if not candidate["metadataReadable"]:
        return blocked(f"{selected}: {candidate.get('metadataError', 'metadata unreadable')}; restore the first-party package.")
    if not result["checks"]["provenanceFirstParty"]:
        return blocked(f"{selected}: package provenance is not first-party; ask-light does not substitute another Skill.")
    if not result["checks"]["invocationCompatible"]:
        return blocked(
            f"{selected}: {candidate['invocationType']} is incompatible with invocationControl={control}."
        )

    body_reads, reference_reads, read_error = validate_selected(candidate)
    result["reads"]["bodies"] = body_reads
    result["reads"]["references"] = reference_reads
    result["checks"]["localPointersResolve"] = not bool(read_error)
    if read_error:
        return blocked(f"{selected}: {read_error}; restore the first-party package.")

    if scope == "current-workflow" and evidence:
        violated: dict[str, Any] | None = None
        for constraint in evidence.get("hardConstraints", []):
            if not constraint.get("blocking"):
                continue
            owner = str(constraint.get("ownerSkill", ""))
            if owner and owner == selected:
                continue
            violated = constraint
            break
        result["checks"]["hardConstraintsRespected"] = violated is None
        if violated is not None:
            owner_text = f" and is owned by `{violated['ownerSkill']}`" if violated.get("ownerSkill") else ""
            return blocked(
                f"current-workflow hard constraint '{violated['type']}' applies{owner_text}; "
                f"selecting '{selected}' would silently violate it. ask-light does not substitute another Skill."
            )
    else:
        result["checks"]["hardConstraintsRespected"] = True

    result.update({
        "status": "VALIDATED",
        "source": f"first-party: {candidate['packagePath']}",
        "invocation": invocation(selected, policy["host"]),
        "invocationType": candidate["invocationType"],
        "provenance": "first-party",
        "reason": (
            f"selected Skill '{selected}' validated: one available first-party copy, readable contract, "
            f"invocation compatible with control '{control}'"
            + ("; current-workflow hard constraints respected" if scope == "current-workflow" else "")
        ),
    })
    return result


# ---------------------------------------------------------------------------
# Approval transition (host-aware; revalidated).
# ---------------------------------------------------------------------------

def approval_transition(
    recommendation: dict[str, Any],
    skill_map: dict[str, Any] | None = None,
    *,
    host: str = "codex",
    context: dict[str, Any] | None = None,
    roots: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute the honest post-approval state for a final recommendation.

    Revalidation first (stale advice is never executed): the accepted Skill's
    availability and any material project hard state are re-checked against
    the current tree. The transition itself is host-aware: a model-invoked
    target may begin in the conversation where the host supports that; a
    user-invoked target begins only when the host verifiably permits an
    explicit approved transition (declared in
    `context["hostCapabilities"]["approvedUserInvokedTransition"]` with host
    evidence) — otherwise ask-light renders the exact invocation and has the
    user start it. It never fakes execution and never assumes a capability
    that was not observed.
    """
    skill_map = skill_map or load_map()
    context = context or {}
    updated = dict(recommendation or {})
    selected = str((recommendation or {}).get("skill", "") or "").strip().lower()
    if (recommendation or {}).get("status") != "RECOMMEND" or not selected:
        updated["next"] = "no-execution"
        return updated
    scope = str((recommendation or {}).get("scope", "") or CONSTRAINT_SCOPE_DEFAULT)
    project_root_value = context.get("projectRoot") or context.get("cwd")
    evidence = None
    if project_root_value and str(project_root_value).strip():
        evidence = inspect_project_evidence(Path(str(project_root_value)))
    validation = validate_recommendation(
        selected,
        evidence=evidence,
        roots=roots,
        host=host,
        skill_map=skill_map,
        invocation_control=str(context.get("invocationControl", "") or "explicit-only"),
        scope=scope,
        context=context,
    )
    updated["revalidation"] = {
        "status": validation["status"],
        "reason": validation.get("reason", ""),
        "source": validation.get("source", ""),
        "invocation": validation.get("invocation", ""),
        "invocationType": validation.get("invocationType", ""),
    }
    if validation["status"] != "VALIDATED":
        updated["next"] = "revalidation-blocked"
        updated["execution"] = (
            "User approval cannot be executed against the current state: "
            f"{validation.get('reason', 'the recommendation became stale')}. "
            "Do not execute stale advice; recompute or explain the changed state."
        )
        return updated
    if validation["invocationType"] == "model-invoked":
        updated["next"] = f"beginning-{selected}"
        updated["execution"] = "User approved; the model-invoked target may begin in this conversation."
        return updated
    capabilities = context.get("hostCapabilities") or {}
    if capabilities.get("approvedUserInvokedTransition") is True:
        updated["next"] = f"beginning-{selected}"
        updated["execution"] = (
            "User approved; this host verifiably permits an explicit approved transition into a "
            "user-invoked Skill, so the user's approval constitutes the required authorization. "
            "Record the observed host capability with the transition."
        )
        return updated
    updated["next"] = "host-transition-required"
    updated["execution"] = (
        "User approved, but repository policy forbids a user-invoked Skill from auto-invoking another "
        "user-invoked Skill and this host exposes no verified approved-transition capability. Render the "
        f"exact invocation ({validation.get('invocation', '')}) and have the user start it. Do not claim a "
        "direct transition without host evidence."
    )
    return updated


def route(roots: list[dict[str, Any]] | None, context: dict[str, Any], host: str = "codex", mode: str = "next") -> dict[str, Any]:
    skill_map = load_map()
    if roots is None or not roots:
        roots = discover_roots()
    if mode == "workflow":
        return recipes_result(roots, context, host, skill_map)
    if mode == "navigate":
        return navigate_result(skill_map, str(context.get("goal", "")), host)
    return next_evidence(roots, context, host, skill_map)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots-json", default="[]")
    parser.add_argument("--context-json", required=True)
    parser.add_argument("--host-name", default="codex")
    # Public modes: choices=("next", "workflow", "navigate") + internal validate
    parser.add_argument("--mode", choices=("next", "workflow", "navigate", "validate"), default="next")
    parser.add_argument("--skill", default="")
    parser.add_argument(
        "--scope",
        default=CONSTRAINT_SCOPE_DEFAULT,
        choices=CONSTRAINT_SCOPES,
    )
    args = parser.parse_args()
    context = json.loads(args.context_json)
    skill_map = load_map()
    roots = json.loads(args.roots_json)
    if not roots:
        roots = discover_roots()
    if args.mode == "validate":
        project_root_value = context.get("projectRoot") or context.get("cwd")
        evidence = None
        if project_root_value and str(project_root_value).strip():
            evidence = inspect_project_evidence(Path(str(project_root_value)))
        result = validate_recommendation(
            args.skill,
            evidence=evidence,
            roots=roots,
            host=args.host_name,
            skill_map=skill_map,
            invocation_control=str(context.get("invocationControl", "") or "explicit-only"),
            scope=args.scope,
            context=context,
        )
    else:
        result = route(roots, context, args.host_name, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
