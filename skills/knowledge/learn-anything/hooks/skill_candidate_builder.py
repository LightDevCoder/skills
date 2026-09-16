#!/usr/bin/env python3
"""Assess source sufficiency and emit an internal learn-anything Method Contract.

This hook deliberately stops before package generation.  A source can yield a
reusable-method contract, a not-promoted learning summary, or a blocked result
that names the missing evidence.  It never fills missing method fields with
generic workflow text and never writes a production-ready ``SKILL.md``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_METHOD_FIELDS = (
    "purpose",
    "triggers",
    "invocation_type",
    "inputs",
    "ordered_method",
    "decisions",
    "constraints",
    "failure_modes",
    "outputs",
    "verification",
)

INLINE_DRAFT_TOKEN_FIELDS = frozenset(
    {
        "purpose",
        "triggers",
        "inputs",
        "ordered_method",
        "decisions",
        "outputs",
        "verification",
    }
)

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "purpose": ("Purpose",),
    "triggers": ("Triggers", "Trigger", "Use When", "When To Use"),
    "invocation_type": ("Invocation Type", "Invocation"),
    "inputs": ("Inputs",),
    "ordered_method": ("Ordered Method", "Workflow", "Steps", "Process"),
    "decisions": ("Decisions", "Decision Rules"),
    "constraints": ("Constraints", "Rules"),
    "failure_modes": ("Failure Modes", "Failure Mode", "Known Failures"),
    "outputs": ("Outputs", "Output Format", "Output", "Deliverable"),
    "resources": ("Resources", "Scripts", "References"),
    "verification": ("Verification", "Quality Checks", "Tests"),
    "corrections": ("Corrections", "Correction"),
    "scope": ("Scope", "Context"),
}

SOURCE_GAP_GUIDANCE = {
    "purpose": "State the durable outcome this method enables.",
    "triggers": "State the repeatable situations in which the method should be used.",
    "invocation_type": "State whether the resulting capability is user-invoked or model-invoked.",
    "inputs": "List the source artifacts, access, paths, or context required before work starts.",
    "ordered_method": "Provide at least two ordered steps that a future agent can repeat.",
    "decisions": "Record the decision rules or trade-offs that change the method's behavior.",
    "constraints": "Record scope boundaries, corrections, or rules that constrain the method.",
    "failure_modes": "Record known failure states, blockers, or recovery boundaries.",
    "outputs": "State the concrete result produced by the method.",
    "resources": "State the required resource or explicitly record that no resource is needed.",
    "verification": "State how a future agent verifies that the result is acceptable.",
}

INVOCATION_CONFLICT_GUIDANCE = (
    "Resolve conflicting invocation evidence: choose exactly one of user-invoked or model-invoked."
)

ONE_OFF_PATTERNS = (
    r"\bone[- ]off\b",
    r"\bsingle incident\b",
    r"\bunique to\b",
    r"\bonce[- ]only\b",
    r"\bthis incident was unique\b",
    r"\bjust this release\b",
)

NEGATED_ONE_OFF_PATTERNS = (
    r"\b(?:not|never|is not|isn't|isnt|no longer)\s+(?:(?:merely|just|only)\s+)?(?:a\s+)?one[- ]off\b",
    r"\bnot\s+unique to\b",
)

PASSIVE_SUMMARY_PATTERNS = (
    r"\bpassive summary\b",
    r"\bweekly .*summary\b",
    r"\bno procedure\b",
    r"\bno .*future task\b",
    r"\bno .*agreed\b",
    r"\bteam read\b",
)

NEGATED_PASSIVE_SUMMARY_PATTERNS = (
    r"\b(?:not|never|is not|isn't|isnt|no longer)\s+(?:(?:merely|just|only)\s+)?(?:a\s+)?passive summary\b",
)

EMBEDDED_PLACEHOLDER_MARKERS = (
    "tbd",
    "todo",
    "n/a",
    "na",
    "unknown",
    "placeholder",
    "to be determined",
    "to be completed",
    "not available",
    "not applicable",
    "coming soon",
)

EXPLICIT_NO_RESOURCE_MARKERS = frozenset(
    {
        "none",
        "no resource",
        "no resources",
        "no resource needed",
        "no resources needed",
        "no resource required",
        "no resources required",
    }
)

PLACEHOLDER_MARKERS = frozenset(
    {
        "",
        "-",
        "...",
        "…",
        "[]",
        "[ ]",
        "<placeholder>",
        "[placeholder]",
        "placeholder",
        "tbd",
        "todo",
        "n/a",
        "na",
        "unknown",
        "none",
        "not applicable",
        "not available",
        "to be determined",
        "to be completed",
        "coming soon",
    }
)

GENERIC_BOILERPLATE_PATTERNS = (
    r"^(?:add|describe|document|insert|provide)\s+(?:the\s+)?(?:purpose|triggers?|inputs?|ordered method|workflow|steps?|decisions?|decision rules|constraints?|failure modes?|outputs?|verification|details)(?:\s+here)?$",
    r"^(?:standard|generic)\s+(?:constraints?|workflow|quality checks?|verification)(?:\s+apply)?$",
    r"^use when an ai agent needs to repeat the .+ method from source notes, transcripts, project files, or user corrections$",
    r"^use this skill to apply a repeatable operating method extracted from source material$",
    r"^return the generated or updated skill files plus a concise verification summary$",
)

GENERIC_BOILERPLATE_VALUES = frozenset(
    {
        "identify the source artifacts and the user's requested reusable outcome",
        "extract repeatable decisions, commands, constraints, and verification gates",
        "separate durable operating method from one-off project narration",
        "draft a compact skill creator compatible skill.md with concrete trigger metadata",
        "validate the draft against frontmatter, trigger, workflow, constraints, output format, and quality checks",
        "extract repeatable operating methods, not passive summaries",
        "preserve exact commands, paths, apis, filenames, and error strings when they change future behavior",
        "do not invent missing workflow details from sparse source material",
        "keep generated skill names kebab-case and under 64 characters",
        "frontmatter contains only name and description",
        "description states both what the skill does and when to use it",
        "workflow steps are imperative and repeatable",
        "constraints include relevant corrections or failure modes from the source",
        "no unresolved draft markers remain",
    }
)

COMMAND_PATTERN = re.compile(
    r"(?:^|\s)(?:python(?:3)?|pytest|npm|pnpm|corepack|git|gh|cargo|node)\b",
    flags=re.IGNORECASE,
)
FENCED_CODE_BLOCK_PATTERN = re.compile(r"```[^\r\n]*\r?\n(.*?)```", flags=re.DOTALL)
INLINE_PLACEHOLDER_MARKUP_PATTERN = re.compile(
    r"(?:<\s*(?:placeholder|tbd|todo|unknown|to be determined|to be completed)\s*>|"
    r"\[\s*(?:placeholder|tbd|todo|unknown|to be determined|to be completed)\s*\])",
    flags=re.IGNORECASE,
)
INLINE_DRAFT_TOKEN_PATTERN = re.compile(r"\b(?:tbd|todo)\b", flags=re.IGNORECASE)
WINDOWS_PATH_PATTERN = re.compile(r"[A-Za-z]:\\[^\s`\"'()\[\],;]+")
POSIX_PATH_PATTERN = re.compile(r"(?<!\w)/(?:[\w.-]+/)+[\w.-]+")
CORRECTION_PATTERN = re.compile(
    r"\b(?:do not|don't|instead|must|never|avoid|blocked|failed because)\b|不要|必须|而是|失败|错误",
    flags=re.IGNORECASE,
)


def _read_input(argv_text: list[str], source_file: str | None) -> dict[str, Any]:
    if source_file:
        return {"source": Path(source_file).read_text(encoding="utf-8")}

    text = " ".join(argv_text) if argv_text else sys.stdin.read()
    text = text.strip()
    if not text:
        return {"source": ""}

    # Treat only short, single-line inputs as candidate paths.  A Markdown
    # source supplied through stdin can be long and is not a filesystem path.
    if "\n" not in text and len(text) < 240:
        try:
            candidate = Path(text)
            if candidate.is_file():
                text = candidate.read_text(encoding="utf-8")
        except OSError:
            pass

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"source": text}

    return data if isinstance(data, dict) else {"source": str(data)}


def _combined_source(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("source", "transcript", "notes", "request", "context"):
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif value is not None:
            parts.append(json.dumps(value, ensure_ascii=False))
    return "\n".join(parts).strip()


def _match_section_heading(line: str) -> tuple[str, str] | None:
    normalized = re.sub(r"^\s*#{1,6}\s*", "", line).strip()
    for field, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            match = re.match(
                rf"^{re.escape(alias)}\s*(?::\s*(.*)|$)",
                normalized,
                flags=re.IGNORECASE,
            )
            if match:
                return field, (match.group(1) or "").strip()
    return None


def _parse_sections(source: str) -> dict[str, list[str]]:
    lines = source.splitlines()
    starts: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        heading = _match_section_heading(line)
        if heading:
            starts.append((index, heading[0], heading[1]))

    sections = {field: [] for field in SECTION_ALIASES}
    for position, (start, field, inline_value) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        block: list[str] = []
        if inline_value:
            block.append(inline_value)
        block.extend(lines[start + 1 : end])
        sections[field].extend(block)
    return sections


def _values(lines: list[str]) -> list[str]:
    values: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            values.append(" ".join(paragraph))
            paragraph.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        item = re.match(r"^(?:[-*]|\d+[.)])\s+(.+)$", stripped)
        if item:
            flush_paragraph()
            values.append(item.group(1).strip())
        else:
            paragraph.append(stripped)
    flush_paragraph()
    return _unique(values)


def _ordered_values(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        match = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if match:
            values.append(match.group(1).strip())
    return _unique(values)


def _invocation_types(values: list[str]) -> list[str]:
    raw = " ".join(values).lower()
    invocation_types: list[str] = []
    if re.search(r"\buser[ -]?invoked\b", raw):
        invocation_types.append("user-invoked")
    if re.search(r"\bmodel[ -]?invoked\b", raw):
        invocation_types.append("model-invoked")
    return invocation_types


def _normalize_invocation(values: list[str]) -> str | None:
    invocation_types = _invocation_types(values)
    return invocation_types[0] if len(invocation_types) == 1 else None


def _invocation_conflict(values: list[str]) -> list[str]:
    invocation_types = _invocation_types(values)
    return invocation_types if len(invocation_types) > 1 else []


def _source_title(source: str) -> str:
    for line in source.splitlines():
        match = re.match(r"^\s*#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return "Untitled method source"


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _placeholder_normalized(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip().strip("` ").rstrip(".!?").strip()
    return normalized.lower()


def _is_placeholder(value: str) -> bool:
    normalized = _placeholder_normalized(value)
    if normalized in PLACEHOLDER_MARKERS:
        return True
    bracketless_marker = normalized.strip("[]<>{}() ")
    if bracketless_marker in PLACEHOLDER_MARKERS:
        return True
    if INLINE_PLACEHOLDER_MARKUP_PATTERN.search(normalized):
        return True
    if normalized in GENERIC_BOILERPLATE_VALUES:
        return True
    for marker in EMBEDDED_PLACEHOLDER_MARKERS:
        escaped_marker = re.escape(marker)
        embedded_pattern = rf"(?:^{escaped_marker}(?=$|[^a-z0-9])|(?:^|[^a-z0-9]){escaped_marker}$)"
        if re.search(embedded_pattern, normalized, flags=re.IGNORECASE):
            return True
    return any(re.fullmatch(pattern, normalized, flags=re.IGNORECASE) for pattern in GENERIC_BOILERPLATE_PATTERNS)


def _placeholder_values(values: Any) -> list[str]:
    if isinstance(values, str):
        candidates = [values]
    elif isinstance(values, list):
        candidates = [value for value in values if isinstance(value, str)]
    else:
        candidates = []
    return [value for value in candidates if _is_placeholder(value)]


def _inline_draft_token_values(field: str, values: Any) -> list[str]:
    if field not in INLINE_DRAFT_TOKEN_FIELDS:
        return []
    if isinstance(values, str):
        candidates = [values]
    elif isinstance(values, list):
        candidates = [value for value in values if isinstance(value, str)]
    else:
        candidates = []
    return [value for value in candidates if INLINE_DRAFT_TOKEN_PATTERN.search(value)]


def _unresolved_field_values(field: str, values: Any) -> list[str]:
    return _unique(_placeholder_values(values) + _inline_draft_token_values(field, values))


def _unresolved_resource_placeholders(values: list[str]) -> list[str]:
    if values and all(_placeholder_normalized(value) in EXPLICIT_NO_RESOURCE_MARKERS for value in values):
        return []
    return _placeholder_values(values)


def _preserved_details(source: str, sections: dict[str, list[str]]) -> dict[str, list[str]]:
    code_spans = re.findall(r"`([^`\r\n]+)`", source)
    commands = [span for span in code_spans if COMMAND_PATTERN.search(span)]
    for fenced_block in FENCED_CODE_BLOCK_PATTERN.findall(source):
        for line in fenced_block.splitlines():
            command = re.sub(r"^\s*\$\s?", "", line).strip()
            if re.match(r"^(?:python(?:3)?|pytest|npm|pnpm|corepack|git|gh|cargo|node)\b", command, flags=re.IGNORECASE):
                commands.append(command)
    paths = [span for span in code_spans if WINDOWS_PATH_PATTERN.search(span) or POSIX_PATH_PATTERN.search(span)]
    paths.extend(WINDOWS_PATH_PATTERN.findall(source))
    paths.extend(POSIX_PATH_PATTERN.findall(source))

    corrections = _values(sections["corrections"])
    corrections.extend(
        line.strip()
        for line in source.splitlines()
        if CORRECTION_PATTERN.search(line) and line.strip()
    )

    return {
        "commands": _unique(commands),
        "paths": _unique(paths),
        "decisions": _values(sections["decisions"]),
        "corrections": _unique(corrections),
        "failure_modes": _values(sections["failure_modes"]),
    }


def _classification_context(source: str) -> str:
    """Return the title and leading narrative, excluding structured method fields."""

    context_lines: list[str] = []
    for line in source.splitlines():
        if _match_section_heading(line):
            break
        context_lines.append(line)
    return "\n".join(context_lines)


def _has_affirmative_context_signal(
    context: str,
    patterns: tuple[str, ...],
    negated_patterns: tuple[str, ...],
) -> bool:
    for line in context.splitlines():
        if not re.search("|".join(patterns), line, flags=re.IGNORECASE):
            continue
        if re.search("|".join(negated_patterns), line, flags=re.IGNORECASE):
            continue
        return True
    return False


def _source_kind(source: str, sections: dict[str, list[str]]) -> str:
    context = _classification_context(source)
    if _has_affirmative_context_signal(context, ONE_OFF_PATTERNS, NEGATED_ONE_OFF_PATTERNS):
        return "one_off_narration"
    structured_classification_context = "\n".join(
        sections["purpose"] + sections["triggers"] + sections["scope"]
    )
    if _has_affirmative_context_signal(
        structured_classification_context,
        ONE_OFF_PATTERNS,
        NEGATED_ONE_OFF_PATTERNS,
    ):
        return "one_off_narration"
    if _has_affirmative_context_signal(
        context,
        PASSIVE_SUMMARY_PATTERNS,
        NEGATED_PASSIVE_SUMMARY_PATTERNS,
    ):
        return "passive_summary"
    if _has_affirmative_context_signal(
        structured_classification_context,
        PASSIVE_SUMMARY_PATTERNS,
        NEGATED_PASSIVE_SUMMARY_PATTERNS,
    ):
        return "passive_summary"
    if not any(_values(lines) for lines in sections.values()):
        return "insufficient_source"
    return "method_candidate"


def _missing_information(fields: dict[str, Any], raw_values: dict[str, list[str]] | None = None) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_METHOD_FIELDS:
        value = fields[field]
        source_values = raw_values[field] if raw_values is not None else value
        if _unresolved_field_values(field, source_values):
            present = False
        elif field == "ordered_method":
            present = isinstance(value, list) and len(value) >= 2
        else:
            present = bool(value)
        if not present:
            missing.append(field)
    return missing


def _confidence(missing_information: list[str], evidence: dict[str, list[str]]) -> float:
    completed = len(REQUIRED_METHOD_FIELDS) - len(missing_information)
    evidence_categories = sum(bool(values) for values in evidence.values())
    return round(min(0.95, 0.2 + completed * 0.07 + min(evidence_categories, 3) * 0.02), 2)


def _learning_summary(source: str, evidence: dict[str, list[str]]) -> dict[str, Any]:
    lines = [line.strip() for line in source.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    return {
        "summary": " ".join(lines)[:600],
        "preserved_details": evidence,
    }


def _not_promoted_result(
    *,
    source: str,
    source_kind: str,
    fields: dict[str, Any],
    evidence: dict[str, list[str]],
) -> dict[str, Any]:
    missing_information = _missing_information(fields)
    reason = (
        "Source is a one-off narration, not a reusable method; it is retained only as a learning summary."
        if source_kind == "one_off_narration"
        else "Source is a passive summary, not an operational method; it is retained only as a learning summary."
    )
    return {
        "outcome": "learning_summary",
        "promotion_status": "not_promoted",
        "source_kind": source_kind,
        "reason": reason,
        "missing_information": missing_information,
        "required_source_gaps": {field: SOURCE_GAP_GUIDANCE[field] for field in missing_information},
        "learning_summary": _learning_summary(source, evidence),
    }


def build_candidate(data: dict[str, Any]) -> dict[str, Any]:
    """Return the documented source-to-result assessment without package output.

    The function name is retained for the established hook interface.  The
    returned ``method_contract`` is internal data for learn-anything's later
    package-build layer, never a standalone installable Skill.
    """

    source = _combined_source(data)
    sections = _parse_sections(source)
    raw_values: dict[str, list[str]] = {
        "purpose": _values(sections["purpose"]),
        "triggers": _values(sections["triggers"]),
        "invocation_type": _values(sections["invocation_type"]),
        "inputs": _values(sections["inputs"]),
        "ordered_method": _ordered_values(sections["ordered_method"]),
        "decisions": _values(sections["decisions"]),
        "constraints": _values(sections["constraints"]),
        "failure_modes": _values(sections["failure_modes"]),
        "outputs": _values(sections["outputs"]),
        "resources": _values(sections["resources"]),
        "verification": _values(sections["verification"]),
    }
    invocation_conflict = _invocation_conflict(raw_values["invocation_type"])
    fields: dict[str, Any] = {
        "purpose": " ".join(raw_values["purpose"]),
        "triggers": raw_values["triggers"],
        "invocation_type": _normalize_invocation(raw_values["invocation_type"]),
        "inputs": raw_values["inputs"],
        "ordered_method": raw_values["ordered_method"],
        "decisions": raw_values["decisions"],
        "constraints": raw_values["constraints"],
        "failure_modes": raw_values["failure_modes"],
        "outputs": raw_values["outputs"],
        "resources": raw_values["resources"],
        "verification": raw_values["verification"],
    }
    evidence = _preserved_details(source, sections)
    source_kind = _source_kind(source, sections)

    if source_kind in {"one_off_narration", "passive_summary"}:
        return _not_promoted_result(
            source=source,
            source_kind=source_kind,
            fields=fields,
            evidence=evidence,
        )

    missing_information = _missing_information(fields, raw_values)
    unresolved_resource_placeholders = _unresolved_resource_placeholders(raw_values["resources"])
    if unresolved_resource_placeholders:
        missing_information.append("resources")
    if missing_information:
        placeholder_source_values = {
            field: (
                unresolved_resource_placeholders
                if field == "resources"
                else _unresolved_field_values(field, raw_values[field])
            )
            for field in missing_information
            if (
                unresolved_resource_placeholders
                if field == "resources"
                else _unresolved_field_values(field, raw_values[field])
            )
        }
        required_source_gaps = {field: SOURCE_GAP_GUIDANCE[field] for field in missing_information}
        if invocation_conflict:
            required_source_gaps["invocation_type"] = INVOCATION_CONFLICT_GUIDANCE
        result: dict[str, Any] = {
            "outcome": "blocked",
            "promotion_status": "not_promoted",
            "source_kind": source_kind,
            "reason": (
                "A reusable method cannot be learned while its invocation-type evidence conflicts."
                if invocation_conflict
                else "A reusable method cannot be learned without the named source evidence."
            ),
            "missing_information": missing_information,
            "required_source_gaps": required_source_gaps,
            "placeholder_source_values": placeholder_source_values,
            "learning_summary": _learning_summary(source, evidence),
        }
        if invocation_conflict:
            result["invocation_type_conflict"] = invocation_conflict
        return result

    return {
        "outcome": "method_contract",
        "promotion_status": "eligible_for_package_build",
        "contract_visibility": "internal",
        "source_kind": "reusable_method",
        "method_contract": {
            "title": _source_title(source),
            **fields,
            "unresolved_gaps": [],
            "confidence": _confidence(missing_information, evidence),
            "source_evidence": evidence,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="Raw source text, JSON, or a file path")
    parser.add_argument("--source-file", help="Path to source text")
    args = parser.parse_args()

    result = build_candidate(_read_input(args.text, args.source_file))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
