#!/usr/bin/env python3
"""Deterministic Light router: project evidence first, semantic map second,
host availability third.

This helper is read-only during the recommendation phase. The Skill itself
reports the host-supported transition after user approval.
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

# Project-state questions are a small intent class: interrogatives about the
# current stage, next work, missing/completed work, or what remains. The
# presence of a projectRoot plus this intent switches ask-light to evidence
# reasoning instead of generic token overlap.
PROJECT_STATE_INTENT_PATTERN = re.compile(
    r"(?i)"
    r"\b(?:what|where)\b[^?.]*\b(?:next|now|stage|status|missing|left|finished|done|complete|completed|remaining|progress|current)\b"
    r"|\bwhat\b[^?.]*\b(?:should|can|do)\b[^?.]*\b(?:next|now)\b"
)

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
TICKET_UNRESOLVED_STATES = {
    "open", "ready", "ready-for-agent", "claimed", "in-progress", "in_progress",
    "todo", "blocked", "awaiting", "awaiting-confirmation", "needs-work",
}

# Acceptance is fail-closed: only explicit PASS-style verdicts count as
# successful. Generic lifecycle states such as complete/done are not verdicts.
ACCEPTANCE_PASS_STATES = {"pass", "passed"}
ACCEPTANCE_FAIL_STATES = {
    "fail", "failed", "blocked", "rejected", "incomplete", "pending", "needs-work",
}

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


def context_text(context: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("goal", "blockers", "projectType", "taskKind"):
        value = context.get(key, "")
        if value:
            values.append(str(value))
    artifacts = context.get("artifacts", [])
    values.extend(str(value) for value in (artifacts if isinstance(artifacts, list) else [artifacts]))
    return " ".join(values).lower()


def logical_ranking(skill_map: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    text = context_text(context)
    task_kind = str(context.get("taskKind", "")).lower()
    task_kind_route = skill_map.get("taskKindRoutes", {}).get(task_kind, task_kind)
    ranked: list[dict[str, Any]] = []
    for entry in skill_map["skills"]:
        matches = [pattern for pattern in entry.get("patterns", []) if re.search(pattern, text, re.I)]
        precedence = [pattern for pattern in entry.get("precedencePatterns", []) if re.search(pattern, text, re.I)]
        task_match = entry["name"] == task_kind_route
        applied_precedence = precedence if matches or task_match else []
        score = 100 * len(matches) + 25 * len(applied_precedence) + (250 if task_match else 0)
        ranked.append({
            **entry,
            "logicalScore": score,
            "matchedPatterns": matches,
            "matchedPrecedence": applied_precedence,
            "matchedTaskKind": task_kind if task_match else "",
        })
    return sorted(ranked, key=lambda item: (-item["logicalScore"], item["name"]))


def _small_text(path: Path, max_bytes: int = 64 * 1024) -> str:
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


def _raw_field_line(text: str, field: str) -> str:
    """Return the full first-line value of a markdown field (no truncation).

    Unlike `_field_values`, the whole line is preserved so prose/path-bearing
    fields such as the Charter's `Source:` line stay intact. The lookahead-style
    anchor keeps `Source revision or identity:` separate from `Source:`.
    """
    pattern = re.compile(
        r"(?mi)^[ \t]*(?:[>#-]+[ \t]*)?(?:\*\*)?" + re.escape(field) + r"(?:\*\*)?[ \t]*[:=][ \t]*(.+)$"
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group(1).strip().strip("`*_ \t")


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
    """Resolve a Charter identity to a local Git commit.

    The producer convention freezes repository sources at a Git revision
    (WORKFLOW.md: freeze the source location plus revision / immutable
    identity). Only locally resolvable commits establish freshness; version
    strings, timestamps, or free-form labels are treated as unverifiable and
    fail closed rather than being guessed into equivalence.
    """
    for candidate in _HEX_REVISION_PATTERN.findall(revision_value):
        resolved = _resolvable_git_commit(root, candidate)
        if resolved:
            return resolved, ""
    return "", "missing" if not revision_value.strip() else "unresolvable"


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
    reviewed baseline is that whole directory: files that appear untracked inside
    it after the revision also invalidate freshness, detected with `git status
    --porcelain` scoped to exactly the reviewed directory. Anything that cannot
    be proven fresh is "unknown"; unknown is fail-closed and never grants
    acceptance.
    """
    revision_value = _raw_field_line(charter_text, "Source revision or identity")
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
    if failure == "unresolvable":
        return "unknown", [
            f"The Charter's `Source revision or identity` ('{revision_value}') does not "
            "resolve to a local Git commit, so review freshness cannot be verified; "
            "ask-light fails closed rather than guessing an equivalence."
        ], ""
    source_value = _raw_field_line(charter_text, "Source")
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
        # directory afterwards — even untracked ones — change that baseline.
        if (root / relative).is_dir():
            directory_status = _run_git(root, "status", "--porcelain", "--", relative)
            if directory_status is None:
                return "unknown", [
                    f"Git could not inspect the reviewed directory '{relative}', so it cannot "
                    "be proven free of post-review additions."
                ], baseline
            if directory_status.returncode != 0:
                return "unknown", [
                    f"The freshness comparison for reviewed directory '{relative}' failed "
                    "(git error), so it cannot be proven unchanged."
                ], baseline
            if any(line.startswith("??") for line in directory_status.stdout.splitlines()):
                return "stale", [
                    f"A new file appeared inside the reviewed directory '{relative}' after the "
                    f"recorded revision ({short_baseline}); the frozen directory baseline no longer matches.",
                ], baseline
    return "current", [], baseline


