#!/usr/bin/env python3
"""Release Integrity Verification Guard.

Enforces release integrity and tag immutability:
1. Tag Immutability & Idempotency:
   - Tag does not exist: PASS (ready for creation).
   - Tag exists with SAME target commit: IDEMPOTENT PASS (safe for CI retry).
   - Tag exists with DIFFERENT target commit: HARD FAIL (blocks tag force-move/retargeting).
2. Mechanical Release Metadata Consistency:
   - Validates existence and format of docs/evidence/releases/<tag>/RELEASE_RECEIPT.md.
   - Validates package count against actual admitted packages (skills/*/*/SKILL.md).
   - Validates tag name consistency across release evidence files.
3. Working Tree Cleanliness:
   - Ensures no whitespace violations or uncommitted tracked changes before tagging.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent


class VerificationResult(NamedTuple):
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


def resolve_tag_sha(tag: str, cwd: Path = REPO_ROOT) -> str | None:
    """Resolve an existing tag to its underlying peeled commit SHA."""
    # First check if tag exists locally
    code, out, _ = run_git(["tag", "-l", tag], cwd=cwd)
    if code == 0 and out == tag:
        # Peel annotated tag to underlying commit
        code_peel, out_peel, _ = run_git(["rev-parse", f"{tag}^{{commit}}"], cwd=cwd)
        if code_peel == 0 and len(out_peel) == 40:
            return out_peel
    return None


def resolve_remote_tag_sha(tag: str, remote: str = "origin", cwd: Path = REPO_ROOT) -> str | None:
    """Query remote for tag commit SHA."""
    code, out, _ = run_git(["ls-remote", "--tags", remote, f"refs/tags/{tag}"], cwd=cwd)
    if code != 0 or not out:
        return None
    # ls-remote output lines: <sha>\trefs/tags/<tag> or <sha>\trefs/tags/<tag>^{}
    # If peeled ref exists, prefer it
    lines = out.splitlines()
    peeled = [l.split()[0] for l in lines if l.endswith("^{}")]
    if peeled:
        return peeled[0]
    unpeeled = [l.split()[0] for l in lines if f"refs/tags/{tag}" in l]
    if unpeeled:
        return unpeeled[0]
    return None


def get_admitted_package_count(repo_root: Path = REPO_ROOT) -> int:
    """Count admitted packages with SKILL.md under skills/*/*."""
    skill_files = list(repo_root.glob("skills/*/*/SKILL.md"))
    return len(skill_files)


