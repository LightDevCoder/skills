#!/usr/bin/env python3
"""Check manuscript Skill interfaces locally; compare exact bytes only at an explicit ref."""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import tarfile
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

from manuscript_ops_core import ContractError, dump_json, load_json


def frontmatter_keys(text: str) -> set[str]:
    if not text.startswith("---\n"):
        return set()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return set()
    return {line.split(":", 1)[0].strip() for line in parts[1].splitlines()
            if ":" in line and not line.startswith((" ", "\t"))}


def package_files(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store"}


def archive_files(repository: str, ref: str) -> dict[str, bytes]:
    url = f"https://codeload.github.com/{repository}/tar.gz/{urllib.parse.quote(ref, safe='')}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "manuscript-ops-dependency-check"}), timeout=30) as response:
        archive = response.read()
    result: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        for member in bundle.getmembers():
            if member.isfile():
                handle = bundle.extractfile(member)
                if handle:
                    result["/".join(Path(member.name).parts[1:])] = handle.read()
    if not result:
        raise ContractError(f"empty archive for {repository}@{ref}")
    return result


def validate_registry(registry: object) -> list[dict]:
    if not isinstance(registry, dict) or registry.get("schema_version") != "2":
        raise ContractError("dependency registry schema_version must be 2")
    records = registry.get("dependencies")
    if not isinstance(records, list) or not records:
        raise ContractError("dependency registry must contain dependencies")
    names: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("name"), str) or record["name"] in names:
            raise ContractError("dependency names must be unique strings")
        names.add(record["name"])
        if record.get("invocation_type") not in ("user-invoked", "model-invoked"):
            raise ContractError(f"{record['name']} has invalid invocation_type")
        if not isinstance(record.get("required"), bool):
            raise ContractError(f"{record['name']} requires a boolean required flag")
        paths = record.get("required_files")
        if not isinstance(paths, list) or "SKILL.md" not in paths or any(not isinstance(p, str) or not p or Path(p).is_absolute() or ".." in Path(p).parts for p in paths):
            raise ContractError(f"{record['name']} has invalid required_files")
        if not isinstance(record.get("interface_tokens"), dict):
            raise ContractError(f"{record['name']} has invalid interface_tokens")
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path(__file__).resolve().parents[1] / "assets/dependency-contracts.json")
    parser.add_argument("--catalog", type=Path, action="append", default=[])
    parser.add_argument("--require-optional", action="append", default=[])
    parser.add_argument("--audit-all", action="store_true")
    parser.add_argument("--strict-agent-skills", action="store_true")
    parser.add_argument("--online", action="store_true", help="Compare installed package bytes with an explicit ref")
    parser.add_argument("--ref", help="Exact published commit or tag; required with --online")
    args = parser.parse_args()
    errors: list[str] = []
    checks: list[str] = []
    try:
        records = validate_registry(load_json(args.registry))
        by_name = {record["name"]: record for record in records}
        if any(name not in by_name or by_name[name]["required"] for name in args.require_optional):
            raise ContractError("--require-optional names unknown or non-optional dependency")
        if args.online and not args.ref:
            raise ContractError("--online requires --ref; never compare against a moving default branch")
        if args.ref and not args.online:
            raise ContractError("--ref requires --online")
        if args.ref and not re.fullmatch(r"(?:[0-9a-f]{40}|v\d+\.\d+\.\d+)", args.ref):
            raise ContractError("--ref must be an exact commit SHA or release tag")
        archives: dict[str, dict[str, bytes]] = {}
        for record in records:
            name = record["name"]
            if not record["required"] and name not in args.require_optional and not args.audit_all:
                checks.append(f"optional-unselected:{name}")
                continue
            roots = [catalog.resolve() / name for catalog in args.catalog if (catalog.resolve() / name / "SKILL.md").is_file()]
            if len(roots) != 1:
                errors.append(f"{name} must resolve to exactly one installed package, found {len(roots)}")
                continue
            files = package_files(roots[0])
            for required in record["required_files"]:
                if required not in files:
                    errors.append(f"{name} is missing required interface file {required}")
            skill = files.get("SKILL.md", b"").decode("utf-8")
            keys = frontmatter_keys(skill)
            if not {"name", "description"}.issubset(keys):
                errors.append(f"{name} has invalid frontmatter")
            observed_type = "user-invoked" if "disable-model-invocation" in keys else "model-invoked"
            if observed_type != record["invocation_type"]:
                errors.append(f"{name} invocation direction changed: {observed_type}")
            if args.strict_agent_skills and observed_type == "user-invoked":
                errors.append(f"{name} requires a host that supports disable-model-invocation")
            for path, tokens in record["interface_tokens"].items():
                content = files.get(path, b"").decode("utf-8")
                functions = ({node.name for node in ast.walk(ast.parse(content))
                              if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                             if path.endswith(".py") and content else set())
                for token in tokens:
                    if (token not in functions if path.endswith(".py") else token not in content):
                        errors.append(f"{name} missing interface token {token!r} in {path}")
            checks.append(f"catalog:{name}")
            if args.online:
                repository = record["repository"]
                if repository not in archives:
                    archives[repository] = archive_files(repository, args.ref)
                prefix = record["path"].rstrip("/") + "/"
                expected = {path[len(prefix):]: content for path, content in archives[repository].items() if path.startswith(prefix)}
                if files != expected:
                    changed = sorted({*files, *expected} - {p for p in files.keys() & expected.keys() if files[p] == expected[p]})
                    errors.append(f"{name} differs from {repository}@{args.ref}: {changed}")
                else:
                    checks.append(f"exact-ref:{name}@{args.ref}")
    except (ContractError, OSError, UnicodeError, ValueError, KeyError, SyntaxError, tarfile.TarError, urllib.error.URLError) as exc:
        errors.append(str(exc))
    print(dump_json({"schema_version": "2", "status": "BLOCKED" if errors else "READY", "errors": errors, "warnings": [], "checks": checks}))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