def _reviewed_profile(charter_text: str) -> str:
    values = _field_values(charter_text, ("Profile",))
    return values[0] if values else ""


def _resolve_revision_chain(root: Path, revision_value: str) -> list[str]:
    """Resolve every locally verifiable Git commit cited by an identity value.

    Order is preserved so a producer that freezes both window endpoints
    (`Fixed point: <base> <candidate>`) yields [base, candidate]; duplicates of
    the same underlying commit collapse to one entry.
    """
    chain: list[str] = []
    for candidate in _HEX_REVISION_PATTERN.findall(revision_value):
        sha = _resolvable_git_commit(root, candidate)
        if sha and sha not in chain:
            chain.append(sha)
    return chain


def _classify_implementation_fixed_point(root: Path, charter_text: str) -> tuple[str, list[str]]:
    """Check the software Profile's reviewed implementation fixed point.

    Returns ("not-applicable"|"current"|"stale"|"unknown", gaps). A software
    review binds its verdict to TWO frozen baselines (profiles/software.md): the
    approved source Charter fields checked by `_classify_review_freshness`, plus
    the reviewed implementation fixed point recorded by the producer in the
    Charter `- Fixed point:` field. ask-light consumes that produced identity;
    it never invents a parallel format.

    Verification compares the current working tree against the reviewed fixed
    point exactly on the reviewed implementation window — the paths the fixed
    point's recorded change touched. Two values (<base> <candidate>) delimit
    that window directly; a single non-root value means the candidate's own
    change set relative to its parent. A single repository-first commit cannot
    delimit any window, and changes outside the window stay unrelated and can
    never invalidate acceptance, while drift inside it — committed or still
    uncommitted — stales the old verdict. A missing, unresolvable, or
    undeterminable fixed point fails closed.
    """
    if _reviewed_profile(charter_text) != "software":
        return "not-applicable", []
    fixed_value = _raw_field_line(charter_text, "Fixed point")
    if not fixed_value.strip():
        return "unknown", [
            "The Charter records the `software` review Profile but no `- Fixed point:` "
            "identity for the reviewed implementation; a software verdict may only be "
            "consumed together with the reviewed implementation baseline it froze."
        ]
    chain = _resolve_revision_chain(root, fixed_value)
    if not chain:
        return "unknown", [
            f"The Charter's `Fixed point` ('{fixed_value}') does not resolve to a local Git "
            "commit, so the reviewed implementation baseline cannot be verified; ask-light "
            "fails closed instead of accepting an unverifiable software review."
        ]
    candidate = chain[-1]
    short_candidate = candidate[:12]
    if len(chain) >= 2:
        window = _run_git(root, "diff", "--name-only", chain[0], candidate)
    else:
        parent = _resolvable_git_commit(root, f"{candidate}^", peel=False)
        if not parent:
            return "unknown", [
                f"The recorded fixed point ({short_candidate}) is a repository-first commit, so "
                "the reviewed implementation window cannot be delimited; freeze both window "
                "endpoints (<base> <candidate>) in the Charter `- Fixed point:` field."
            ]
        window = _run_git(root, "diff", "--name-only", parent, candidate)
    if window is None or window.returncode != 0:
        return "unknown", [
            "Git could not reconstruct the reviewed implementation window behind the "
            "recorded fixed point, so implementation freshness cannot be proven."
        ]
    reviewed_paths = [line for line in window.stdout.splitlines() if line.strip()]
    if not reviewed_paths:
        return "unknown", [
            f"The recorded fixed point ({short_candidate}) identifies no reviewed "
            "implementation content, so there is no reviewed baseline to verify against."
        ]
    for relative in reviewed_paths:
        difference = _run_git(root, "diff", "--quiet", candidate, "--", relative)
        if difference is None or difference.returncode not in (0, 1):
            return "unknown", [
                f"The implementation freshness comparison for '{relative}' failed (git error), "
                "so it cannot be proven that the reviewed implementation is unchanged."
            ]
        if difference.returncode == 1:
            return "stale", [
                f"The reviewed implementation '{relative}' changed after the fixed point "
                f"({short_candidate}) the software review froze, including uncommitted "
                "working-tree changes; the previous verdict no longer describes the "
                "current implementation.",
            ]
    return "current", []


