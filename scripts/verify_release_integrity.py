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
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ensure scripts dir is on sys.path for sibling imports
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_release_tag_preflight import (
    AnnotatedTagIdentity,
    RemoteTagResult,
    RemoteTagStatus,
    resolve_annotated_tag_identity,
    resolve_remote_tag,
)


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


def git_path_exists(revision: str, path: str, cwd: Path = REPO_ROOT) -> bool:
    """Check if path exists in git revision."""
    code, _, _ = run_git(["cat-file", "-e", f"{revision}:{path}"], cwd=cwd)
    return code == 0


def git_read_text(revision: str, path: str, cwd: Path = REPO_ROOT) -> str | None:
    """Read file content as text from git revision."""
    code, out, _ = run_git(["cat-file", "-p", f"{revision}:{path}"], cwd=cwd)
    if code == 0:
        return out
    return None


def resolve_commit_sha(commit_ref: str, cwd: Path = REPO_ROOT) -> str | None:
    """Resolve a commit reference to its full 40-character SHA."""
    code, out, _ = run_git(["rev-parse", f"{commit_ref}^{{commit}}"], cwd=cwd)
    if code == 0 and len(out) == 40:
        return out
    return None


def resolve_tag_object_sha(tag: str, cwd: Path = REPO_ROOT) -> str | None:
    """Resolve an annotated tag to its underlying tag object SHA."""
    ident = resolve_annotated_tag_identity(tag, cwd=cwd)
    if ident.is_annotated:
        return ident.tag_object_sha
    return None


def resolve_tag_sha(tag: str, cwd: Path = REPO_ROOT) -> str | None:
    """Resolve an existing tag to its underlying peeled commit SHA."""
    ident = resolve_annotated_tag_identity(tag, cwd=cwd)
    if ident.tag_type:
        return ident.peeled_commit_sha
    return None


def resolve_remote_tag_sha(tag: str, remote: str = "origin", cwd: Path = REPO_ROOT) -> str | None:
    """Query remote for tag peeled commit SHA."""
    res = resolve_remote_tag(tag, remote=remote, cwd=cwd)
    if res.status == RemoteTagStatus.EXISTS:
        return res.peeled_commit_sha
    return None


def get_admitted_package_count(repo_root: Path = REPO_ROOT, revision: str | None = None) -> int:
    """Count admitted packages with SKILL.md under skills/*/*."""
    if revision:
        code, out, _ = run_git(["ls-tree", "-r", "--name-only", revision, "skills"], cwd=repo_root)
        if code == 0:
            count = 0
            pattern = re.compile(r"^skills/[^/]+/[^/]+/SKILL\.md$")
            for line in out.splitlines():
                if pattern.match(line.strip()):
                    count += 1
            return count
    skill_files = list(repo_root.glob("skills/*/*/SKILL.md"))
    return len(skill_files)


def check_tag_immutability(
    tag: str,
    target_commit_ref: str = "HEAD",
    check_remote: bool = False,
    stage: str = "auto",
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
    tag_ident = resolve_annotated_tag_identity(tag, cwd=cwd)
    remote_res = resolve_remote_tag(tag, remote="origin", cwd=cwd) if check_remote else None
    if remote_res is not None:
        if remote_res.status == RemoteTagStatus.QUERY_FAILED:
            return VerificationResult(False, "QUERY_FAILED", f"Could not verify remote tag state for '{tag}': {remote_res.error}")
        if stage in ("prepared", "candidate") and remote_res.status != RemoteTagStatus.ABSENT:
            return VerificationResult(False, "REMOTE_TAG_EXISTS", f"Candidate tag '{tag}' already exists on origin.")
        if stage in ("tagged", "attested") and remote_res.status != RemoteTagStatus.EXISTS:
            return VerificationResult(False, "REMOTE_TAG_MISSING", f"Published tag '{tag}' is missing on origin.")
        if remote_res.status == RemoteTagStatus.EXISTS:
            if not remote_res.is_annotated:
                return VerificationResult(False, "LIGHTWEIGHT_TAG_FORBIDDEN", f"Remote tag '{tag}' is not annotated.")
            if remote_res.peeled_commit_sha != target_sha:
                return VerificationResult(False, "HARD_FAIL", f"Remote tag '{tag}' targets {remote_res.peeled_commit_sha}, not {target_sha}.")
            if tag_ident.tag_type and remote_res.tag_object_sha != tag_ident.tag_object_sha:
                return VerificationResult(False, "HARD_FAIL", f"Remote tag object for '{tag}' differs from the local annotated tag.")
    if tag_ident.tag_type:
        # For tagged and attested stages, release tags MUST be annotated
        if stage in ("tagged", "attested") and not tag_ident.is_annotated:
            return VerificationResult(
                passed=False,
                status="LIGHTWEIGHT_TAG_FORBIDDEN",
                message=(
                    f"Tag '{tag}' is not an annotated tag (git cat-file -t returned '{tag_ident.tag_type}'). "
                    "Lightweight tags are strictly forbidden for release tags; tags must be created with 'git tag -a'."
                ),
            )

        local_tag_sha = tag_ident.peeled_commit_sha
        if local_tag_sha == target_sha:
            return VerificationResult(
                passed=True,
                status="IDEMPOTENT_PASS",
                message=f"Local tag '{tag}' already exists pointing to candidate commit {target_sha}. Safe for CI retry.",
            )
        else:
            return VerificationResult(
                passed=False,
                status="HARD_FAIL",
                message=(
                    f"Tag immutability violation! Local tag '{tag}' points to {local_tag_sha}, "
                    f"which differs from candidate commit {target_sha}. Tag retargeting/force-moving is strictly forbidden."
                ),
            )

    if stage in ("tagged", "attested"):
        return VerificationResult(
            passed=False,
            status="TAG_MISSING",
            message=f"Tag '{tag}' does not exist locally, but is required for stage '{stage}'.",
        )

    if remote_res is not None and remote_res.status == RemoteTagStatus.EXISTS:
        return VerificationResult(True, "IDEMPOTENT_PASS", f"Remote annotated tag '{tag}' matches candidate commit {target_sha} and local tag object.")

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Tag '{tag}' does not exist yet. Ready for creation on candidate commit {target_sha}.",
    )


