#!/usr/bin/env python3
"""Idempotently write the repository contract consumed by Light Project Skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Optional

PROJECT_PATH = Path("docs/agents/light-project.md")
TRACKER_PATH = Path("docs/agents/issue-tracker.md")
START = "<!-- light-project:managed:start -->"
END = "<!-- light-project:managed:end -->"
POINTER_START = "<!-- light-project:pointer:start -->"
POINTER_END = "<!-- light-project:pointer:end -->"

REQUIRED = (
    "projectType", "goal", "outputs", "preset", "relevantSkills",
    "issueTracker", "domainContext", "reviewProfile", "workingArea",
    "instructionFile",
)
PRESETS = {
    "generic", "software", "manuscript", "skill-development", "research",
    "knowledge-base", "data-analysis", "research-fallback",
}
MARKER_TOKENS = (START, END, POINTER_START, POINTER_END)


def validate_render_text(label: str, value: Any) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if "\n" in value or "\r" in value or any(marker in value for marker in MARKER_TOKENS):
        raise ValueError(f"{label} contains a newline or managed marker")


def validate_config(config: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in config or config[key] in (None, "")]
    if missing:
        raise ValueError(f"missing bootstrap fields: {', '.join(missing)}")
    if not isinstance(config["issueTracker"], dict) or not config["issueTracker"].get("kind") or not config["issueTracker"].get("path"):
        raise ValueError("issueTracker requires kind and path")
    if config["issueTracker"]["kind"] != "local-markdown":
        raise ValueError("unsupported issueTracker kind; current Light Project Skills require local-markdown")
    if config["workingArea"] != ".scratch":
        raise ValueError("unsupported workingArea; current Light Project Skills require .scratch")
    if str(config["instructionFile"]).lower() not in {"agents.md", "claude.md"}:
        raise ValueError("instructionFile must be AGENTS.md or CLAUDE.md based on inspected host evidence")
    if config["preset"] not in PRESETS:
        raise ValueError(f"unsupported preset: {config['preset']}")
    if config["preset"] == "research-fallback":
        fallback_missing = [
            key for key in ("sources", "confirmation", "validation")
            if key not in config or config[key] in (None, "", [])
        ]
        if fallback_missing:
            raise ValueError(f"research-fallback requires: {', '.join(fallback_missing)}")
        if not isinstance(config["sources"], list):
            raise ValueError("research-fallback sources must be a list")
    tracker_path = Path(str(config["issueTracker"]["path"]))
    if tracker_path.is_absolute() or ".." in tracker_path.parts or not tracker_path.parts or tracker_path.parts[0] != config["workingArea"]:
        raise ValueError("issueTracker path must stay under the configured .scratch working area")
    if tracker_path.as_posix() != ".scratch/<effort>/issues":
        raise ValueError("issueTracker path must use the supported .scratch/<effort>/issues contract")
    for key in ("outputs", "relevantSkills", "domainContext"):
        if not isinstance(config[key], list):
            raise ValueError(f"{key} must be a list")
    if not config["outputs"] or not config["relevantSkills"]:
        raise ValueError("outputs and relevantSkills must not be empty")
    scalar_keys = ("projectType", "goal", "preset", "reviewProfile", "workingArea", "instructionFile")
    optional_scalars = ("acceptanceStrategy", "collaboration", "confirmation", "validation")
    for key in scalar_keys:
        validate_render_text(key, config[key])
    for key in optional_scalars:
        if key in config:
            validate_render_text(key, config[key])
    for key in ("kind", "path"):
        validate_render_text(f"issueTracker.{key}", config["issueTracker"][key])
    for key in ("outputs", "relevantSkills", "domainContext", "constraints", "sources"):
        if key in config:
            if not isinstance(config[key], list):
                raise ValueError(f"{key} must be a list")
            for index, value in enumerate(config[key]):
                validate_render_text(f"{key}[{index}]", value)


def inspect_capabilities(
    relevant_skills: list[str],
    roots: Optional[list[Path]] = None,
    unavailable: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Classify declared relevant Light capabilities without over-claiming.

    Statuses are available, unavailable, or unknown. A missing root means
    unknown, never a silent promotion to available.
    """
    unavailable = unavailable or []
    results: list[dict[str, Any]] = []
    for name in relevant_skills:
        status = "unknown"
        reason = "no capability root supplied; availability not verified"
        if roots:
            matches = [root / name / "SKILL.md" for root in roots if (root / name / "SKILL.md").is_file()]
            if name in unavailable:
                status, reason = "unavailable", "declared unavailable by the active host"
            elif matches:
                status, reason = "available", "readable SKILL.md found in supplied capability root"
            else:
                status, reason = "unavailable", "no readable SKILL.md found in supplied capability root"
        results.append({"skill": name, "status": status, "reason": reason})
    return results