def _project_review_dir(root: Path) -> Path | None:
    primary = root / PROJECT_REVIEW_DIRNAME
    if primary.is_dir():
        return primary
    legacy = root / LEGACY_PROJECT_REVIEW_DIRNAME
    return legacy if legacy.is_dir() else None


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
    source_value = _raw_field_line(charter_text, "Source")
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


def _acceptance_verdicts(text: str) -> list[str]:
    """Extract acceptance values, preferring verdict/result/outcome fields.

    Generic lifecycle `Status`/`State` values are only used when no explicit
    verdict field exists, so a `Status: complete` line cannot downgrade an
    explicit `Verdict: PASS`.
    """
    explicit = _field_values(text, ("Verdict", "Result", "Outcome", "Acceptance"))
    if explicit:
        return explicit
    return _field_values(text, ("Status", "State"))


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


def inspect_project_state(project_root: Path) -> dict[str, Any]:
    """Inspect a bounded set of real project evidence, not the whole repository.

    Returns a stage, completed/missing summaries, and the Light Skill that owns
    the next step when the evidence supports a deterministic recommendation.
    """
    root = project_root.resolve()
    evidence: dict[str, Any] = {
        "projectRoot": str(root),
        "initialized": False,
        "hasSpec": False,
        "hasTickets": False,
        "unresolvedTickets": False,
        "allTicketsResolved": False,
        "unknownTicketState": False,
        "hasAcceptanceEvidence": False,
        "acceptancePassed": False,
        "acceptanceFailed": False,
        "acceptanceUnknown": False,
        "specPaths": [],
        "ticketPaths": [],
        "acceptancePaths": [],
        "currentEffort": "",
        "ambiguousCurrentEffort": False,
        "stage": "",
        "skill": "",
        "reason": "",
        "completed": [],
        "missing": [],
        "gaps": [],
    }
    if not root.is_dir():
        evidence["stage"] = "unknown"
        evidence["reason"] = "project root is not readable"
        evidence["gaps"] = ["project root is not readable"]
        return evidence

    project_contract = root / "docs/agents/light-project.md"
    evidence["initialized"] = project_contract.is_file()

    if not evidence["initialized"]:
        evidence["stage"] = "uninitialized"
        evidence["skill"] = "project-init"
        evidence["reason"] = "No docs/agents/light-project.md exists; the repository has not been initialized for Light Project workflows."
        evidence["completed"] = []
        evidence["missing"] = ["Light project configuration and tracker contract"]
        evidence["gaps"] = []
        return evidence

    # Resolve the current/active effort before reading effort-owned evidence so
    # historical .scratch efforts cannot contaminate the current workflow state.
    current_effort, effort_failure, effort_gaps = _resolve_current_effort(root)
    evidence["currentEffort"] = current_effort or ""
    evidence["ambiguousCurrentEffort"] = bool(effort_failure)
    if effort_failure:
        evidence["stage"] = effort_failure
        evidence["skill"] = ""
        evidence["reason"] = (
            effort_gaps[0]
            if effort_gaps
            else "The current Light effort cannot be established reliably from repository evidence."
        )
        evidence["completed"] = ["Light project contract present"]
        evidence["missing"] = ["resolve which Light effort is current"]
        evidence["gaps"] = effort_gaps
        return evidence

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
    evidence["hasSpec"] = bool(spec_paths)
    evidence["specPaths"] = [str(path.relative_to(root)) for path in spec_paths[:10]]

    # Tickets: local-markdown issue files only, bounded to the current effort.
    if current_effort:
        issues_dir = root / ".scratch" / current_effort / "issues"
        ticket_paths = sorted(issues_dir.glob("*.md")) if issues_dir.is_dir() else []
    else:
        ticket_paths = []
    ticket_paths = [path for path in ticket_paths if path.is_file()]
    evidence["hasTickets"] = bool(ticket_paths)
    evidence["ticketPaths"] = [str(path.relative_to(root)) for path in ticket_paths[:20]]

    # Ticket completion is fail-closed. A missing status or a status outside the
    # known resolved/unresolved vocabulary is unknown, not resolved.
    statuses: list[str] = []
    unknown_ticket = False
    for ticket in ticket_paths:
        ticket_statuses = _field_values(_small_text(ticket), ("Status", "State"))
        if not ticket_statuses or any(
            status not in TICKET_RESOLVED_STATES and status not in TICKET_UNRESOLVED_STATES
            for status in ticket_statuses
        ):
            unknown_ticket = True
        statuses.extend(ticket_statuses)
    evidence["unknownTicketState"] = unknown_ticket
    evidence["unresolvedTickets"] = any(status in TICKET_UNRESOLVED_STATES for status in statuses)
    evidence["allTicketsResolved"] = (
        bool(ticket_paths)
        and not unknown_ticket
        and bool(statuses)
        and all(status in TICKET_RESOLVED_STATES for status in statuses)
        and not evidence["unresolvedTickets"]
    )

    # Acceptance/review evidence: the canonical `project-review` durable state.
    # The record is authoritative only when the Charter's Source proves it
    # reviewed the resolved current effort AND the reviewed source still
    # matches the Charter's frozen `Source revision or identity`. Verdicts from
    # historical efforts are ignored for current acceptance; records whose
    # ownership or freshness cannot be proven fail closed. Legacy human-facing
    # verdict files are never aggregated here.
    review_dir = _project_review_dir(root)
    review_ownership = ""
    review_gaps: list[str] = []
    review_freshness = ""
    freshness_gaps: list[str] = []
    acceptance_paths: list[Path] = []
    if review_dir is not None:
        review_ownership, review_gaps = _classify_review_ownership(review_dir, root, current_effort)
        if review_ownership == "current":
            conclusion = review_dir / "verdict.md"
            if conclusion.is_file():
                # A verdict applies only to the baseline it reviewed; decide
                # freshness before any verdict interpretation trusts it.
                charter_text = _small_text(review_dir / "charter.md")
                review_freshness, freshness_gaps, _baseline = _classify_review_freshness(
                    root, charter_text
                )
                if review_freshness == "current":
                    # Source freshness alone is not the whole software contract:
                    # a software Profile additionally binds its verdict to the
                    # reviewed implementation fixed point it froze.
                    fixed_point_state, fixed_point_gaps = _classify_implementation_fixed_point(
                        root, charter_text
                    )
                    if fixed_point_state in ("stale", "unknown"):
                        review_freshness = fixed_point_state
                        freshness_gaps = fixed_point_gaps
                if review_freshness == "current":
                    acceptance_paths = [conclusion]
                    evidence["hasAcceptanceEvidence"] = True
                    evidence["acceptancePaths"] = [str(conclusion.relative_to(root))]
        elif review_gaps:
            evidence["gaps"].extend(review_gaps)

    acceptance_pass = 0
    acceptance_fail = 0
    acceptance_unknown = 0
    for path in acceptance_paths:
        verdicts = _acceptance_verdicts(_small_text(path))
        if not verdicts:
            acceptance_unknown += 1
            continue
        for verdict in verdicts:
            if verdict in ACCEPTANCE_PASS_STATES:
                acceptance_pass += 1
            elif verdict in ACCEPTANCE_FAIL_STATES:
                acceptance_fail += 1
            else:
                acceptance_unknown += 1
    evidence["acceptancePassed"] = bool(acceptance_paths) and acceptance_pass > 0 and acceptance_fail == 0 and acceptance_unknown == 0
    evidence["acceptanceFailed"] = acceptance_fail > 0
    evidence["acceptanceUnknown"] = acceptance_unknown > 0

    if not evidence["hasSpec"]:
        contract_text = _small_text(project_contract)
        has_goal = bool(re.search(r"(?im)^-\s*Goal:\s*(?!\?|\(none recorded\)|$)\S", contract_text))
        has_outputs = bool(re.search(r"(?im)^-\s*Outputs:\s*(?!\(none recorded\)|$)\S", contract_text))
        goal_state = "clear goal and outputs are recorded" if (has_goal and has_outputs) else "goal/outputs are missing or unclear"
        if goal_state.startswith("clear"):
            skill, stage, missing = "project-spec", "initialized-no-spec", ["approved SPEC with acceptance criteria"]
            reason = "The Light project contract exists and records a goal, but no active SPEC is present. `project-spec` owns turning the recorded goal and constraints into a traceable SPEC."
        else:
            skill, stage, missing = "project-clarify", "initialized-unclear", ["clarified goal and constraints before a SPEC can be written"]
            reason = "The Light project contract exists but does not yet give `project-spec` a clear goal/outputs base. `project-clarify` owns resolving the remaining user-owned decisions first."
        evidence["stage"] = stage
        evidence["skill"] = skill
        evidence["reason"] = reason
        evidence["completed"] = ["Light project contract present"]
        evidence["missing"] = missing
        evidence["gaps"] = []
        return evidence

    if not evidence["hasTickets"]:
        evidence["stage"] = "spec-no-tickets"
        evidence["skill"] = "project-tickets"
        evidence["reason"] = "A stable SPEC exists but no implementation tickets are present. `project-tickets` owns slicing the SPEC into dependency-ordered, unblocked work items."
        evidence["completed"] = ["Light project contract", "active SPEC"]
        evidence["missing"] = ["implementation tickets and unblocked frontier"]
        evidence["gaps"] = []
        return evidence

    if evidence["unresolvedTickets"]:
        evidence["stage"] = "work-in-progress"
        evidence["skill"] = "implement"
        evidence["reason"] = "Implementation tickets exist and at least one remains unresolved. `implement` owns executing the next ready, unblocked ticket."
        evidence["completed"] = ["Light project contract", "active SPEC", "ticket graph"]
        evidence["missing"] = ["completion of the unresolved ticket(s)"]
        evidence["gaps"] = []
        return evidence

    if evidence["unknownTicketState"]:
        evidence["stage"] = "tickets-unknown"
        evidence["skill"] = ""
        evidence["reason"] = (
            "Ticket files exist but their completion state cannot be established from repository evidence. "
            "At least one ticket has no Status field or uses a status outside the known resolved/unresolved "
            "vocabulary, so `ask-light` cannot claim implementation is complete."
        )
        evidence["completed"] = ["Light project contract", "active SPEC", "ticket files present"]
        evidence["missing"] = ["reliable ticket completion state"]
        evidence["gaps"] = [evidence["reason"]]
        return evidence

    # A durable review whose ownership cannot be proven for the current effort
    # fails closed even though implementation looks finished.
    if review_dir is not None and review_ownership == "unresolvable":
        reason = (
            "A `.project-review` durable record exists but its ownership cannot be established from the "
            "Charter's `Source:` line, so `ask-light` cannot prove the verdict belongs to the current effort. "
            "Fail closed: link the review by recording the reviewed SPEC path "
            f"(`.scratch/{current_effort or '<effort>'}/spec.md`) in the Charter `Source:`."
        )
        evidence["stage"] = "review-ownership-unknown"
        evidence["skill"] = ""
        evidence["reason"] = reason
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["missing"] = ["review ownership proven for the current effort"]
        evidence["gaps"] = [*evidence["gaps"], reason]
        return evidence

    # A verdict binds to the baseline revision it reviewed. A verified change
    # since that revision routes back to project-review for a fresh review,
    # whatever the old verdict said; PASS stops being accepted and FAIL/BLOCKED
    # stop being authoritative.
    if review_ownership == "current" and review_freshness == "stale":
        detail = freshness_gaps[0] if freshness_gaps else "the reviewed source changed after the recorded revision."
        reason = (
            "The current effort has changed since the recorded project-review baseline. "
            "The previous verdict no longer proves the current state is accepted; run a "
            f"fresh `project-review` for the current baseline. {detail}"
        )
        evidence["stage"] = "review-stale"
        evidence["skill"] = "project-review"
        evidence["reason"] = reason
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved", "recorded project-review baseline exists"]
        evidence["missing"] = ["a fresh project-review verdict for the changed baseline"]
        evidence["gaps"] = [*evidence["gaps"], *freshness_gaps]
        return evidence

    if review_ownership == "current" and review_freshness == "unknown":
        reason = (
            "A `.project-review` verdict exists for the current effort, but its freshness "
            "cannot be verified against the frozen `Source revision or identity` baseline, "
            "so `ask-light` neither accepts nor reports the old verdict as current. Fail closed: "
            "re-freeze a verifiable baseline with `project-review`."
        )
        evidence["stage"] = "review-freshness-unknown"
        evidence["skill"] = ""
        evidence["reason"] = reason
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["missing"] = ["a verifiable frozen baseline behind the recorded review"]
        evidence["gaps"] = [*evidence["gaps"], *freshness_gaps]
        return evidence

    if not evidence["hasAcceptanceEvidence"]:
        evidence["stage"] = "implementation-complete"
        evidence["skill"] = "project-review"
        evidence["reason"] = "Implementation tickets are resolved but no acceptance/review verdict evidence is present. `project-review` owns final acceptance against the frozen baseline."
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["missing"] = ["final acceptance/review verdict evidence"]
        evidence["gaps"] = []
        return evidence

    if not evidence["acceptancePassed"]:
        if evidence["acceptanceFailed"]:
            evidence["stage"] = "acceptance-not-passed"
            evidence["reason"] = (
                "Acceptance evidence exists but reports a FAIL, BLOCKED, rejected, incomplete, or pending "
                "verdict. This is not a successful acceptance, so `ask-light` does not mark the workflow complete."
            )
            evidence["missing"] = ["successful acceptance verdict"]
        else:
            evidence["stage"] = "acceptance-unknown"
            evidence["reason"] = (
                "Acceptance evidence exists but a clear PASS verdict cannot be established from the repository "
                "evidence. `ask-light` therefore does not claim the project is accepted."
            )
            evidence["missing"] = ["verifiable acceptance PASS verdict"]
        evidence["skill"] = ""
        evidence["completed"] = ["Light project contract", "active SPEC", "tickets resolved"]
        evidence["gaps"] = [evidence["reason"]]
        return evidence

    evidence["stage"] = "accepted"
    evidence["skill"] = ""
    evidence["reason"] = "The current Light workflow is complete: the project is initialized, has an active SPEC, all implementation tickets are explicitly resolved, and acceptance evidence explicitly passes."
    evidence["completed"] = [
        "project initialized",
        "SPEC completed",
        "tickets resolved",
        "implementation completed",
        "acceptance passed",
    ]
    evidence["missing"] = []
    evidence["gaps"] = []
    return evidence


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


