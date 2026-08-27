#!/usr/bin/env python3
"""Deterministic Light router: semantic map first, host availability second."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

MAP_PATH = Path(__file__).resolve().parents[1] / "references" / "light-skill-map.json"
LIGHT_CATEGORIES = {"first-party", "light-first-party"}
INVOCATION_CONTROLS = {"explicit-only", "model-callable", "either"}


def load_map(path: Path = MAP_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [item["name"] for item in data["skills"]]
    if len(names) != len(set(names)):
        raise ValueError("Light Skill Map contains duplicate names")
    duplicated_metadata = {"category", "role", "invocation"}
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
    return {"mode": mode, "status": status, "skill": "", "source": "", "reason": "", "invocation": "", "confidence": "low", "alternative": None, "gaps": gaps, "reads": {"metadata": 0, "bodies": 0, "references": 0}, "candidates": [], "execution": "recommendation only; nothing was invoked, installed, or orchestrated"}


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


def next_result(roots: list[dict[str, Any]], context: dict[str, Any], host: str, skill_map: dict[str, Any]) -> dict[str, Any]:
    if not context.get("goal") and not context.get("taskKind"):
        return base_result("next", "NEED-INPUT", ["Provide goal or taskKind before routing."])
    control = str(context.get("invocationControl", ""))
    if control not in INVOCATION_CONTROLS:
        return base_result("next", "NEED-INPUT", ["invocationControl must be explicit-only, model-callable, or either."])
    ranking = logical_ranking(skill_map, context)
    if not ranking or ranking[0]["logicalScore"] <= 0:
        return base_result("next", "NEED-INPUT", ["No reliable Light route matches the supplied intent."])
    tied = [item["name"] for item in ranking if item["logicalScore"] == ranking[0]["logicalScore"]]
    if len(tied) > 1:
        return base_result("next", "NEED-INPUT", [f"Material Light route tie: {', '.join(tied)}. Provide the intended outcome or project stage."])
    policy = availability_policy(context, host)
    candidates, gaps, metadata_reads = discover(roots, skill_map, policy)
    logical = ranking[0]
    installed = sorted([item for item in candidates if item["name"] == logical["name"] and item["availabilityStatus"] == "available"], key=lambda item: item["packagePath"])
    if not installed:
        result = base_result("next", "BLOCKED", gaps + [f"{logical['name']}: known Light Skill is not available on this host."])
        result.update({"skill": logical["name"], "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0}, "candidates": candidates})
        return result
    if len(installed) > 1:
        result = base_result("next", "BLOCKED", gaps + [f"{logical['name']}: multiple available first-party copies require host precedence evidence."])
        result.update({"skill": logical["name"], "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0}, "candidates": candidates})
        return result
    selected = installed[0]
    if not invocation_compatible(selected["invocationType"], control):
        result = base_result(
            "next",
            "BLOCKED",
            gaps + [f"{selected['name']}: {selected['invocationType']} is incompatible with invocationControl={control}."],
        )
        result.update({"skill": selected["name"], "reads": {"metadata": metadata_reads, "bodies": 0, "references": 0}, "candidates": candidates})
        return result
    body_reads, reference_reads, read_error = validate_selected(selected)
    selected["readStatus"] = "unavailable" if read_error else "available"
    if read_error:
        result = base_result("next", "BLOCKED", gaps + [f"{selected['name']}: {read_error}; restore the first-party package."])
        result.update({"skill": selected["name"], "reads": {"metadata": metadata_reads, "bodies": body_reads, "references": reference_reads}, "candidates": candidates})
        return result
    evidence = logical["matchedPatterns"] + logical["matchedPrecedence"]
    if logical["matchedTaskKind"]:
        evidence.append(f"taskKind:{logical['matchedTaskKind']}->{logical['name']}")
    return {"mode": "next", "status": "RECOMMEND", "skill": selected["name"], "source": f"first-party: {selected['packagePath']}", "reason": f"Light Skill Map matched: {', '.join(evidence)}", "invocation": invocation(selected["name"], policy["host"]), "confidence": "high", "alternative": None, "gaps": gaps, "reads": {"metadata": metadata_reads, "bodies": body_reads, "references": reference_reads}, "candidates": candidates, "execution": "recommendation only; nothing was invoked, installed, or orchestrated"}


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


def route(roots: list[dict[str, Any]], context: dict[str, Any], host: str = "codex", mode: str = "next") -> dict[str, Any]:
    skill_map = load_map()
    return workflow_result(roots, context, host, skill_map) if mode == "workflow" else next_result(roots, context, host, skill_map)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots-json", required=True)
    parser.add_argument("--context-json", required=True)
    parser.add_argument("--host-name", default="codex")
    parser.add_argument("--mode", choices=("next", "workflow"), default="next")
    args = parser.parse_args()
    print(json.dumps(route(json.loads(args.roots_json), json.loads(args.context_json), args.host_name, args.mode), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