def check_release_manifest_consistency(
    tag: str,
    revision: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> VerificationResult:
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

    rel_manifest_en = f"docs/evidence/releases/{tag}/RELEASE_MANIFEST.md"
    rel_manifest_zh = f"docs/evidence/releases/{tag}/RELEASE_MANIFEST.zh-CN.md"

    if revision:
        if not git_path_exists(revision, rel_manifest_en, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="MANIFEST_MISSING",
                message=f"English release manifest missing in git revision '{revision}' at {rel_manifest_en}",
            )
        if not git_path_exists(revision, rel_manifest_zh, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="MANIFEST_MISSING",
                message=f"Chinese release manifest missing in git revision '{revision}' at {rel_manifest_zh}",
            )
        text_en = git_read_text(revision, rel_manifest_en, cwd=repo_root) or ""
        text_zh = git_read_text(revision, rel_manifest_zh, cwd=repo_root) or ""
        actual_pkg_count = get_admitted_package_count(repo_root, revision=revision)
    else:
        evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
        manifest_en = evidence_dir / "RELEASE_MANIFEST.md"
        manifest_zh = evidence_dir / "RELEASE_MANIFEST.zh-CN.md"

        if not manifest_en.is_file():
            return VerificationResult(
                passed=False,
                status="MANIFEST_MISSING",
                message=f"English release manifest missing at {rel_manifest_en}",
            )
        if not manifest_zh.is_file():
            return VerificationResult(
                passed=False,
                status="MANIFEST_MISSING",
                message=f"Chinese release manifest missing at {rel_manifest_zh}",
            )
        text_en = manifest_en.read_text(encoding="utf-8")
        text_zh = manifest_zh.read_text(encoding="utf-8")
        actual_pkg_count = get_admitted_package_count(repo_root)

    # Verify release identifier appears in manifest
    if tag not in text_en or tag not in text_zh:
        return VerificationResult(
            passed=False,
            status="METADATA_MISMATCH",
            message=f"Tag '{tag}' not found in manifest files for {tag}",
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
                    f"Package count mismatch in {rel_manifest_en}: "
                    f"manifest claims {claimed_count}, but repository has {actual_pkg_count} admitted packages."
                ),
            )

    # Verify expected tag / release identity ref
    if f"refs/tags/{tag}" not in text_en and tag not in text_en:
        return VerificationResult(
            passed=False,
            status="METADATA_MISMATCH",
            message=f"Expected tag reference for '{tag}' not found in {rel_manifest_en}",
        )

    # Verify policy status
    if "Policy status" not in text_en and "Policy Status" not in text_en:
        return VerificationResult(
            passed=False,
            status="POLICY_STATUS_MISSING",
            message=f"Policy status field missing in {rel_manifest_en}",
        )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release manifest for {tag} verified: valid dual manifests, verified {actual_pkg_count} packages, and policy status confirmed.",
    )


