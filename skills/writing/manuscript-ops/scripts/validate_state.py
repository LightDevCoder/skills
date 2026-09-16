#!/usr/bin/env python3
"""Validate manuscript-ops state without changing the project."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from manuscript_ops_core import (
    ContractError,
    DIMENSIONS,
    HARD_TRIGGERS,
    dump_json,
    ensure_within_root,
    load_json,
    parse_timestamp,
    select_route,
    sha256_file,
    utc_now,
)
from probe_capabilities import (
    DERIVED_ALIAS_PARENTS,
    PROCESS_OPERATIONS,
    adapter_status as recompute_adapter_status,
    load_platform_capabilities,
    observe as observe_process_capabilities,
)

CANONICAL_FORMAT_REGISTRY = (
    Path(__file__).resolve().parents[1] / "assets" / "format-registry.json"
)
CANONICAL_CAPABILITY_MAP = (
    Path(__file__).resolve().parents[1] / "assets" / "platform-capability-map.json"
)
CANONICAL_ADAPTER_FIELDS = {
    "format",
    "tier",
    "extensions",
    "media_types",
    "operations",
    "required_dependencies",
    "optional_dependencies",
    "validation_dependencies",
    "blocking_qa_gaps",
    "validation",
    "degradation",
}
ALLOWED_ORIGINS = {"资料发现", "用户决定", "规则推导"}
ALLOWED_CAPABILITIES = {"supported", "conditional", "unsupported", "not_applicable"}
OPERATION_KEYS = {"read", "edit", "generate", "render", "visual_qa", "round_trip"}
TIER1_IDS = {"txt", "markdown", "docx", "pdf", "html", "epub", "pptx"}
SOURCE_ADAPTER_IDS = {"web", "email", "image-scan", "audio", "video", "transcript"}
REVIEW_AXIS_IDS = {
    "intent-structure",
    "factual-sources",
    "terminology-localization",
    "reader-accessibility",
    "safety-privacy-legal",
    "format-layout",
    "images",
    "reproducibility-recovery",
    "compatibility-round-trip",
}
CORE_PROJECT_REVIEW_AXES = REVIEW_AXIS_IDS - {"images"}
GATE_ALIASES = {
    "brief-approved": "current-brief",
    "baseline": "current-baseline",
    "framework-approved": "current-framework",
    "source-locked": "current-source-locked",
    "final-approved": "current-final",
    "publish-approved": "current-publish",
}
PHASE_GATES = {
    "brief-approved": {"brief-approved"},
    "initialized": {"brief-approved", "baseline"},
    "framework-approved": {"brief-approved", "baseline", "framework-approved"},
    "working": {"brief-approved", "baseline", "framework-approved"},
    "candidate": {"brief-approved", "baseline", "framework-approved"},
    "source-locked": {"brief-approved", "baseline", "framework-approved", "source-locked"},
    "deriving": {"brief-approved", "baseline", "framework-approved", "source-locked"},
    "final-approved": {
        "brief-approved",
        "baseline",
        "framework-approved",
        "source-locked",
        "final-approved",
    },
    "published": {
        "brief-approved",
        "baseline",
        "framework-approved",
        "source-locked",
        "final-approved",
        "publish-approved",
    },
    "archived": {
        "brief-approved",
        "baseline",
        "framework-approved",
        "source-locked",
        "final-approved",
        "publish-approved",
    },
}
MATRIX_PHASES = set(PHASE_GATES) - {"brief-approved", "initialized"}
REPORT_PHASES = {
    "framework-approved",
    "candidate",
    "source-locked",
    "deriving",
    "final-approved",
    "published",
    "archived",
}
FINAL_PHASES = {"final-approved", "published", "archived"}
REVIEW_GATES = {"framework-approved", "source-locked", "final-approved"}
GATE_REVIEW_MILESTONES = {
    "framework-approved": "outline",
    "source-locked": "source-lock",
    "final-approved": "final",
}
PHASE_REVIEW_GATE = {
    "framework-approved": "framework-approved",
    "source-locked": "source-locked",
    "deriving": "source-locked",
    "final-approved": "final-approved",
    "published": "final-approved",
    "archived": "final-approved",
}
REVIEW_MILESTONES = {"outline", "batch", "candidate", "source-lock", "final"}
PHASE_ACTIVE_BATCH_KINDS = {
    "brief-approved": set(),
    "initialized": {"outline"},
    "framework-approved": {"content"},
    "working": {"content"},
    "candidate": {"candidate"},
    "source-locked": {"source-lock", "derivative"},
    "deriving": {"derivative"},
    "final-approved": {"final"},
    "published": set(),
    "archived": set(),
}
FORCE_CUMULATIVE_BATCH_KINDS = {"outline", "candidate", "final"}
CAPABILITY_OPERATIONS = {
    "read",
    "edit",
    "generate",
    "render",
    "visual_qa",
    "round_trip",
    "structural_qa",
    "standards_validation",
    "runtime_qa",
    "accessibility_qa",
    "version_control",
}
DATE_VERSION_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}(?:-\d{2})?$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SOURCE_USES = {"factual", "context", "style", "incoming"}
BRIEF_REPRODUCIBILITY_POLICIES = {"required", "not_required"}
BRIEF_VISUAL_QA_POLICIES = {"full", "sampled", "not_applicable"}
BATCH_REVIEW_MILESTONES = {
    "outline": "outline",
    "content": "batch",
    "candidate": "candidate",
    "source-lock": "source-lock",
    "derivative": "batch",
    "final": "final",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check-jj", action="store_true")
    parser.add_argument("--now", help="RFC 3339 UTC timestamp for reproducible validation")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args()


class Report:
    def __init__(self, root: Path) -> None:
        # Resolve once so every later relative-path comparison uses the same
        # canonical Windows spelling (including expansion of 8.3 short paths).
        self.root = root.resolve()
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []
        self.checks: list[dict[str, str]] = []

    def ok(self, code: str, message: str) -> None:
        self.checks.append({"code": code, "message": message})

    def warn(self, code: str, message: str) -> None:
        self.warnings.append({"code": code, "message": message})

    def error(self, code: str, message: str) -> None:
        self.errors.append({"code": code, "message": message})

    @property
    def status(self) -> str:
        if self.errors:
            return "BLOCKED"
        if self.warnings:
            return "DEGRADED"
        return "READY"

    @property
    def exit_code(self) -> int:
        return 2 if self.errors else (1 if self.warnings else 0)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1",
            "validated_at": utc_now(),
            "root": str(self.root),
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks": self.checks,
        }


def read_required(path: Path, report: Report) -> dict[str, Any] | None:
    if not path.is_file():
        report.error("MISSING_STATE_FILE", f"missing {path.relative_to(report.root)}")
        return None
    try:
        value = load_json(path)
    except ContractError as exc:
        report.error("INVALID_JSON", str(exc))
        return None
    if not isinstance(value, dict):
        report.error("INVALID_STATE_OBJECT", f"{path} must contain a JSON object")
        return None
    report.ok("JSON_VALID", str(path.relative_to(report.root)))
    return value


def valid_date_version(value: Any) -> bool:
    if not isinstance(value, str) or not DATE_VERSION_RE.fullmatch(value):
        return False
    if value[-3:-2] == "-" and int(value[-2:]) < 2:
        return False
    try:
        datetime.strptime(value[:10], "%Y.%m.%d")
    except ValueError:
        return False
    return True


def validate_timestamp(value: Any, code: str, report: Report) -> datetime | None:
    try:
        return parse_timestamp(str(value))
    except (ContractError, ValueError) as exc:
        report.error(code, f"invalid timestamp {value!r}: {exc}")
        return None


def validate_hashed_path(
    relative: Any,
    expected: Any,
    code_prefix: str,
    report: Report,
) -> Path | None:
    if not isinstance(relative, str) or not relative:
        report.error(f"{code_prefix}_PATH", "evidence path must be a non-empty string")
        return None
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        report.error(f"{code_prefix}_HASH", f"invalid SHA-256 for {relative}")
        return None
    try:
        target = ensure_within_root(report.root, Path(relative))
    except ContractError as exc:
        report.error(f"{code_prefix}_PATH", str(exc))
        return None
    if not target.is_file():
        report.error(f"{code_prefix}_MISSING", f"missing evidence file: {relative}")
        return None
    observed = sha256_file(target)
    if observed.lower() != expected.lower():
        report.error(f"{code_prefix}_MISMATCH", f"hash mismatch: {relative}")
        return None
    report.ok(f"{code_prefix}_HASH", relative)
    return target


def unwrap_profile_value(
    wrapper: Any,
    label: str,
    report: Report,
    *,
    allow_null: bool = False,
) -> Any:
    if not isinstance(wrapper, dict):
        report.error("PROFILE_WRAPPER", f"{label} must be a provenance wrapper")
        return None
    if wrapper.get("origin") not in ALLOWED_ORIGINS:
        report.error("PROFILE_ORIGIN", f"{label} has an invalid origin")
    evidence = wrapper.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        report.error("PROFILE_EVIDENCE", f"{label} requires provenance evidence")
    if "value" not in wrapper:
        report.error("PROFILE_VALUE", f"{label} has no value")
        return None
    value = wrapper["value"]
    if value is None and not allow_null:
        report.error("PROFILE_VALUE", f"{label} cannot be null")
    if "confirmed_at" in wrapper:
        validate_timestamp(wrapper["confirmed_at"], "PROFILE_CONFIRMED_AT", report)
    return value


def validate_profile(profile: dict[str, Any], report: Report) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    if profile.get("schema_version") != "1":
        report.error("PROFILE_SCHEMA", "ProjectProfile schema_version must be 1")

    for field in (
        "date_version",
        "project_root",
        "route",
        "languages",
        "formats",
        "dependencies",
        "capabilities_snapshot",
        "snapshot_max_age_hours",
        "unknowns",
    ):
        normalized[field] = unwrap_profile_value(
            profile.get(field),
            field,
            report,
            allow_null=field == "capabilities_snapshot",
        )

    if not valid_date_version(normalized.get("date_version")):
        report.error("PROFILE_VERSION", "date_version must be a valid YYYY.MM.DD[-NN]")

    root_value = normalized.get("project_root")
    if isinstance(root_value, str):
        try:
            resolved_root = ensure_within_root(report.root, Path(root_value))
            if resolved_root != report.root:
                report.error("PROFILE_ROOT", "project_root does not resolve to validator root")
        except ContractError as exc:
            report.error("PROFILE_ROOT", str(exc))
    else:
        report.error("PROFILE_ROOT", "project_root must be a string")

    if normalized.get("route") != "Project":
        report.error("PROFILE_ROUTE", "machine project state requires route=Project")

    paths = profile.get("paths")
    normalized_paths: dict[str, str] = {}
    if not isinstance(paths, dict) or not paths:
        report.error("PROFILE_PATHS", "ProjectProfile paths must be a non-empty object")
    else:
        for role, wrapper in paths.items():
            value = unwrap_profile_value(wrapper, f"paths.{role}", report)
            if not isinstance(value, str) or not value:
                report.error("PROFILE_PATH_VALUE", f"path role {role!r} requires a path")
                continue
            try:
                resolved = ensure_within_root(report.root, Path(value))
            except ContractError as exc:
                report.error("PROFILE_PATH_ESCAPE", str(exc))
                continue
            if not resolved.exists():
                report.warn("PROFILE_PATH_MISSING", f"mapped role {role!r} does not exist yet: {value}")
            normalized_paths[role] = value
    normalized["paths"] = normalized_paths

    for field in ("languages", "formats"):
        value = normalized.get(field)
        if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(item, str) and item for item in value)
        ):
            report.error("PROFILE_LIST", f"{field} must be a non-empty string array")
        elif len(value) != len(set(value)):
            report.error("PROFILE_LIST", f"{field} values must be unique")
        elif any(item != item.strip().lower() for item in value):
            report.error(
                "PROFILE_LIST",
                f"{field} values must use normalized lowercase identifiers",
            )
    dependencies = normalized.get("dependencies")
    if not isinstance(dependencies, list):
        report.error("PROFILE_DEPENDENCIES", "dependencies must be an array")
    unknowns = normalized.get("unknowns")
    if not isinstance(unknowns, list) or not all(isinstance(item, str) for item in unknowns):
        report.error("PROFILE_UNKNOWNS", "unknowns must be a string array")

    capability = normalized.get("capabilities_snapshot")
    if capability is not None:
        if not isinstance(capability, str) or not capability:
            report.error("PROFILE_CAPABILITIES", "capabilities_snapshot must be null or a path")
        else:
            try:
                target = ensure_within_root(report.root, Path(capability))
                if not target.is_file():
                    report.warn("PROFILE_CAPABILITIES", f"capability snapshot not found: {capability}")
            except ContractError as exc:
                report.error("PROFILE_CAPABILITIES", str(exc))

    max_age = normalized.get("snapshot_max_age_hours")
    if not isinstance(max_age, (int, float)) or isinstance(max_age, bool) or max_age <= 0:
        report.error("PROFILE_FRESHNESS", "snapshot_max_age_hours must be positive")

    vcs = profile.get("version_control")
    normalized_vcs: dict[str, Any] = {}
    if not isinstance(vcs, dict):
        report.error("PROFILE_VCS", "version_control must be an object")
    else:
        expected = {"system", "tested_baseline", "colocated", "remote_allowed"}
        if set(vcs) != expected:
            report.error("PROFILE_VCS", f"version_control keys must be {sorted(expected)}")
        for field in expected:
            normalized_vcs[field] = unwrap_profile_value(
                vcs.get(field),
                f"version_control.{field}",
                report,
            )
        if not isinstance(normalized_vcs.get("system"), str):
            report.error("PROFILE_VCS", "version_control.system must be a string")
        if not isinstance(normalized_vcs.get("tested_baseline"), str):
            report.error("PROFILE_VCS", "version_control.tested_baseline must be a string")
        for field in ("colocated", "remote_allowed"):
            if not isinstance(normalized_vcs.get(field), bool):
                report.error("PROFILE_VCS", f"version_control.{field} must be boolean")
    normalized["version_control"] = normalized_vcs
    report.ok("PROFILE_PROVENANCE", "all configurable Profile values checked")
    return normalized


def validate_brief(
    profile: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    report: Report,
) -> dict[str, Any] | None:
    brief_value = profile.get("paths", {}).get("brief")
    if not isinstance(brief_value, str):
        report.error("BRIEF_PATH", "ProjectProfile has no resolved Brief path")
        return None
    try:
        path = ensure_within_root(report.root, Path(brief_value))
    except ContractError as exc:
        report.error("BRIEF_PATH", str(exc))
        return None
    if not path.is_file():
        report.error("BRIEF_MISSING", f"missing approved ManuscriptBrief: {brief_value}")
        return None
    if path.suffix.lower() != ".md":
        report.error("BRIEF_FORMAT", "ManuscriptBrief must use the Markdown contract")
        return None
    text = path.read_text(encoding="utf-8")
    headings = {
        "## Goal",
        "## Audience and use",
        "## Scope",
        "## Source authority",
        "## Framework",
        "## Deliverables",
        "## Review and gates",
        "## Acceptance",
        "## Risks, assumptions, and open questions",
        "## Approval",
    }
    missing_headings = sorted(heading for heading in headings if heading not in text)
    if missing_headings:
        report.error("BRIEF_STRUCTURE", f"Brief omits headings: {missing_headings}")
    fields = {
        match.group(1).strip(): match.group(2).strip()
        for match in re.finditer(r"^- ([^:\n]+):[ \t]*(.*)$", text, re.MULTILINE)
    }
    required_fields = {
        "Schema version",
        "Date version",
        "Approval state",
        "Primary audience",
        "Reading environment",
        "Required accessibility or localization",
        "Included",
        "Excluded",
        "Authoritative sources",
        "Reference-only material",
        "Incoming draft status",
        "Prohibited or unavailable sources",
        "Approved outline or outline acceptance rule",
        "Required terminology",
        "Content boundaries",
        "Applicable review axes",
        "Required independent milestones",
        "Human gates",
        "Content",
        "Sources",
        "Format",
        "Privacy and safety",
        "Reproducibility",
        "Risks",
        "Assumptions",
        "Open questions",
        "Approver",
        "Exact confirmation",
        "Confirmed at",
    }
    missing_fields = sorted(
        field for field in required_fields if not fields.get(field, "").strip()
    )
    if missing_fields:
        report.error("BRIEF_FIELDS", f"Brief has unresolved fields: {missing_fields}")
    if fields.get("Schema version") != "1":
        report.error("BRIEF_SCHEMA", "Brief Schema version must be 1")
    if fields.get("Date version") != profile.get("date_version"):
        report.error("BRIEF_VERSION", "Brief and ProjectProfile date versions differ")
    if fields.get("Approval state", "").lower() != "approved":
        report.error("BRIEF_APPROVAL", "Brief Approval state must be approved")
    brief_confirmed_at = validate_timestamp(
        fields.get("Confirmed at"),
        "BRIEF_CONFIRMATION_TIME",
        report,
    )

    deliverable_rows: list[list[str]] = []
    normalized_deliverables: list[dict[str, str]] = []
    in_deliverables = False
    for line in text.splitlines():
        if line == "## Deliverables":
            in_deliverables = True
            continue
        if in_deliverables and line.startswith("## "):
            break
        if in_deliverables and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if (
                len(cells) == 6
                and cells[0] != "Deliverable"
                and not all(set(cell) <= {"-", ":"} for cell in cells)
            ):
                deliverable_rows.append(cells)
    if not deliverable_rows or any(not all(row) for row in deliverable_rows):
        report.error(
            "BRIEF_DELIVERABLES",
            "Brief requires at least one complete deliverable row",
        )
    else:
        languages = {str(value).lower() for value in profile.get("languages", [])}
        formats = {str(value).lower() for value in profile.get("formats", [])}
        row_languages = {row[1].lower() for row in deliverable_rows}
        row_formats = {row[2].lower() for row in deliverable_rows}
        if languages != row_languages:
            report.error(
                "BRIEF_DELIVERABLES",
                "Brief deliverable languages must exactly match ProjectProfile languages",
            )
        if formats != row_formats:
            report.error(
                "BRIEF_DELIVERABLES",
                "Brief deliverable formats must exactly match ProjectProfile formats",
            )
        seen_paths: set[str] = set()
        for row in deliverable_rows:
            name, language, format_id, reproducible, visual_qa, stable_path = row
            try:
                resolved = ensure_within_root(report.root, Path(stable_path))
                normalized_path = resolved.relative_to(report.root).as_posix()
            except (ContractError, ValueError) as exc:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} has an unsafe stable path: {exc}",
                )
                continue
            if Path(stable_path).is_absolute() or normalized_path in {"", "."}:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} stable path must be project-relative",
                )
                continue
            if normalized_path in seen_paths:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"duplicate deliverable stable path: {normalized_path}",
                )
                continue
            seen_paths.add(normalized_path)
            adapter = adapters.get(format_id.lower())
            if adapter is None:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} references unknown format {format_id!r}",
                )
            else:
                path_suffix = Path(normalized_path).suffix.lower()
                extensions = {
                    str(extension).lower()
                    for extension in adapter.get("extensions", [])
                    if isinstance(extension, str)
                }
                if extensions and Path(normalized_path).suffix.lower() not in extensions:
                    report.error(
                        "BRIEF_DELIVERABLES",
                        f"deliverable {name!r} path {normalized_path!r} does not match "
                        f"{format_id.lower()} extensions {sorted(extensions)}",
                    )
                suffix_owners = {
                    adapter_key
                    for adapter_key, candidate in adapters.items()
                    if path_suffix
                    and path_suffix
                    in {
                        str(extension).lower()
                        for extension in candidate.get("extensions", [])
                        if isinstance(extension, str)
                    }
                }
                if suffix_owners and format_id.lower() not in suffix_owners:
                    report.error(
                        "BRIEF_DELIVERABLES",
                        f"deliverable {name!r} suffix {path_suffix!r} belongs to "
                        f"{sorted(suffix_owners)}, not {format_id.lower()}",
                    )
            reproducibility_policy = reproducible.strip().lower()
            if reproducibility_policy not in BRIEF_REPRODUCIBILITY_POLICIES:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} Reproducible must be required or not_required",
                )
            visual_qa_policy = visual_qa.strip().lower()
            if visual_qa_policy not in BRIEF_VISUAL_QA_POLICIES:
                report.error(
                    "BRIEF_DELIVERABLES",
                    f"deliverable {name!r} Visual QA must be full, sampled, or not_applicable",
                )
            normalized_deliverables.append(
                {
                    "name": name,
                    "language": language.lower(),
                    "format": format_id.lower(),
                    "reproducible": reproducibility_policy,
                    "visual_qa": visual_qa_policy,
                    "path": normalized_path,
                }
            )
    report.ok("BRIEF_APPROVED", brief_value)
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "approver": fields.get("Approver", "").strip(),
        "exact_confirmation": fields.get("Exact confirmation", "").strip(),
        "confirmed_at": fields.get("Confirmed at", "").strip(),
        "confirmed_time": brief_confirmed_at,
        "deliverables": normalized_deliverables,
        "source_expectations": {
            "authoritative": fields.get("Authoritative sources", "").strip(),
            "reference-only": fields.get("Reference-only material", "").strip(),
            "incoming-draft": fields.get("Incoming draft status", "").strip(),
        },
    }


def validate_routing(
    snapshot: dict[str, Any],
    profile: dict[str, Any],
    report: Report,
    now: datetime,
) -> None:
    if snapshot.get("schema_version") != "1":
        report.error("ROUTING_SCHEMA", "RoutingSnapshot schema_version must be 1")
    dimensions = snapshot.get("dimensions")
    normalized_dimensions: dict[str, dict[str, Any]] = {}
    if not isinstance(dimensions, dict) or set(dimensions) != set(DIMENSIONS):
        report.error("ROUTING_DIMENSIONS", "routing snapshot must contain exactly six dimensions")
    else:
        for name in DIMENSIONS:
            item = dimensions[name]
            if not isinstance(item, dict):
                report.error("ROUTING_DIMENSION", f"{name} must be an object")
                continue
            score = item.get("score")
            effective = item.get("effective_score")
            unknown = item.get("unknown")
            evidence = item.get("evidence")
            if score is not None and (isinstance(score, bool) or score not in (0, 1, 2)):
                report.error("ROUTING_SCORE", f"{name}.score must be 0, 1, 2, or null")
            if not isinstance(unknown, bool):
                report.error("ROUTING_UNKNOWN", f"{name}.unknown must be boolean")
            expected_effective = 1 if score is None else score
            if effective != expected_effective:
                report.error(
                    "ROUTING_EFFECTIVE",
                    f"{name}.effective_score must be {expected_effective}",
                )
            if unknown is not (score is None):
                report.error("ROUTING_UNKNOWN", f"{name}.unknown is inconsistent with score")
            if (
                not isinstance(evidence, list)
                or not evidence
                or not all(isinstance(value, str) and value for value in evidence)
            ):
                report.error("ROUTING_EVIDENCE", f"{name}.evidence must be non-empty")
            if (
                (score is None or score in (0, 1, 2))
                and effective == expected_effective
                and isinstance(unknown, bool)
            ):
                normalized_dimensions[name] = item

    hard_triggers = snapshot.get("hard_triggers")
    valid_triggers = isinstance(hard_triggers, dict) and set(hard_triggers) == set(HARD_TRIGGERS)
    if not valid_triggers:
        report.error("ROUTING_TRIGGERS", "routing snapshot must contain exactly all hard triggers")
    else:
        for name, value in hard_triggers.items():
            if not (isinstance(value, bool) or value is None):
                report.error("ROUTING_TRIGGER_VALUE", f"{name} must be true, false, or null")
                valid_triggers = False

    unknowns = snapshot.get("unknowns")
    if not isinstance(unknowns, list) or not all(isinstance(item, str) for item in unknowns):
        report.error("ROUTING_UNKNOWNS", "unknowns must be a string array")
        unknowns = []
    else:
        required_unknowns = {
            name for name, item in normalized_dimensions.items() if item.get("unknown") is True
        }
        if isinstance(hard_triggers, dict):
            required_unknowns.update(
                f"hard_trigger:{name}"
                for name, value in hard_triggers.items()
                if value is None
            )
        missing_unknowns = sorted(required_unknowns - set(unknowns))
        if missing_unknowns:
            report.error("ROUTING_UNKNOWNS", f"missing unknown markers: {missing_unknowns}")

    if len(normalized_dimensions) == len(DIMENSIONS) and valid_triggers:
        if normalized_dimensions["scale"]["score"] == 2 and not hard_triggers["large_volume"]:
            report.error("ROUTING_DERIVED_TRIGGER", "scale score 2 requires large_volume=true")
        if normalized_dimensions["risk"]["score"] == 2 and not hard_triggers["high_risk_facts"]:
            report.error("ROUTING_DERIVED_TRIGGER", "risk score 2 requires high_risk_facts=true")
        total, route, _, _ = select_route(normalized_dimensions, hard_triggers, unknowns)
        if snapshot.get("total") != total:
            report.error("ROUTING_TOTAL", f"stored total does not match recomputed total {total}")
        if snapshot.get("route") != route:
            report.error("ROUTING_ROUTE", f"stored route does not match recomputed route {route}")
        if profile.get("route") != route:
            report.error("ROUTING_PROFILE", "RoutingSnapshot route and ProjectProfile route differ")
        expected_action = {
            "Quick": "perform_bounded_task",
            "Structured": "prepare_lightweight_brief_and_review_plan",
            "Project": "handoff_discovery",
        }[route]
        if snapshot.get("next_action") != expected_action:
            report.error("ROUTING_NEXT_ACTION", f"next_action must be {expected_action}")
        invocation = snapshot.get("next_invocation")
        if route == "Project" and (not isinstance(invocation, str) or not invocation):
            report.error("ROUTING_NEXT_INVOCATION", "Project route requires a handoff invocation")
        if route != "Project" and invocation is not None:
            report.error("ROUTING_NEXT_INVOCATION", f"{route} route must not set next_invocation")
        report.ok("ROUTING_RECOMPUTED", f"{total} -> {route}")

    if not isinstance(snapshot.get("reasons"), list) or not snapshot["reasons"]:
        report.error("ROUTING_REASONS", "routing reasons must be non-empty")
    if not isinstance(snapshot.get("repository_evidence"), dict):
        report.error("ROUTING_REPOSITORY", "repository_evidence must be an object")
    try:
        snapshot_root = Path(str(snapshot.get("root"))).resolve()
        if snapshot_root != report.root:
            report.error("ROUTING_ROOT", "snapshot root differs from validator root")
    except (OSError, TypeError, ValueError):
        report.error("ROUTING_ROOT", "snapshot root is invalid")

    captured = validate_timestamp(snapshot.get("captured_at"), "ROUTING_TIMESTAMP", report)
    max_age = profile.get("snapshot_max_age_hours")
    if captured and isinstance(max_age, (int, float)) and not isinstance(max_age, bool):
        age_hours = (now - captured).total_seconds() / 3600
        if age_hours < -1:
            report.error("SNAPSHOT_FUTURE", f"routing snapshot is {abs(age_hours):.1f} hours in the future")
        elif age_hours > max_age:
            report.error("SNAPSHOT_STALE", f"routing snapshot age {age_hours:.1f}h exceeds {max_age}h")
        else:
            report.ok("SNAPSHOT_FRESH", f"routing snapshot age {age_hours:.1f}h")


def string_array(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(isinstance(item, str) and item for item in value)
    )


def validate_batches(
    manifest: dict[str, Any],
    profile: dict[str, Any],
    report: Report,
) -> dict[str, dict[str, Any]]:
    if manifest.get("schema_version") != "1":
        report.error("BATCH_SCHEMA", "BatchManifest schema_version must be 1")
    if not valid_date_version(manifest.get("date_version")):
        report.error("BATCH_VERSION", "BatchManifest date_version is invalid")
    if manifest.get("date_version") != profile.get("date_version"):
        report.error(
            "BATCH_VERSION",
            "BatchManifest and ProjectProfile date versions differ",
        )
    batches = manifest.get("batches")
    if not isinstance(batches, list) or not batches:
        report.error("BATCHES_MISSING", "BatchManifest requires at least one batch")
        return {}
    ids = [item.get("id") for item in batches if isinstance(item, dict)]
    if len(ids) != len(batches) or any(not isinstance(item, str) or not item for item in ids):
        report.error("BATCH_ID", "every batch requires a non-empty string id")
        return {}
    if len(ids) != len(set(ids)):
        report.error("BATCH_DUPLICATE", "batch ids must be unique")
        return {
            item["id"]: item
            for item in batches
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    known = set(ids)
    by_id = {item["id"]: item for item in batches}
    normalized_outputs_by_id: dict[str, dict[str, str | None]] = {}
    graph: dict[str, list[str]] = {}
    live_batches: list[str] = []
    for item in batches:
        batch_id = item["id"]
        required = {
            "label",
            "kind",
            "scope",
            "source_dependencies",
            "depends_on",
            "risk",
            "review_axes",
            "reviewable_volume",
            "review_cadence",
            "cumulative_regression",
            "regression_surface",
            "input_snapshot",
            "outputs",
            "status",
            "user_gate",
            "review_report",
            "user_confirmation",
        }
        missing_fields = sorted(required - set(item))
        if missing_fields:
            report.error("BATCH_FIELDS", f"{batch_id} missing fields: {missing_fields}")
        if not isinstance(item.get("label"), str) or not item["label"]:
            report.error("BATCH_LABEL", f"{batch_id} requires a label")
        if item.get("kind") not in {
            "outline",
            "content",
            "candidate",
            "source-lock",
            "derivative",
            "final",
        }:
            report.error("BATCH_KIND", f"{batch_id} has invalid kind")
        if not string_array(item.get("scope"), nonempty=True):
            report.error("BATCH_SCOPE", f"{batch_id} requires semantic scope")
        source_dependencies = item.get("source_dependencies")
        if not isinstance(source_dependencies, list):
            report.error("BATCH_SOURCES", f"{batch_id} source_dependencies must be an array")
        else:
            source_ids: set[str] = set()
            for dependency in source_dependencies:
                if not isinstance(dependency, dict):
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency entries must be objects",
                    )
                    continue
                source_id = dependency.get("source_id")
                if (
                    not isinstance(source_id, str)
                    or not source_id.strip()
                    or source_id in source_ids
                ):
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency IDs must be non-empty and unique",
                    )
                else:
                    source_ids.add(source_id)
                if dependency.get("use") not in {
                    "factual",
                    "context",
                    "style",
                    "incoming",
                }:
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency {source_id!r} has invalid use",
                    )
                if (
                    not isinstance(dependency.get("purpose"), str)
                    or not dependency["purpose"].strip()
                ):
                    report.error(
                        "BATCH_SOURCES",
                        f"{batch_id} source dependency {source_id!r} requires a purpose",
                    )
        deps = item.get("depends_on")
        if not string_array(deps):
            report.error("BATCH_DEPENDENCY", f"{batch_id} depends_on must be a string array")
            deps = []
        missing = sorted(set(deps) - known)
        if missing:
            report.error("BATCH_DEPENDENCY", f"{batch_id} references missing batches: {missing}")
        graph[batch_id] = deps
        if item.get("risk") not in {"low", "medium", "high", "critical"}:
            report.error("BATCH_RISK", f"{batch_id} has invalid risk")
        if not string_array(item.get("review_axes"), nonempty=True):
            report.error("BATCH_AXES", f"{batch_id} requires review axes")
        else:
            unknown_axes = sorted(set(item["review_axes"]) - REVIEW_AXIS_IDS)
            if unknown_axes:
                report.error(
                    "BATCH_AXES",
                    f"{batch_id} references unknown review axes: {unknown_axes}",
                )
        volume = item.get("reviewable_volume")
        if not isinstance(volume, dict):
            report.error("BATCH_VOLUME", f"{batch_id} reviewable_volume must be an object")
        else:
            if not isinstance(volume.get("unit"), str) or not volume["unit"]:
                report.error("BATCH_VOLUME", f"{batch_id} volume requires a unit")
            target = volume.get("target")
            if not isinstance(target, (int, float)) or isinstance(target, bool) or target <= 0:
                report.error("BATCH_VOLUME", f"{batch_id} volume target must be positive")
            if not isinstance(volume.get("rationale"), str) or not volume["rationale"]:
                report.error("BATCH_VOLUME", f"{batch_id} volume requires a rationale")
        cadence = item.get("review_cadence")
        if cadence not in {"incremental", "cumulative"}:
            report.error("BATCH_CADENCE", f"{batch_id} has invalid review cadence")
        cumulative = item.get("cumulative_regression")
        if not isinstance(cumulative, bool) or cumulative is not (cadence == "cumulative"):
            report.error("BATCH_REGRESSION", f"{batch_id} cadence and cumulative flag disagree")
        if item.get("kind") in FORCE_CUMULATIVE_BATCH_KINDS and cadence != "cumulative":
            report.error(
                "BATCH_REGRESSION",
                f"{batch_id} kind {item.get('kind')} requires cumulative review",
            )
        surface = item.get("regression_surface")
        if not string_array(surface):
            report.error("BATCH_REGRESSION", f"{batch_id} regression_surface must be an array")
        if cadence == "cumulative" and not surface:
            report.error("BATCH_REGRESSION", f"{batch_id} cumulative review needs a regression surface")
        status = item.get("status")
        if status not in {"planned", "active", "review", "accepted", "blocked"}:
            report.error("BATCH_STATUS", f"{batch_id} has invalid status")
        elif status in {"active", "review"}:
            live_batches.append(batch_id)

        outputs = item.get("outputs")
        normalized_outputs: dict[str, str | None] = {}
        if not isinstance(outputs, list) or not outputs:
            report.error("BATCH_OUTPUTS", f"{batch_id} requires intended outputs")
        else:
            for output in outputs:
                if not isinstance(output, dict):
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output entries must be path/hash objects",
                    )
                    continue
                output_value = output.get("path")
                output_hash = output.get("sha256")
                if not isinstance(output_value, str) or not output_value.strip():
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output requires a non-empty path",
                    )
                    continue
                try:
                    resolved_output = ensure_within_root(
                        report.root,
                        Path(output_value),
                    )
                    normalized_output = resolved_output.relative_to(
                        report.root
                    ).as_posix()
                except (ContractError, ValueError) as exc:
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output path is unsafe: {exc}",
                    )
                    continue
                if Path(output_value).is_absolute() or normalized_output in {"", "."}:
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} output path must be project-relative",
                    )
                    continue
                if normalized_output in normalized_outputs:
                    report.error(
                        "BATCH_OUTPUTS",
                        f"{batch_id} repeats output {normalized_output}",
                    )
                    continue
                if status in {"review", "accepted"}:
                    validated_output = validate_hashed_path(
                        output_value,
                        output_hash,
                        "BATCH_OUTPUT",
                        report,
                    )
                    if validated_output:
                        normalized_outputs[normalized_output] = str(
                            output_hash
                        ).lower()
                elif output_hash is None:
                    normalized_outputs[normalized_output] = None
                else:
                    validated_output = validate_hashed_path(
                        output_value,
                        output_hash,
                        "BATCH_OUTPUT",
                        report,
                    )
                    if validated_output:
                        normalized_outputs[normalized_output] = str(
                            output_hash
                        ).lower()
        normalized_outputs_by_id[batch_id] = normalized_outputs

        input_snapshot = item.get("input_snapshot")
        input_snapshot_time: datetime | None = None
        if input_snapshot is None:
            if status in {"active", "review", "accepted", "blocked"}:
                report.error(
                    "BATCH_SNAPSHOT",
                    f"{batch_id} status {status} requires a frozen input snapshot",
                )
        elif not isinstance(input_snapshot, dict):
            report.error(
                "BATCH_SNAPSHOT",
                f"{batch_id} input_snapshot must be null or a hashed snapshot object",
            )
        else:
            validate_hashed_path(
                input_snapshot.get("path"),
                input_snapshot.get("sha256"),
                "BATCH_SNAPSHOT",
                report,
            )
            input_snapshot_time = validate_timestamp(
                input_snapshot.get("captured_at"),
                "BATCH_SNAPSHOT_TIME",
                report,
            )
        user_gate = item.get("user_gate")
        if user_gate not in {"required", "not_required"}:
            report.error("BATCH_USER_GATE", f"{batch_id} has invalid user_gate")

        review_reference = item.get("review_report")
        batch_review: dict[str, Any] | None = None
        if review_reference is not None:
            if not isinstance(review_reference, dict):
                report.error(
                    "BATCH_REVIEW",
                    f"{batch_id} review_report must be null or a hash-bound object",
                )
            else:
                review_path = validate_hashed_path(
                    review_reference.get("path"),
                    review_reference.get("sha256"),
                    "BATCH_REVIEW",
                    report,
                )
                if review_path:
                    batch_review = validate_project_review_report(
                        review_path.relative_to(report.root).as_posix(),
                        report,
                    )
                    if (
                        batch_review
                        and batch_review.get("sha256")
                        != str(review_reference.get("sha256", "")).lower()
                    ):
                        report.error(
                            "BATCH_REVIEW",
                            f"{batch_id} project-review result hash differs from parsed result",
                        )
        if status == "accepted":
            if not batch_review:
                report.error(
                    "BATCH_REVIEW",
                        f"{batch_id} accepted status requires a hash-bound project-review result",
                )
            else:
                expected_milestone = BATCH_REVIEW_MILESTONES.get(item.get("kind"))
                if batch_review.get("milestone") != expected_milestone:
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} accepted review must use milestone {expected_milestone}",
                    )
                if batch_review.get("verdict") != "PASS":
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} accepted review must return PASS",
                    )
                missing_axes = sorted(
                    set(item.get("review_axes", []))
                    - set(batch_review.get("manuscript_axes", set()))
                )
                if missing_axes:
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} review omits required axes: {missing_axes}",
                    )
                for output_path, output_hash in normalized_outputs.items():
                    if (
                        output_hash is None
                        or batch_review.get("snapshot", {}).get(output_path)
                        != output_hash
                    ):
                        report.error(
                            "BATCH_REVIEW",
                            f"{batch_id} review snapshot does not bind output {output_path}",
                        )
                if (
                    input_snapshot_time
                    and batch_review.get("snapshot_captured_time")
                    and batch_review["snapshot_captured_time"] < input_snapshot_time
                ):
                    report.error(
                        "BATCH_REVIEW",
                        f"{batch_id} review snapshot predates its frozen input snapshot",
                    )

        confirmation = item.get("user_confirmation")
        if status == "accepted" and user_gate == "required":
            if not isinstance(confirmation, dict):
                report.error(
                    "BATCH_USER_GATE",
                    f"{batch_id} accepted status requires user confirmation",
                )
            else:
                for field in ("actor", "exact_statement"):
                    if (
                        not isinstance(confirmation.get(field), str)
                        or not confirmation[field].strip()
                    ):
                        report.error(
                            "BATCH_USER_GATE",
                            f"{batch_id} confirmation requires {field}",
                        )
                confirmation_time = validate_timestamp(
                    confirmation.get("confirmed_at"),
                    "BATCH_USER_GATE_TIME",
                    report,
                )
                if (
                    confirmation_time
                    and batch_review
                    and isinstance(batch_review.get("completed_at"), datetime)
                    and confirmation_time < batch_review["completed_at"]
                ):
                    report.error(
                        "BATCH_USER_GATE_TIME",
                        f"{batch_id} was confirmed before specialist review completed",
                    )
        elif confirmation is not None:
            report.error(
                "BATCH_USER_GATE",
                f"{batch_id} may record user_confirmation only when an accepted batch requires it",
            )

    if len(live_batches) > 1:
        report.error(
            "BATCH_ACTIVE",
            f"BatchManifest has multiple active/review batches: {sorted(live_batches)}",
        )

    for batch_id, item in by_id.items():
        if item.get("status") not in {"active", "review", "accepted"}:
            continue
        unaccepted = sorted(
            dependency
            for dependency in graph.get(batch_id, [])
            if dependency in by_id
            and by_id[dependency].get("status") != "accepted"
        )
        if unaccepted:
            report.error(
                "BATCH_DEPENDENCY_STATUS",
                f"{batch_id} cannot advance before prerequisites are accepted: {unaccepted}",
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(dep) for dep in graph.get(node, []) if dep in graph):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(visit(node) for node in graph):
        report.error("BATCH_CYCLE", "batch dependency graph contains a cycle")
    else:
        report.ok("BATCH_GRAPH", f"{len(ids)} batches with an acyclic dependency graph")
    return {
        batch_id: {
            **item,
            "_validated_outputs": normalized_outputs_by_id.get(batch_id, {}),
        }
        for batch_id, item in by_id.items()
    }


def validate_format_registry(
    registry: dict[str, Any],
    profile: dict[str, Any],
    report: Report,
) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != "1":
        report.error("FORMAT_SCHEMA", "format registry schema_version must be 1")
    adapters = registry.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        report.error("FORMAT_REGISTRY", "format registry must contain adapters")
        return {}
    by_id: dict[str, dict[str, Any]] = {}
    for adapter in adapters:
        if not isinstance(adapter, dict):
            report.error("FORMAT_ADAPTER", "every adapter must be an object")
            continue
        adapter_id = adapter.get("id")
        if not isinstance(adapter_id, str) or not adapter_id:
            report.error("FORMAT_ID", "every adapter requires an id")
            continue
        if adapter_id in by_id:
            report.error("FORMAT_DUPLICATE", f"duplicate adapter id: {adapter_id}")
        by_id[adapter_id] = adapter
        if not isinstance(adapter.get("format"), str) or not adapter["format"]:
            report.error("FORMAT_NAME", f"{adapter_id} requires a format name")
        if adapter.get("tier") not in {1, 2}:
            report.error("FORMAT_TIER", f"{adapter_id} tier must be 1 or 2")
        if not string_array(adapter.get("extensions")):
            report.error("FORMAT_EXTENSIONS", f"{adapter_id} extensions must be an array")
        if not string_array(adapter.get("media_types")):
            report.error("FORMAT_MEDIA_TYPES", f"{adapter_id} media_types must be an array")
        operations = adapter.get("operations")
        if not isinstance(operations, dict) or set(operations) != OPERATION_KEYS:
            report.error("FORMAT_OPERATIONS", f"{adapter_id} must define all six operations")
        elif any(value not in ALLOWED_CAPABILITIES for value in operations.values()):
            report.error("FORMAT_CAPABILITY", f"{adapter_id} has an invalid capability value")
        for field in ("required_dependencies", "optional_dependencies"):
            if not string_array(adapter.get(field)):
                report.error("FORMAT_DEPENDENCIES", f"{adapter_id}.{field} must be an array")
        validation_dependencies = adapter.get("validation_dependencies")
        if not isinstance(validation_dependencies, list):
            report.error(
                "FORMAT_DEPENDENCIES",
                f"{adapter_id}.validation_dependencies must be an array",
            )
        else:
            for requirement in validation_dependencies:
                if (
                    not isinstance(requirement, dict)
                    or not string_array(requirement.get("alternatives"), nonempty=True)
                    or requirement.get("operation") not in CAPABILITY_OPERATIONS
                ):
                    report.error(
                        "FORMAT_DEPENDENCIES",
                        f"{adapter_id} has an invalid validation dependency group",
                    )
        if not string_array(adapter.get("validation"), nonempty=True):
            report.error("FORMAT_VALIDATION", f"{adapter_id} requires validation steps")
        if not isinstance(adapter.get("degradation"), str) or not adapter["degradation"]:
            report.error("FORMAT_DEGRADATION", f"{adapter_id} requires degradation rules")
        if not isinstance(adapter.get("blocking_qa_gaps"), bool):
            report.error("FORMAT_BLOCKING_POLICY", f"{adapter_id} requires blocking_qa_gaps")

    extension_owners: dict[str, list[str]] = {}
    for adapter_id, adapter in by_id.items():
        for extension in adapter.get("extensions", []):
            if not isinstance(extension, str):
                continue
            normalized_extension = extension.strip().lower()
            if (
                not normalized_extension.startswith(".")
                or normalized_extension in {".", ".."}
            ):
                report.error(
                    "FORMAT_EXTENSIONS",
                    f"{adapter_id} has invalid extension {extension!r}",
                )
                continue
            extension_owners.setdefault(normalized_extension, []).append(adapter_id)
    for extension, owners in sorted(extension_owners.items()):
        if len(owners) > 1:
            report.error(
                "FORMAT_EXTENSION_COLLISION",
                f"extension {extension} is claimed by multiple adapters: {sorted(owners)}",
            )

    missing = sorted(TIER1_IDS - set(by_id))
    if missing:
        report.error("FORMAT_TIER1", f"missing Tier 1 adapters: {missing}")
    else:
        report.ok("FORMAT_TIER1", "all Tier 1 adapters present")

    source_adapters = registry.get("source_adapters")
    source_ids: set[str] = set()
    if not isinstance(source_adapters, list):
        report.error("SOURCE_ADAPTERS", "source_adapters must be an array")
    else:
        for adapter in source_adapters:
            if not isinstance(adapter, dict) or not isinstance(adapter.get("id"), str):
                report.error("SOURCE_ADAPTER", "every source adapter requires an id")
                continue
            source_ids.add(adapter["id"])
            if not string_array(adapter.get("required_metadata"), nonempty=True):
                report.error("SOURCE_METADATA", f"{adapter['id']} requires metadata fields")
            if not string_array(adapter.get("derivatives")):
                report.error("SOURCE_DERIVATIVES", f"{adapter['id']} derivatives must be an array")
    if source_ids != SOURCE_ADAPTER_IDS:
        report.error("SOURCE_ADAPTERS", "source adapter catalog is incomplete or contains unknown ids")

    try:
        canonical = load_json(CANONICAL_FORMAT_REGISTRY)
    except ContractError as exc:
        report.error("FORMAT_BASELINE", str(exc))
        canonical = {}
    canonical_adapters = {
        item.get("id"): item
        for item in canonical.get("adapters", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for adapter_id, baseline in canonical_adapters.items():
        observed = by_id.get(adapter_id)
        if observed is None:
            report.error(
                "FORMAT_BASELINE",
                f"local format registry omits canonical adapter {adapter_id}",
            )
            continue
        changed = sorted(
            field
            for field in CANONICAL_ADAPTER_FIELDS
            if observed.get(field) != baseline.get(field)
        )
        if changed:
            report.error(
                "FORMAT_BASELINE",
                f"{adapter_id} weakens or changes canonical fields: {changed}",
            )
    canonical_sources = {
        item.get("id"): item
        for item in canonical.get("source_adapters", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    observed_sources = {
        item.get("id"): item
        for item in source_adapters
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    } if isinstance(source_adapters, list) else {}
    if observed_sources != canonical_sources:
        report.error(
            "FORMAT_BASELINE",
            "local source-adapter contract differs from the packaged canonical baseline",
        )
    if canonical_adapters and not any(
        item["code"] == "FORMAT_BASELINE" for item in report.errors
    ):
        report.ok(
            "FORMAT_BASELINE",
            f"local registry preserves {len(canonical_adapters)} canonical adapters",
        )

    formats = profile.get("formats")
    if isinstance(formats, list):
        unknown_formats = sorted(set(formats) - set(by_id))
        if unknown_formats:
            report.error("PROFILE_FORMATS", f"unknown selected formats: {unknown_formats}")
    return by_id


def validate_lifecycle_state(
    state: dict[str, Any],
    batches: dict[str, dict[str, Any]],
    profile: dict[str, Any],
    report: Report,
) -> dict[str, Any]:
    if state.get("schema_version") != "1":
        report.error("STATE_SCHEMA", "state schema_version must be 1")
    if not valid_date_version(state.get("date_version")):
        report.error("STATE_VERSION", "state date_version is invalid")
    if state.get("date_version") != profile.get("date_version"):
        report.error("STATE_VERSION", "state and ProjectProfile date versions differ")
    phase = state.get("phase")
    if phase not in PHASE_GATES:
        report.error("STATE_PHASE", f"invalid lifecycle phase: {phase!r}")
        expected_gates: set[str] = set()
    else:
        expected_gates = PHASE_GATES[phase]
    required_gates = state.get("required_gates")
    if not string_array(required_gates, nonempty=True):
        report.error("STATE_GATES", "required_gates must be a non-empty string array")
        required_gates = []
    unknown_gates = sorted(set(required_gates) - set(GATE_ALIASES))
    if unknown_gates:
        report.error("STATE_GATES", f"unknown required gates: {unknown_gates}")
    missing_gates = sorted(expected_gates - set(required_gates))
    if missing_gates:
        report.error("STATE_GATES", f"phase {phase} omits required gates: {missing_gates}")
    extra_gates = sorted(set(required_gates) - expected_gates)
    if extra_gates:
        report.error("STATE_GATES", f"phase {phase} includes later gates: {extra_gates}")
    active_receipts = state.get("active_receipts")
    if not isinstance(active_receipts, dict):
        report.error("STATE_RECEIPTS", "active_receipts must be an object")
        active_receipts = {}
    else:
        if set(active_receipts) != set(required_gates):
            report.error(
                "STATE_RECEIPTS",
                "active_receipts keys must exactly match required_gates",
            )
        for gate, bookmark in active_receipts.items():
            if gate not in GATE_ALIASES:
                report.error("STATE_RECEIPTS", f"unknown active receipt gate {gate!r}")
            elif (
                not isinstance(bookmark, str)
                or not bookmark
                or not bookmark.startswith(f"{gate}-")
                or not valid_date_version(bookmark[len(gate) + 1 :])
            ):
                report.error(
                    "STATE_RECEIPTS",
                    f"{gate} active receipt must name a dated gate bookmark",
                )

    active_batch = state.get("active_batch")
    live_batches = sorted(
        batch_id
        for batch_id, batch in batches.items()
        if batch.get("status") in {"active", "review"}
    )
    if active_batch is not None:
        batch = batches.get(active_batch)
        if batch is None:
            report.error("STATE_BATCH", f"unknown active_batch: {active_batch}")
        elif phase in PHASE_ACTIVE_BATCH_KINDS:
            allowed_kinds = PHASE_ACTIVE_BATCH_KINDS[phase]
            if batch.get("kind") not in allowed_kinds:
                report.error(
                    "STATE_BATCH_PHASE",
                    f"phase {phase} cannot activate batch kind {batch.get('kind')!r}",
                )
            if batch.get("status") not in {"active", "review"}:
                report.error(
                    "STATE_BATCH_STATUS",
                    f"active batch {active_batch} must have status active or review",
                )
        if live_batches != [active_batch]:
            report.error(
                "STATE_BATCH_BINDING",
                f"active_batch must exactly match the sole active/review batch: {live_batches}",
            )
    elif phase in {"candidate", "deriving"}:
        report.error("STATE_BATCH", f"phase {phase} requires an active batch")
    elif live_batches:
        report.error(
            "STATE_BATCH_BINDING",
            f"BatchManifest has active/review work but LifecycleState has no active_batch: {live_batches}",
        )
    source_register = state.get("source_register")
    if not isinstance(source_register, str) or not source_register:
        report.error("STATE_SOURCES", "source_register must be a path")
    for field in ("review_matrix", "latest_review_report", "capability_snapshot"):
        value = state.get(field)
        if value is not None and (not isinstance(value, str) or not value):
            report.error("STATE_PATH", f"{field} must be null or a path")
    if phase in MATRIX_PHASES and not state.get("review_matrix"):
        report.error("STATE_REVIEW_MATRIX", f"phase {phase} requires a ReviewMatrix")
    if phase in REPORT_PHASES and not state.get("latest_review_report"):
        report.error("STATE_REVIEW_REPORT", f"phase {phase} requires a ReviewReport")
    if phase in FINAL_PHASES:
        if not state.get("capability_snapshot"):
            report.error("STATE_CAPABILITIES", f"phase {phase} requires a capability snapshot")
        if not isinstance(state.get("format_qa_records"), list) or not state["format_qa_records"]:
            report.error("STATE_FORMAT_QA", f"phase {phase} requires format QA records")
    elif not isinstance(state.get("format_qa_records"), list):
        report.error("STATE_FORMAT_QA", "format_qa_records must be an array")
    validate_timestamp(state.get("updated_at"), "STATE_UPDATED_AT", report)
    report.ok("STATE_PHASE", f"phase={phase}, required gates={len(required_gates)}")
    return {
        "phase": phase,
        "date_version": state.get("date_version"),
        "required_gates": set(required_gates),
        "active_receipts": active_receipts,
        "active_batch": active_batch,
        "source_register": source_register,
        "review_matrix": state.get("review_matrix"),
        "latest_review_report": state.get("latest_review_report"),
        "capability_snapshot": state.get("capability_snapshot"),
        "format_qa_records": state.get("format_qa_records", []),
    }


def validate_snapshot_files(
    snapshot: Any,
    code: str,
    report: Report,
) -> tuple[dict[str, str], datetime | None, str | None]:
    normalized: dict[str, str] = {}
    if not isinstance(snapshot, dict):
        report.error(code, "artifact_snapshot must be an object")
        return normalized, None, None
    captured_value = snapshot.get("captured_at")
    captured = validate_timestamp(captured_value, f"{code}_TIME", report)
    files = snapshot.get("files")
    if not isinstance(files, list) or not files:
        report.error(f"{code}_FILES", "frozen snapshot requires at least one file")
        return normalized, captured, (
            captured_value if isinstance(captured_value, str) else None
        )
    for entry in files:
        if not isinstance(entry, dict):
            report.error(f"{code}_FILES", "snapshot file entry must be an object")
            continue
        path = validate_hashed_path(entry.get("path"), entry.get("sha256"), code, report)
        if path:
            relative = path.relative_to(report.root).as_posix()
            if relative in normalized:
                report.error(f"{code}_FILES", f"duplicate snapshot path: {relative}")
            normalized[relative] = str(entry["sha256"]).lower()
    return normalized, captured, (
        captured_value if isinstance(captured_value, str) else None
    )


def validate_review_matrix(path_value: Any, report: Report) -> dict[str, Any] | None:
    """Validate the manuscript-specific review profile sent to project-review."""
    if not isinstance(path_value, str):
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("REVIEW_PROFILE_PATH", str(exc))
        return None
    matrix = read_required(path, report)
    if not matrix:
        return None
    if matrix.get("schema_version") != "1":
        report.error("REVIEW_PROFILE_SCHEMA", "manuscript review profile schema_version must be 1")
    if matrix.get("profile") != "manuscript":
        report.error("REVIEW_PROFILE_TYPE", "review profile must identify the manuscript profile")
    if matrix.get("milestone") not in REVIEW_MILESTONES:
        report.error("REVIEW_PROFILE_MILESTONE", "manuscript review profile milestone is invalid")
    snapshot, snapshot_captured_time, snapshot_captured_at = validate_snapshot_files(
        matrix.get("artifact_snapshot"),
        "REVIEW_PROFILE_SNAPSHOT",
        report,
    )
    axes = matrix.get("axes")
    if not isinstance(axes, list):
        report.error("REVIEW_PROFILE_AXES", "manuscript review profile axes must be an array")
        return None
    ids = [axis.get("id") for axis in axes if isinstance(axis, dict)]
    if len(ids) != len(set(ids)):
        report.error("REVIEW_PROFILE_AXES", "manuscript review profile axis ids must be unique")
    missing = sorted(REVIEW_AXIS_IDS - set(ids))
    if missing:
        report.error("REVIEW_PROFILE_AXES", f"manuscript review profile omitted axes: {missing}")
    for axis in axes:
        if not isinstance(axis, dict):
            report.error("REVIEW_PROFILE_AXIS", "every manuscript review axis must be an object")
            continue
        axis_id = axis.get("id", "<unknown>")
        if axis_id not in REVIEW_AXIS_IDS:
            report.error("REVIEW_PROFILE_AXIS", f"{axis_id} is not a manuscript review axis")
        applicable = axis.get("applicable")
        if not isinstance(applicable, bool):
            report.error("REVIEW_PROFILE_APPLICABILITY", f"{axis_id} applicability is unresolved")
        if not isinstance(axis.get("reason"), str) or not axis["reason"].strip():
            report.error("REVIEW_PROFILE_REASON", f"{axis_id} requires an applicability reason")
        evidence_required = axis.get("evidence_required")
        if not string_array(evidence_required):
            report.error(
                "REVIEW_PROFILE_EVIDENCE",
                f"{axis_id} evidence_required must be a string array",
            )
        elif applicable is True and not evidence_required:
            report.error(
                "REVIEW_PROFILE_EVIDENCE",
                f"{axis_id} requires at least one evidence requirement",
            )
    report.ok("REVIEW_PROFILE", f"validated {len(axes)} manuscript axes")
    applicable_axes = {
        axis["id"]
        for axis in axes
        if isinstance(axis, dict)
        and isinstance(axis.get("id"), str)
        and axis.get("applicable") is True
    }
    return {
        "path": path.relative_to(report.root).as_posix(),
        "milestone": matrix.get("milestone"),
        "snapshot": snapshot,
        "snapshot_captured_at": snapshot_captured_at,
        "snapshot_captured_time": snapshot_captured_time,
        "applicable_axes": applicable_axes,
        "axes": set(ids),
    }


def _validate_manuscript_evidence(
    evidence: Any,
    report: Report,
) -> set[str]:
    if not isinstance(evidence, list):
        report.error(
            "PROJECT_REVIEW_EVIDENCE",
            "project-review result requires manuscript_evidence entries",
        )
        return set()
    axes: set[str] = set()
    for entry in evidence:
        if not isinstance(entry, dict):
            report.error("PROJECT_REVIEW_EVIDENCE", "manuscript evidence entry must be an object")
            continue
        axis = entry.get("axis")
        if (
            not isinstance(axis, str)
            or axis not in REVIEW_AXIS_IDS
            or axis in axes
        ):
            report.error(
                "PROJECT_REVIEW_EVIDENCE",
                f"manuscript evidence has unknown or duplicate axis {axis!r}",
            )
            continue
        axes.add(axis)
        artifacts = entry.get("evidence")
        if not isinstance(artifacts, list) or not artifacts:
            report.error(
                "PROJECT_REVIEW_EVIDENCE",
                f"{axis} requires at least one hashed evidence artifact",
            )
            continue
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                report.error(
                    "PROJECT_REVIEW_EVIDENCE",
                    f"{axis} evidence artifacts must be objects",
                )
                continue
            if (
                not isinstance(artifact.get("kind"), str)
                or not artifact["kind"].strip()
            ):
                report.error(
                    "PROJECT_REVIEW_EVIDENCE",
                    f"{axis} evidence artifacts require a kind",
                )
            validate_hashed_path(
                artifact.get("path"),
                artifact.get("sha256"),
                "PROJECT_REVIEW_EVIDENCE",
                report,
            )
    return axes


def validate_project_review_report(
    path_value: Any,
    report: Report,
    _visited: set[str] | None = None,
) -> dict[str, Any] | None:
    """Validate only the manuscript integration envelope emitted by project-review.

    Generic findings, repair rounds, independence, review state, and verdict
    reasoning remain owned by project-review. This adapter checks the frozen
    manuscript snapshot and its domain evidence projection.
    """
    if not isinstance(path_value, str):
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("PROJECT_REVIEW_PATH", str(exc))
        return None
    if not path.is_file():
        report.error("PROJECT_REVIEW_MISSING", f"missing project-review result: {path_value}")
        return None
    if path.suffix.lower() != ".json":
        report.error(
            "PROJECT_REVIEW_MACHINE",
            "LifecycleState and GateReceipt must reference the JSON project-review result",
        )
        return None
    review = read_required(path, report)
    if not review:
        return None
    if review.get("schema_version") != "1":
        report.error("PROJECT_REVIEW_SCHEMA", "project-review result schema_version must be 1")
    if review.get("provider") != "project-review":
        report.error("PROJECT_REVIEW_PROVIDER", "review result must identify project-review as provider")
    if review.get("profile") != "manuscript":
        report.error("PROJECT_REVIEW_PROFILE", "review result must use the manuscript Profile")
    milestone = review.get("milestone")
    if milestone not in REVIEW_MILESTONES:
        report.error("PROJECT_REVIEW_MILESTONE", "project-review result milestone is invalid")
    snapshot, snapshot_captured_time, snapshot_captured_at = validate_snapshot_files(
        review.get("artifact_snapshot"),
        "PROJECT_REVIEW_SNAPSHOT",
        report,
    )
    verdict = review.get("verdict")
    result = verdict.get("result") if isinstance(verdict, dict) else verdict
    if result not in {"PASS", "FAIL", "BLOCKED"}:
        report.error(
            "PROJECT_REVIEW_VERDICT",
            "project-review result must expose PASS, FAIL, or BLOCKED",
        )
    completed_at = validate_timestamp(
        review.get("completed_at"),
        "PROJECT_REVIEW_COMPLETED_AT",
        report,
    )
    manuscript_axes = _validate_manuscript_evidence(
        review.get("manuscript_evidence"),
        report,
    )
    report.ok("PROJECT_REVIEW_RESULT", path_value)
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "milestone": milestone,
        "snapshot": snapshot,
        "snapshot_captured_at": snapshot_captured_at,
        "snapshot_captured_time": snapshot_captured_time,
        "axes": manuscript_axes,
        "manuscript_axes": manuscript_axes,
        "verdict": result,
        "completed_at": completed_at,
    }


def validate_review_report(
    path_value: Any,
    report: Report,
    _visited: set[str] | None = None,
) -> dict[str, Any] | None:
    """Compatibility name for the project-review integration adapter."""
    return validate_project_review_report(path_value, report, _visited)


def validate_source_register(
    path_value: Any,
    registry: dict[str, Any],
    report: Report,
) -> dict[str, Any] | None:
    if not isinstance(path_value, str):
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("SOURCE_REGISTER_PATH", str(exc))
        return None
    if not path.is_file():
        report.error("SOURCE_REGISTER_MISSING", f"missing source register: {path_value}")
        return None
    required_columns = {
        "source_id",
        "class",
        "adapter_id",
        "path_or_url",
        "publisher_or_owner",
        "retrieved_at",
        "sha256",
        "privacy_class",
        "permitted_use",
        "exclusions",
        "metadata_json",
        "derived_artifacts_json",
    }
    adapters = {
        item["id"]: item
        for item in registry.get("source_adapters", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if set(reader.fieldnames or []) != required_columns:
            report.error("SOURCE_REGISTER_COLUMNS", "source register columns do not match the contract")
            return None
        rows = list(reader)
        seen: set[str] = set()
        row_adapters: dict[str, str] = {}
        for line_number, row in enumerate(rows, start=2):
            source_id = row["source_id"].strip()
            if not source_id or source_id in seen:
                report.error("SOURCE_ID", f"invalid or duplicate source_id at line {line_number}")
            seen.add(source_id)
            row_adapters[source_id] = row["adapter_id"]

        for line_number, row in enumerate(rows, start=2):
            source_id = row["source_id"].strip()
            if row["class"] not in {"authoritative", "reference-only", "incoming-draft"}:
                report.error("SOURCE_CLASS", f"{source_id} has invalid authority class")
            adapter_id = row["adapter_id"]
            adapter = adapters.get(adapter_id)
            if adapter is None:
                report.error("SOURCE_ADAPTER", f"{source_id} has unknown adapter {adapter_id!r}")
                continue
            for field in (
                "path_or_url",
                "publisher_or_owner",
                "retrieved_at",
                "sha256",
                "privacy_class",
                "permitted_use",
                "exclusions",
            ):
                if not row[field].strip():
                    report.error("SOURCE_POLICY", f"{source_id} requires {field}")
            permitted_tokens = {
                token.strip().lower()
                for token in row["permitted_use"].split(",")
                if token.strip()
            }
            excluded_tokens = {
                token.strip().lower()
                for token in row["exclusions"].split(",")
                if token.strip()
            }
            if (
                not permitted_tokens
                or "none" in permitted_tokens
                or not permitted_tokens.issubset(SOURCE_USES)
            ):
                report.error(
                    "SOURCE_POLICY",
                    f"{source_id} permitted_use must be a comma-separated subset of "
                    f"{sorted(SOURCE_USES)}",
                )
            if (
                not excluded_tokens
                or (
                    excluded_tokens != {"none"}
                    and not excluded_tokens.issubset(SOURCE_USES)
                )
            ):
                report.error(
                    "SOURCE_POLICY",
                    f"{source_id} exclusions must be none or a comma-separated subset "
                    f"of {sorted(SOURCE_USES)}",
                )
            normalized_exclusions = (
                set() if excluded_tokens == {"none"} else excluded_tokens
            )
            overlap = sorted(permitted_tokens & normalized_exclusions)
            if overlap:
                report.error(
                    "SOURCE_POLICY",
                    f"{source_id} both permits and excludes uses: {overlap}",
                )
            validate_timestamp(row["retrieved_at"], "SOURCE_RETRIEVED_AT", report)
            if not SHA256_RE.fullmatch(row["sha256"]):
                report.error("SOURCE_HASH", f"{source_id} requires a SHA-256 content hash")
            try:
                metadata = json.loads(row["metadata_json"] or "{}")
                derivatives = json.loads(row["derived_artifacts_json"] or "[]")
            except json.JSONDecodeError as exc:
                report.error("SOURCE_METADATA_JSON", f"{source_id}: {exc}")
                continue
            if not isinstance(metadata, dict) or not isinstance(derivatives, list):
                report.error("SOURCE_METADATA_JSON", f"{source_id} metadata/derivatives have wrong shapes")
                continue
            common = {
                "url": row["path_or_url"],
                "path": row["path_or_url"],
                "publisher": row["publisher_or_owner"],
                "retrieved_at": row["retrieved_at"],
                "sha256": row["sha256"],
                "privacy_class": row["privacy_class"],
                "capture_or_hash": metadata.get("capture_or_hash") or row["sha256"],
                "export_hash": metadata.get("export_hash") or row["sha256"],
            }
            combined = {**common, **metadata}
            missing = [
                name
                for name in adapter.get("required_metadata", [])
                if combined.get(name) in (None, "", [])
            ]
            if missing:
                report.error("SOURCE_METADATA", f"{source_id} missing adapter metadata: {missing}")
            if adapter_id == "transcript":
                parent_source_id = metadata.get("parent_source_id")
                if (
                    not isinstance(parent_source_id, str)
                    or not parent_source_id
                    or parent_source_id == source_id
                    or row_adapters.get(parent_source_id) not in {"audio", "video"}
                ):
                    report.error(
                        "SOURCE_LINEAGE",
                        f"{source_id} transcript must reference a registered audio/video parent_source_id",
                    )
            allowed_derivatives = set(adapter.get("derivatives", []))
            for derivative in derivatives:
                if not isinstance(derivative, dict):
                    report.error(
                        "SOURCE_DERIVATIVE",
                        f"{source_id} derivative entries must be objects",
                    )
                    continue
                kind = derivative.get("kind")
                if kind not in allowed_derivatives:
                    report.error(
                        "SOURCE_DERIVATIVE",
                        f"{source_id} has unsupported derivative kind {kind!r}",
                    )
                parent_ids = derivative.get("parent_source_ids")
                if (
                    not string_array(parent_ids, nonempty=True)
                    or source_id not in parent_ids
                ):
                    report.error(
                        "SOURCE_LINEAGE",
                        f"{source_id} derivative must link its registered parent",
                    )
                derivative_path = derivative.get("path")
                derivative_hash = derivative.get("sha256")
                validate_hashed_path(
                    derivative_path,
                    derivative_hash,
                    "SOURCE_DERIVATIVE",
                    report,
                )
                validate_timestamp(
                    derivative.get("created_at"),
                    "SOURCE_DERIVATIVE_TIME",
                    report,
                )
                if kind in {"ocr_text", "transcript", "cleaned_transcript"}:
                    for field in ("engine_or_author", "language"):
                        if (
                            not isinstance(derivative.get(field), str)
                            or not derivative[field].strip()
                        ):
                            report.error(
                                "SOURCE_DERIVATIVE",
                                f"{source_id} {kind} requires {field}",
                            )
            local_value = row["path_or_url"]
            expected_hash = row["sha256"]
            if local_value and expected_hash and not re.match(r"^[a-z]+://", local_value, re.I):
                validate_hashed_path(local_value, expected_hash, "SOURCE_FILE", report)
        report.ok("SOURCE_REGISTER", f"{len(seen)} source record(s)")
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "sources": {
            row["source_id"].strip(): {
                "class": row["class"],
                "adapter_id": row["adapter_id"],
                "privacy_class": row["privacy_class"],
                "permitted_use": {
                    token.strip().lower()
                    for token in row["permitted_use"].split(",")
                    if token.strip().lower() in SOURCE_USES
                },
                "exclusions": (
                    set()
                    if row["exclusions"].strip().lower() == "none"
                    else {
                        token.strip().lower()
                        for token in row["exclusions"].split(",")
                        if token.strip().lower() in SOURCE_USES
                    }
                ),
            }
            for row in rows
            if row["source_id"].strip()
        },
    }


def validate_batch_source_dependencies(
    batches: dict[str, dict[str, Any]],
    source_result: dict[str, Any] | None,
    report: Report,
) -> None:
    if not source_result:
        return
    sources = source_result.get("sources", {})
    for batch_id, batch in batches.items():
        dependencies = batch.get("source_dependencies")
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue
            source_id = dependency.get("source_id")
            source = sources.get(source_id)
            if source is None:
                report.error(
                    "BATCH_SOURCE_BINDING",
                    f"{batch_id} references unregistered source {source_id!r}",
                )
                continue
            source_class = source.get("class")
            use = dependency.get("use")
            if use not in source.get("permitted_use", set()):
                report.error(
                    "BATCH_SOURCE_POLICY",
                    f"{batch_id} use {use!r} is not permitted for source {source_id!r}",
                )
            if use in source.get("exclusions", set()):
                report.error(
                    "BATCH_SOURCE_POLICY",
                    f"{batch_id} use {use!r} is explicitly excluded for source {source_id!r}",
                )
            if use == "factual" and source_class != "authoritative":
                report.error(
                    "BATCH_SOURCE_AUTHORITY",
                    f"{batch_id} cannot use {source_id!r} ({source_class}) as factual authority",
                )
            elif use in {"context", "style"} and source_class == "incoming-draft":
                report.error(
                    "BATCH_SOURCE_AUTHORITY",
                    f"{batch_id} must label incoming draft {source_id!r} with use=incoming",
                )
            elif use == "incoming" and source_class != "incoming-draft":
                report.error(
                    "BATCH_SOURCE_AUTHORITY",
                    f"{batch_id} use=incoming requires an incoming-draft source: {source_id!r}",
                )


def validate_brief_source_expectations(
    brief_result: dict[str, Any] | None,
    source_result: dict[str, Any] | None,
    report: Report,
) -> None:
    if not brief_result or not source_result:
        return
    sources = source_result.get("sources", {})
    observed_classes = {
        source.get("class")
        for source in sources.values()
        if isinstance(source, dict)
    }
    none_values = {"none", "n/a", "not applicable", "not_applicable"}
    for source_class, statement in brief_result.get(
        "source_expectations",
        {},
    ).items():
        if (
            isinstance(statement, str)
            and statement.strip().lower() not in none_values
            and source_class not in observed_classes
        ):
            report.error(
                "BRIEF_SOURCE_BINDING",
                f"Brief declares {source_class} material but the Source Register has none",
            )


def validate_qa_check(
    adapter_id: str,
    check_name: str,
    check: dict[str, Any],
    artifact_path: str | None,
    brief_result: dict[str, Any] | None,
    report: Report,
) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "reference_artifact": None,
        "output_artifact": None,
    }
    status = check.get("status")
    coverage = check.get("coverage")
    evidence_artifacts = check.get("evidence_artifacts")
    if not isinstance(coverage, dict):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} requires structured coverage",
        )
        coverage = {}
    mode = coverage.get("mode")
    unit = coverage.get("unit")
    total = coverage.get("total")
    inspected = coverage.get("inspected")
    items = coverage.get("items")
    authority = coverage.get("sampling_authority")
    if not isinstance(unit, str) or not unit.strip():
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} coverage requires a unit",
        )
    if (
        not isinstance(total, int)
        or isinstance(total, bool)
        or total < 0
        or not isinstance(inspected, int)
        or isinstance(inspected, bool)
        or inspected < 0
        or inspected > total
    ):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} has invalid total/inspected coverage",
        )
    if not string_array(items):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} coverage items must be a string array",
        )
        items = []
    elif len(items) != len(set(items)):
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} coverage items must be unique",
        )
    if isinstance(inspected, int) and not isinstance(inspected, bool) and len(items) != inspected:
        report.error(
            "FORMAT_QA_COVERAGE",
            f"{adapter_id}.{check_name} inspected count must equal listed items",
        )

    if status == "NOT_APPLICABLE":
        if mode != "not_applicable" or total != 0 or inspected != 0 or items:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} NOT_APPLICABLE requires zero not_applicable coverage",
            )
        if authority is not None:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} NOT_APPLICABLE cannot retain sampling authority",
            )
    else:
        allowed_modes = (
            {"full", "sampled"}
            if status == "PASS"
            else {"full", "sampled", "partial"}
        )
        if mode not in allowed_modes or not isinstance(total, int) or total < 1:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} has invalid positive coverage mode",
            )
        if mode == "full":
            if inspected != total:
                report.error(
                    "FORMAT_QA_COVERAGE",
                    f"{adapter_id}.{check_name} full coverage must inspect every item",
                )
            if authority is not None:
                report.error(
                    "FORMAT_QA_COVERAGE",
                    f"{adapter_id}.{check_name} full coverage cannot retain sampling authority",
                )
        elif mode == "sampled":
            if not isinstance(authority, dict):
                report.error(
                    "FORMAT_QA_COVERAGE",
                    f"{adapter_id}.{check_name} sampled coverage requires Brief authority",
                )
            else:
                authority_path = validate_hashed_path(
                    authority.get("path"),
                    authority.get("sha256"),
                    "FORMAT_QA_SAMPLING",
                    report,
                )
                if set(authority) != {
                    "path",
                    "sha256",
                    "deliverable",
                    "policy",
                }:
                    report.error(
                        "FORMAT_QA_COVERAGE",
                        f"{adapter_id}.{check_name} sampling authority must contain "
                        "path, sha256, deliverable, and policy",
                    )
                if brief_result:
                    normalized_authority = (
                        authority_path.relative_to(report.root).as_posix()
                        if authority_path
                        else None
                    )
                    if (
                        normalized_authority != brief_result.get("path")
                        or str(authority.get("sha256", "")).lower()
                        != brief_result.get("sha256")
                    ):
                        report.error(
                            "FORMAT_QA_COVERAGE",
                            f"{adapter_id}.{check_name} sampling authority is not the approved Brief",
                        )
                    deliverable = next(
                        (
                            item
                            for item in brief_result.get("deliverables", [])
                            if isinstance(item, dict)
                            and item.get("path") == artifact_path
                        ),
                        None,
                    )
                    if (
                        not deliverable
                        or deliverable.get("visual_qa") != "sampled"
                        or authority.get("deliverable") != artifact_path
                        or authority.get("policy") != "sampled"
                    ):
                        report.error(
                            "FORMAT_QA_COVERAGE",
                            f"{adapter_id}.{check_name} sampled coverage is not "
                            "authorized by the deliverable's approved Brief policy",
                        )
                else:
                    report.error(
                        "FORMAT_QA_COVERAGE",
                        f"{adapter_id}.{check_name} sampling cannot be verified without the approved Brief",
                    )
        elif mode == "partial" and authority is not None:
            report.error(
                "FORMAT_QA_COVERAGE",
                f"{adapter_id}.{check_name} partial failure coverage cannot claim sampling authority",
            )

    if not isinstance(evidence_artifacts, list):
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} evidence_artifacts must be an array",
        )
        evidence_artifacts = []
    normalized_evidence_paths: set[str] = set()
    evidence_kinds: set[str] = set()
    for evidence_artifact in evidence_artifacts:
        if not isinstance(evidence_artifact, dict):
            report.error(
                "FORMAT_QA_EVIDENCE_ARTIFACT",
                f"{adapter_id}.{check_name} evidence artifact must be an object",
            )
            continue
        evidence_kind = evidence_artifact.get("kind")
        if evidence_kind not in {
            "validator_log",
            "rendered_output",
            "inspection_record",
            "comparison_report",
        }:
            report.error(
                "FORMAT_QA_EVIDENCE_ARTIFACT",
                f"{adapter_id}.{check_name} evidence artifact has invalid kind",
            )
        else:
            evidence_kinds.add(evidence_kind)
        validated = validate_hashed_path(
            evidence_artifact.get("path"),
            evidence_artifact.get("sha256"),
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            report,
        )
        if validated:
            normalized_evidence = validated.relative_to(report.root).as_posix()
            if normalized_evidence in normalized_evidence_paths:
                report.error(
                    "FORMAT_QA_EVIDENCE_ARTIFACT",
                    f"{adapter_id}.{check_name} repeats evidence artifact {normalized_evidence}",
                )
            normalized_evidence_paths.add(normalized_evidence)
    if status in {"PASS", "FAIL"} and not evidence_artifacts:
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} PASS/FAIL requires hashed evidence artifacts",
        )
    required_evidence_kind = {
        "structural": "validator_log",
        "render": "rendered_output",
        "visual": "inspection_record",
        "semantic": "comparison_report",
        "round_trip": "comparison_report",
    }[check_name]
    if status == "PASS" and required_evidence_kind not in evidence_kinds:
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} PASS requires {required_evidence_kind} evidence",
        )
    if status == "NOT_APPLICABLE" and evidence_artifacts:
        report.error(
            "FORMAT_QA_EVIDENCE_ARTIFACT",
            f"{adapter_id}.{check_name} NOT_APPLICABLE cannot retain evidence artifacts",
        )

    if check_name in {"semantic", "round_trip"} and status == "PASS":
        if not string_array(check.get("invariants"), nonempty=True):
            report.error(
                "FORMAT_QA_INVARIANTS",
                f"{adapter_id}.{check_name} PASS requires compared invariants",
            )
    if check_name == "semantic":
        reference = check.get("reference_artifact")
        if status == "PASS":
            if not isinstance(reference, dict):
                report.error(
                    "FORMAT_QA_SEMANTIC",
                    f"{adapter_id}.semantic PASS requires a hash-bound reference artifact",
                )
            else:
                validated_reference = validate_hashed_path(
                    reference.get("path"),
                    reference.get("sha256"),
                    "FORMAT_QA_SEMANTIC",
                    report,
                )
                if validated_reference:
                    normalized_reference = validated_reference.relative_to(
                        report.root
                    ).as_posix()
                    if artifact_path and normalized_reference == artifact_path:
                        report.error(
                            "FORMAT_QA_SEMANTIC",
                            f"{adapter_id}.semantic reference must be distinct from the output artifact",
                        )
                    normalized["reference_artifact"] = {
                        "path": normalized_reference,
                        "sha256": str(reference.get("sha256", "")).lower(),
                    }
        elif reference is not None:
            report.error(
                "FORMAT_QA_SEMANTIC",
                f"{adapter_id}.semantic reference_artifact is allowed only for PASS",
            )
    if check_name == "round_trip":
        output = check.get("output_artifact")
        if status == "PASS":
            if not isinstance(output, dict):
                report.error(
                    "FORMAT_QA_ROUND_TRIP",
                    f"{adapter_id}.round_trip PASS requires a hashed output artifact",
                )
            else:
                validated_output = validate_hashed_path(
                    output.get("path"),
                    output.get("sha256"),
                    "FORMAT_QA_ROUND_TRIP",
                    report,
                )
                if (
                    validated_output
                    and artifact_path
                    and validated_output.relative_to(report.root).as_posix()
                    == artifact_path
                ):
                    report.error(
                        "FORMAT_QA_ROUND_TRIP",
                        f"{adapter_id}.round_trip output must be distinct from the input artifact",
                    )
                if validated_output:
                    normalized["output_artifact"] = {
                        "path": validated_output.relative_to(report.root).as_posix(),
                        "sha256": str(output.get("sha256", "")).lower(),
                    }
        elif output is not None:
            report.error(
                "FORMAT_QA_ROUND_TRIP",
                f"{adapter_id}.round_trip output_artifact is allowed only for PASS",
            )
    return normalized


def validate_generation_record(
    generation: Any,
    artifact_path: str | None,
    artifact_sha256: str | None,
    brief_result: dict[str, Any] | None,
    adapter_id: str,
    report: Report,
) -> dict[str, Any] | None:
    if not isinstance(generation, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} READY evidence requires a generation record",
        )
        return None
    mode = generation.get("mode")
    if mode not in {"reproducible", "manual"}:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation mode must be reproducible or manual",
        )
    tool = generation.get("tool")
    if not isinstance(tool, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires tool identity",
        )
    else:
        for field in ("name", "version", "evidence"):
            if not isinstance(tool.get(field), str) or not tool[field].strip():
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} generation tool requires {field}",
                )
    command = generation.get("command")
    if not string_array(command, nonempty=True):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires an exact command or ordered action array",
        )
    configuration = generation.get("configuration")
    if not isinstance(configuration, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires configuration provenance",
        )
    else:
        configuration_path = configuration.get("path")
        configuration_hash = configuration.get("sha256")
        not_applicable_reason = configuration.get("not_applicable_reason")
        if configuration_path is None and configuration_hash is None:
            if (
                not isinstance(not_applicable_reason, str)
                or not not_applicable_reason.strip()
            ):
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} generation must hash-bind configuration or "
                    "record why none exists",
                )
        else:
            validate_hashed_path(
                configuration_path,
                configuration_hash,
                "FORMAT_QA_GENERATION_CONFIG",
                report,
            )
            if not_applicable_reason is not None:
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} hashed configuration cannot also be not_applicable",
                )
    inputs = generation.get("inputs")
    normalized_inputs: dict[str, str] = {}
    if not isinstance(inputs, list) or not inputs:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires hash-bound inputs",
        )
    else:
        for input_artifact in inputs:
            if not isinstance(input_artifact, dict):
                report.error(
                    "FORMAT_QA_GENERATION",
                    f"{adapter_id} generation input must be an object",
                )
                continue
            validated_input = validate_hashed_path(
                input_artifact.get("path"),
                input_artifact.get("sha256"),
                "FORMAT_QA_GENERATION_INPUT",
                report,
            )
            if validated_input:
                normalized_path = validated_input.relative_to(report.root).as_posix()
                if normalized_path in normalized_inputs:
                    report.error(
                        "FORMAT_QA_GENERATION",
                        f"{adapter_id} repeats generation input {normalized_path}",
                    )
                normalized_inputs[normalized_path] = str(
                    input_artifact.get("sha256", "")
                ).lower()
    output = generation.get("output")
    if not isinstance(output, dict):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation requires a hash-bound output",
        )
    else:
        validated_output = validate_hashed_path(
            output.get("path"),
            output.get("sha256"),
            "FORMAT_QA_GENERATION_OUTPUT",
            report,
        )
        if validated_output and (
            validated_output.relative_to(report.root).as_posix() != artifact_path
            or str(output.get("sha256", "")).lower() != artifact_sha256
        ):
            report.error(
                "FORMAT_QA_GENERATION",
                f"{adapter_id} generation output differs from the QA artifact",
            )
    manual_disposition = generation.get("manual_disposition")
    if mode == "manual":
        if (
            not isinstance(manual_disposition, str)
            or not manual_disposition.strip()
        ):
            report.error(
                "FORMAT_QA_GENERATION",
                f"{adapter_id} manual generation requires a reproducibility disposition",
            )
    elif manual_disposition is not None:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} reproducible generation cannot retain a manual disposition",
        )
    deliverable = next(
        (
            item
            for item in (brief_result or {}).get("deliverables", [])
            if isinstance(item, dict) and item.get("path") == artifact_path
        ),
        None,
    )
    if deliverable is None:
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} generation is not bound to an approved Brief deliverable",
        )
    elif (
        deliverable.get("reproducible") == "required"
        and mode != "reproducible"
    ):
        report.error(
            "FORMAT_QA_GENERATION",
            f"{adapter_id} deliverable requires reproducible generation",
        )
    return {
        "mode": mode,
        "inputs": normalized_inputs,
    }


def validate_format_qa_entry(
    item: Any,
    adapters: dict[str, dict[str, Any]],
    report: Report,
    brief_result: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        report.error("FORMAT_QA", "format QA entry must be an object")
        return None
    adapter_id = item.get("format")
    if adapter_id not in adapters:
        report.error("FORMAT_QA", f"unknown format QA adapter: {adapter_id!r}")
        return None
    if item.get("status") not in {"READY", "DEGRADED", "BLOCKED"}:
        report.error("FORMAT_QA", f"{adapter_id} has invalid QA status")
    evidence_path = validate_hashed_path(
        item.get("evidence_path"),
        item.get("sha256"),
        "FORMAT_QA",
        report,
    )
    for field in ("rendered", "visually_inspected"):
        if not isinstance(item.get(field), bool):
            report.error("FORMAT_QA", f"{adapter_id}.{field} must be boolean")
    visual_operation = adapters[adapter_id]["operations"]["visual_qa"]
    if item.get("status") == "READY" and visual_operation != "not_applicable":
        if item.get("rendered") is not True or item.get("visually_inspected") is not True:
            report.error("FORMAT_QA", f"{adapter_id} READY requires render and visual inspection")
    evidence: dict[str, Any] | None = None
    artifact_path: str | None = None
    artifact_sha256: str | None = None
    completed_at: datetime | None = None
    check_results: dict[str, dict[str, Any]] = {}
    generation_result: dict[str, Any] | None = None
    if evidence_path:
        if evidence_path.suffix.lower() != ".json":
            report.error("FORMAT_QA_EVIDENCE", f"{adapter_id} QA evidence must be JSON")
        else:
            evidence = read_required(evidence_path, report)
    if evidence is not None:
        if evidence.get("schema_version") != "1":
            report.error("FORMAT_QA_EVIDENCE", f"{adapter_id} evidence schema_version must be 1")
        if evidence.get("format") != adapter_id:
            report.error("FORMAT_QA_EVIDENCE", f"{adapter_id} evidence format differs")
        if evidence.get("status") != item.get("status"):
            report.error("FORMAT_QA_EVIDENCE", f"{adapter_id} evidence status differs")
        completed_at = validate_timestamp(
            evidence.get("completed_at"),
            "FORMAT_QA_EVIDENCE_TIME",
            report,
        )
        artifact = evidence.get("artifact")
        if not isinstance(artifact, dict):
            report.error("FORMAT_QA_EVIDENCE", f"{adapter_id} evidence requires artifact")
        else:
            validated_artifact = validate_hashed_path(
                artifact.get("path"),
                artifact.get("sha256"),
                "FORMAT_QA_ARTIFACT",
                report,
            )
            if validated_artifact:
                artifact_path = validated_artifact.relative_to(report.root).as_posix()
                artifact_sha256 = str(artifact.get("sha256", "")).lower()
        provider = evidence.get("provider")
        if not isinstance(provider, dict):
            report.error("FORMAT_QA_EVIDENCE", f"{adapter_id} evidence requires provider")
        else:
            for field in ("name", "version", "evidence"):
                if (
                    not isinstance(provider.get(field), str)
                    or not provider[field].strip()
                ):
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id} provider requires {field}",
                    )
        checks = evidence.get("checks")
        required_checks = {"structural", "render", "visual", "semantic", "round_trip"}
        if not isinstance(checks, dict) or set(checks) != required_checks:
            report.error(
                "FORMAT_QA_EVIDENCE",
                f"{adapter_id} evidence must define {sorted(required_checks)} checks",
            )
        else:
            for check_name, check in checks.items():
                if not isinstance(check, dict) or check.get("status") not in {
                    "PASS",
                    "FAIL",
                    "NOT_APPLICABLE",
                }:
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id}.{check_name} has invalid status",
                    )
                    continue
                if (
                    not isinstance(check.get("evidence"), str)
                    or not check["evidence"].strip()
                ):
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id}.{check_name} requires evidence",
                    )
                check_results[check_name] = validate_qa_check(
                    adapter_id,
                    check_name,
                    check,
                    artifact_path,
                    brief_result,
                    report,
                )
            if item.get("status") == "READY":
                generation_result = validate_generation_record(
                    evidence.get("generation"),
                    artifact_path,
                    artifact_sha256,
                    brief_result,
                    adapter_id,
                    report,
                )
            elif evidence.get("generation") is not None:
                generation_result = validate_generation_record(
                    evidence.get("generation"),
                    artifact_path,
                    artifact_sha256,
                    brief_result,
                    adapter_id,
                    report,
                )
            if item.get("status") == "READY":
                for check_name in ("structural", "semantic"):
                    if checks.get(check_name, {}).get("status") != "PASS":
                        report.error(
                            "FORMAT_QA_EVIDENCE",
                            f"{adapter_id} READY requires {check_name}=PASS",
                        )
                if visual_operation != "not_applicable":
                    for check_name in ("render", "visual"):
                        if checks.get(check_name, {}).get("status") != "PASS":
                            report.error(
                                "FORMAT_QA_EVIDENCE",
                                f"{adapter_id} READY requires {check_name}=PASS",
                            )
                round_trip = adapters[adapter_id]["operations"]["round_trip"]
                expected_round_trip = (
                    "NOT_APPLICABLE"
                    if round_trip in {"unsupported", "not_applicable"}
                    else "PASS"
                )
                if checks.get("round_trip", {}).get("status") != expected_round_trip:
                    report.error(
                        "FORMAT_QA_EVIDENCE",
                        f"{adapter_id} READY requires round_trip={expected_round_trip}",
                    )
            if item.get("rendered") is not (
                checks.get("render", {}).get("status") == "PASS"
            ):
                report.error(
                    "FORMAT_QA_EVIDENCE",
                    f"{adapter_id} rendered flag differs from evidence",
                )
            if item.get("visually_inspected") is not (
                checks.get("visual", {}).get("status") == "PASS"
            ):
                report.error(
                    "FORMAT_QA_EVIDENCE",
                    f"{adapter_id} visually_inspected flag differs from evidence",
                )
    return {
        "format": adapter_id,
        "status": item.get("status"),
        "evidence_path": (
            evidence_path.relative_to(report.root).as_posix() if evidence_path else None
        ),
        "sha256": str(item.get("sha256", "")).lower(),
        "rendered": item.get("rendered"),
        "visually_inspected": item.get("visually_inspected"),
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "completed_at": completed_at,
        "semantic_reference": check_results.get("semantic", {}).get(
            "reference_artifact"
        ),
        "generation": generation_result,
    }


def validate_capability_snapshot(
    path_value: Any,
    profile: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    report: Report,
    now: datetime,
) -> dict[str, Any] | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    try:
        path = ensure_within_root(report.root, Path(path_value))
    except ContractError as exc:
        report.error("STATE_CAPABILITIES", str(exc))
        return None
    snapshot = read_required(path, report)
    if not snapshot:
        return None
    if snapshot.get("schema_version") != "1":
        report.error("CAPABILITY_SCHEMA", "capability snapshot schema_version must be 1")
    captured = validate_timestamp(
        snapshot.get("captured_at"),
        "CAPABILITY_TIMESTAMP",
        report,
    )
    max_age = profile.get("snapshot_max_age_hours")
    if captured and isinstance(max_age, (int, float)) and not isinstance(max_age, bool):
        age_hours = (now - captured).total_seconds() / 3600
        if age_hours < -1:
            report.error(
                "CAPABILITY_FUTURE",
                f"capability snapshot is {abs(age_hours):.1f} hours in the future",
            )
        elif age_hours > max_age:
            report.error(
                "CAPABILITY_STALE",
                f"capability snapshot age {age_hours:.1f}h exceeds {max_age}h",
            )
        else:
            report.ok("CAPABILITY_FRESH", f"capability snapshot age {age_hours:.1f}h")
    if not isinstance(snapshot.get("registry"), str) or not snapshot["registry"]:
        report.error("CAPABILITY_REGISTRY", "capability snapshot requires registry provenance")
    declared = snapshot.get("declared_capabilities")
    if not string_array(declared):
        report.error("CAPABILITY_DECLARED", "declared_capabilities must be an array")
    elif declared:
        report.warn(
            "CAPABILITY_DECLARED",
            "legacy declared capabilities cannot establish final acceptance",
        )
    platform_snapshot = snapshot.get("platform_snapshot")
    validated_platform_observed: dict[str, dict[str, Any]] = {}
    if platform_snapshot is not None:
        if not isinstance(platform_snapshot, dict):
            report.error(
                "CAPABILITY_PLATFORM",
                "platform_snapshot must be null or a hash-bound object",
            )
        else:
            platform_path = validate_hashed_path(
                platform_snapshot.get("path"),
                platform_snapshot.get("sha256"),
                "CAPABILITY_PLATFORM",
                report,
            )
            capability_map = platform_snapshot.get("capability_map")
            if not isinstance(capability_map, dict):
                report.error(
                    "CAPABILITY_PLATFORM",
                    "platform_snapshot requires capability_map provenance",
                )
                capability_map_hash = None
            else:
                capability_map_hash = capability_map.get("sha256")
                if (
                    not isinstance(capability_map.get("path"), str)
                    or not capability_map["path"].strip()
                    or capability_map_hash != sha256_file(CANONICAL_CAPABILITY_MAP)
                ):
                    report.error(
                        "CAPABILITY_PLATFORM",
                        "platform snapshot capability map differs from the packaged canonical map",
                    )
            if platform_path and capability_map_hash:
                try:
                    validated_platform_observed, provenance = (
                        load_platform_capabilities(
                            platform_path,
                            CANONICAL_CAPABILITY_MAP,
                        )
                    )
                except (ContractError, OSError, json.JSONDecodeError) as exc:
                    report.error("CAPABILITY_PLATFORM", str(exc))
                else:
                    if (
                        platform_snapshot.get("platform") != provenance.get("platform")
                        or platform_snapshot.get("captured_at")
                        != provenance.get("captured_at")
                        or str(platform_snapshot.get("sha256", "")).lower()
                        != provenance.get("sha256")
                    ):
                        report.error(
                            "CAPABILITY_PLATFORM",
                            "platform snapshot provenance differs from its hashed source",
                        )
                    platform_captured = validate_timestamp(
                        provenance.get("captured_at"),
                        "CAPABILITY_PLATFORM_TIMESTAMP",
                        report,
                    )
                    if (
                        platform_captured
                        and isinstance(max_age, (int, float))
                        and not isinstance(max_age, bool)
                    ):
                        platform_age_hours = (
                            now - platform_captured
                        ).total_seconds() / 3600
                        if platform_age_hours < -1:
                            report.error(
                                "CAPABILITY_PLATFORM_FUTURE",
                                "platform capability evidence is "
                                f"{abs(platform_age_hours):.1f} hours in the future",
                            )
                        elif platform_age_hours > max_age:
                            report.error(
                                "CAPABILITY_PLATFORM_STALE",
                                "platform capability evidence age "
                                f"{platform_age_hours:.1f}h exceeds {max_age}h",
                            )
                        else:
                            report.ok(
                                "CAPABILITY_PLATFORM_FRESH",
                                "platform capability evidence age "
                                f"{platform_age_hours:.1f}h",
                            )
    observed = snapshot.get("observed")
    if not isinstance(observed, dict):
        report.error("CAPABILITY_OBSERVED", "capability snapshot requires observed evidence")
    else:
        live_process_observed: dict[str, dict[str, Any]] = {}
        if any(
            isinstance(item, dict) and item.get("source") == "process_probe"
            for item in observed.values()
        ):
            try:
                live_process_observed = observe_process_capabilities(set())
            except Exception as exc:
                report.error(
                    "CAPABILITY_PROCESS",
                    f"cannot reproduce process capability probe: {exc}",
                )
        for name, item in observed.items():
            if not isinstance(name, str) or not name or not isinstance(item, dict):
                report.error("CAPABILITY_OBSERVED", "observed capability entries are invalid")
                continue
            available = item.get("available")
            if not isinstance(available, bool):
                report.error("CAPABILITY_OBSERVED", f"{name}.available must be boolean")
            operations = item.get("operations")
            if (
                not isinstance(operations, list)
                or not all(
                    isinstance(operation, str)
                    and operation in CAPABILITY_OPERATIONS
                    for operation in operations
                )
            ):
                report.error("CAPABILITY_OPERATIONS", f"{name} has invalid operations")
            if available:
                for field in ("provider", "version", "evidence", "source"):
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"available capability {name} requires {field}",
                        )
                source = item.get("source")
                if source not in {
                    "process_probe",
                    "platform_snapshot",
                    "legacy_declare",
                } and not (
                    isinstance(source, str)
                    and source.startswith("derived_alias:")
                ):
                    report.error(
                        "CAPABILITY_EVIDENCE",
                        f"available capability {name} has unknown evidence source {source!r}",
                    )
                if source == "platform_snapshot":
                    if validated_platform_observed.get(name) != item:
                        report.error(
                            "CAPABILITY_PLATFORM",
                            f"{name} does not match the hash-bound platform snapshot",
                        )
                elif source == "process_probe":
                    if (
                        name not in PROCESS_OPERATIONS
                        or item.get("operations") != PROCESS_OPERATIONS.get(name)
                        or live_process_observed.get(name) != item
                    ):
                        report.error(
                            "CAPABILITY_PROCESS",
                            f"{name} does not match the live, fixed process-probe contract",
                        )
                elif isinstance(source, str) and source.startswith("derived_alias:"):
                    source_name = source.split(":", 1)[1]
                    parent = observed.get(source_name)
                    allowed_parents = DERIVED_ALIAS_PARENTS.get(name, ())
                    if source_name not in allowed_parents:
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"{name} is not an allowed alias of {source_name!r}",
                        )
                    elif not isinstance(parent, dict) or not parent.get("available"):
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"{name} derived alias has no available parent {source_name!r}",
                        )
                    elif {
                        key: value
                        for key, value in item.items()
                        if key != "source"
                    } != {
                        key: value
                        for key, value in parent.items()
                        if key != "source"
                    }:
                        report.error(
                            "CAPABILITY_EVIDENCE",
                            f"{name} derived alias differs from parent {source_name!r}",
                        )
    platform_names = {
        name
        for name, item in (observed or {}).items()
        if isinstance(item, dict) and item.get("source") == "platform_snapshot"
    } if isinstance(observed, dict) else set()
    if platform_names != set(validated_platform_observed):
        report.error(
            "CAPABILITY_PLATFORM",
            "observed platform capabilities do not exactly match the hash-bound platform snapshot",
        )

    capability_adapters = snapshot.get("adapters")
    statuses: dict[str, str] = {}
    if not isinstance(capability_adapters, list):
        report.error("CAPABILITY_ADAPTERS", "capability snapshot requires adapter results")
    else:
        for item in capability_adapters:
            if not isinstance(item, dict):
                report.error("CAPABILITY_ADAPTERS", "adapter result must be an object")
                continue
            adapter_id = item.get("id")
            if adapter_id not in adapters or adapter_id in statuses:
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"unknown or duplicate capability adapter {adapter_id!r}",
                )
                continue
            status = item.get("status")
            if status not in {"READY", "DEGRADED", "BLOCKED"}:
                report.error("CAPABILITY_ADAPTERS", f"{adapter_id} has invalid status")
                continue
            statuses[adapter_id] = status
            for field in (
                "missing_required",
                "missing_render_or_visual_groups",
                "missing_validation_groups",
            ):
                if not isinstance(item.get(field), list):
                    report.error(
                        "CAPABILITY_ADAPTERS",
                        f"{adapter_id}.{field} must be an array",
                    )
            if status == "READY" and item.get("claim_limit") is not None:
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"{adapter_id} READY cannot retain a claim limit",
                )
            if status != "READY" and (
                not isinstance(item.get("claim_limit"), str)
                or not item["claim_limit"].strip()
            ):
                report.error(
                    "CAPABILITY_ADAPTERS",
                    f"{adapter_id} {status} requires a claim limit",
                )
            if isinstance(observed, dict):
                recomputed = recompute_adapter_status(adapters[adapter_id], observed)
                for field in (
                    "status",
                    "missing_required",
                    "missing_render_or_visual_groups",
                    "missing_validation_groups",
                    "claim_limit",
                ):
                    if item.get(field) != recomputed.get(field):
                        report.error(
                            "CAPABILITY_RECOMPUTE",
                            f"{adapter_id}.{field} differs from observed capability evidence",
                        )
    missing_selected = sorted(set(profile.get("formats", [])) - set(statuses))
    if missing_selected:
        report.error(
            "CAPABILITY_ADAPTERS",
            f"selected formats are absent from capability results: {missing_selected}",
        )
    if not isinstance(snapshot.get("claim_warning"), str) or not snapshot[
        "claim_warning"
    ].strip():
        report.error("CAPABILITY_WARNING", "capability snapshot requires its claim warning")
    report.ok("CAPABILITY_SNAPSHOT", path.relative_to(report.root).as_posix())
    return {
        "path": path.relative_to(report.root).as_posix(),
        "sha256": sha256_file(path),
        "statuses": statuses,
        "captured_at": snapshot.get("captured_at"),
        "captured_time": captured,
    }


def validate_ready_deliverable_qa(
    brief_result: dict[str, Any] | None,
    qa_by_artifact: dict[str, dict[str, Any]],
    code: str,
    label: str,
    report: Report,
) -> None:
    deliverables = {
        item["path"]: item
        for item in (brief_result or {}).get("deliverables", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    missing = sorted(set(deliverables) - set(qa_by_artifact))
    unexpected = sorted(set(qa_by_artifact) - set(deliverables))
    if missing:
        report.error(code, f"{label} lacks QA for deliverables: {missing}")
    if unexpected:
        report.error(
            code,
            f"{label} contains QA for unapproved deliverables: {unexpected}",
        )
    for deliverable_path, deliverable in deliverables.items():
        qa_record = qa_by_artifact.get(deliverable_path)
        if qa_record and qa_record.get("format") != deliverable.get("format"):
            report.error(
                code,
                f"{label} QA format for {deliverable_path} differs from the approved Brief",
            )
    if any(item.get("status") != "READY" for item in qa_by_artifact.values()):
        report.error(code, f"{label} cannot retain DEGRADED or BLOCKED format QA")


def validate_publication_policy(
    publication: Any,
    gate: str,
    report: Report,
) -> dict[str, Any] | None:
    if not isinstance(publication, dict):
        report.error("GATE_PUBLICATION", f"{gate} requires publication policy")
        return None
    if gate != "publish-approved":
        if (
            publication.get("required") is not False
            or publication.get("target") is not None
            or publication.get("final_receipt") is not None
        ):
            report.error(
                "GATE_PUBLICATION",
                f"{gate} must record publication as not required",
            )
        return None
    if publication.get("required") is not True:
        report.error(
            "GATE_PUBLICATION",
            "publish-approved requires publication.required=true",
        )
    target = publication.get("target")
    if not isinstance(target, dict):
        report.error(
            "GATE_PUBLICATION",
            "publish-approved requires a structured publication target",
        )
    else:
        if target.get("kind") not in {
            "repository",
            "release",
            "deployment",
            "installation",
            "distribution",
            "other",
        }:
            report.error("GATE_PUBLICATION", "publication target kind is invalid")
        if target.get("visibility") not in {
            "public",
            "private",
            "internal",
            "local",
        }:
            report.error(
                "GATE_PUBLICATION",
                "publication target visibility is invalid",
            )
        for field in ("identifier", "action", "evidence"):
            if (
                not isinstance(target.get(field), str)
                or not target[field].strip()
            ):
                report.error(
                    "GATE_PUBLICATION",
                    f"publication target requires {field}",
                )
    final_receipt = publication.get("final_receipt")
    parsed_final_receipt: dict[str, Any] | None = None
    final_receipt_path: Path | None = None
    final_created_at: datetime | None = None
    final_confirmed_at: datetime | None = None
    if not isinstance(final_receipt, dict):
        report.error(
            "GATE_PUBLICATION",
            "publish-approved requires a hash-bound final receipt",
        )
    else:
        final_receipt_path = validate_hashed_path(
            final_receipt.get("path"),
            final_receipt.get("sha256"),
            "GATE_PUBLICATION_FINAL",
            report,
        )
        if final_receipt_path:
            parsed_final_receipt = read_required(final_receipt_path, report)
            if (
                not parsed_final_receipt
                or parsed_final_receipt.get("gate") != "final-approved"
            ):
                report.error(
                    "GATE_PUBLICATION",
                    "publication final_receipt must reference a final-approved receipt",
                )
            else:
                final_created_at = validate_timestamp(
                    parsed_final_receipt.get("created_at"),
                    "GATE_PUBLICATION_FINAL_TIME",
                    report,
                )
                final_confirmation = parsed_final_receipt.get("user_confirmation")
                if not isinstance(final_confirmation, dict):
                    report.error(
                        "GATE_PUBLICATION_FINAL_TIME",
                        "publication final receipt has no user confirmation",
                    )
                else:
                    final_confirmed_at = validate_timestamp(
                        final_confirmation.get("confirmed_at"),
                        "GATE_PUBLICATION_FINAL_TIME",
                        report,
                    )
    return {
        "final_bookmark": (
            parsed_final_receipt.get("bookmark") if parsed_final_receipt else None
        ),
        "final_path": (
            final_receipt_path.relative_to(report.root).as_posix()
            if final_receipt_path
            else None
        ),
        "final_sha256": (
            str(final_receipt.get("sha256", "")).lower()
            if isinstance(final_receipt, dict)
            else None
        ),
        "final_created_at": final_created_at,
        "final_confirmed_at": final_confirmed_at,
        "target": target if isinstance(target, dict) else None,
    }


def validate_receipts(
    state_dir: Path,
    lifecycle: dict[str, Any],
    profile: dict[str, Any],
    adapters: dict[str, dict[str, Any]],
    lifecycle_review: dict[str, Any] | None,
    lifecycle_qa: dict[str, dict[str, Any]],
    lifecycle_capability: dict[str, Any] | None,
    brief_result: dict[str, Any] | None,
    source_result: dict[str, Any] | None,
    report: Report,
) -> dict[str, Any]:
    receipts: list[dict[str, Any]] = []
    gates_dir = state_dir / "gates"
    if not gates_dir.is_dir():
        report.error("GATES_MISSING", "missing .manuscript-ops/gates directory")
        return {"all": receipts, "active": {}, "metadata": {}}
    seen_gates: set[str] = set()
    seen_bookmarks: set[str] = set()
    by_bookmark: dict[str, dict[str, Any]] = {}
    receipt_metadata: dict[str, dict[str, str]] = {}
    receipt_file_sets: dict[str, dict[str, str]] = {}
    publication_bindings: dict[str, dict[str, Any]] = {}
    locked_source_bindings: dict[str, dict[str, str]] = {}
    for path in sorted(gates_dir.rglob("*.json")):
        try:
            receipt = load_json(path)
        except ContractError as exc:
            report.error("GATE_JSON", str(exc))
            continue
        if not isinstance(receipt, dict):
            report.error("GATE_OBJECT", f"{path} must contain an object")
            continue
        gate = receipt.get("gate")
        if gate not in GATE_ALIASES:
            report.error("GATE_TYPE", f"invalid gate type in {path}")
            continue
        seen_gates.add(gate)
        if receipt.get("schema_version") != "1":
            report.error("GATE_SCHEMA", f"{path} schema_version must be 1")
        date_version = receipt.get("date_version")
        if not valid_date_version(date_version):
            report.error("GATE_VERSION", f"invalid date version in {path}")
        bookmark = receipt.get("bookmark")
        expected_bookmark = f"{gate}-{date_version}"
        if bookmark != expected_bookmark:
            report.error("GATE_BOOKMARK", f"{path} bookmark must be {expected_bookmark}")
        elif bookmark in seen_bookmarks:
            report.error("GATE_DUPLICATE", f"duplicate gate bookmark: {bookmark}")
        else:
            seen_bookmarks.add(bookmark)
            by_bookmark[bookmark] = receipt
            receipt_metadata[bookmark] = {
                "path": path.resolve().relative_to(report.root).as_posix(),
                "sha256": sha256_file(path),
            }
        if isinstance(bookmark, str) and path.stem != bookmark:
            report.error(
                "GATE_FILENAME",
                f"receipt filename {path.name} must match bookmark {bookmark}",
            )
        expected_alias = GATE_ALIASES[gate]
        if receipt.get("current_alias") != expected_alias:
            report.error("GATE_ALIAS", f"{path} current_alias must be {expected_alias}")
        created_time = validate_timestamp(
            receipt.get("created_at"),
            "GATE_CREATED_AT",
            report,
        )

        jj = receipt.get("jujutsu")
        if not isinstance(jj, dict):
            report.error("GATE_JJ", f"{path} requires Jujutsu evidence")
        else:
            for field in ("version", "change_id", "commit_id"):
                if not isinstance(jj.get(field), str) or not jj[field]:
                    report.error("GATE_JJ", f"{path} missing jujutsu.{field}")
            remote_count = jj.get("remote_count")
            if not isinstance(remote_count, int) or isinstance(remote_count, bool) or remote_count < 0:
                report.error("GATE_JJ", f"{path} has invalid remote_count")
            if remote_count and not profile.get("version_control", {}).get("remote_allowed", False):
                report.error("GATE_JJ_REMOTE", f"{path} records a forbidden remote")

        files = receipt.get("files")
        normalized_files: dict[str, str] = {}
        if not isinstance(files, list) or not files:
            report.error("GATE_FILES", f"receipt has no files: {path}")
        else:
            for entry in files:
                if not isinstance(entry, dict):
                    report.error("GATE_FILE_ENTRY", f"invalid file entry in {path}")
                    continue
                target = validate_hashed_path(
                    entry.get("path"),
                    entry.get("sha256"),
                    "GATE_FILE",
                    report,
                )
                if target:
                    normalized_files[target.relative_to(report.root).as_posix()] = str(
                        entry["sha256"]
                    ).lower()
        if isinstance(bookmark, str):
            receipt_file_sets[bookmark] = normalized_files

        baseline_profile = receipt.get("baseline_profile")
        baseline_required = gate == "baseline"
        if (
            not isinstance(baseline_profile, dict)
            or baseline_profile.get("required") is not baseline_required
        ):
            report.error(
                "GATE_BASELINE_PROFILE",
                f"{gate} baseline_profile.required must be {baseline_required}",
            )
        elif baseline_required:
            baseline_profile_path = validate_hashed_path(
                baseline_profile.get("path"),
                baseline_profile.get("sha256"),
                "GATE_BASELINE_PROFILE",
                report,
            )
            if baseline_profile_path:
                relative_profile_snapshot = baseline_profile_path.relative_to(
                    report.root
                ).as_posix()
                if not relative_profile_snapshot.startswith(
                    ".manuscript-ops/snapshots/"
                ):
                    report.error(
                        "GATE_BASELINE_PROFILE",
                        "baseline Profile snapshot must be stored under "
                        ".manuscript-ops/snapshots/",
                    )
                if (
                    normalized_files.get(relative_profile_snapshot)
                    != str(baseline_profile.get("sha256", "")).lower()
                ):
                    report.error(
                        "GATE_BASELINE_PROFILE",
                        "baseline receipt files do not bind its Profile snapshot",
                    )
                baseline_payload = read_required(baseline_profile_path, report)
                baseline_date = (
                    baseline_payload.get("date_version")
                    if isinstance(baseline_payload, dict)
                    else None
                )
                baseline_normalized = (
                    validate_profile(baseline_payload, report)
                    if isinstance(baseline_payload, dict)
                    else {}
                )
                if (
                    not baseline_payload
                    or baseline_payload.get("schema_version") != "1"
                    or not isinstance(baseline_payload.get("paths"), dict)
                    or not baseline_payload.get("paths")
                    or not isinstance(
                        baseline_payload.get("version_control"),
                        dict,
                    )
                    or not isinstance(baseline_date, dict)
                    or not valid_date_version(baseline_date.get("value"))
                    or not baseline_normalized.get("paths")
                    or not baseline_normalized.get("version_control")
                ):
                    report.error(
                        "GATE_BASELINE_PROFILE",
                        "baseline Profile snapshot lacks the dated path/VCS configuration",
                    )
        elif (
            baseline_profile.get("path") not in {"", None}
            or baseline_profile.get("sha256") not in {"", None}
        ):
            report.error(
                "GATE_BASELINE_PROFILE",
                f"{gate} cannot retain baseline Profile evidence",
            )

        locked_source = receipt.get("locked_source")
        locked_source_required = gate == "source-locked"
        if (
            not isinstance(locked_source, dict)
            or locked_source.get("required") is not locked_source_required
        ):
            report.error(
                "GATE_LOCKED_SOURCE",
                f"{gate} locked_source.required must be {locked_source_required}",
            )
        elif locked_source_required:
            locked_source_path = validate_hashed_path(
                locked_source.get("path"),
                locked_source.get("sha256"),
                "GATE_LOCKED_SOURCE",
                report,
            )
            if locked_source_path:
                normalized_locked_source = locked_source_path.relative_to(
                    report.root
                ).as_posix()
                locked_source_hash = str(
                    locked_source.get("sha256", "")
                ).lower()
                if normalized_files.get(normalized_locked_source) != locked_source_hash:
                    report.error(
                        "GATE_LOCKED_SOURCE",
                        "source-lock receipt files do not bind the locked manuscript",
                    )
                manuscript_value = profile.get("paths", {}).get("manuscript")
                if isinstance(manuscript_value, str):
                    try:
                        manuscript_root = ensure_within_root(
                            report.root,
                            Path(manuscript_value),
                        )
                        inside_mapping = (
                            locked_source_path == manuscript_root
                            if manuscript_root.is_file()
                            else locked_source_path.is_relative_to(manuscript_root)
                        )
                    except (ContractError, OSError, ValueError):
                        inside_mapping = False
                    if not inside_mapping:
                        report.error(
                            "GATE_LOCKED_SOURCE",
                            "locked manuscript is outside the Profile manuscript mapping",
                        )
                else:
                    report.error(
                        "GATE_LOCKED_SOURCE",
                        "ProjectProfile has no manuscript mapping for source lock",
                    )
                if isinstance(bookmark, str):
                    locked_source_bindings[bookmark] = {
                        "path": normalized_locked_source,
                        "sha256": locked_source_hash,
                    }
        elif (
            locked_source.get("path") not in {"", None}
            or locked_source.get("sha256") not in {"", None}
        ):
            report.error(
                "GATE_LOCKED_SOURCE",
                f"{gate} cannot retain locked-source evidence",
            )

        publication_binding = validate_publication_policy(
            receipt.get("publication"),
            gate,
            report,
        )
        if isinstance(bookmark, str) and publication_binding:
            publication_bindings[bookmark] = publication_binding

        capability = receipt.get("capability_snapshot")
        capability_time: datetime | None = None
        if not isinstance(capability, dict) or not isinstance(capability.get("required"), bool):
            report.error("GATE_CAPABILITY", f"{path} has invalid capability evidence")
        elif capability["required"]:
            capability_path = validate_hashed_path(
                capability.get("path"),
                capability.get("sha256"),
                "GATE_CAPABILITY",
                report,
            )
            if capability_path:
                capability_payload = read_required(capability_path, report)
                if capability_payload:
                    capability_time = validate_timestamp(
                        capability_payload.get("captured_at"),
                        "GATE_CAPABILITY_TIME",
                        report,
                    )

        qa = receipt.get("format_qa")
        qa_by_artifact: dict[str, dict[str, Any]] = {}
        if not isinstance(qa, list):
            report.error("GATE_FORMAT_QA", f"{path} format_qa must be an array")
        else:
            for item in qa:
                normalized_qa = validate_format_qa_entry(
                    item,
                    adapters,
                    report,
                    brief_result,
                )
                if normalized_qa:
                    artifact_id = normalized_qa.get("artifact_path")
                    if not artifact_id:
                        report.error(
                            "GATE_FORMAT_QA",
                            f"{gate} QA record has no validated artifact",
                        )
                    elif artifact_id in qa_by_artifact:
                        report.error(
                            "GATE_FORMAT_QA",
                            f"{gate} repeats QA for deliverable {artifact_id}",
                        )
                    else:
                        qa_by_artifact[artifact_id] = normalized_qa
        if gate in {"final-approved", "publish-approved"}:
            validate_ready_deliverable_qa(
                brief_result,
                qa_by_artifact,
                "GATE_FORMAT_QA",
                gate,
                report,
            )
            if not isinstance(capability, dict) or capability.get("required") is not True:
                report.error(
                    "GATE_CAPABILITY",
                    f"{gate} requires a hashed capability snapshot",
                )

        review = receipt.get("review")
        should_review = gate in REVIEW_GATES
        parsed_review: dict[str, Any] | None = None
        if not isinstance(review, dict) or review.get("required") is not should_review:
            report.error("GATE_REVIEW", f"{gate} review.required must be {should_review}")
        elif should_review:
            review_path = validate_hashed_path(
                review.get("report_path"),
                review.get("report_sha256"),
                "GATE_REVIEW",
                report,
            )
            parsed_review = validate_project_review_report(review.get("report_path"), report)
            if review.get("verdict") != "PASS":
                report.error("GATE_REVIEW", f"{gate} requires a project-review PASS")
            if parsed_review:
                expected_milestone = GATE_REVIEW_MILESTONES[gate]
                if parsed_review["milestone"] != expected_milestone:
                    report.error(
                        "GATE_REVIEW",
                        f"{gate} requires milestone {expected_milestone}",
                    )
                if review.get("verdict") != parsed_review.get("verdict"):
                    report.error(
                        "GATE_REVIEW_MISMATCH",
                        f"{gate} receipt verdict differs from the hashed project-review result",
                    )
                for artifact_path, artifact_hash in parsed_review["snapshot"].items():
                    if normalized_files.get(artifact_path) != artifact_hash:
                        report.error(
                            "GATE_REVIEW_ARTIFACT",
                            f"{gate} receipt does not bind reviewed artifact {artifact_path}",
                        )
                if gate == "framework-approved":
                    outline_value = profile.get("paths", {}).get("outline")
                    if not isinstance(outline_value, str):
                        report.error(
                            "GATE_FRAMEWORK_ARTIFACT",
                            "ProjectProfile has no mapped outline artifact",
                        )
                    else:
                        try:
                            outline_path = ensure_within_root(
                                report.root,
                                Path(outline_value),
                            )
                            normalized_outline = outline_path.relative_to(
                                report.root
                            ).as_posix()
                        except (ContractError, ValueError) as exc:
                            report.error("GATE_FRAMEWORK_ARTIFACT", str(exc))
                        else:
                            if not outline_path.is_file():
                                report.error(
                                    "GATE_FRAMEWORK_ARTIFACT",
                                    "framework gate requires the mapped outline to be a file",
                                )
                            outline_hash = normalized_files.get(normalized_outline)
                            if (
                                not outline_hash
                                or parsed_review["snapshot"].get(normalized_outline)
                                != outline_hash
                            ):
                                report.error(
                                    "GATE_FRAMEWORK_ARTIFACT",
                                    "framework receipt and review must hash-bind the mapped outline",
                                )
                if gate == "source-locked" and isinstance(bookmark, str):
                    locked_binding = locked_source_bindings.get(bookmark)
                    if (
                        not locked_binding
                        or parsed_review["snapshot"].get(
                            locked_binding["path"]
                        )
                        != locked_binding["sha256"]
                    ):
                        report.error(
                            "GATE_LOCKED_SOURCE",
                            "source-lock review does not hash-bind the locked manuscript",
                        )
            if review_path and str(review_path.relative_to(report.root)) != str(
                Path(review.get("report_path"))
            ):
                report.error("GATE_REVIEW", f"{gate} review path normalization differs")
        else:
            if review.get("verdict") != "NOT_REQUIRED":
                report.error("GATE_REVIEW", f"{gate} review verdict must be NOT_REQUIRED")

        if gate in {"final-approved", "publish-approved"}:
            for artifact_id, qa_entry in qa_by_artifact.items():
                artifact_path = qa_entry.get("artifact_path")
                artifact_hash = qa_entry.get("artifact_sha256")
                if (
                    not artifact_path
                    or not artifact_hash
                    or normalized_files.get(artifact_path) != artifact_hash
                ):
                    report.error(
                        "GATE_FORMAT_QA_ARTIFACT",
                        f"{gate} receipt does not bind QA artifact {artifact_id}",
                    )
                if (
                    parsed_review
                    and parsed_review["snapshot"].get(artifact_path) != artifact_hash
                ):
                    report.error(
                        "GATE_REVIEW_ARTIFACT",
                        f"{gate} review snapshot does not bind QA artifact {artifact_id}",
                    )

        confirmation = receipt.get("user_confirmation")
        confirmation_time: datetime | None = None
        if not isinstance(confirmation, dict):
            report.error("GATE_CONFIRMATION", f"{path} requires user confirmation")
        else:
            for field in ("actor", "exact_statement"):
                if (
                    not isinstance(confirmation.get(field), str)
                    or not confirmation[field].strip()
                ):
                    report.error("GATE_CONFIRMATION", f"{path} missing confirmation {field}")
            confirmation_time = validate_timestamp(
                confirmation.get("confirmed_at"),
                "GATE_CONFIRMATION_TIME",
                report,
            )
        if created_time and confirmation_time and created_time < confirmation_time:
            report.error(
                "GATE_CONFIRMATION_TIME",
                f"{gate} receipt was created before its user confirmation",
            )
        evidence_times = [
            parsed_review.get("completed_at") if parsed_review else None,
            capability_time,
            *[item.get("completed_at") for item in qa_by_artifact.values()],
        ]
        if confirmation_time and any(
            isinstance(evidence_time, datetime) and evidence_time > confirmation_time
            for evidence_time in evidence_times
        ):
            report.error(
                "GATE_CONFIRMATION_TIME",
                f"{gate} was confirmed before its review, capability, or format-QA evidence completed",
            )
        if gate == "publish-approved" and publication_binding and confirmation_time:
            final_times = (
                publication_binding.get("final_confirmed_at"),
                publication_binding.get("final_created_at"),
            )
            if any(
                isinstance(final_time, datetime) and final_time > confirmation_time
                for final_time in final_times
            ):
                report.error(
                    "GATE_PUBLICATION_CHRONOLOGY",
                    "publish approval was confirmed before the referenced final "
                    "approval receipt existed",
                )
        receipts.append(receipt)

    required = lifecycle.get("required_gates", set())
    missing = sorted(required - seen_gates)
    if missing:
        report.error("GATES_REQUIRED", f"missing required gate receipts: {missing}")
    ahead = sorted(seen_gates - required)
    if ahead:
        report.error("GATES_PHASE", f"gate receipts are ahead of lifecycle state: {ahead}")
    if not receipts:
        report.error("GATES_EMPTY", "no gate receipts found")
    else:
        report.ok("GATES_PRESENT", f"{len(receipts)} phase-consistent receipt(s)")
    active: dict[str, dict[str, Any]] = {}
    for gate, bookmark in lifecycle.get("active_receipts", {}).items():
        receipt = by_bookmark.get(bookmark)
        if receipt is None:
            report.error(
                "GATE_ACTIVE_MISSING",
                f"active receipt {bookmark!r} for {gate} was not found",
            )
            continue
        if receipt.get("gate") != gate:
            report.error(
                "GATE_ACTIVE_TYPE",
                f"active receipt {bookmark!r} is not a {gate} receipt",
            )
            continue
        active[gate] = receipt

    active_brief = active.get("brief-approved")
    if active_brief and brief_result:
        brief_files = receipt_file_sets.get(active_brief["bookmark"], {})
        if brief_files.get(brief_result["path"]) != brief_result["sha256"]:
            report.error(
                "BRIEF_GATE_BINDING",
                "active brief-approved receipt does not bind the approved ManuscriptBrief",
            )
        brief_confirmation = active_brief.get("user_confirmation", {})
        expected_confirmation = {
            "actor": brief_result.get("approver"),
            "exact_statement": brief_result.get("exact_confirmation"),
            "confirmed_at": brief_result.get("confirmed_at"),
        }
        if any(
            brief_confirmation.get(field) != expected
            for field, expected in expected_confirmation.items()
        ):
            report.error(
                "BRIEF_GATE_CONFIRMATION",
                "active brief-approved receipt confirmation differs from the approved ManuscriptBrief",
            )

    active_source = active.get("source-locked")
    if active_source and source_result:
        source_files = receipt_file_sets.get(active_source["bookmark"], {})
        if source_files.get(source_result["path"]) != source_result["sha256"]:
            report.error(
                "SOURCE_GATE_BINDING",
                "active source-locked receipt does not bind the current Source Register",
            )
        source_review = active_source.get("review", {})
        parsed_source_review = validate_project_review_report(
            source_review.get("report_path"),
            report,
        )
        if (
            parsed_source_review
            and parsed_source_review["snapshot"].get(source_result["path"])
            != source_result["sha256"]
        ):
            report.error(
                "SOURCE_GATE_BINDING",
                "source-lock ReviewReport snapshot does not bind the current Source Register",
            )
    if active_source and lifecycle_qa:
        locked_binding = locked_source_bindings.get(
            active_source.get("bookmark"),
        )
        if not locked_binding:
            report.error(
                "SOURCE_GATE_BINDING",
                "active source-lock receipt has no locked manuscript binding",
            )
        else:
            for artifact_id, qa_entry in lifecycle_qa.items():
                if qa_entry.get("semantic_reference") != locked_binding:
                    report.error(
                        "FORMAT_QA_SOURCE_LINEAGE",
                        f"{artifact_id} semantic QA does not compare the active locked manuscript",
                    )
                generation_inputs = (
                    qa_entry.get("generation", {}).get("inputs", {})
                    if isinstance(qa_entry.get("generation"), dict)
                    else {}
                )
                if (
                    generation_inputs.get(locked_binding["path"])
                    != locked_binding["sha256"]
                ):
                    report.error(
                        "FORMAT_QA_SOURCE_LINEAGE",
                        f"{artifact_id} generation inputs do not bind the active locked manuscript",
                    )

    active_publish = active.get("publish-approved")
    active_final = active.get("final-approved")
    if active_publish:
        binding = publication_bindings.get(active_publish.get("bookmark"), {})
        active_final_metadata = (
            receipt_metadata.get(active_final.get("bookmark"))
            if active_final
            else None
        )
        if (
            not active_final
            or binding.get("final_bookmark") != active_final.get("bookmark")
            or not active_final_metadata
            or binding.get("final_path") != active_final_metadata.get("path")
            or binding.get("final_sha256") != active_final_metadata.get("sha256")
        ):
            report.error(
                "GATE_PUBLICATION_BINDING",
                "active publish-approved receipt does not path/hash-bind the active final-approved receipt",
            )

    expected_review_gate = PHASE_REVIEW_GATE.get(lifecycle.get("phase"))
    if (
        lifecycle.get("phase") in REPORT_PHASES
        and lifecycle_review
        and lifecycle_review.get("verdict") != "PASS"
    ):
        report.error(
            "STATE_REVIEW_VERDICT",
            f"phase {lifecycle.get('phase')} requires ReviewReport PASS",
        )
    if expected_review_gate and lifecycle_review:
        receipt = active.get(expected_review_gate)
        receipt_review = receipt.get("review", {}) if receipt else {}
        if not receipt or receipt_review.get("report_path") != lifecycle_review["path"]:
            report.error(
                "STATE_REVIEW_BINDING",
                f"latest ReviewReport is not bound by active {expected_review_gate}",
            )
        elif str(receipt_review.get("report_sha256", "")).lower() != lifecycle_review["sha256"]:
            report.error(
                "STATE_REVIEW_BINDING",
                "latest ReviewReport hash differs from its active gate receipt",
            )
    if lifecycle.get("phase") in FINAL_PHASES:
        for gate in (
            {"final-approved", "publish-approved"}
            if lifecycle.get("phase") in {"published", "archived"}
            else {"final-approved"}
        ):
            receipt = active.get(gate)
            if not receipt:
                continue
            receipt_qa = {
                item["artifact_path"]: item
                for item in (
                    validate_format_qa_entry(
                        entry,
                        adapters,
                        report,
                        brief_result,
                    )
                    for entry in receipt.get("format_qa", [])
                )
                if item and item.get("artifact_path")
            }
            if receipt_qa != lifecycle_qa:
                report.error(
                    "STATE_FORMAT_QA_BINDING",
                    f"lifecycle format QA differs from active {gate} receipt",
                )
            capability = receipt.get("capability_snapshot", {})
            if not lifecycle_capability or (
                capability.get("path") != lifecycle_capability["path"]
                or str(capability.get("sha256", "")).lower()
                != lifecycle_capability["sha256"]
            ):
                report.error(
                    "STATE_CAPABILITY_BINDING",
                    f"lifecycle capability snapshot differs from active {gate} receipt",
                )
    return {
        "all": receipts,
        "active": active,
        "metadata": receipt_metadata,
    }


def run_jj(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    command = ["jj", "--ignore-working-copy", "-R", str(root), *args]
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def run_jj_bytes(
    root: Path,
    *args: str,
) -> subprocess.CompletedProcess[bytes] | None:
    command = ["jj", "--ignore-working-copy", "-R", str(root), *args]
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            cwd=root,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def validate_jj(
    profile: dict[str, Any],
    receipt_index: dict[str, Any],
    report: Report,
) -> None:
    if not (report.root / ".jj" / "repo").exists():
        report.error("JJ_MISSING", "Project route has no valid .jj repository")
        return
    version = run_jj(report.root, "--version")
    if not version or version.returncode != 0:
        report.error("JJ_UNAVAILABLE", "cannot execute jj for this repository")
        return
    observed_version = version.stdout.strip()
    baseline = profile.get("version_control", {}).get("tested_baseline")
    if isinstance(baseline, str) and baseline not in observed_version:
        report.warn("JJ_VERSION", f"command probing required for {observed_version}")
    else:
        report.ok("JJ_VERSION", observed_version)

    immutable_config = run_jj(
        report.root,
        "config",
        "list",
        "--repo",
        'revset-aliases."immutable_heads()"',
        "-T",
        "value",
    )
    if not immutable_config or immutable_config.returncode != 0:
        report.error(
            "JJ_IMMUTABLE_CONFIG",
            "cannot read repository-local immutable_heads configuration",
        )
    else:
        configured = immutable_config.stdout
        required_patterns = [f"{gate}-*" for gate in GATE_ALIASES]
        missing_patterns = [
            pattern for pattern in required_patterns if pattern not in configured
        ]
        if missing_patterns:
            report.error(
                "JJ_IMMUTABLE_CONFIG",
                f"immutable_heads omits dated gate patterns: {missing_patterns}",
            )
        if "current-" in configured:
            report.error(
                "JJ_ALIAS_IMMUTABLE",
                "immutable_heads must not include mutable current-* aliases",
            )
        if not missing_patterns and "current-" not in configured:
            report.ok(
                "JJ_IMMUTABLE_CONFIG",
                "repository config protects dated gates and excludes current aliases",
            )

    remotes = run_jj(report.root, "git", "remote", "list")
    if not remotes or remotes.returncode != 0:
        report.error("JJ_REMOTE_CHECK", "could not list Jujutsu Git remotes")
    else:
        lines = [line for line in remotes.stdout.splitlines() if line.strip()]
        remote_policy = profile.get("version_control", {}).get("remote_allowed", False)
        if lines and not remote_policy:
            report.error("JJ_REMOTE_POLICY", f"unexpected remote(s): {lines}")
        else:
            report.ok("JJ_REMOTE_POLICY", f"{len(lines)} remote(s), policy={remote_policy}")

    bookmarks = run_jj(report.root, "bookmark", "list")
    if not bookmarks or bookmarks.returncode != 0:
        report.error("JJ_BOOKMARK_CHECK", "could not list Jujutsu bookmarks")
        return
    names = {
        line.split(":", 1)[0].strip()
        for line in bookmarks.stdout.splitlines()
        if ":" in line and not line.startswith(" ")
    }

    def revision_value(revision: str, template: str) -> str | None:
        result = run_jj(
            report.root,
            "log",
            "-r",
            revision,
            "--no-graph",
            "-T",
            template,
        )
        if not result or result.returncode != 0:
            return None
        return result.stdout.strip()

    active_bookmarks = {
        receipt["bookmark"]
        for receipt in receipt_index.get("active", {}).values()
        if isinstance(receipt, dict) and isinstance(receipt.get("bookmark"), str)
    }
    for receipt in receipt_index.get("all", []):
        if not isinstance(receipt, dict):
            report.error("JJ_RECEIPT_SCHEMA", "GateReceipt must be an object")
            continue
        bookmark = receipt.get("bookmark")
        alias = receipt.get("current_alias")
        if (
            not isinstance(bookmark, str)
            or not bookmark
            or not isinstance(alias, str)
            or not alias
        ):
            report.error(
                "JJ_RECEIPT_SCHEMA",
                "GateReceipt requires string bookmark and current_alias",
            )
            continue
        if bookmark not in names:
            report.error("JJ_GATE_MISSING", f"missing gate bookmark: {bookmark}")
            continue
        seal_commit = revision_value(bookmark, "commit_id")
        if not seal_commit:
            report.error("JJ_GATE_RESOLVE", f"cannot resolve gate bookmark: {bookmark}")
            continue
        receipt_jj = receipt.get("jujutsu")
        if not isinstance(receipt_jj, dict):
            report.error(
                "JJ_RECEIPT_SCHEMA",
                f"{bookmark} requires a Jujutsu evidence object",
            )
            receipt_jj = {}
        receipt_commit = receipt_jj.get("commit_id")
        content_commit = revision_value(f"parents({bookmark})", "commit_id")
        if not content_commit or content_commit != receipt_commit:
            report.error(
                "JJ_RECEIPT_COMMIT",
                f"receipt content commit is not the parent of seal {bookmark}",
            )
        gate_change = revision_value(f"parents({bookmark})", "change_id")
        receipt_change = receipt_jj.get("change_id")
        if not gate_change or gate_change != receipt_change:
            report.error(
                "JJ_RECEIPT_CHANGE",
                f"receipt content change is not the parent of seal {bookmark}",
            )
        immutable = revision_value(bookmark, 'if(immutable, "true", "false")')
        if immutable != "true":
            report.error("JJ_GATE_MUTABLE", f"dated gate is not immutable: {bookmark}")
        else:
            report.ok("JJ_GATE_IMMUTABLE", bookmark)
        receipt_metadata = receipt_index.get("metadata", {}).get(bookmark)
        if not isinstance(receipt_metadata, dict):
            report.error(
                "JJ_GATE_RECEIPT_MISSING",
                f"no local receipt metadata for {bookmark}",
            )
        else:
            receipt_path = receipt_metadata.get("path")
            gated_receipt = (
                run_jj_bytes(
                    report.root,
                    "file",
                    "show",
                    "-r",
                    bookmark,
                    receipt_path,
                )
                if isinstance(receipt_path, str)
                else None
            )
            if not gated_receipt or gated_receipt.returncode != 0:
                report.error(
                    "JJ_GATE_RECEIPT_MISSING",
                    f"{bookmark} does not contain its GateReceipt",
                )
            elif (
                hashlib.sha256(gated_receipt.stdout).hexdigest()
                != receipt_metadata.get("sha256")
            ):
                report.error(
                    "JJ_GATE_RECEIPT_HASH",
                    f"{bookmark} contains different GateReceipt bytes",
                )
            else:
                report.ok("JJ_GATE_RECEIPT_HASH", bookmark)
        receipt_files = receipt.get("files")
        if not isinstance(receipt_files, list):
            report.error(
                "JJ_RECEIPT_SCHEMA",
                f"{bookmark} requires a files array",
            )
            receipt_files = []
        for file_entry in receipt_files:
            if (
                not isinstance(file_entry, dict)
                or not isinstance(file_entry.get("path"), str)
                or not isinstance(file_entry.get("sha256"), str)
            ):
                continue
            file_path = Path(file_entry["path"]).as_posix()
            gated_file = run_jj_bytes(
                report.root,
                "file",
                "show",
                "-r",
                content_commit or f"parents({bookmark})",
                file_path,
            )
            if not gated_file or gated_file.returncode != 0:
                report.error(
                    "JJ_GATE_FILE_MISSING",
                    f"{bookmark} does not contain gated file {file_path}",
                )
                continue
            observed_hash = hashlib.sha256(gated_file.stdout).hexdigest()
            if observed_hash != file_entry["sha256"].lower():
                report.error(
                    "JJ_GATE_FILE_HASH",
                    f"{bookmark} bytes differ from receipt hash for {file_path}",
                )
            else:
                report.ok(
                    "JJ_GATE_FILE_HASH",
                    f"{bookmark} parent:{file_path}",
                )
        if bookmark in active_bookmarks:
            if alias not in names:
                report.error("JJ_ALIAS_MISSING", f"missing current alias: {alias}")
            else:
                alias_commit = revision_value(alias, "commit_id")
                if alias_commit != seal_commit:
                    report.error("JJ_ALIAS_TARGET", f"{alias} does not point to {bookmark}")
                else:
                    report.ok("JJ_ALIAS_TARGET", f"{alias} -> {bookmark}")
    report.ok("JJ_BOOKMARK_CHECK", f"observed {len(names)} bookmark(s)")


def required_review_axes(
    profile: dict[str, Any],
    source_result: dict[str, Any] | None,
    active_batch: dict[str, Any] | None,
) -> set[str]:
    required = set(CORE_PROJECT_REVIEW_AXES)
    if source_result and any(
        source.get("adapter_id") == "image-scan"
        for source in source_result.get("sources", {}).values()
        if isinstance(source, dict)
    ):
        required.add("images")
    if active_batch and isinstance(active_batch.get("review_axes"), list):
        required.update(
            axis
            for axis in active_batch["review_axes"]
            if axis in REVIEW_AXIS_IDS
        )
    if "pptx" in set(profile.get("formats", [])):
        required.add("images")
    return required


def validate_review_scope(
    lifecycle: dict[str, Any],
    batches: dict[str, dict[str, Any]],
    profile: dict[str, Any],
    source_result: dict[str, Any] | None,
    matrix_result: dict[str, Any],
    review_result: dict[str, Any],
    report: Report,
) -> None:
    active_batch = batches.get(lifecycle.get("active_batch"))
    mandatory_axes = required_review_axes(profile, source_result, active_batch)
    omitted_mandatory = sorted(
        mandatory_axes - matrix_result["applicable_axes"]
    )
    if omitted_mandatory:
        report.error(
            "REVIEW_APPLICABILITY",
            f"Project review marked mandatory axes inapplicable: {omitted_mandatory}",
        )
    missing_domain_evidence = sorted(
        matrix_result["applicable_axes"] - review_result["manuscript_axes"]
    )
    if missing_domain_evidence:
        report.error(
            "REVIEW_EVIDENCE",
            f"project-review result omits manuscript evidence for: {missing_domain_evidence}",
        )
    if lifecycle.get("phase") != "candidate":
        return
    if matrix_result["milestone"] != "candidate":
        report.error(
            "STATE_REVIEW_BINDING",
            "candidate phase requires a candidate milestone review",
        )
    if not active_batch:
        return
    for normalized_output, output_hash in active_batch.get(
        "_validated_outputs",
        {},
    ).items():
        if (
            output_hash is None
            or review_result["snapshot"].get(normalized_output) != output_hash
        ):
            report.error(
                "STATE_REVIEW_BINDING",
                f"candidate review snapshot does not hash-bind batch output {normalized_output}",
            )


def render_text(result: dict[str, Any]) -> str:
    lines = [f"status: {result['status']}", f"root: {result['root']}"]
    for label in ("errors", "warnings", "checks"):
        lines.append(f"{label}:")
        for item in result[label]:
            lines.append(f"  - {item['code']}: {item['message']}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    report = Report(root)
    if not root.is_dir():
        report.error("ROOT_MISSING", f"project root does not exist: {root}")
        result = report.as_dict()
        print(render_text(result) if args.format == "text" else dump_json(result))
        return report.exit_code

    state_dir = root / ".manuscript-ops"
    if not state_dir.is_dir():
        report.error("STATE_DIR_MISSING", "missing .manuscript-ops directory")
        result = report.as_dict()
        print(render_text(result) if args.format == "text" else dump_json(result))
        return report.exit_code

    profile_raw = read_required(state_dir / "project-profile.json", report)
    snapshot = read_required(state_dir / "routing-snapshot.json", report)
    batches = read_required(state_dir / "batch-manifest.json", report)
    registry = read_required(state_dir / "format-registry.json", report)
    state = read_required(state_dir / "state.json", report)

    try:
        now = parse_timestamp(args.now) if args.now else datetime.now(timezone.utc)
    except (ContractError, ValueError) as exc:
        report.error("NOW_INVALID", str(exc))
        now = datetime.now(timezone.utc)

    profile = validate_profile(profile_raw, report) if profile_raw else {}
    if snapshot and profile:
        validate_routing(snapshot, profile, report, now)
    batch_index = validate_batches(batches, profile, report) if batches and profile else {}
    adapters = validate_format_registry(registry, profile, report) if registry else {}
    brief_result = (
        validate_brief(profile, adapters, report)
        if profile and adapters
        else None
    )
    lifecycle = (
        validate_lifecycle_state(state, batch_index, profile, report)
        if state and profile
        else {"required_gates": set()}
    )

    source_result: dict[str, Any] | None = None
    if lifecycle.get("source_register") and registry:
        source_result = validate_source_register(
            lifecycle["source_register"],
            registry,
            report,
        )
    validate_brief_source_expectations(brief_result, source_result, report)
    validate_batch_source_dependencies(batch_index, source_result, report)
    matrix_result: dict[str, Any] | None = None
    if lifecycle.get("review_matrix"):
        matrix_result = validate_review_matrix(lifecycle["review_matrix"], report)
    review_result: dict[str, Any] | None = None
    if lifecycle.get("latest_review_report"):
        review_result = validate_project_review_report(
            lifecycle["latest_review_report"],
            report,
        )
    if matrix_result and review_result:
        if matrix_result["milestone"] != review_result["milestone"]:
            report.error(
                "REVIEW_BINDING",
                "ReviewMatrix and ReviewReport milestones differ",
            )
        if matrix_result["snapshot"] != review_result["snapshot"]:
            report.error(
                "REVIEW_BINDING",
                "ReviewMatrix and ReviewReport frozen snapshots differ",
            )
        if (
            matrix_result.get("snapshot_captured_at")
            != review_result.get("snapshot_captured_at")
        ):
            report.error(
                "REVIEW_BINDING",
                "ReviewMatrix and ReviewReport snapshot capture times differ",
            )
        if matrix_result["applicable_axes"] != review_result["manuscript_axes"]:
            report.error(
                "REVIEW_BINDING",
                "project-review manuscript evidence does not exactly cover the profile axes",
            )
        validate_review_scope(
            lifecycle,
            batch_index,
            profile,
            source_result,
            matrix_result,
            review_result,
            report,
        )

    capability_result: dict[str, Any] | None = None
    if lifecycle.get("capability_snapshot"):
        capability_result = validate_capability_snapshot(
            lifecycle["capability_snapshot"],
            profile,
            adapters,
            report,
            now,
        )
        profile_capability = profile.get("capabilities_snapshot")
        if isinstance(profile_capability, str) and (
            not capability_result or profile_capability != capability_result["path"]
        ):
            report.error(
                "PROFILE_CAPABILITIES",
                "ProjectProfile and LifecycleState capability snapshots differ",
            )
    lifecycle_qa: dict[str, dict[str, Any]] = {}
    for item in lifecycle.get("format_qa_records", []):
        normalized_qa = validate_format_qa_entry(
            item,
            adapters,
            report,
            brief_result,
        )
        if normalized_qa:
            artifact_id = normalized_qa.get("artifact_path")
            if not artifact_id:
                report.error(
                    "STATE_FORMAT_QA",
                    "format QA record has no validated deliverable artifact",
                )
            elif artifact_id in lifecycle_qa:
                report.error(
                    "STATE_FORMAT_QA",
                    f"duplicate QA record for deliverable {artifact_id}",
                )
            else:
                lifecycle_qa[artifact_id] = normalized_qa
    if lifecycle.get("phase") in FINAL_PHASES:
        selected_formats = set(profile.get("formats", []))
        if not isinstance(profile.get("capabilities_snapshot"), str):
            report.error(
                "PROFILE_CAPABILITIES",
                "final ProjectProfile must bind the capability snapshot path",
            )
        validate_ready_deliverable_qa(
            brief_result,
            lifecycle_qa,
            "STATE_FORMAT_QA",
            "final lifecycle",
            report,
        )
        if capability_result:
            not_ready = sorted(
                adapter_id
                for adapter_id in selected_formats
                if capability_result["statuses"].get(adapter_id) != "READY"
            )
            if not_ready:
                report.error(
                    "STATE_CAPABILITIES",
                    f"selected final formats are not capability READY: {not_ready}",
                )

    receipts = validate_receipts(
        state_dir,
        lifecycle,
        profile,
        adapters,
        review_result,
        lifecycle_qa,
        capability_result,
        brief_result,
        source_result,
        report,
    )
    if args.check_jj and profile:
        validate_jj(profile, receipts, report)

    result = report.as_dict()
    print(render_text(result) if args.format == "text" else dump_json(result))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
