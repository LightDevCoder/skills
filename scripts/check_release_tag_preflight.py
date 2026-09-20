#!/usr/bin/env python3
"""Release Tag Preflight Verification Gate.

Pre-action validation executed before creating a release tag:
1. Candidate commit exists and resolves to a full 40-character SHA.
2. Working tree is clean (zero whitespace errors, zero uncommitted tracked changes).
3. Remote GitHub ruleset protection for release tags is confirmed active (fail-closed).
4. Target tag does NOT exist locally (blocks premature creation or collisions).
5. Target tag does NOT exist remotely on origin (blocks remote tag overwrite).

Unless explicit --allow-retry is enabled, existing tags cause BLOCKED to ensure
safe, unidirectional tag creation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ensure scripts dir is on sys.path for sibling imports
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_release_tag_protection import fetch_remote_rulesets, verify_ruleset_payload


class PreflightResult(NamedTuple):
    passed: bool
    status: str
    message: str


def run_git(cmd: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
    """Execute git command and return (code, stdout, stderr)."""
    proc = subprocess.run(
        ["git"] + cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def resolve_commit_sha(commit_ref: str, cwd: Path = REPO_ROOT) -> str | None:
    """Resolve a commit reference to its full 40-character SHA."""
    code, out, _ = run_git(["rev-parse", f"{commit_ref}^{{commit}}"], cwd=cwd)
    if code == 0 and len(out) == 40:
        return out
    return None


def resolve_local_tag(tag: str, cwd: Path = REPO_ROOT) -> str | None:
    """Check if local tag exists, returning peeled commit if it does."""
    code, out, _ = run_git(["tag", "-l", tag], cwd=cwd)
    if code == 0 and out == tag:
        code_peel, out_peel, _ = run_git(["rev-parse", f"{tag}^{{commit}}"], cwd=cwd)
        if code_peel == 0 and len(out_peel) == 40:
            return out_peel
        return "UNKNOWN"
    return None


def resolve_remote_tag(tag: str, remote: str = "origin", cwd: Path = REPO_ROOT) -> str | None:
    """Query remote for tag existence."""
    code, out, _ = run_git(["ls-remote", "--tags", remote, f"refs/tags/{tag}"], cwd=cwd)
    if code != 0 or not out:
        return None
    lines = out.splitlines()
    peeled = [l.split()[0] for l in lines if l.endswith("^{}")]
    if peeled:
        return peeled[0]
    unpeeled = [l.split()[0] for l in lines if f"refs/tags/{tag}" in l]
    if unpeeled:
        return unpeeled[0]
    return None


def check_working_tree(repo_root: Path = REPO_ROOT) -> tuple[bool, str]:
    """Verify git diff and whitespace cleanliness."""
    code_ws, _, err_ws = run_git(["diff", "--check"], cwd=repo_root)
    if code_ws != 0:
        return False, f"Whitespace errors detected: {err_ws}"

    code_st, out_st, _ = run_git(["status", "--porcelain"], cwd=repo_root)
    tracked_mods = [line for line in out_st.splitlines() if line and not line.startswith("??")]
    if tracked_mods:
        return False, "Uncommitted tracked changes detected:\n" + "\n".join(tracked_mods[:5])

    return True, "Working tree clean."


def run_tag_preflight(
    tag: str,
    release_commit: str,
    repo: str = "LightDevCoder/skills",
    pattern: str = "refs/tags/v*",
    fixture: str | None = None,
    check_remote_tag: bool = False,
    allow_retry: bool = False,
    repo_root: Path = REPO_ROOT,
) -> PreflightResult:
    """Execute all tag preflight gates."""
    # 1. Candidate commit exists
    cand_sha = resolve_commit_sha(release_commit, cwd=repo_root)
    if not cand_sha:
        return PreflightResult(
            passed=False,
            status="BLOCKED",
            message=f"Release candidate commit '{release_commit}' cannot be resolved to a 40-character commit SHA.",
        )

    # 2. Working tree clean
    tree_ok, tree_msg = check_working_tree(repo_root)
    if not tree_ok:
        return PreflightResult(
            passed=False,
            status="BLOCKED",
            message=f"Working tree must be clean before creating release tag: {tree_msg}",
        )

    # 3. Ruleset protection gate (fail closed)
    if fixture:
        fixture_path = Path(fixture)
        if not fixture_path.is_file():
            return PreflightResult(
                passed=False,
                status="BLOCKED",
                message=f"Ruleset fixture file not found: {fixture}",
            )
        try:
            data = json.loads(fixture_path.read_text(encoding="utf-8"))
            ruleset_res = verify_ruleset_payload(data, target_pattern=pattern)
        except Exception as e:
            return PreflightResult(
                passed=False,
                status="BLOCKED",
                message=f"Failed to parse ruleset fixture: {e}",
            )
    else:
        try:
            remote_rulesets = fetch_remote_rulesets(repo)
            ruleset_res = verify_ruleset_payload(remote_rulesets, target_pattern=pattern)
        except Exception as e:
            return PreflightResult(
                passed=False,
                status="BLOCKED",
                message=f"Failed to fetch remote ruleset protection from {repo}: {e}",
            )

    if not ruleset_res.passed:
        return PreflightResult(
            passed=False,
            status="BLOCKED",
            message=f"Remote tag ruleset protection check failed: {ruleset_res.message}",
        )

    # 4. Local tag existence check
    local_tag_sha = resolve_local_tag(tag, cwd=repo_root)
    if local_tag_sha:
        if allow_retry and local_tag_sha == cand_sha:
            # Idempotent retry allowed if flag set and points to candidate
            pass
        else:
            return PreflightResult(
                passed=False,
                status="BLOCKED",
                message=(
                    f"Local tag '{tag}' already exists pointing to {local_tag_sha}. "
                    "For new releases, the tag must not exist prior to creation."
                ),
            )

    # 5. Remote tag existence check (if requested)
    if check_remote_tag:
        remote_tag_sha = resolve_remote_tag(tag, remote="origin", cwd=repo_root)
        if remote_tag_sha:
            if allow_retry and remote_tag_sha == cand_sha:
                pass
            else:
                return PreflightResult(
                    passed=False,
                    status="BLOCKED",
                    message=(
                        f"Remote tag '{tag}' already exists on origin pointing to {remote_tag_sha}. "
                        "Cannot overwrite an existing remote release tag."
                    ),
                )

    return PreflightResult(
        passed=True,
        status="PASS",
        message=f"Tag preflight passed: candidate {cand_sha} confirmed, clean working tree, remote ruleset protected, and tag '{tag}' ready for creation.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight check before release tag creation.")
    parser.add_argument("--tag", required=True, help="Release tag to create (e.g. v0.2.4).")
    parser.add_argument("--release-commit", required=True, help="Candidate commit SHA.")
    parser.add_argument("--repo", default="LightDevCoder/skills", help="Target GitHub repository.")
    parser.add_argument("--pattern", default="refs/tags/v*", help="Target tag pattern.")
    parser.add_argument("--fixture", help="Path to ruleset JSON fixture for offline/hermetic testing.")
    parser.add_argument("--check-remote", action="store_true", help="Also check remote tag existence via ls-remote.")
    parser.add_argument("--allow-retry", action="store_true", help="Allow tag creation preflight if existing tag matches candidate.")
    parser.add_argument("--root", default=None, help="Repository root path.")

    args = parser.parse_args()
    repo_root = Path(args.root).resolve() if args.root else REPO_ROOT

    print(f"=== Release Tag Preflight Guard ===")
    print(f"Target Tag:     {args.tag}")
    print(f"Release Commit: {args.release_commit}")
    print(f"Repository:     {repo_root}")
    print("-----------------------------------")

    result = run_tag_preflight(
        tag=args.tag,
        release_commit=args.release_commit,
        repo=args.repo,
        pattern=args.pattern,
        fixture=args.fixture,
        check_remote_tag=args.check_remote,
        allow_retry=args.allow_retry,
        repo_root=repo_root,
    )

    print(f"[{result.status}] {result.message}")
    print("-----------------------------------")

    if result.passed:
        print("RESULT: PASS — Preconditions met. Proceed with: git tag -a <tag> -m '<message>'")
        return 0
    else:
        print("RESULT: BLOCKED — Tag creation preconditions NOT met. Do not create tag.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