def check_github_release_navigation(
    tag: str,
    repo: str = "LightDevCoder/skills",
    cwd: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify that published GitHub Release body does not contain bare relative links that 404."""
    version_match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if version_match:
        major, minor, patch = map(int, version_match.groups())
        if (major, minor, patch) <= (0, 2, 2):
            return VerificationResult(
                passed=True,
                status="SKIPPED_HISTORICAL",
                message=f"Release {tag} precedes release body link verification.",
            )

    proc = subprocess.run(
        ["gh", "release", "view", tag, "--repo", repo, "--json", "body"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        return VerificationResult(
            passed=False,
            status="REMOTE_RELEASE_UNAVAILABLE",
            message=f"Could not query GitHub Release body via gh CLI ({proc.stderr.strip() or 'gh unavailable'}).",
        )

    try:
        data = json.loads(proc.stdout)
        body = data.get("body", "")
    except Exception as e:
        return VerificationResult(
            passed=False,
            status="RELEASE_BODY_ERROR",
            message=f"Failed to parse GitHub Release body JSON: {e}",
        )

    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    bare_links = []
    for match in pattern.finditer(body):
        label = match.group(1)
        target = match.group(2).strip()
        if re.match(r"^(?:https?://|mailto:|#)", target, re.IGNORECASE):
            continue
        bare_links.append(f"[{label}]({target})")

    if bare_links:
        return VerificationResult(
            passed=False,
            status="RELEASE_BODY_RELATIVE_LINK_FORBIDDEN",
            message=(
                f"GitHub Release body for '{tag}' contains bare relative link(s): {', '.join(bare_links)}. "
                "GitHub Releases evaluates relative links against repository root, causing 404 Not Found. "
                "All release body navigation links must use full repository URLs."
            ),
        )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"GitHub Release body for {tag} verified: all navigation links use full repository URLs.",
    )


def check_manifest_navigation(
    tag: str,
    revision: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify that release manifest does not contain relative links to candidate receipts (v0.2.4+)."""
    # Historical tags through v0.2.3 are preserved as immutable legacy artifacts
    version_match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if version_match:
        major, minor, patch = map(int, version_match.groups())
        if (major, minor, patch) <= (0, 2, 3):
            return VerificationResult(
                passed=True,
                status="SKIPPED_HISTORICAL",
                message=f"Release {tag} is a known legacy lifecycle artifact with historical manifest navigation.",
            )

    manifest_names = ["RELEASE_MANIFEST.md", "RELEASE_MANIFEST.zh-CN.md"]
    for manifest_name in manifest_names:
        rel_path = f"docs/evidence/releases/{tag}/{manifest_name}"
        if revision:
            if git_path_exists(revision, rel_path, cwd=repo_root):
                text = git_read_text(revision, rel_path, cwd=repo_root) or ""
                if re.search(r"\[[^\]]+\]\(\s*RELEASE_RECEIPT(?:\.zh-CN)?\.md\s*\)", text):
                    return VerificationResult(
                        passed=False,
                        status="RELATIVE_RECEIPT_LINK_FORBIDDEN",
                        message=(
                            f"Manifest in revision '{revision}' at {rel_path} contains a relative link to RELEASE_RECEIPT.md. "
                            "Manifest must not navigate to candidate receipts in immutable tags; "
                            "post-publication attestation lives on main."
                        ),
                    )
        else:
            p = repo_root / rel_path
            if p.is_file():
                text = p.read_text(encoding="utf-8")
                if re.search(r"\[[^\]]+\]\(\s*RELEASE_RECEIPT(?:\.zh-CN)?\.md\s*\)", text):
                    return VerificationResult(
                        passed=False,
                        status="RELATIVE_RECEIPT_LINK_FORBIDDEN",
                        message=(
                            f"Manifest {rel_path} contains a relative link to RELEASE_RECEIPT.md. "
                            "Manifest must not navigate to candidate receipts in immutable tags; "
                            "post-publication attestation lives on main."
                        ),
                    )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Manifest navigation for {tag} verified: no relative links to post-publication receipts.",
    )


def check_release_notes_consistency(
    tag: str,
    revision: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify dual release notes exist."""
    rel_notes_en = f"docs/evidence/releases/{tag}/RELEASE_NOTES.md"
    rel_notes_zh = f"docs/evidence/releases/{tag}/RELEASE_NOTES.zh-CN.md"

    if revision:
        if not git_path_exists(revision, rel_notes_en, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="NOTES_MISSING",
                message=f"English release notes missing in git revision '{revision}' at {rel_notes_en}",
            )
        if not git_path_exists(revision, rel_notes_zh, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="NOTES_MISSING",
                message=f"Chinese release notes missing in git revision '{revision}' at {rel_notes_zh}",
            )
    else:
        notes_en = repo_root / rel_notes_en
        notes_zh = repo_root / rel_notes_zh
        if not notes_en.is_file():
            return VerificationResult(
                passed=False,
                status="NOTES_MISSING",
                message=f"English release notes missing at {rel_notes_en}",
            )
        if not notes_zh.is_file():
            return VerificationResult(
                passed=False,
                status="NOTES_MISSING",
                message=f"Chinese release notes missing at {rel_notes_zh}",
            )
    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release notes for {tag} verified.",
    )


def check_receipt_absence_in_candidate(
    tag: str,
    revision: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify that candidate/pre-tag directories and git trees do not contain pre-publication candidate receipts (v0.2.4+)."""
    version_match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if version_match:
        major, minor, patch = map(int, version_match.groups())
        if (major, minor, patch) <= (0, 2, 3):
            return VerificationResult(
                passed=True,
                status="SKIPPED_HISTORICAL",
                message=f"Release {tag} is a known legacy lifecycle artifact.",
            )

    rel_receipt_en = f"docs/evidence/releases/{tag}/RELEASE_RECEIPT.md"
    rel_receipt_zh = f"docs/evidence/releases/{tag}/RELEASE_RECEIPT.zh-CN.md"

    # Check git revision tree if specified
    if revision:
        if git_path_exists(revision, rel_receipt_en, cwd=repo_root) or git_path_exists(revision, rel_receipt_zh, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="CANDIDATE_RECEIPT_FORBIDDEN",
                message=(
                    f"Git revision '{revision}' contains premature release receipt(s) at docs/evidence/releases/{tag}. "
                    "Receipts may only be created on main during stage ATTESTED following publication."
                ),
            )
        return VerificationResult(
            passed=True,
            status="PASS",
            message=f"No premature candidate receipts found in revision '{revision}' for {tag}.",
        )

    # Check filesystem ONLY if revision is None
    receipt_en = repo_root / rel_receipt_en
    receipt_zh = repo_root / rel_receipt_zh
    if receipt_en.is_file() or receipt_zh.is_file():
        return VerificationResult(
            passed=False,
            status="CANDIDATE_RECEIPT_FORBIDDEN",
            message=(
                f"Candidate release directory docs/evidence/releases/{tag} contains pre-publication receipt(s). "
                "Receipts may only be created on main during stage ATTESTED following publication."
            ),
        )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"No premature candidate receipts found for {tag}.",
    )