def base_result(mode: str, status: str, gaps: list[str]) -> dict[str, Any]:
    return {
        "mode": mode,
        "status": status,
        "skill": "",
        "source": "",
        "reason": "",
        "invocation": "",
        "confidence": "low",
        "alternative": None,
        "gaps": gaps,
        "reads": {"metadata": 0, "bodies": 0, "references": 0},
        "candidates": [],
        "next": "awaiting-approval",
        "execution": "recommendation phase was read-only; execution begins only after explicit user approval",
        "projectStage": "",
        "completed": [],
        "missing": [],
    }


def workflow_base_result(status: str, gaps: list[str]) -> dict[str, Any]:
    result = base_result("workflow", status, gaps)
    result.update({
        "workflow": "",
        "entryCondition": "",
        "steps": [],
        "stoppingBoundary": "",
        "missingDependency": "",
        "finalAuthority": "",
    })
    return result


def _known_skill(skill_map: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((entry for entry in skill_map["skills"] if entry["name"].lower() == name.lower()), None)


def navigate_result(skill_map: dict[str, Any], query: str, host: str = "codex") -> dict[str, Any]:
    """Resolve collection-navigation intent with explicit family/skill parsing.

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

def next_result(roots: list[dict[str, Any]], context: dict[str, Any], host: str, skill_map: dict[str, Any]) -> dict[str, Any]:
    project_root_value = context.get("projectRoot") or context.get("cwd")
    project_state: dict[str, Any] = {}
    if project_root_value:
        project_state = inspect_project_state(Path(str(project_root_value)))

    goal = str(context.get("goal") or "")
    task_kind = str(context.get("taskKind") or "")
    # Terminating and evidence-blocked project stages are valid conclusions even
    # when no next Skill is recommended. Do not let them fall through into a
    # generic NEED-INPUT or unrelated logical route. (`review-stale` is NOT
    # listed: its next step is clearly another project-review run.)
    if project_state.get("stage") in {
        "accepted", "tickets-unknown", "acceptance-not-passed", "acceptance-unknown",
        "ambiguous-current-effort", "contradictory-current-effort",
        "review-ownership-unknown", "review-freshness-unknown",
    }:
        status = "RECOMMEND" if project_state.get("stage") == "accepted" else "NEED-INPUT"
        result = base_result("next", status, project_state.get("gaps", []))
        result.update({
            "skill": "",
            "reason": project_state.get("reason", ""),
            "invocation": "",
            "projectStage": project_state.get("stage", ""),
            "completed": project_state.get("completed", []),
            "missing": project_state.get("missing", []),
        })
        result["next"] = "no-execution"
        return result

    project_state_intent = bool(goal and PROJECT_STATE_INTENT_PATTERN.search(goal))
    state_driven = bool(
        project_state.get("stage")
        and project_state.get("skill")
        and not task_kind
        and (not goal or project_state_intent)
    )
    if not goal and not task_kind and not state_driven:
        return base_result("next", "NEED-INPUT", ["Provide goal, taskKind, or a projectRoot with enough evidence to derive the current stage."])
    control = str(context.get("invocationControl", ""))
    if control not in INVOCATION_CONTROLS:
        return base_result("next", "NEED-INPUT", ["invocationControl must be explicit-only, model-callable, or either."])

    if state_driven:
        logical_name = project_state["skill"]
        logical = next((entry for entry in skill_map["skills"] if entry["name"] == logical_name), None)
        if logical is None:
            return base_result("next", "BLOCKED", [f"Derived project stage names an unknown Light Skill: {logical_name}"])
        reason = project_state.get("reason", "Derived from real project evidence.")
        evidence = [f"project-state:{project_state['stage']}->{logical_name}"]
    else:
        ranking = logical_ranking(skill_map, context)
        if not ranking or ranking[0]["logicalScore"] <= 0:
            return base_result("next", "NEED-INPUT", ["No reliable Light route matches the supplied intent."])
        tied = [item["name"] for item in ranking if item["logicalScore"] == ranking[0]["logicalScore"]]
        if len(tied) > 1:
            return base_result("next", "NEED-INPUT", [f"Material Light route tie: {', '.join(tied)}. Provide the intended outcome or project stage."])
        logical = ranking[0]
        reason = f"Light Skill Map matched: {', '.join(logical['matchedPatterns'] + logical['matchedPrecedence'])}"
        if logical["matchedTaskKind"]:
            reason += f"; taskKind:{logical['matchedTaskKind']}->{logical['name']}"
        evidence = logical["matchedPatterns"] + logical["matchedPrecedence"]
        if logical["matchedTaskKind"]:
            evidence.append(f"taskKind:{logical['matchedTaskKind']}->{logical['name']}")

    policy = availability_policy(context, host)
    candidates, gaps, metadata_reads = discover(roots, skill_map, policy)
    selected_name = logical["name"]
    installed = sorted(
        [item for item in candidates if item["name"] == selected_name and item["availabilityStatus"] == "available"],
        key=lambda item: item["packagePath"],
    )
    if not installed:
        result = base_result("next", "BLOCKED", gaps + [f"{selected_name}: known Light Skill is not available on this host."])
        result.update({
            "skill": selected_name,
            "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0},
            "candidates": candidates,
            "projectStage": project_state.get("stage", ""),
            "completed": project_state.get("completed", []),
            "missing": project_state.get("missing", []),
        })
        return result
    if len(installed) > 1:
        result = base_result("next", "BLOCKED", gaps + [f"{selected_name}: multiple available first-party copies require host precedence evidence."])
        result.update({
            "skill": selected_name,
            "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0},
            "candidates": candidates,
            "projectStage": project_state.get("stage", ""),
            "completed": project_state.get("completed", []),
            "missing": project_state.get("missing", []),
        })
        return result
    selected = installed[0]
    if not invocation_compatible(selected["invocationType"], control):
        result = base_result(
            "next",
            "BLOCKED",
            gaps + [f"{selected_name}: {selected['invocationType']} is incompatible with invocationControl={control}."],
        )
        result.update({
            "skill": selected_name,
            "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0},
            "candidates": candidates,
            "projectStage": project_state.get("stage", ""),
            "completed": project_state.get("completed", []),
            "missing": project_state.get("missing", []),
        })
        return result
    body_reads, reference_reads, read_error = validate_selected(selected)
    selected["readStatus"] = "unavailable" if read_error else "available"
    if read_error:
        result = base_result("next", "BLOCKED", gaps + [f"{selected_name}: {read_error}; restore the first-party package."])
        result.update({
            "skill": selected_name,
            "reads": {"metadata": metadata_reads, "bodies": body_reads, "references": reference_reads},
            "candidates": candidates,
            "projectStage": project_state.get("stage", ""),
            "completed": project_state.get("completed", []),
            "missing": project_state.get("missing", []),
        })
        return result

    result = {
        "mode": "next",
        "status": "RECOMMEND",
        "skill": selected_name,
        "source": f"first-party: {selected['packagePath']}",
        "reason": reason,
        "invocation": invocation(selected_name, policy["host"]),
        "confidence": "high",
        "alternative": None,
        "gaps": gaps,
        "reads": {"metadata": metadata_reads, "bodies": body_reads, "references": reference_reads},
        "candidates": candidates,
        "next": "awaiting-approval",
        "execution": "recommendation phase was read-only; execution begins only after explicit user approval",
        "projectStage": project_state.get("stage", ""),
        "completed": project_state.get("completed", []),
        "missing": project_state.get("missing", []),
    }
    return result
def approval_transition(result: dict[str, Any], skill_map: dict[str, Any]) -> dict[str, Any]:
    """Compute the honest post-approval state for a recommendation result.

    Repository policy is authoritative: a user-invoked Skill (frontmatter
    `disable-model-invocation: true`) must not be auto-invoked by another
    Skill. `ask-light` is user-invoked, so after approval it cannot begin a
    user-invoked target itself; it renders the exact invocation and asks the
    user to start it. A model-invoked target may begin in the current
    conversation when the host supports it.
    """
    if result.get("status") != "RECOMMEND" or not result.get("skill"):
        updated = dict(result)
        updated["next"] = "no-execution"
        return updated
    skill_name = result["skill"]
    candidate = next((item for item in result.get("candidates", []) if item["name"] == skill_name), None)
    invocation_type = candidate.get("invocationType", "unknown") if candidate else "unknown"
    updated = dict(result)
    if invocation_type == "model-invoked":
        updated["next"] = f"beginning-{skill_name}"
        updated["execution"] = "user approved; the model-invoked target may begin in this conversation."
    else:
        updated["next"] = "host-transition-required"
        updated["execution"] = (
            "User approved, but repository policy forbids a user-invoked Skill from auto-invoking another "
            "user-invoked Skill. `ask-light` cannot begin the target itself; render the exact invocation "
            "and have the user start it."
        )
    return updated



def workflow_result(roots: list[dict[str, Any]], context: dict[str, Any], host: str, skill_map: dict[str, Any]) -> dict[str, Any]:
    required = [
        key
        for key in ("goal", "artifacts", "blockers", "projectType", "taskKind", "availability", "invocationControl")
        if key not in context
        or context.get(key) is None
        or (key != "blockers" and context.get(key) in ("", {}))
    ]
    if required:
        return workflow_base_result("NEED-INPUT", [f"Provide reliable workflow context: {', '.join(required)}."])
    control = str(context.get("invocationControl", ""))
    if control not in INVOCATION_CONTROLS:
        return workflow_base_result("NEED-INPUT", ["invocationControl must be explicit-only, model-callable, or either."])
    text = context_text(context)
    project_type, task_kind = str(context["projectType"]).lower(), str(context["taskKind"]).lower()
    recipes = [item for item in skill_map["workflows"] if project_type in item["projectTypes"] and task_kind in item["taskKinds"] and any(re.search(pattern, text, re.I) for pattern in item["patterns"])]
    if not recipes:
        return workflow_base_result("NEED-INPUT", ["No reliable workflow recipe matches the supplied context."])
    recipes.sort(key=lambda item: (len(item["projectTypes"]), item["id"]))
    if len(recipes) > 1 and len(recipes[0]["projectTypes"]) == len(recipes[1]["projectTypes"]):
        return workflow_base_result("NEED-INPUT", [f"Material workflow tie: {recipes[0]['id']}, {recipes[1]['id']}. Provide the intended stopping boundary."])
    policy = availability_policy(context, host)
    candidates, gaps, metadata_reads = discover(roots, skill_map, policy)
    available_groups: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        if candidate["availabilityStatus"] == "available":
            available_groups.setdefault(candidate["name"], []).append(candidate)
    recipe = recipes[0]
    step_names = [step["skill"] for step in recipe["steps"]]
    duplicates = sorted({name for name in step_names if len(available_groups.get(name, [])) > 1})
    body_reads = 0
    reference_reads = 0
    for name in sorted(set(step_names).difference(duplicates)):
        group = available_groups.get(name, [])
        if len(group) != 1:
            continue
        candidate = group[0]
        body_count, reference_count, read_error = validate_selected(candidate)
        body_reads += body_count
        reference_reads += reference_count
        candidate["readStatus"] = "unavailable" if read_error else "available"
        if read_error:
            candidate["availabilityStatus"] = "unavailable"
            candidate["availabilityError"] = read_error
            gaps.append(f"{name}: {read_error}")
            del available_groups[name]
    missing = sorted({name for name in step_names if name not in available_groups})
    incompatible = sorted({
        name for name in step_names
        if len(available_groups.get(name, [])) == 1
        and not invocation_compatible(available_groups[name][0]["invocationType"], control)
    })
    steps = [{
        "skill": step["skill"],
        "sourceCategory": "first-party",
        "invocationType": (
            available_groups[step["skill"]][0]["invocationType"]
            if len(available_groups.get(step["skill"], [])) == 1 else "unknown"
        ),
        "invocation": invocation(step["skill"], policy["host"]),
        "availability": "ambiguous" if step["skill"] in duplicates else ("incompatible" if step["skill"] in incompatible else ("available" if step["skill"] in available_groups else "unavailable")),
        "expectedInput": step["expectedInput"],
        "expectedOutput": step["expectedOutput"],
        "handoffArtifact": step["handoffArtifact"],
        "stopCondition": step["stopCondition"],
        "optional": step.get("optional", False),
        "missingDependency": step["skill"] if step["skill"] in missing or step["skill"] in duplicates else "",
    } for step in recipe["steps"]]
    blocked = bool(missing or duplicates or incompatible)
    workflow_gaps = gaps
    if missing:
        workflow_gaps += [f"Missing Light Skills: {', '.join(missing)}"]
    if duplicates:
        workflow_gaps += [f"Duplicate first-party workflow steps require host precedence evidence: {', '.join(duplicates)}"]
    if incompatible:
        workflow_gaps += [f"Invocation control {control} is incompatible with user-invoked workflow steps: {', '.join(incompatible)}"]
    first_group = available_groups.get(step_names[0], [])
    top_missing = (missing or duplicates or incompatible or [""])[0]
    result = base_result("workflow", "BLOCKED" if blocked else "RECOMMEND", workflow_gaps)
    result.update({
        "skill": step_names[0] if not blocked else "",
        "source": f"first-party: {first_group[0]['packagePath']}" if len(first_group) == 1 else "",
        "reason": f"Light workflow map matched: {recipe['id']}",
        "invocation": invocation(step_names[0], policy["host"]) if len(first_group) == 1 else "",
        "confidence": "low" if blocked else "high",
        "workflow": recipe["id"],
        "entryCondition": f"{project_type}/{task_kind}",
        "steps": steps,
        "stoppingBoundary": recipe["stoppingBoundary"],
        "missingDependency": top_missing,
        "finalAuthority": recipe["finalAuthority"],
        "reads": {"metadata": metadata_reads, "bodies": body_reads, "references": reference_reads},
        "candidates": candidates,
    })
    return result


def route(roots: list[dict[str, Any]] | None, context: dict[str, Any], host: str = "codex", mode: str = "next") -> dict[str, Any]:
    skill_map = load_map()
    if roots is None or not roots:
        roots = discover_roots()
    if mode == "workflow":
        return workflow_result(roots, context, host, skill_map)
    if mode == "navigate":
        return navigate_result(skill_map, str(context.get("goal", "")), host)
    return next_result(roots, context, host, skill_map)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots-json", default="[]")
    parser.add_argument("--context-json", required=True)
    parser.add_argument("--host-name", default="codex")
    parser.add_argument("--mode", choices=("next", "workflow", "navigate"), default="next")
    args = parser.parse_args()
    print(json.dumps(route(json.loads(args.roots_json), json.loads(args.context_json), args.host_name, args.mode), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())