def csv(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values)


def existing_managed_value(existing: str, label: str) -> Optional[str]:
    """Read one generated field without interpreting its rendered value."""
    block_pattern = re.compile(re.escape(START) + r"(.*?)" + re.escape(END), re.S)
    block = block_pattern.search(existing)
    if block is None:
        return None
    matches = re.findall(rf"^- {re.escape(label)}: (.*)$", block.group(1), re.M)
    if len(matches) > 1:
        raise ValueError(f"multiple {label} fields in the Light managed block require manual reconciliation")
    return matches[0] if matches and matches[0] else None


def render_project(config: dict[str, Any], existing: str = "") -> str:
    if "constraints" in config:
        constraints = csv(config["constraints"]) if config["constraints"] else "none recorded"
    else:
        constraints = existing_managed_value(existing, "Constraints") or "none recorded"
    collaboration = config.get("collaboration") or existing_managed_value(existing, "Collaboration") or "default"
    acceptance = (
        config.get("acceptanceStrategy")
        or existing_managed_value(existing, "Acceptance strategy")
        or f"{config['reviewProfile']} profile via project-review"
    )
    lines = [
        START,
        "# Light Project Configuration",
        "",
        f"- Project type: {config['projectType']}",
        f"- Goal: {config['goal']}",
        f"- Outputs: {csv(config['outputs'])}",
        f"- Preset: {config['preset']}",
        f"- Relevant Skills: {csv(config['relevantSkills'])}",
        f"- Issue tracker: {config['issueTracker']['kind']} at {config['issueTracker']['path']}",
        f"- Domain context: {csv(config['domainContext']) if config['domainContext'] else 'none recorded'}",
        f"- Review profile: {config['reviewProfile']}",
        f"- Acceptance strategy: {acceptance}",
        f"- Working area: {config['workingArea']}",
        f"- Collaboration: {collaboration}",
        f"- Constraints: {constraints}",
    ]
    if config["preset"] == "research-fallback":
        lines.extend((
            f"- Sources: {csv(config['sources'])}",
            f"- Confirmation: {config['confirmation']}",
            f"- Validation: {config['validation']}",
        ))
    lines.append(END)
    return "\n".join(lines) + "\n"


def render_tracker(config: dict[str, Any]) -> str:
    tracker = config["issueTracker"]
    return "\n".join((
        START,
        "# Issue Tracker Contract",
        "",
        f"- Kind: {tracker['kind']}",
        f"- Work item location: {tracker['path']}",
        "- SPEC location: <working-area>/<effort>/spec.md",
        "- Ticket location: <working-area>/<effort>/issues/NN-<slug>.md",
        "- Edge field: Blocked by: NN, NN",
        "- Statuses: open | ready-for-agent | claimed | resolved",
        "- Frontier: unblocked open/ready-for-agent items, first by number",
        END,
    )) + "\n"


def merge_managed(existing: str, rendered: str) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
    starts, ends = existing.count(START), existing.count(END)
    if starts != ends:
        raise ValueError("unbalanced Light managed block markers require manual reconciliation")
    if starts > 1 or len(pattern.findall(existing)) > 1:
        raise ValueError("multiple Light managed blocks require manual reconciliation")
    match = pattern.search(existing)
    if starts == 1 and match is None:
        raise ValueError("misordered Light managed block markers require manual reconciliation")
    if match:
        return pattern.sub(lambda _match: rendered, existing, count=1)
    if not existing.strip():
        return rendered
    return existing.rstrip() + "\n\n" + rendered