def check_public_candidate_docs(repo_root: Path = REPO_ROOT) -> VerificationResult:
    """Verify that public documentation is internally consistent during candidate stages."""
    if (repo_root / "CATALOG.md").is_file() and (repo_root / "README.md").is_file():
        scripts_dir = repo_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        try:
            import check_public_docs
            res = check_public_docs.run_checks(repo_root)
            if not res.passed:
                return VerificationResult(
                    passed=False,
                    status="PUBLIC_DOCS_INCONSISTENT",
                    message="Public candidate docs inconsistent: " + "; ".join(res.errors[:3]),
                )
        except Exception as e:
            return VerificationResult(
                passed=False,
                status="PUBLIC_DOCS_ERROR",
                message=f"Error executing public documentation checks: {e}",
            )
    return VerificationResult(
        passed=True,
        status="PASS",
        message="Public candidate docs internally consistent.",
    )


def extract_checklist_status(text: str, gate_label: str) -> str | None:
    """Extract gate status from a markdown table row: | **Gate** | `Status` | ... |."""
    pattern = re.compile(
        r"\|\s*(?:\*\*)?" + re.escape(gate_label) + r"(?:\*\*)?[^\|]*\|\s*`?([A-Z_]+)`?\s*\|",
        re.IGNORECASE,
    )
    m = pattern.search(text)
    if m:
        return m.group(1).upper()
    return None


