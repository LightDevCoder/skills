#!/usr/bin/env python3
"""Verify released-source installs in a fresh GitHub-hosted Linux user environment."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/LightDevCoder/skills.git"
SOURCE = "LightDevCoder/skills"


def validate_identity(tag: str, commit: str) -> None:
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("tag must be a stable vX.Y.Z identifier")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("expected commit must be a full lowercase SHA")


def package_files(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
        and p.suffix != ".pyc" and p.name != ".DS_Store"
    }


def source_packages(root: Path) -> dict[str, dict[str, str]]:
    result = {}
    for entry in sorted((root / "skills").glob("*/*/SKILL.md")):
        sections = entry.read_text().split("---", 2)
        if len(sections) != 3:
            raise ValueError("source package has no valid frontmatter")
        frontmatter = sections[1]
        match = re.search(r"^name:\s*([^\n]+)$", frontmatter, re.MULTILINE)
        name = match.group(1).strip().strip("\"'") if match else ""
        if name != entry.parent.name or name in result:
            raise ValueError("source package identity mismatch")
        result[name] = package_files(entry.parent)
    if not result:
        raise ValueError("source has no admitted packages")
    return result


def verify_destination(root: Path, expected: dict[str, dict[str, str]]) -> dict:
    names = {p.name for p in root.iterdir() if p.is_dir() or p.is_symlink()}
    if names != set(expected):
        raise ValueError(f"destination package set mismatch at {root}")
    for name, files in expected.items():
        if package_files(root / name) != files:
            raise ValueError(f"destination content mismatch: {name}")
    return {
        "destination": str(root), "packages": len(expected),
        "files": sum(map(len, expected.values())), "exact": True,
        "links": {name: str((root / name).resolve()) for name in sorted(expected)},
        "actual_package_manifest": {name: package_files(root / name) for name in sorted(expected)},
    }


PROJECT_TARGETS = {"codex": ".agents/skills", "claude-code": ".claude/skills"}


def verify_project_targets(project: Path, expected: dict, selected: list[str]) -> list[dict]:
    if not selected or any(name not in PROJECT_TARGETS for name in selected):
        raise ValueError("verification is limited to the declared Codex/Claude Code targets")
    destinations = sorted({project / PROJECT_TARGETS[name] for name in selected})
    for destination in destinations:
        if not destination.is_dir():
            raise ValueError(f"installer omitted a required Agent target: {destination}")
    return [verify_destination(destination, expected) for destination in destinations]


def require_fresh_runner(home: Path) -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or sys.platform != "linux":
        raise ValueError("global installation requires a fresh GitHub-hosted Linux runner")
    if os.environ.get("CODEX_HOME"):
        raise ValueError("runner must use its native default Codex home")
    for root in (home / ".codex/skills", home / ".agents/skills"):
        if root.exists() or root.is_symlink():
            raise ValueError(f"runner already has a global Skills destination: {root}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    validate_identity(args.tag, args.expected_commit)
    require_fresh_runner(Path.home())
    args.output.mkdir(parents=True, exist_ok=False)
    commands, observations = [], []

    def run(argv: list[str], cwd: Path | None = None) -> str:
        result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=300)
        number = len(commands)
        (args.output / f"command-{number:02d}.log").write_text(result.stdout + result.stderr)
        commands.append({"argv": argv, "cwd": str(cwd) if cwd else None, "exit": result.returncode})
        (args.output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        if result.returncode:
            raise RuntimeError(f"command {number} failed; see its log")
        return result.stdout.strip()

    def clone(ref: str, name: str) -> tuple[Path, str, dict]:
        root = args.output / name
        run(["git", "clone", "--quiet", "--depth", "1", "--branch", ref, REPOSITORY, str(root)])
        return root, run(["git", "rev-parse", "HEAD"], root), source_packages(root)

    _, pinned_sha, pinned = clone(args.tag, "pinned-source")
    if pinned_sha != args.expected_commit or len(pinned) != 36:
        raise ValueError("published tag does not match the expected 36-package candidate")
    _, default_sha, latest = clone("main", "default-source")
    cli = ["npx", "--yes", "--cache", str(args.output / "npm-cache"), "skills"]
    cli_version = run(cli + ["--version"])
    cli_files = list((args.output / "npm-cache").glob("_npx/*/node_modules/skills/dist/cli.mjs"))
    if len(cli_files) != 1:
        raise ValueError("cannot bind the resolved CLI distribution")
    cli_sha = hashlib.sha256(cli_files[0].read_bytes()).hexdigest()
    resolved_version = json.loads((cli_files[0].parent.parent / "package.json").read_text())["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", resolved_version) or resolved_version not in cli_version:
        raise ValueError("CLI version response does not match its resolved distribution")
    cli[-1] = "skills@" + resolved_version

    def install(name: str, source: str, flags: list[str], expected: dict, selected: list[str], global_scope: bool = False) -> None:
        project = args.output / name
        project.mkdir()
        run(cli + ["add", source, *flags, "--yes"], project)
        if global_scope:
            checked = [verify_destination(Path.home() / ".codex/skills", expected)]
        else:
            checked = verify_project_targets(project, expected, selected)
        observations.append({
            "case": name, "selected_agents": selected, "destinations": checked,
        })

    fixed_source = f"{SOURCE}#{args.tag}"
    install("pinned-global-codex", fixed_source, ["--global", "--agent", "codex"], pinned, ["codex"], True)
    install("pinned-whole", fixed_source, ["--agent", "codex", "claude-code", "--skill", "*", "--copy"], pinned, ["codex", "claude-code"])
    for name in ("light-implement", "light-tdd", "light-research"):
        install("single-" + name, fixed_source, ["--agent", "codex", "--skill", name], {name: pinned[name]}, ["codex"])
    install("default-whole", SOURCE, ["--agent", "codex", "claude-code", "--skill", "*", "--copy"], latest, ["codex", "claude-code"])
    default_after = run(["git", "ls-remote", REPOSITORY, "refs/heads/main"]).split()[0]
    if default_after != default_sha:
        raise ValueError("default branch moved during installation; rerun against stable identities")
    final_cli_files = list((args.output / "npm-cache").glob("_npx/*/node_modules/skills/dist/cli.mjs"))
    if not final_cli_files or any(hashlib.sha256(p.read_bytes()).hexdigest() != cli_sha for p in final_cli_files):
        raise ValueError("resolved CLI distribution changed during verification")
    record = {
        "status": "VERIFIED", "tag": args.tag, "pinned_commit": pinned_sha,
        "default_commit": default_sha, "cli_version": cli_version, "cli_sha256": cli_sha,
        "native_home": str(Path.home()), "HOME_or_CODEX_HOME_overridden": False,
        "pinned_package_manifest": pinned, "default_package_manifest": latest,
        "declared_project_targets": PROJECT_TARGETS,
        "observations": observations,
        "scope": "fresh ephemeral Linux runner; installer evidence, not Linux Codex runtime evidence",
    }
    (args.output / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    summary = {k: v for k, v in record.items() if "manifest" not in k and k != "observations"}
    summary["observations"] = [{"case": o["case"], "targets": len(o["destinations"]),
                                "packages_per_target": o["destinations"][0]["packages"],
                                "files_per_target": o["destinations"][0]["files"], "exact": True} for o in observations]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