def check_tag_immutability(
    tag: str,
    target_commit_ref: str = "HEAD",
    check_remote: bool = False,
    cwd: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify tag immutability: idempotent pass if target matches, fail if different."""
    target_sha = resolve_commit_sha(target_commit_ref, cwd=cwd)
    if not target_sha:
        return VerificationResult(
            passed=False,
            status="ERROR",
            message=f"Target commit reference '{target_commit_ref}' could not be resolved to a 40-character SHA.",
        )

    # 1. Check local tag
    local_tag_sha = resolve_tag_sha(tag, cwd=cwd)
    if local_tag_sha:
        if local_tag_sha == target_sha:
            return VerificationResult(
                passed=True,
                status="IDEMPOTENT_PASS",
                message=f"Local tag '{tag}' already exists pointing to target commit {target_sha}. Safe for CI retry.",
            )
        else:
            return VerificationResult(
                passed=False,
                status="HARD_FAIL",
                message=(
                    f"Tag immutability violation! Local tag '{tag}' points to {local_tag_sha}, "
                    f"which differs from target commit {target_sha}. Tag retargeting/force-moving is strictly forbidden."
                ),
            )

    # 2. Check remote tag if requested
    if check_remote:
        remote_tag_sha = resolve_remote_tag_sha(tag, cwd=cwd)
        if remote_tag_sha:
            if remote_tag_sha == target_sha:
                return VerificationResult(
                    passed=True,
                    status="IDEMPOTENT_PASS",
                    message=f"Remote tag '{tag}' already exists pointing to target commit {target_sha}. Safe for CI retry.",
                )
            else:
                return VerificationResult(
                    passed=False,
                    status="HARD_FAIL",
                    message=(
                        f"Tag immutability violation! Remote tag '{tag}' points to {remote_tag_sha}, "
                        f"which differs from target commit {target_sha}. Tag retargeting/force-moving is strictly forbidden."
                    ),
                )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Tag '{tag}' does not exist yet. Ready for creation on target commit {target_sha}.",
    )


def check_release_manifest_consistency(tag: str, repo_root: Path = REPO_ROOT) -> VerificationResult:
    """Verify mechanical consistency of release manifest for v0.2.3+."""
    # Manifest architecture introduced in v0.2.3
    # Check if this tag version is < v0.2.3
    version_match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if version_match:
        major, minor, patch = map(int, version_match.groups())
        if (major, minor, patch) < (0, 2, 3):
            return VerificationResult(
                passed=True,
                status="SKIPPED_HISTORICAL",
                message=f"Release {tag} precedes immutable manifest architecture (introduced in v0.2.3).",
            )

    evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
    manifest_en = evidence_dir / "RELEASE_MANIFEST.md"
    manifest_zh = evidence_dir / "RELEASE_MANIFEST.zh-CN.md"

    if not manifest_en.is_file():
        return VerificationResult(
            passed=False,
            status="MANIFEST_MISSING",
            message=f"English release manifest missing at {manifest_en.relative_to(repo_root)}",
        )

    if not manifest_zh.is_file():
        return VerificationResult(
            passed=False,
            status="MANIFEST_MISSING",
            message=f"Chinese release manifest missing at {manifest_zh.relative_to(repo_root)}",
        )

    text_en = manifest_en.read_text(encoding="utf-8")
    text_zh = manifest_zh.read_text(encoding="utf-8")
    actual_pkg_count = get_admitted_package_count(repo_root)

    # Verify release identifier appears in manifest
    if tag not in text_en or tag not in text_zh:
        return VerificationResult(
            passed=False,
            status="METADATA_MISMATCH",
            message=f"Tag '{tag}' not found in manifest files at {evidence_dir.relative_to(repo_root)}",
        )

    # Verify admitted package count matches
    pkg_pattern = re.compile(r"(\d+)\s+admitted\s+packages", re.IGNORECASE)
    match = pkg_pattern.search(text_en)
    if match:
        claimed_count = int(match.group(1))
        if claimed_count != actual_pkg_count:
            return VerificationResult(
                passed=False,
                status="COUNT_MISMATCH",
                message=(
                    f"Package count mismatch in {manifest_en.relative_to(repo_root)}: "
                    f"manifest claims {claimed_count}, but repository has {actual_pkg_count} admitted packages."
                ),
            )

    # Verify expected tag / release identity ref
    if f"refs/tags/{tag}" not in text_en and tag not in text_en:
        return VerificationResult(
            passed=False,
            status="METADATA_MISMATCH",
            message=f"Expected tag reference for '{tag}' not found in {manifest_en.relative_to(repo_root)}",
        )

    # Verify policy status
    if "Policy status" not in text_en and "Policy Status" not in text_en:
        return VerificationResult(
            passed=False,
            status="POLICY_STATUS_MISSING",
            message=f"Policy status field missing in {manifest_en.relative_to(repo_root)}",
        )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release manifest for {tag} verified: valid dual manifests, verified {actual_pkg_count} packages, and policy status confirmed.",
    )


def check_release_receipt_consistency(tag: str, repo_root: Path = REPO_ROOT) -> VerificationResult:
    """Verify mechanical consistency of release receipt and evidence files."""
    evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
    receipt_en = evidence_dir / "RELEASE_RECEIPT.md"
    receipt_zh = evidence_dir / "RELEASE_RECEIPT.zh-CN.md"

    if not receipt_en.is_file():
        return VerificationResult(
            passed=False,
            status="RECEIPT_MISSING",
            message=f"English release receipt missing at {receipt_en.relative_to(repo_root)}",
        )

    if not receipt_zh.is_file():
        return VerificationResult(
            passed=False,
            status="RECEIPT_MISSING",
            message=f"Chinese release receipt missing at {receipt_zh.relative_to(repo_root)}",
        )

    text_en = receipt_en.read_text(encoding="utf-8")
    actual_pkg_count = get_admitted_package_count(repo_root)

    # Verify release identifier appears in receipt
    if tag not in text_en:
        return VerificationResult(
            passed=False,
            status="METADATA_MISMATCH",
            message=f"Tag '{tag}' not found in {receipt_en.relative_to(repo_root)}",
        )

    # Verify admitted package count matches
    pkg_pattern = re.compile(r"(\d+)\s+admitted\s+packages", re.IGNORECASE)
    match = pkg_pattern.search(text_en)
    if match:
        claimed_count = int(match.group(1))
        if claimed_count != actual_pkg_count:
            return VerificationResult(
                passed=False,
                status="COUNT_MISMATCH",
                message=(
                    f"Package count mismatch in {receipt_en.relative_to(repo_root)}: "
                    f"receipt claims {claimed_count}, but repository has {actual_pkg_count} admitted packages."
                ),
            )

    # If post-publication receipt specifies an exact tag target commit, verify against local tag if present
    target_match = re.search(r"Tag target commit\s*\|\s*`?([0-9a-f]{40})`?", text_en, re.IGNORECASE)
    if target_match:
        receipt_target_sha = target_match.group(1)
        local_tag_sha = resolve_tag_sha(tag, cwd=repo_root)
        if local_tag_sha and local_tag_sha != receipt_target_sha:
            return VerificationResult(
                passed=False,
                status="RECEIPT_TARGET_MISMATCH",
                message=(
                    f"Receipt target commit {receipt_target_sha} does not match local tag {tag} target commit {local_tag_sha}."
                ),
            )

    # Verify release URL format if present
    url_match = re.search(r"https://github\.com/LightDevCoder/skills/releases/tag/([^\s\)\`\|]+)", text_en)
    if url_match:
        url_tag = url_match.group(1)
        if url_tag != tag:
            return VerificationResult(
                passed=False,
                status="RECEIPT_URL_MISMATCH",
                message=f"Release URL tag '{url_tag}' does not match release tag '{tag}'.",
            )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release receipt for {tag} verified: valid dual receipts and verified {actual_pkg_count} packages.",
    )


def check_working_tree(repo_root: Path = REPO_ROOT) -> VerificationResult:
    """Verify git diff and whitespace cleanliness."""
    code_ws, _, err_ws = run_git(["diff", "--check"], cwd=repo_root)
    if code_ws != 0:
        return VerificationResult(
            passed=False,
            status="WHITESPACE_ERROR",
            message=f"Whitespace errors detected: {err_ws}",
        )

    code_st, out_st, _ = run_git(["status", "--porcelain"], cwd=repo_root)
    # Check tracked modifications (ignore untracked files like .scratch/)
    tracked_mods = [line for line in out_st.splitlines() if line and not line.startswith("??")]
    if tracked_mods:
        return VerificationResult(
            passed=False,
            status="DIRTY_TREE",
            message=f"Uncommitted tracked changes detected:\n" + "\n".join(tracked_mods[:5]),
        )

    return VerificationResult(
        passed=True,
        status="PASS",
        message="Working tree clean: zero whitespace errors, zero uncommitted tracked changes.",
    )


def detect_candidate_tag(repo_root: Path = REPO_ROOT) -> str:
    """Infer candidate tag from releases evidence directory or CHANGELOG.md."""
    releases_dir = repo_root / "docs" / "evidence" / "releases"
    if releases_dir.is_dir():
        versions = sorted(
            [d.name for d in releases_dir.iterdir() if d.is_dir() and d.name.startswith("v")],
            key=lambda v: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", v)],
        )
        if versions:
            return versions[-1]
    return "v0.2.2"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release integrity and tag immutability.")
    parser.add_argument("--tag", help="Release tag to verify (e.g. v0.2.2). Default: latest candidate tag.")
    parser.add_argument("--commit", default="HEAD", help="Target commit ref (default: HEAD).")
    parser.add_argument("--check-remote", action="store_true", help="Also query git remote for tag status.")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow uncommitted tracked changes.")

    args = parser.parse_args()
    tag = args.tag or detect_candidate_tag(REPO_ROOT)
    commit = args.commit

    print(f"=== Release Integrity Guard ===")
    print(f"Target Tag:    {tag}")
    print(f"Target Commit: {commit}")
    print(f"Repository:    {REPO_ROOT}")
    print("--------------------------------")

    all_passed = True

    # 1. Working tree check
    if not args.allow_dirty:
        res_tree = check_working_tree(REPO_ROOT)
        print(f"[{res_tree.status}] Working Tree: {res_tree.message}")
        if not res_tree.passed:
            all_passed = False
    else:
        print("[SKIPPED] Working Tree check bypassed via --allow-dirty.")

    # 2. Tag immutability & idempotency check
    res_tag = check_tag_immutability(tag, commit, check_remote=args.check_remote, cwd=REPO_ROOT)
    print(f"[{res_tag.status}] Tag Immutability: {res_tag.message}")
    if not res_tag.passed:
        all_passed = False

    # 3. Release manifest consistency check
    res_manifest = check_release_manifest_consistency(tag, repo_root=REPO_ROOT)
    print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
    if not res_manifest.passed:
        all_passed = False

    # 4. Release receipt consistency check
    res_receipt = check_release_receipt_consistency(tag, repo_root=REPO_ROOT)
    print(f"[{res_receipt.status}] Receipt Consistency: {res_receipt.message}")
    if not res_receipt.passed:
        all_passed = False

    print("--------------------------------")
    if all_passed:
        print("RESULT: PASS — Release integrity verified.")
        return 0
    else:
        print("RESULT: FAIL — Release integrity violation detected.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
