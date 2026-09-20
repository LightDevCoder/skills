#!/usr/bin/env python3
"""Release Tag Preflight Verification Gate.

Pre-action validation executed before creating a release tag:
1. Candidate commit exists and resolves to a full 40-character SHA.
2. Working tree is clean (zero whitespace errors, zero uncommitted tracked changes).
3. Remote GitHub ruleset protection for release tags is confirmed active (fail-closed).
4. Target tag does NOT exist locally (blocks premature creation or collisions).
5. Target tag does NOT exist remotely on origin (blocks remote tag overwrite).

Any existing local or remote tag causes BLOCKED to ensure safe, unidirectional tag creation.
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


class RemoteTagStatus:
    ABSENT = "ABSENT"
    EXISTS = "EXISTS"
    QUERY_FAILED = "QUERY_FAILED"


class RemoteTagResult(NamedTuple):
    status: str  # RemoteTagStatus.ABSENT | EXISTS | QUERY_FAILED
    tag_object_sha: str | None = None
    peeled_commit_sha: str | None = None
    is_annotated: bool = False
    error: str | None = None


class AnnotatedTagIdentity(NamedTuple):
    tag_type: str | None
    tag_object_sha: str | None
    peeled_commit_sha: str | None
    is_annotated: bool


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


def resolve_annotated_tag_identity(tag: str, cwd: Path = REPO_ROOT) -> AnnotatedTagIdentity:
    """Resolve tag identity using git cat-file -t and git rev-parse."""
    code_type, out_type, _ = run_git(["cat-file", "-t", f"refs/tags/{tag}"], cwd=cwd)
    if code_type != 0 or not out_type:
        return AnnotatedTagIdentity(tag_type=None, tag_object_sha=None, peeled_commit_sha=None, is_annotated=False)

    tag_type = out_type.strip()
    if tag_type != "tag":
        code_rev, out_rev, _ = run_git(["rev-parse", f"refs/tags/{tag}"], cwd=cwd)
        sha = out_rev if code_rev == 0 and len(out_rev) == 40 else None
        return AnnotatedTagIdentity(
            tag_type=tag_type,
            tag_object_sha=sha,
            peeled_commit_sha=sha,
            is_annotated=False,
        )

    code_obj, out_obj, _ = run_git(["rev-parse", f"refs/tags/{tag}"], cwd=cwd)
    code_peel, out_peel, _ = run_git(["rev-parse", f"refs/tags/{tag}^{{commit}}"], cwd=cwd)
    obj_sha = out_obj if code_obj == 0 and len(out_obj) == 40 else None
    peel_sha = out_peel if code_peel == 0 and len(out_peel) == 40 else None

    return AnnotatedTagIdentity(
        tag_type="tag",
        tag_object_sha=obj_sha,
        peeled_commit_sha=peel_sha,
        is_annotated=True,
    )


def resolve_local_tag(tag: str, cwd: Path = REPO_ROOT) -> str | None:
    """Check if local tag exists, returning peeled commit if it does."""
    ident = resolve_annotated_tag_identity(tag, cwd=cwd)
    if ident.tag_type:
        return ident.peeled_commit_sha
    return None


def resolve_remote_tag(tag: str, remote: str = "origin", cwd: Path = REPO_ROOT) -> RemoteTagResult:
    """Query remote for tag existence and peeled commit identity.

    Executes git ls-remote --tags <remote> refs/tags/<tag> refs/tags/<tag>^{}
    and returns a structured RemoteTagResult (ABSENT, EXISTS, or QUERY_FAILED).
    """
    code, out, err = run_git(
        ["ls-remote", "--tags", remote, f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],
        cwd=cwd,
    )
    if code != 0:
        error_msg = err if err else f"git ls-remote exited with status {code}"
        return RemoteTagResult(status=RemoteTagStatus.QUERY_FAILED, error=error_msg)

    if not out.strip():
        # Exit code 0 and empty output means tag does not exist on remote
        return RemoteTagResult(status=RemoteTagStatus.ABSENT)

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    direct_sha: str | None = None
    peeled_sha: str | None = None

    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            sha, ref = parts[0], parts[1]
            if ref == f"refs/tags/{tag}":
                direct_sha = sha
            elif ref == f"refs/tags/{tag}^{{}}":
                peeled_sha = sha

    if peeled_sha:
        # Annotated tag: direct_sha is the tag object SHA, peeled_sha is the peeled commit SHA
        return RemoteTagResult(
            status=RemoteTagStatus.EXISTS,
            tag_object_sha=direct_sha,
            peeled_commit_sha=peeled_sha,
            is_annotated=True,
        )
    elif direct_sha:
        # Lightweight tag: direct_sha is the commit SHA
        return RemoteTagResult(
            status=RemoteTagStatus.EXISTS,
            tag_object_sha=None,
            peeled_commit_sha=direct_sha,
            is_annotated=False,
        )

    return RemoteTagResult(status=RemoteTagStatus.ABSENT)


def check_working_tree(repo_root: Path = REPO_ROOT, tag: str | None = None) -> tuple[bool, str]:
    """Verify git diff, whitespace cleanliness, and absence of uncommitted release evidence."""
    code_ws, _, err_ws = run_git(["diff", "--check"], cwd=repo_root)
    if code_ws != 0:
        return False, f"Whitespace errors detected: {err_ws}"

    code_st, out_st, _ = run_git(["status", "--porcelain", "-uall"], cwd=repo_root)
    tracked_mods = [line for line in out_st.splitlines() if line and not line.startswith("??")]
    if tracked_mods:
        return False, "Uncommitted tracked changes detected:\n" + "\n".join(tracked_mods[:5])

    if tag:
        target_prefix = f"docs/evidence/releases/{tag}/"
        untracked = [
            line[3:].strip()
            for line in out_st.splitlines()
            if line.startswith("?? ") and line[3:].strip().startswith(target_prefix)
        ]
        if untracked:
            return False, (
                f"Untracked release evidence detected for {tag}:\n"
                + "\n".join(untracked[:5])
                + "\nRelease evidence must be committed into git before preflight."
            )

    return True, "Working tree clean."


def run_tag_preflight(
    tag: str,
    release_commit: str,
    repo: str = "LightDevCoder/skills",
    pattern: str = "refs/tags/v*",
    fixture: str | None = None,
    check_remote_tag: bool = True,
    skip_remote: bool = False,
    repo_root: Path = REPO_ROOT,
) -> PreflightResult:
    """Execute all tag preflight gates."""
    if skip_remote:
        check_remote_tag = False

    # 1. Candidate commit exists
    cand_sha = resolve_commit_sha(release_commit, cwd=repo_root)
    if not cand_sha:
        return PreflightResult(
            passed=False,
            status="BLOCKED",
            message=f"Release candidate commit '{release_commit}' cannot be resolved to a 40-character commit SHA.",
        )

    # 2. Working tree clean (including absence of untracked release evidence)
    tree_ok, tree_msg = check_working_tree(repo_root, tag=tag)
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
    local_ident = resolve_annotated_tag_identity(tag, cwd=repo_root)
    if local_ident.tag_type:
        return PreflightResult(
            passed=False,
            status="BLOCKED",
            message=(
                f"Local tag '{tag}' already exists pointing to {local_ident.peeled_commit_sha}. "
                "Release tags must not exist prior to creation."
            ),
        )

    # 5. Remote tag existence check (default enabled)
    if check_remote_tag:
        remote_res = resolve_remote_tag(tag, remote="origin", cwd=repo_root)
        if remote_res.status == RemoteTagStatus.QUERY_FAILED:
            return PreflightResult(
                passed=False,
                status="BLOCKED",
                message=f"Could not verify remote tag state on origin: {remote_res.error}",
            )
        elif remote_res.status == RemoteTagStatus.EXISTS:
            return PreflightResult(
                passed=False,
                status="BLOCKED",
                message=(
                    f"Remote tag '{tag}' already exists on origin pointing to {remote_res.peeled_commit_sha}. "
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
    parser.add_argument("--skip-remote", action="store_true", help="Skip remote tag existence check (default: remote check enabled).")
    parser.add_argument("--check-remote", action="store_true", help="Deprecated: remote tag check is enabled by default.")
    parser.add_argument("--root", default=None, help="Repository root path.")

    args = parser.parse_args()
    repo_root = Path(args.root).resolve() if args.root else REPO_ROOT
    check_remote = not args.skip_remote

    print(f"=== Release Tag Preflight Guard ===")
    print(f"Target Tag:     {args.tag}")
    print(f"Release Commit: {args.release_commit}")
    print(f"Repository:     {repo_root}")
    print(f"Remote Check:   {'ENABLED' if check_remote else 'SKIPPED'}")
    print("-----------------------------------")

    result = run_tag_preflight(
        tag=args.tag,
        release_commit=args.release_commit,
        repo=args.repo,
        pattern=args.pattern,
        fixture=args.fixture,
        check_remote_tag=check_remote,
        skip_remote=args.skip_remote,
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
