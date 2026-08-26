#!/usr/bin/env python3
"""Check manuscript-ops dependency contracts without installing anything."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from manuscript_ops_core import ContractError, dump_json, load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_registry = Path(__file__).resolve().parents[1] / "assets" / "dependency-contracts.json"
    parser.add_argument("--registry", type=Path, default=default_registry)
    parser.add_argument(
        "--catalog",
        type=Path,
        action="append",
        default=[],
        help="Skill catalog root containing <name>/SKILL.md; may be repeated",
    )
    parser.add_argument(
        "--strict-agent-skills",
        action="store_true",
        help="Block when a required upstream Skill uses observed non-standard frontmatter",
    )
    parser.add_argument(
        "--require-optional",
        action="append",
        default=[],
        metavar="SKILL",
        help="Promote a selected optional branch to a required dependency; may be repeated",
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Verify effective dependencies against pinned GitHub package bytes and default-branch drift",
    )
    parser.add_argument(
        "--audit-all",
        action="store_true",
        help="Also audit unselected optional dependency contracts; intended for repository CI",
    )
    return parser.parse_args()


def frontmatter_keys(text: str) -> set[str]:
    if not text.startswith("---\n"):
        return set()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return set()
    return {
        line.split(":", 1)[0].strip()
        for line in parts[1].splitlines()
        if ":" in line and not line.startswith((" ", "\t"))
    }


def find_skill(name: str, catalogs: list[Path]) -> Path | None:
    for catalog in catalogs:
        candidate = catalog.resolve() / name / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def fetch_github_file(
    record: dict[str, Any],
    relative_path: str,
    *,
    ref: str | None,
) -> tuple[str, bytes]:
    repository = record["repository"]
    path = f"{record['path']}/{relative_path}"
    url = f"https://api.github.com/repos/{repository}/contents/{path}"
    if ref:
        url = f"{url}?ref={ref}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "manuscript-ops-dependency-check",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("sha"), str):
        raise ContractError(f"unexpected GitHub response for {repository}/{path}")
    download_url = payload.get("download_url")
    if not isinstance(download_url, str) or not download_url:
        raise ContractError(f"GitHub response has no download_url for {repository}/{path}")
    content_request = urllib.request.Request(
        download_url,
        headers={"User-Agent": "manuscript-ops-dependency-check"},
    )
    with urllib.request.urlopen(content_request, timeout=20) as response:
        content = response.read()
    return payload["sha"], content


def fetch_default_branch(repository: str) -> str:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "manuscript-ops-dependency-check",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    branch = payload.get("default_branch") if isinstance(payload, dict) else None
    if not isinstance(branch, str) or not branch:
        raise ContractError(f"cannot resolve default branch for {repository}")
    return branch


def fetch_repository_archive(
    repository: str,
    ref: str,
    cache: dict[tuple[str, str], dict[str, bytes]],
) -> dict[str, bytes]:
    cache_key = (repository, ref)
    if cache_key in cache:
        return cache[cache_key]
    encoded_ref = urllib.parse.quote(ref, safe="")
    request = urllib.request.Request(
        f"https://codeload.github.com/{repository}/tar.gz/{encoded_ref}",
        headers={"User-Agent": "manuscript-ops-dependency-check"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        archive_bytes = response.read()
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                parts = Path(member.name).as_posix().split("/")
                if len(parts) < 2:
                    continue
                extracted = archive.extractfile(member)
                if extracted is not None:
                    files["/".join(parts[1:])] = extracted.read()
    except tarfile.TarError as exc:
        raise ContractError(
            f"invalid GitHub archive for {repository}@{ref}: {exc}"
        ) from exc
    if not files:
        raise ContractError(f"empty GitHub archive for {repository}@{ref}")
    cache[cache_key] = files
    return files


def package_from_archive(
    record: dict[str, Any],
    ref: str,
    cache: dict[tuple[str, str], dict[str, bytes]],
) -> dict[str, bytes]:
    repository_files = fetch_repository_archive(record["repository"], ref, cache)
    prefix = f"{str(record['path']).strip('/')}/"
    return {
        path[len(prefix) :]: content
        for path, content in repository_files.items()
        if path.startswith(prefix)
    }


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def package_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store"
    }


def validate_registry(registry: Any) -> list[dict[str, Any]]:
    if not isinstance(registry, dict) or registry.get("schema_version") != "1":
        raise ContractError("dependency registry schema_version must be 1")
    dependencies = registry.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        raise ContractError("dependency registry must contain dependencies")
    names: set[str] = set()
    for item in dependencies:
        if not isinstance(item, dict):
            raise ContractError("dependency entries must be objects")
        name = item.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ContractError(f"invalid or duplicate dependency name: {name!r}")
        names.add(name)
        for field in (
            "repository",
            "repository_commit",
            "path",
            "blob_sha",
            "layer",
        ):
            if not isinstance(item.get(field), str) or not item[field]:
                raise ContractError(f"{name} requires {field}")
        for field in ("repository_commit", "blob_sha"):
            value = item[field]
            if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
                raise ContractError(f"{name}.{field} must be a lowercase 40-character Git SHA")
        files = item.get("package_files")
        if (
            not isinstance(files, list)
            or not files
            or files[0] != "SKILL.md"
            or len(files) != len(set(files))
            or not all(
                isinstance(path, str)
                and path
                and not Path(path).is_absolute()
                and ".." not in Path(path).parts
                for path in files
            )
        ):
            raise ContractError(f"{name}.package_files must be a unique safe list starting with SKILL.md")
        if not isinstance(item.get("required"), bool):
            raise ContractError(f"{name}.required must be boolean")
        if not isinstance(item.get("required_mentions"), list):
            raise ContractError(f"{name}.required_mentions must be an array")
        if not isinstance(item.get("strict_agent_skills_compatible"), bool):
            raise ContractError(f"{name} requires a strict compatibility declaration")
    return dependencies


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    try:
        dependencies = validate_registry(load_json(args.registry))
        by_name = {record["name"]: record for record in dependencies}
        selected_optional = set(args.require_optional)
        invalid_selected = sorted(
            name
            for name in selected_optional
            if name not in by_name or by_name[name]["required"]
        )
        if invalid_selected:
            raise ContractError(
                f"--require-optional names unknown or non-optional dependencies: {invalid_selected}"
            )
        catalogs = [path.resolve() for path in args.catalog]
        archive_cache: dict[tuple[str, str], dict[str, bytes]] = {}
        default_branches: dict[str, str] = {}
        for record in dependencies:
            name = record["name"]
            required = record["required"] or name in selected_optional
            audit_record = required or args.audit_all
            text: str | None = None
            local_contents: dict[str, bytes] = {}
            if catalogs:
                skill_path = find_skill(name, catalogs)
                if skill_path is None:
                    if required:
                        errors.append(f"{name} is missing from the supplied catalogs")
                    else:
                        checks.append(f"optional-unselected:{name}")
                elif not audit_record:
                    checks.append(f"optional-unselected:{name}")
                else:
                    skill_root = skill_path.parent
                    expected_files = set(record["package_files"])
                    actual_files = package_files(skill_root)
                    missing_files = sorted(expected_files - actual_files)
                    unexpected_files = sorted(actual_files - expected_files)
                    if missing_files:
                        errors.append(
                            f"{name} installed package omits files: {missing_files}"
                        )
                    if unexpected_files:
                        errors.append(
                            f"{name} installed package contains unregistered files: "
                            f"{unexpected_files}"
                        )
                    for relative_path in expected_files & actual_files:
                        local_contents[relative_path] = (
                            skill_root / relative_path
                        ).read_bytes()
                    skill_content = local_contents.get("SKILL.md")
                    if skill_content is not None:
                        observed_blob = git_blob_sha(skill_content)
                        if observed_blob != record["blob_sha"]:
                            errors.append(
                                f"{name} installed SKILL.md differs from pinned blob: "
                                f"expected {record['blob_sha']}, observed {observed_blob}"
                            )
                        text = skill_content.decode("utf-8")
                    if (
                        required
                        and len(record["package_files"]) > 1
                        and not args.online
                    ):
                        warnings.append(
                            f"{name} resource bytes require --online to compare with "
                            f"pinned commit {record['repository_commit']}"
                        )
                    checks.append(f"catalog:{name}")
            if args.online and audit_record:
                pinned_contents: dict[str, bytes] = {}
                try:
                    pinned_contents = package_from_archive(
                        record,
                        record["repository_commit"],
                        archive_cache,
                    )
                    expected_files = set(record["package_files"])
                    pinned_files = set(pinned_contents)
                    if pinned_files != expected_files:
                        errors.append(
                            f"{name} registry package_files differs from pinned "
                            f"directory tree: registry_omits={sorted(pinned_files - expected_files)}, "
                            f"registry_adds={sorted(expected_files - pinned_files)}"
                        )
                    skill_content = pinned_contents.get("SKILL.md")
                    if skill_content is None:
                        errors.append(f"{name} pinned package omits SKILL.md")
                    else:
                        observed_sha = git_blob_sha(skill_content)
                        if observed_sha != record["blob_sha"]:
                            errors.append(
                                f"{name} pinned commit SKILL.md mismatch: "
                                f"expected {record['blob_sha']}, observed {observed_sha}"
                            )
                    repository = record["repository"]
                    if repository not in default_branches:
                        default_branches[repository] = fetch_default_branch(repository)
                    current_contents = package_from_archive(
                        record,
                        default_branches[repository],
                        archive_cache,
                    )
                except (
                    ContractError,
                    OSError,
                    tarfile.TarError,
                    urllib.error.URLError,
                    json.JSONDecodeError,
                ) as exc:
                    errors.append(f"{name} online contract check failed: {exc}")
                else:
                    if current_contents != pinned_contents:
                        changed_paths = sorted(
                            {
                                *set(current_contents),
                                *set(pinned_contents),
                            }
                            - {
                                path
                                for path in set(current_contents) & set(pinned_contents)
                                if current_contents[path] == pinned_contents[path]
                            }
                        )
                        errors.append(
                            f"{name} upstream default branch package drifted at: "
                            f"{changed_paths}"
                        )
                    else:
                        checks.append(
                            f"upstream:{name}@{record['repository_commit']}"
                        )
                    if local_contents:
                        for relative_path, expected_content in pinned_contents.items():
                            observed_content = local_contents.get(relative_path)
                            if observed_content is not None and observed_content != expected_content:
                                errors.append(
                                    f"{name} installed {relative_path} differs from "
                                    f"pinned commit {record['repository_commit']}"
                                )
                    if "SKILL.md" in pinned_contents:
                        text = pinned_contents["SKILL.md"].decode("utf-8")
            if text is not None:
                keys = frontmatter_keys(text)
                if not {"name", "description"}.issubset(keys):
                    errors.append(f"{name} has invalid or missing frontmatter")
                missing_mentions = [
                    value for value in record["required_mentions"] if value not in text
                ]
                if missing_mentions:
                    errors.append(f"{name} contract omitted calls: {missing_mentions}")
                observed_strict = "disable-model-invocation" not in keys
                if observed_strict != record["strict_agent_skills_compatible"]:
                    errors.append(f"{name} strict-compatibility declaration is stale")
            if (
                args.strict_agent_skills
                and required
                and not record["strict_agent_skills_compatible"]
            ):
                errors.append(
                    f"{name} is required but the pinned contract is not strict Agent Skills compatible"
                )
    except (ContractError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    status = "BLOCKED" if errors else ("DEGRADED" if warnings else "READY")
    print(
        dump_json(
            {
                "schema_version": "1",
                "status": status,
                "errors": errors,
                "warnings": warnings,
                "checks": checks,
            }
        )
    )
    return 2 if errors else (1 if warnings else 0)


if __name__ == "__main__":
    raise SystemExit(main())