def mask_markdown_fences(text: str) -> str:
    """Mask fenced code while preserving byte offsets and line endings."""
    masked: list[str] = []
    fence_character = ""
    fence_length = 0
    for line in text.splitlines(keepends=True):
        candidate = line.lstrip(" ")
        indent = len(line) - len(candidate)
        marker = re.match(r"(`{3,}|~{3,})", candidate) if indent <= 3 else None
        if not fence_character and marker:
            token = marker.group(1)
            fence_character, fence_length = token[0], len(token)
            masked.append("".join(character if character in "\r\n" else " " for character in line))
            continue
        if fence_character:
            closing = re.match(rf"{re.escape(fence_character)}{{{fence_length},}}[ \t]*(?:\r?\n)?$", candidate) if indent <= 3 else None
            masked.append("".join(character if character in "\r\n" else " " for character in line))
            if closing:
                fence_character, fence_length = "", 0
            continue
        masked.append(line)
    return "".join(masked)


def merge_instruction(existing: str) -> str:
    pointer = "\n".join((
        POINTER_START,
        "Read `docs/agents/light-project.md` before Light Project workflows. Its managed block is the stable project contract; preserve manual notes outside it.",
        POINTER_END,
    ))
    visible = mask_markdown_fences(existing)
    pointer_pattern = re.compile(re.escape(POINTER_START) + r".*?" + re.escape(POINTER_END), re.S)
    section_pattern = re.compile(r"(?ms)^## Project Initialization\s*$.*?(?=^## (?!#)|\Z)")
    sections = list(section_pattern.finditer(visible))
    if len(sections) > 1:
        raise ValueError("multiple Project Initialization sections require manual reconciliation")
    pointer_starts, pointer_ends = visible.count(POINTER_START), visible.count(POINTER_END)
    if pointer_starts != pointer_ends:
        raise ValueError("unbalanced Light project pointer markers require manual reconciliation")
    if pointer_starts > 1 or len(pointer_pattern.findall(existing)) > 1:
        raise ValueError("multiple Light project pointers require manual reconciliation")
    pointer_match = pointer_pattern.search(visible)
    if pointer_starts == 1 and pointer_match is None:
        raise ValueError("misordered Light project pointer markers require manual reconciliation")
    if pointer_match:
        if not sections or not (sections[0].start() <= pointer_match.start() and pointer_match.end() <= sections[0].end()):
            raise ValueError("Light project pointer must be inside one Project Initialization section")
        return existing[:pointer_match.start()] + pointer + existing[pointer_match.end():]
    if sections:
        section_match = sections[0]
        section = existing[section_match.start():section_match.end()].rstrip()
        updated = section + "\n\n" + pointer + "\n"
        return existing[:section_match.start()] + updated + existing[section_match.end():]
    block = "## Project Initialization\n\n" + pointer + "\n"
    if not existing.strip():
        return block
    return existing.rstrip() + "\n\n" + block


def named_file(root: Path, name: str) -> Optional[Path]:
    matches = sorted(
        (path for path in root.iterdir() if path.is_file() and path.name.lower() == name.lower()),
        key=lambda path: path.name,
    )
    if len(matches) > 1:
        raise ValueError(f"multiple case variants of {name} require manual reconciliation")
    return matches[0] if matches else None


def instruction_target(root: Path, preferred_name: str) -> tuple[Path, bool]:
    agents = named_file(root, "AGENTS.md")
    claude = named_file(root, "CLAUDE.md")
    preferred = agents if preferred_name.lower() == "agents.md" else claude
    other = claude if preferred_name.lower() == "agents.md" else agents
    return (preferred or root / preferred_name), bool(other)


def safe_target(root: Path, relative: Path, *, reject_symlink: bool = False) -> Path:
    unresolved = root / relative
    if reject_symlink and unresolved.is_symlink():
        raise ValueError(f"managed bootstrap target must not be a symlink: {relative}")
    target = unresolved.resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"bootstrap target escapes project root: {relative}") from exc
    return target


def preflight_file_target(path: Path) -> None:
    if path.exists() and not path.is_file():
        raise ValueError(f"bootstrap target exists but is not a regular file: {path}")
    if path.is_file() and not (path.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)):
        raise ValueError(f"bootstrap target is not writable: {path}")


def prepare_merged(path: Path, rendered: str, *, instruction: bool = False) -> tuple[str, str]:
    existed = path.is_file()
    existing = path.read_text(encoding="utf-8") if existed else ""
    updated = merge_instruction(existing) if instruction else merge_managed(existing, rendered)
    if updated == existing:
        return updated, "preserved"
    return updated, "updated" if existed else "created"


