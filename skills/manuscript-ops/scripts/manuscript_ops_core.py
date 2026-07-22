#!/usr/bin/env python3
"""Shared, dependency-free helpers for manuscript-ops read-only tools."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1"

DIMENSIONS = (
    "scale",
    "source_complexity",
    "risk",
    "output_complexity",
    "collaboration",
    "reproducibility",
)

HARD_TRIGGERS = (
    "explicit_project",
    "cross_session",
    "large_volume",
    "high_risk_facts",
    "locked_derivatives",
    "reproducible_multi_format",
    "independent_multi_thread_acceptance",
)

SKIP_DIRS = {
    ".git",
    ".jj",
    ".hg",
    ".svn",
    ".tmp",
    ".venv",
    "build",
    "dist",
    "node_modules",
    "__pycache__",
}

SOURCE_GROUPS = {
    "text": {".txt", ".md", ".markdown", ".rst", ".tex", ".rtf"},
    "office": {".docx", ".pdf", ".odt", ".pptx", ".odp", ".xlsx", ".ods", ".csv"},
    "image": {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".svg"},
    "audio": {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "web": {".html", ".htm", ".mhtml", ".eml", ".msg", ".epub"},
}

DATE_VERSION_RE = re.compile(r"(?<!\d)(\d{4}\.\d{2}\.\d{2})(?:-(\d{2}))?(?!\d)")


class ContractError(ValueError):
    """Raised when an input violates a public manuscript-ops contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ContractError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ContractError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _should_skip(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in relative.parts)


def inspect_repository(root: Path, max_files: int = 5000) -> dict[str, Any]:
    """Inspect file metadata only; never read manuscript contents."""
    root = root.resolve()
    if not root.exists():
        raise ContractError(f"project root does not exist: {root}")
    if not root.is_dir():
        raise ContractError(f"project root is not a directory: {root}")

    count = 0
    total_bytes = 0
    extensions: dict[str, int] = {}
    source_groups: set[str] = set()
    markers: list[str] = []
    truncated = False

    marker_names = {
        "AGENTS.md",
        "README.md",
        "IMPLEMENTATION_PLAN.md",
        "SOURCE_MAP.md",
        "pyproject.toml",
        "package.json",
    }

    for path in root.rglob("*"):
        if _should_skip(path, root) or not path.is_file():
            continue
        count += 1
        if count > max_files:
            truncated = True
            count = max_files
            break
        try:
            total_bytes += path.stat().st_size
        except OSError:
            pass
        suffix = path.suffix.lower() or "<none>"
        extensions[suffix] = extensions.get(suffix, 0) + 1
        for group, suffixes in SOURCE_GROUPS.items():
            if suffix in suffixes:
                source_groups.add(group)
        if path.name in marker_names:
            markers.append(path.relative_to(root).as_posix())

    vcs = []
    if (root / ".jj" / "repo").exists():
        vcs.append(".jj")
    if (root / ".git").is_file() or (root / ".git" / "HEAD").is_file():
        vcs.append(".git")
    if (root / ".hg" / "requires").is_file():
        vcs.append(".hg")
    if (root / ".svn" / "wc.db").is_file():
        vcs.append(".svn")

    ordered_extensions = sorted(extensions.items(), key=lambda item: (-item[1], item[0]))
    return {
        "file_count": count,
        "total_bytes": total_bytes,
        "extensions": dict(ordered_extensions[:25]),
        "source_groups": sorted(source_groups),
        "markers": sorted(markers),
        "version_control_markers": vcs,
        "scan_truncated": truncated,
        "max_files": max_files,
    }