def check_release_receipt_consistency(
    tag: str,
    release_commit: str | None = None,
    receipt_revision: str | None = None,
    release_revision: str | None = None,
    revision: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify mechanical consistency of release receipt and evidence files."""
    # Backwards compatibility: if receipt_revision is None and revision is provided
    if receipt_revision is None and revision is not None:
        receipt_revision = revision

    # Release scope authority: release_revision defaults to release_commit or tag snapshot
    if release_revision is None:
        if release_commit:
            release_revision = release_commit
        else:
            tag_peel = resolve_tag_sha(tag, cwd=repo_root)
            if tag_peel:
                release_revision = f"refs/tags/{tag}"

    # Canonical relative paths for deterministic diagnostics
    rel_evidence_dir = f"docs/evidence/releases/{tag}"
    rel_receipt_en = f"docs/evidence/releases/{tag}/RELEASE_RECEIPT.md"
    rel_receipt_zh = f"docs/evidence/releases/{tag}/RELEASE_RECEIPT.zh-CN.md"

    # Release receipts must only attest real annotated tags (fail closed on lightweight tags)
    tag_ident = resolve_annotated_tag_identity(tag, cwd=repo_root)
    if tag_ident.tag_type:
        if not tag_ident.is_annotated or tag_ident.tag_type != "tag":
            return VerificationResult(
                passed=False,
                status="RELEASE_TAG_NOT_ANNOTATED",
                message=(
                    f"Release tag '{tag}' is not an annotated tag (git cat-file -t returned '{tag_ident.tag_type}'). "
                    "Release receipts may only attest annotated release tags."
                ),
            )

    if receipt_revision:
        if not git_path_exists(receipt_revision, rel_receipt_en, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="RECEIPT_MISSING",
                message=f"English release receipt missing in git revision '{receipt_revision}' at {rel_receipt_en}",
            )
        if not git_path_exists(receipt_revision, rel_receipt_zh, cwd=repo_root):
            return VerificationResult(
                passed=False,
                status="RECEIPT_MISSING",
                message=f"Chinese release receipt missing in git revision '{receipt_revision}' at {rel_receipt_zh}",
            )
        text_en = git_read_text(receipt_revision, rel_receipt_en, cwd=repo_root) or ""
        text_zh = git_read_text(receipt_revision, rel_receipt_zh, cwd=repo_root) or ""
    else:
        receipt_en_path = repo_root / rel_receipt_en
        receipt_zh_path = repo_root / rel_receipt_zh

        if not receipt_en_path.is_file():
            return VerificationResult(
                passed=False,
                status="RECEIPT_MISSING",
                message=f"English release receipt missing at {rel_receipt_en}",
            )

        if not receipt_zh_path.is_file():
            return VerificationResult(
                passed=False,
                status="RECEIPT_MISSING",
                message=f"Chinese release receipt missing at {rel_receipt_zh}",
            )

        text_en = receipt_en_path.read_text(encoding="utf-8")
        text_zh = receipt_zh_path.read_text(encoding="utf-8")

    # Package count authority comes strictly from release_revision (the immutable release snapshot)
    if release_revision:
        actual_pkg_count = get_admitted_package_count(repo_root, revision=release_revision)
    else:
        actual_pkg_count = get_admitted_package_count(repo_root)

    # Legacy policy check: <= v0.2.3 uses historical format
    version_match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if version_match:
        version_tuple = (int(version_match.group(1)), int(version_match.group(2)), int(version_match.group(3)))
    else:
        version_tuple = (999, 999, 999)
    is_legacy = version_tuple <= (0, 2, 3)

    # 1. Verify release identifier appears in both receipts
    if tag not in text_en or tag not in text_zh:
        return VerificationResult(
            passed=False,
            status="METADATA_MISMATCH",
            message=f"Tag '{tag}' not found in release receipts under {rel_evidence_dir}",
        )

    # 2. Verify admitted package count matches
    pkg_pattern_en = re.compile(r"(\d+)\s+admitted\s+packages", re.IGNORECASE)
    match_en = pkg_pattern_en.search(text_en)
    if match_en:
        claimed_count = int(match_en.group(1))
        if claimed_count != actual_pkg_count:
            return VerificationResult(
                passed=False,
                status="COUNT_MISMATCH",
                message=(
                    f"Package count mismatch in {rel_receipt_en}: "
                    f"receipt claims {claimed_count}, but release snapshot has {actual_pkg_count} admitted packages."
                ),
            )
    elif not is_legacy:
        return VerificationResult(
            passed=False,
            status="COUNT_MISMATCH",
            message=f"Collection package count field missing in {rel_receipt_en}",
        )

    pkg_pattern_zh = re.compile(r"(\d+)\s*(?:admitted\s+packages|个(?:已准入)?包)", re.IGNORECASE)
    match_zh = pkg_pattern_zh.search(text_zh)
    if match_zh:
        claimed_count_zh = int(match_zh.group(1))
        if claimed_count_zh != actual_pkg_count:
            return VerificationResult(
                passed=False,
                status="COUNT_MISMATCH",
                message=(
                    f"Package count mismatch in {rel_receipt_zh}: "
                    f"receipt claims {claimed_count_zh}, but release snapshot has {actual_pkg_count} admitted packages."
                ),
            )
    elif not is_legacy:
        return VerificationResult(
            passed=False,
            status="COUNT_MISMATCH",
            message=f"Collection package count field missing in {rel_receipt_zh}",
        )

    # 3. Check tag target commit against local tag and supplied release commit
    target_match = re.search(r"Tag target commit\s*\|\s*`?([0-9a-f]{40})`?", text_en, re.IGNORECASE)
    if target_match:
        receipt_target_sha = target_match.group(1)
        if tag_ident.peeled_commit_sha and tag_ident.peeled_commit_sha != receipt_target_sha:
            return VerificationResult(
                passed=False,
                status="RECEIPT_TARGET_MISMATCH",
                message=(
                    f"Receipt target commit {receipt_target_sha} does not match local tag {tag} target commit {tag_ident.peeled_commit_sha}."
                ),
            )
        if release_commit and release_commit != receipt_target_sha:
            return VerificationResult(
                passed=False,
                status="RECEIPT_TARGET_MISMATCH",
                message=(
                    f"Receipt target commit {receipt_target_sha} does not match supplied release commit {release_commit}."
                ),
            )

    # 4. Check release URL format if present
    expected_url = f"https://github.com/LightDevCoder/skills/releases/tag/{tag}"
    url_match = re.search(r"https://github\.com/LightDevCoder/skills/releases/tag/([^\s\)\`\|]+)", text_en)
    if url_match:
        url_tag = url_match.group(1)
        if url_tag != tag:
            return VerificationResult(
                passed=False,
                status="RECEIPT_URL_MISMATCH",
                message=f"Release URL tag '{url_tag}' does not match release tag '{tag}'.",
            )

    # If legacy release (<= v0.2.3), skip new strict structural requirements
    if is_legacy:
        return VerificationResult(
            passed=True,
            status="PASS",
            message=f"Release receipt for {tag} verified: valid dual receipts and verified {actual_pkg_count} packages.",
        )

    # --- Strict Required-Field Contract for v0.2.4+ ---
    # 5. Status must be VERIFIED (Fail closed on CANDIDATE, PREPARED, PENDING)
    status_m_en = re.search(r"^Status:\s*`?([A-Z_]+)`?", text_en, re.MULTILINE)
    status_m_zh = re.search(r"^(?:状态|Status)[：:]\s*`?([A-Z_]+)`?", text_zh, re.MULTILINE)
    status_en = status_m_en.group(1) if status_m_en else None
    status_zh = status_m_zh.group(1) if status_m_zh else None

    if status_en != "VERIFIED":
        return VerificationResult(
            passed=False,
            status="RECEIPT_STATUS_INVALID",
            message=f"English receipt status must be 'VERIFIED', got '{status_en}'.",
        )
    if status_zh != "VERIFIED":
        return VerificationResult(
            passed=False,
            status="RECEIPT_STATUS_INVALID",
            message=f"Chinese receipt status must be 'VERIFIED', got '{status_zh}'.",
        )

    # 6. Release & Release Tag identity fields
    rel_m_en = re.search(r"\|\s*\*\*Release\*\*\s*\|\s*`?([^\s\`\|]+)`?", text_en)
    rel_m_zh = re.search(r"\|\s*\*\*发布版本\*\*\s*\|\s*`?([^\s\`\|]+)`?", text_zh)
    if not rel_m_en or rel_m_en.group(1) not in (tag, tag.lstrip("v")):
        return VerificationResult(
            passed=False,
            status="RECEIPT_RELEASE_MISMATCH",
            message=f"Release field in English receipt must match '{tag}'.",
        )
    if not rel_m_zh or rel_m_zh.group(1) not in (tag, tag.lstrip("v")):
        return VerificationResult(
            passed=False,
            status="RECEIPT_RELEASE_MISMATCH",
            message=f"发布版本 field in Chinese receipt must match '{tag}'.",
        )

    tag_m_en = re.search(r"\|\s*\*\*Release Tag\*\*\s*\|\s*`?([^\s\`\|]+)`?", text_en)
    tag_m_zh = re.search(r"\|\s*\*\*发布 Tag\*\*\s*\|\s*`?([^\s\`\|]+)`?", text_zh)
    if not tag_m_en or tag_m_en.group(1) != tag:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_MISMATCH",
            message=f"Release Tag field in English receipt must match '{tag}'.",
        )
    if not tag_m_zh or tag_m_zh.group(1) != tag:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_MISMATCH",
            message=f"发布 Tag field in Chinese receipt must match '{tag}'.",
        )

    # 7. Annotated Tag Object
    obj_m_en = re.search(r"\|\s*\*\*Annotated Tag Object\*\*\s*\|\s*`?([0-9a-f]{40})`?", text_en, re.IGNORECASE)
    obj_m_zh = re.search(r"\|\s*\*\*Annotated Tag 对象\*\*\s*\|\s*`?([0-9a-f]{40})`?", text_zh, re.IGNORECASE)
    if not obj_m_en:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_OBJECT_MISSING",
            message=f"Annotated Tag Object SHA missing or invalid in {rel_receipt_en}",
        )
    if not obj_m_zh:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_OBJECT_MISSING",
            message=f"Annotated Tag 对象 SHA missing or invalid in {rel_receipt_zh}",
        )
    if obj_m_en.group(1) != obj_m_zh.group(1):
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_OBJECT_MISMATCH",
            message="Annotated Tag Object SHA differs between English and Chinese receipts.",
        )
    if tag_ident.is_annotated and tag_ident.tag_object_sha and obj_m_en.group(1) != tag_ident.tag_object_sha:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_OBJECT_MISMATCH",
            message=f"Receipt tag object {obj_m_en.group(1)} does not match actual annotated tag object {tag_ident.tag_object_sha}.",
        )

    # 8. Tag Target Commit
    tgt_m_en = re.search(r"\|\s*\*\*Tag Target Commit\*\*\s*\|\s*`?([0-9a-f]{40})`?", text_en, re.IGNORECASE)
    tgt_m_zh = re.search(r"\|\s*\*\*Tag 目标 Commit\*\*\s*\|\s*`?([0-9a-f]{40})`?", text_zh, re.IGNORECASE)
    if not tgt_m_en:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISSING",
            message=f"Tag Target Commit SHA missing in {rel_receipt_en}",
        )
    if not tgt_m_zh:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISSING",
            message=f"Tag 目标 Commit SHA missing in {rel_receipt_zh}",
        )
    if tgt_m_en.group(1) != tgt_m_zh.group(1):
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISMATCH",
            message="Tag Target Commit SHA differs between English and Chinese receipts.",
        )
    target_sha_val = tgt_m_en.group(1)
    if release_commit and target_sha_val != release_commit:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISMATCH",
            message=f"Receipt tag target commit {target_sha_val} does not match supplied release commit {release_commit}.",
        )
    if tag_ident.is_annotated and tag_ident.peeled_commit_sha and target_sha_val != tag_ident.peeled_commit_sha:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISMATCH",
            message=f"Receipt tag target commit {target_sha_val} does not match actual local tag peeled commit {tag_ident.peeled_commit_sha}.",
        )
    if release_commit and tag_ident.is_annotated and tag_ident.peeled_commit_sha and tag_ident.peeled_commit_sha != release_commit:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISMATCH",
            message=f"Actual tag peeled commit {tag_ident.peeled_commit_sha} does not match supplied release commit {release_commit}.",
        )

    # 9. Release URL
    url_m_en = re.search(r"\|\s*\*\*Release URL\*\*\s*\|\s*(https://github\.com/[^\s\`\|\)]+)", text_en)
    url_m_zh = re.search(r"\|\s*\*\*发布 URL\*\*\s*\|\s*(https://github\.com/[^\s\`\|\)]+)", text_zh)
    if not url_m_en or url_m_en.group(1) != expected_url:
        return VerificationResult(
            passed=False,
            status="RECEIPT_URL_MISMATCH",
            message=f"Release URL in English receipt must be '{expected_url}'.",
        )
    if not url_m_zh or url_m_zh.group(1) != expected_url:
        return VerificationResult(
            passed=False,
            status="RECEIPT_URL_MISMATCH",
            message=f"Release URL in Chinese receipt must be '{expected_url}'.",
        )

    # 10. Publication Timestamp
    ts_m_en = re.search(r"\|\s*\*\*Publication Timestamp\*\*\s*\|\s*`?([^\`\|\n]+)`?", text_en)
    ts_m_zh = re.search(r"\|\s*\*\*公开发布时间戳\*\*\s*\|\s*`?([^\`\|\n]+)`?", text_zh)
    if not ts_m_en or not ts_m_en.group(1).strip() or "PENDING" in ts_m_en.group(1).upper():
        return VerificationResult(
            passed=False,
            status="RECEIPT_TIMESTAMP_MISSING",
            message=f"Publication timestamp missing or pending in {rel_receipt_en}",
        )
    if not ts_m_zh or not ts_m_zh.group(1).strip() or "PENDING" in ts_m_zh.group(1).upper():
        return VerificationResult(
            passed=False,
            status="RECEIPT_TIMESTAMP_MISSING",
            message=f"公开发布时间戳 missing or pending in {rel_receipt_zh}",
        )

    # 11. Required Evidence Gates
    en_gates = [
        ("GitHub Actions CI", "CI"),
        ("Pinned Fresh Install", "pinned install"),
        ("Generic Latest Fresh Install", "latest install"),
        ("GitHub Release Publication", "GitHub release publication"),
    ]
    for gate_name, gate_desc in en_gates:
        st = extract_checklist_status(text_en, gate_name)
        if not st:
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_MISSING",
                message=f"Required evidence row '{gate_name}' ({gate_desc}) missing in {rel_receipt_en}",
            )
        if st in ("PENDING", "TODO", "CANDIDATE"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_PENDING",
                message=f"Evidence row '{gate_name}' in {rel_receipt_en} is '{st}', not final PASS/SUCCESS.",
            )
        if st not in ("PASS", "SUCCESS"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_INCOMPLETE",
                message=f"Evidence row '{gate_name}' in {rel_receipt_en} has non-passing status '{st}'.",
            )

    zh_gates = [
        ("GitHub Actions CI", "CI"),
        ("锁定版本全量全新安装", "pinned install"),
        ("最新主干全量全新安装", "latest install"),
        ("GitHub Release 发布", "GitHub release publication"),
    ]
    for gate_name, gate_desc in zh_gates:
        st = extract_checklist_status(text_zh, gate_name)
        if not st:
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_MISSING",
                message=f"Required evidence row '{gate_name}' ({gate_desc}) missing in {rel_receipt_zh}",
            )
        if st in ("PENDING", "TODO", "CANDIDATE"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_PENDING",
                message=f"Evidence row '{gate_name}' in {rel_receipt_zh} is '{st}', not final PASS/SUCCESS.",
            )
        if st not in ("PASS", "SUCCESS"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_INCOMPLETE",
                message=f"Evidence row '{gate_name}' in {rel_receipt_zh} has non-passing status '{st}'.",
            )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release receipt for {tag} verified: valid dual receipts, verified {actual_pkg_count} packages, and all required evidence confirmed.",
    )


def check_working_tree(repo_root: Path = REPO_ROOT, tag: str | None = None) -> VerificationResult:
    """Verify git diff, whitespace cleanliness, and absence of uncommitted release evidence."""
    code_ws, _, err_ws = run_git(["diff", "--check"], cwd=repo_root)
    if code_ws != 0:
        return VerificationResult(
            passed=False,
            status="WHITESPACE_ERROR",
            message=f"Whitespace errors detected: {err_ws}",
        )

    code_st, out_st, _ = run_git(["status", "--porcelain", "-uall"], cwd=repo_root)
    # Check tracked modifications (ignore untracked files like .scratch/)
    tracked_mods = [line for line in out_st.splitlines() if line and not line.startswith("??")]
    if tracked_mods:
        return VerificationResult(
            passed=False,
            status="DIRTY_TREE",
            message=f"Uncommitted tracked changes detected:\n" + "\n".join(tracked_mods[:5]),
        )

    # Check for release-critical untracked files
    if tag:
        target_prefix = f"docs/evidence/releases/{tag}/"
        untracked_release_files = []
        for line in out_st.splitlines():
            if line.startswith("?? "):
                path_str = line[3:].strip()
                if path_str.startswith(target_prefix):
                    untracked_release_files.append(path_str)

        if untracked_release_files:
            return VerificationResult(
                passed=False,
                status="UNTRACKED_RELEASE_EVIDENCE_FORBIDDEN",
                message=(
                    f"Untracked release evidence detected for {tag}:\n"
                    + "\n".join(untracked_release_files[:5])
                    + "\nRelease evidence must be committed into git before verification."
                ),
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
    return "v0.2.3"


def get_repo_root(root_arg: str | None = None) -> Path:
    """Resolve repository root from CLI argument, git root, or script location."""
    if root_arg:
        return Path(root_arg).resolve()
    code, out, _ = run_git(["rev-parse", "--show-toplevel"], cwd=Path.cwd())
    if code == 0 and out:
        return Path(out).resolve()
    return REPO_ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release integrity and tag immutability.")
    parser.add_argument("--root", default=None, help="Repository root path.")
    parser.add_argument("--tag", help="Release tag to verify (e.g. v0.2.3). Default: latest candidate tag.")
    parser.add_argument("--release-commit", "--commit", dest="release_commit", default=None,
                        help="Release candidate / tag target commit SHA. (Default: HEAD for prepared/candidate/tagged stages).")
    parser.add_argument("--stage", choices=["auto", "prepared", "candidate", "tagged", "attested"], default="auto",
                        help="Lifecycle stage to verify (default: auto).")
    parser.add_argument("--check-remote", action="store_true", help="Also query git remote for tag status.")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow uncommitted tracked changes.")

    args = parser.parse_args()
    repo_root = get_repo_root(args.root)
    tag = args.tag or detect_candidate_tag(repo_root)
    stage = args.stage

    # Auto-resolve stage if auto
    if stage == "auto":
        tag_peel = resolve_tag_sha(tag, cwd=repo_root)
        receipt_rel = f"docs/evidence/releases/{tag}/RELEASE_RECEIPT.md"
        receipt_exists = (repo_root / receipt_rel).is_file() or git_path_exists("HEAD", receipt_rel, cwd=repo_root)
        if tag_peel and receipt_exists:
            stage = "attested"
        elif tag_peel:
            stage = "tagged"
        else:
            stage = "prepared"

    # Resolve candidate commit ref according to stage contract
    if stage == "attested":
        if args.release_commit:
            candidate_ref = args.release_commit
            candidate_sha = resolve_commit_sha(candidate_ref, cwd=repo_root)
        else:
            # In attested stage, NEVER implicitly use HEAD!
            # Infer candidate SHA from local tag if present
            tag_peel = resolve_tag_sha(tag, cwd=repo_root)
            if tag_peel:
                candidate_ref = tag_peel
                candidate_sha = tag_peel
            else:
                candidate_ref = "UNKNOWN"
                candidate_sha = None
    elif stage == "tagged":
        if args.release_commit:
            candidate_ref = args.release_commit
            candidate_sha = resolve_commit_sha(candidate_ref, cwd=repo_root)
        else:
            # In tagged stage, tag target != arbitrary HEAD inference
            tag_peel = resolve_tag_sha(tag, cwd=repo_root)
            if tag_peel:
                candidate_ref = tag_peel
                candidate_sha = tag_peel
            else:
                candidate_ref = "UNKNOWN"
                candidate_sha = None
    else:
        candidate_ref = args.release_commit or "HEAD"
        candidate_sha = resolve_commit_sha(candidate_ref, cwd=repo_root)

    print(f"=== Release Integrity Guard ===")
    print(f"Target Tag:     {tag}")
    print(f"Release Commit: {candidate_sha or candidate_ref}")
    print(f"Stage:          {stage}")
    print(f"Repository:     {repo_root}")
    print("--------------------------------")

    all_passed = True

    # 1. Working tree check (always run against current working tree / HEAD)
    if not args.allow_dirty:
        res_tree = check_working_tree(repo_root, tag=tag)
        print(f"[{res_tree.status}] Working Tree: {res_tree.message}")
        if not res_tree.passed:
            all_passed = False
    else:
        print("[SKIPPED] Working Tree check bypassed via --allow-dirty.")

    # 2. Candidate commit resolution check
    if not candidate_sha:
        print(f"[ERROR] Release Candidate Commit: Could not resolve '{candidate_ref}' to a 40-character SHA.")
        all_passed = False

    # 3. Stage-specific checks:
    if stage in ("prepared", "candidate"):
        # In prepared/candidate stage, HEAD must match supplied candidate commit
        head_sha = resolve_commit_sha("HEAD", cwd=repo_root)
        if candidate_sha and head_sha and head_sha != candidate_sha:
            print(f"[HEAD_NOT_CANDIDATE] In stage '{stage}', HEAD ({head_sha}) must match candidate commit ({candidate_sha}).")
            all_passed = False

        if candidate_sha:
            res_tag = check_tag_immutability(tag, candidate_sha, check_remote=args.check_remote, stage=stage, cwd=repo_root)
            print(f"[{res_tag.status}] Tag Status: {res_tag.message}")
            if not res_tag.passed:
                all_passed = False

        res_absence = check_receipt_absence_in_candidate(tag, revision=candidate_sha, repo_root=repo_root)
        print(f"[{res_absence.status}] Candidate Receipt Absence: {res_absence.message}")
        if not res_absence.passed:
            all_passed = False

        res_manifest = check_release_manifest_consistency(tag, revision=candidate_sha, repo_root=repo_root)
        print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
        if not res_manifest.passed:
            all_passed = False

        res_nav = check_manifest_navigation(tag, revision=candidate_sha, repo_root=repo_root)
        print(f"[{res_nav.status}] Manifest Navigation: {res_nav.message}")
        if not res_nav.passed:
            all_passed = False

        res_notes = check_release_notes_consistency(tag, revision=candidate_sha, repo_root=repo_root)
        print(f"[{res_notes.status}] Notes Consistency: {res_notes.message}")
        if not res_notes.passed:
            all_passed = False

        res_docs = check_public_candidate_docs(repo_root=repo_root)
        print(f"[{res_docs.status}] Public Candidate Docs: {res_docs.message}")
        if not res_docs.passed:
            all_passed = False

    elif stage == "tagged":
        if candidate_sha:
            res_tag = check_tag_immutability(tag, candidate_sha, check_remote=args.check_remote, stage="tagged", cwd=repo_root)
            print(f"[{res_tag.status}] Tag Immutability: {res_tag.message}")
            if not res_tag.passed:
                all_passed = False

        tag_ref = f"refs/tags/{tag}"

        res_absence = check_receipt_absence_in_candidate(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_absence.status}] Candidate Receipt Absence: {res_absence.message}")
        if not res_absence.passed:
            all_passed = False

        res_manifest = check_release_manifest_consistency(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
        if not res_manifest.passed:
            all_passed = False

        res_nav = check_manifest_navigation(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_nav.status}] Manifest Navigation: {res_nav.message}")
        if not res_nav.passed:
            all_passed = False

        res_notes = check_release_notes_consistency(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_notes.status}] Notes Consistency: {res_notes.message}")
        if not res_notes.passed:
            all_passed = False

    elif stage == "attested":
        if candidate_sha:
            res_tag = check_tag_immutability(tag, candidate_sha, check_remote=args.check_remote, stage="attested", cwd=repo_root)
            print(f"[{res_tag.status}] Tag Immutability: {res_tag.message}")
            if not res_tag.passed:
                all_passed = False

        # Manifest and notes are verified from the immutable tag snapshot
        tag_ref = f"refs/tags/{tag}" if resolve_tag_sha(tag, cwd=repo_root) else (candidate_sha or "HEAD")

        res_manifest = check_release_manifest_consistency(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
        if not res_manifest.passed:
            all_passed = False

        res_nav = check_manifest_navigation(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_nav.status}] Manifest Navigation: {res_nav.message}")
        if not res_nav.passed:
            all_passed = False

        res_notes = check_release_notes_consistency(tag, revision=tag_ref, repo_root=repo_root)
        print(f"[{res_notes.status}] Notes Consistency: {res_notes.message}")
        if not res_notes.passed:
            all_passed = False

        if args.check_remote:
            res_rel_body = check_github_release_navigation(tag, repo="LightDevCoder/skills", cwd=repo_root)
            print(f"[{res_rel_body.status}] GitHub Release Navigation: {res_rel_body.message}")
            if not res_rel_body.passed:
                all_passed = False

        # Release receipt is verified from committed HEAD (receipt_revision)
        # against the immutable candidate/tag snapshot (release_revision)
        head_sha = resolve_commit_sha("HEAD", cwd=repo_root)
        rel_rev = candidate_sha or tag_ref
        res_receipt = check_release_receipt_consistency(
            tag,
            release_commit=candidate_sha,
            receipt_revision=head_sha,
            release_revision=rel_rev,
            repo_root=repo_root,
        )
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