def commit_prepared(root: Path, prepared: dict[Path, tuple[str, str]]) -> None:
    """Stage every changed file, then replace targets with rollback on failure."""
    changed = {path: content for path, (content, status) in prepared.items() if status != "preserved"}
    staged: dict[Path, Path] = {}
    records: list[dict[str, Any]] = []
    created_dirs: list[Path] = []
    try:
        for path, content in changed.items():
            missing: list[Path] = []
            parent = path.parent
            while not parent.exists() and parent != root:
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                created_dirs.append(directory)
            descriptor, staged_name = tempfile.mkstemp(prefix=f".{path.name}.light-stage-", dir=path.parent)
            staged_path = Path(staged_name)
            staged[path] = staged_path
            try:
                handle = os.fdopen(descriptor, "w", encoding="utf-8")
                descriptor = -1
                with handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
            except Exception:
                if descriptor >= 0:
                    os.close(descriptor)
                raise
            if path.exists():
                os.chmod(staged_path, stat.S_IMODE(path.stat().st_mode))
        for path, staged_path in staged.items():
            record: dict[str, Any] = {"target": path, "backup": None, "installed": False}
            records.append(record)
            if path.exists():
                descriptor, backup_name = tempfile.mkstemp(prefix=f".{path.name}.light-backup-", dir=path.parent)
                os.close(descriptor)
                os.remove(backup_name)
                backup = Path(backup_name)
                os.replace(path, backup)
                record["backup"] = backup
            os.replace(staged_path, path)
            record["installed"] = True

        for record in records:
            backup = record["backup"]
            if backup is not None and backup.exists():
                try:
                    os.remove(backup)
                except OSError:
                    pass
    except Exception:
        for record in reversed(records):
            target, backup = record["target"], record["backup"]
            if record["installed"] and target.exists():
                os.remove(target)
            if backup is not None and backup.exists():
                os.replace(backup, target)
        for staged_path in staged.values():
            if staged_path.exists():
                os.remove(staged_path)
        for directory in reversed(created_dirs):
            try:
                os.rmdir(directory)
            except OSError:
                pass
        raise


def bootstrap(
    root: Path,
    config: dict[str, Any],
    capability_roots: Optional[list[Path]] = None,
    unavailable_capabilities: Optional[list[str]] = None,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    validate_config(config)
    capabilities = inspect_capabilities(config["relevantSkills"], capability_roots, unavailable_capabilities)
    project = safe_target(root, PROJECT_PATH, reject_symlink=True)
    tracker = safe_target(root, TRACKER_PATH, reject_symlink=True)
    instruction, instruction_conflict = instruction_target(root, config["instructionFile"])
    instruction = instruction.resolve()
    instruction.relative_to(root)
    if len({project, tracker, instruction}) != 3:
        raise ValueError("bootstrap targets resolve to the same file; reconcile instruction symlinks before retrying")
    for path in (project, tracker, instruction):
        preflight_file_target(path)
    existing_project = project.read_text(encoding="utf-8") if project.is_file() else ""
    prepared = {
        project: prepare_merged(project, render_project(config, existing_project)),
        tracker: prepare_merged(tracker, render_tracker(config)),
        instruction: prepare_merged(instruction, "", instruction=True),
    }
    commit_prepared(root, prepared)
    statuses = {
        str(path.relative_to(root)): status
        for path, (_, status) in prepared.items()
    }
    conflicts = [f"Both instruction styles exist; only inspected host target {config['instructionFile']} was updated"] if instruction_conflict else []
    return {
        "projectRoot": str(root),
        "instructionTarget": str(instruction),
        "paths": statuses,
        "conflicts": conflicts,
        "capabilities": capabilities,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--config-json", required=True)
    parser.add_argument("--capability-roots-json", default="[]")
    parser.add_argument("--unavailable-capabilities-json", default="[]")
    args = parser.parse_args()
    roots = [Path(value) for value in json.loads(args.capability_roots_json)]
    unavailable = json.loads(args.unavailable_capabilities_json)
    print(json.dumps(bootstrap(args.project_root, json.loads(args.config_json), roots, unavailable), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