def _automatic_dimensions(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    file_count = int(evidence["file_count"])
    total_bytes = int(evidence["total_bytes"])
    groups = list(evidence["source_groups"])

    if file_count <= 2 and total_bytes <= 1_000_000:
        scale_score = 0
    elif file_count <= 40 and total_bytes <= 20_000_000:
        scale_score = 1
    else:
        scale_score = 2

    if len(groups) <= 1 and file_count <= 2:
        source_score = 0
    elif len(groups) <= 3:
        source_score = 1
    else:
        source_score = 2

    dimensions = {
        name: {
            "score": None,
            "effective_score": 1,
            "unknown": True,
            "evidence": [
                "not established by read-only repository metadata; user evidence required"
            ],
        }
        for name in DIMENSIONS
    }
    dimensions["scale"].update(
        {
            "score": scale_score,
            "effective_score": scale_score,
            "unknown": False,
            "evidence": [
                f"{file_count} files",
                f"{total_bytes} bytes",
                f"scan_truncated={evidence['scan_truncated']}",
            ],
        }
    )
    dimensions["source_complexity"].update(
        {
            "score": source_score,
            "effective_score": source_score,
            "unknown": False,
            "evidence": [f"source groups: {', '.join(groups) if groups else 'none observed'}"],
        }
    )
    return dimensions


def _normalize_dimension(name: str, raw: Any, fallback: dict[str, Any]) -> dict[str, Any]:
    if raw is None:
        return fallback
    if isinstance(raw, int):
        raw = {"score": raw}
    if not isinstance(raw, dict):
        raise ContractError(f"dimension {name!r} must be an integer, object, or null")

    score = raw.get("score")
    if score is not None and (isinstance(score, bool) or score not in (0, 1, 2)):
        raise ContractError(f"dimension {name!r} score must be 0, 1, 2, or null")
    evidence = raw.get("evidence", fallback.get("evidence", []))
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise ContractError(f"dimension {name!r} evidence must be a list of strings")
    if score is None:
        return {
            "score": None,
            "effective_score": 1,
            "unknown": True,
            "evidence": evidence,
        }
    return {
        "score": score,
        "effective_score": score,
        "unknown": False,
        "evidence": evidence,
    }


def select_route(
    dimensions: dict[str, dict[str, Any]],
    hard_triggers: dict[str, bool | None],
    unknowns: Iterable[str],
) -> tuple[int, str, list[str], bool]:
    """Recompute the route from normalized public-contract values."""
    total = sum(int(item["effective_score"]) for item in dimensions.values())
    active_triggers = [name for name, value in hard_triggers.items() if value is True]
    unresolved_triggers = [name for name, value in hard_triggers.items() if value is None]
    boundary_escalation = bool(set(unknowns)) and total in (3, 7)
    # An unresolved hard trigger cannot safely be treated as false. Unlike an
    # unknown scored dimension, any one of these conditions would independently
    # force the Project route if confirmed.
    if (
        active_triggers
        or unresolved_triggers
        or total >= 8
        or (total == 7 and boundary_escalation)
    ):
        route = "Project"
    elif total >= 4 or (total == 3 and boundary_escalation):
        route = "Structured"
    else:
        route = "Quick"
    return total, route, active_triggers, boundary_escalation


def build_routing_snapshot(
    root: Path,
    answers: dict[str, Any] | None = None,
    captured_at: str | None = None,
    max_files: int = 5000,
) -> dict[str, Any]:
    repository_evidence = inspect_repository(root, max_files=max_files)
    dimensions = _automatic_dimensions(repository_evidence)
    answers = answers or {}
    answer_dimensions = answers.get("dimensions", {})
    if not isinstance(answer_dimensions, dict):
        raise ContractError("dimensions must be an object")
    for name in DIMENSIONS:
        dimensions[name] = _normalize_dimension(
            name,
            answer_dimensions.get(name),
            dimensions[name],
        )

    raw_triggers = answers.get("hard_triggers", {})
    if not isinstance(raw_triggers, dict):
        raise ContractError("hard_triggers must be an object")
    hard_triggers: dict[str, bool | None] = {}
    for name in HARD_TRIGGERS:
        value = raw_triggers.get(name)
        if not (isinstance(value, bool) or value is None):
            raise ContractError(f"hard trigger {name!r} must be true, false, or null")
        hard_triggers[name] = value

    derived_triggers: dict[str, bool] = {}
    if dimensions["scale"]["score"] is not None:
        derived_triggers["large_volume"] = dimensions["scale"]["score"] == 2
    if dimensions["risk"]["score"] is not None:
        derived_triggers["high_risk_facts"] = dimensions["risk"]["score"] == 2
    for name, active in derived_triggers.items():
        if active and name in raw_triggers and raw_triggers[name] is False:
            raise ContractError(
                f"hard trigger {name!r} cannot be false when its paired dimension scores 2"
            )
        if active:
            hard_triggers[name] = True
        elif name not in raw_triggers:
            hard_triggers[name] = False

    unknowns = list(answers.get("unknowns", []))
    if not all(isinstance(item, str) for item in unknowns):
        raise ContractError("unknowns must be a list of strings")
    for name, value in dimensions.items():
        if value["unknown"] and name not in unknowns:
            unknowns.append(name)
    for name, value in hard_triggers.items():
        if value is None and f"hard_trigger:{name}" not in unknowns:
            unknowns.append(f"hard_trigger:{name}")

    total, route, active_triggers, boundary_escalation = select_route(
        dimensions,
        hard_triggers,
        unknowns,
    )

    reasons = [f"effective six-dimension total is {total}"]
    if active_triggers:
        reasons.append(f"hard trigger(s): {', '.join(active_triggers)}")
    unresolved_triggers = [
        name for name, value in hard_triggers.items() if value is None
    ]
    if unresolved_triggers:
        reasons.append(
            "unresolved hard trigger(s) require Project: "
            + ", ".join(unresolved_triggers)
        )
    if boundary_escalation:
        reasons.append("unknown item at a routing boundary requires upward routing")
    if unknowns:
        reasons.append(f"unknowns preserved: {', '.join(sorted(set(unknowns)))}")

    next_actions = {
        "Quick": ("perform_bounded_task", None),
        "Structured": ("prepare_lightweight_brief_and_review_plan", None),
        "Project": (
            "handoff_discovery",
            "Activate grill-me for one-session decisions or wayfinder for multi-session fog using host syntax; then activate manuscript-ops with resume.",
        ),
    }
    next_action, next_invocation = next_actions[route]

    return {
        "schema_version": SCHEMA_VERSION,
        "captured_at": captured_at or utc_now(),
        "root": str(root.resolve()),
        "dimensions": dimensions,
        "hard_triggers": hard_triggers,
        "repository_evidence": repository_evidence,
        "unknowns": sorted(set(unknowns)),
        "total": total,
        "route": route,
        "reasons": reasons,
        "next_action": next_action,
        "next_invocation": next_invocation,
    }


def extract_date_versions(values: Iterable[str]) -> set[str]:
    versions: set[str] = set()
    for value in values:
        for match in DATE_VERSION_RE.finditer(value):
            base, suffix = match.groups()
            try:
                date.fromisoformat(base.replace(".", "-"))
            except ValueError:
                continue
            if suffix is not None and int(suffix) < 2:
                continue
            versions.add(base if suffix is None else f"{base}-{suffix}")
    return versions


def next_date_version(base_date: str, existing_values: Iterable[str]) -> str:
    try:
        date.fromisoformat(base_date.replace(".", "-"))
    except ValueError as exc:
        raise ContractError("date must use a valid YYYY.MM.DD value") from exc
    if not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", base_date):
        raise ContractError("date must use YYYY.MM.DD")

    existing = extract_date_versions(existing_values)
    same_day = {
        version
        for version in existing
        if version == base_date or version.startswith(f"{base_date}-")
    }
    if not same_day:
        return base_date
    observed_suffixes = [
        1 if version == base_date else int(version.rsplit("-", 1)[1])
        for version in same_day
    ]
    suffix = max(2, max(observed_suffixes) + 1)
    return f"{base_date}-{suffix:02d}"


def ensure_within_root(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    resolved = (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ContractError(f"path escapes project root: {candidate}") from exc
    return resolved


def dump_json(data: Any, pretty: bool = True) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2 if pretty else None,
        sort_keys=False,
    )
