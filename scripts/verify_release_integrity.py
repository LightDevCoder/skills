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


class AnnotatedTagIdentity(NamedTuple):
    tag_type: str | None
    tag_object_sha: str | None
    peeled_commit_sha: str | None
    is_annotated: bool


def resolve_annotated_tag_identity(tag: str, cwd: Path = REPO_ROOT) -> AnnotatedTagIdentity:
    """Resolve tag identity using git cat-file -t and git rev-parse.

    For annotated tags, git cat-file -t returns 'tag'.
    For lightweight tags, git cat-file -t returns 'commit' and is_annotated is False.
    """
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

    # 2. Check remote tag if requested
    if check_remote:
        remote_tag_sha = resolve_remote_tag_sha(tag, cwd=cwd)
        if remote_tag_sha:
            if remote_tag_sha == target_sha:
                return VerificationResult(
                    passed=True,
                    status="IDEMPOTENT_PASS",
                    message=f"Remote tag '{tag}' already exists pointing to candidate commit {target_sha}. Safe for CI retry.",
                )
            else:
                return VerificationResult(
                    passed=False,
                    status="HARD_FAIL",
                    message=(
                        f"Tag immutability violation! Remote tag '{tag}' points to {remote_tag_sha}, "
                        f"which differs from candidate commit {target_sha}. Tag retargeting/force-moving is strictly forbidden."
                    ),
                )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Tag '{tag}' does not exist yet. Ready for creation on candidate commit {target_sha}.",
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


def check_manifest_navigation(tag: str, repo_root: Path = REPO_ROOT) -> VerificationResult:
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

    evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
    for manifest_name in ["RELEASE_MANIFEST.md", "RELEASE_MANIFEST.zh-CN.md"]:
        p = evidence_dir / manifest_name
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            if re.search(r"\[[^\]]+\]\(\s*RELEASE_RECEIPT(?:\.zh-CN)?\.md\s*\)", text):
                return VerificationResult(
                    passed=False,
                    status="RELATIVE_RECEIPT_LINK_FORBIDDEN",
                    message=(
                        f"Manifest {p.relative_to(repo_root)} contains a relative link to RELEASE_RECEIPT.md. "
                        "Manifest must not navigate to candidate receipts in immutable tags; "
                        "post-publication attestation lives on main."
                    ),
                )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Manifest navigation for {tag} verified: no relative links to post-publication receipts.",
    )


def check_release_notes_consistency(tag: str, repo_root: Path = REPO_ROOT) -> VerificationResult:
    """Verify dual release notes exist."""
    evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
    notes_en = evidence_dir / "RELEASE_NOTES.md"
    notes_zh = evidence_dir / "RELEASE_NOTES.zh-CN.md"

    if not notes_en.is_file():
        return VerificationResult(
            passed=False,
            status="NOTES_MISSING",
            message=f"English release notes missing at {notes_en.relative_to(repo_root)}",
        )
    if not notes_zh.is_file():
        return VerificationResult(
            passed=False,
            status="NOTES_MISSING",
            message=f"Chinese release notes missing at {notes_zh.relative_to(repo_root)}",
        )
    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release notes for {tag} verified.",
    )


def check_receipt_absence_in_candidate(tag: str, repo_root: Path = REPO_ROOT) -> VerificationResult:
    """Verify that candidate/pre-tag directories do not contain pre-publication candidate receipts (v0.2.4+)."""
    version_match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if version_match:
        major, minor, patch = map(int, version_match.groups())
        if (major, minor, patch) <= (0, 2, 3):
            return VerificationResult(
                passed=True,
                status="SKIPPED_HISTORICAL",
                message=f"Release {tag} is a known legacy lifecycle artifact.",
            )

    evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
    receipt_en = evidence_dir / "RELEASE_RECEIPT.md"
    receipt_zh = evidence_dir / "RELEASE_RECEIPT.zh-CN.md"

    if receipt_en.is_file() or receipt_zh.is_file():
        return VerificationResult(
            passed=False,
            status="CANDIDATE_RECEIPT_FORBIDDEN",
            message=(
                f"Candidate release directory {evidence_dir.relative_to(repo_root)} contains pre-publication receipt(s). "
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
    repo_root: Path = REPO_ROOT,
) -> VerificationResult:
    """Verify mechanical consistency of release receipt and evidence files."""
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
    text_zh = receipt_zh.read_text(encoding="utf-8")
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
            message=f"Tag '{tag}' not found in release receipts under {evidence_dir.relative_to(repo_root)}",
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
                    f"Package count mismatch in {receipt_en.relative_to(repo_root)}: "
                    f"receipt claims {claimed_count}, but repository has {actual_pkg_count} admitted packages."
                ),
            )
    elif not is_legacy:
        return VerificationResult(
            passed=False,
            status="COUNT_MISMATCH",
            message=f"Collection package count field missing in {receipt_en.relative_to(repo_root)}",
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
                    f"Package count mismatch in {receipt_zh.relative_to(repo_root)}: "
                    f"receipt claims {claimed_count_zh}, but repository has {actual_pkg_count} admitted packages."
                ),
            )
    elif not is_legacy:
        return VerificationResult(
            passed=False,
            status="COUNT_MISMATCH",
            message=f"Collection package count field missing in {receipt_zh.relative_to(repo_root)}",
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
            message=f"Annotated Tag Object SHA missing or invalid in {receipt_en.relative_to(repo_root)}",
        )
    if not obj_m_zh:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_OBJECT_MISSING",
            message=f"Annotated Tag 对象 SHA missing or invalid in {receipt_zh.relative_to(repo_root)}",
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
            message=f"Tag Target Commit SHA missing in {receipt_en.relative_to(repo_root)}",
        )
    if not tgt_m_zh:
        return VerificationResult(
            passed=False,
            status="RECEIPT_TAG_TARGET_MISSING",
            message=f"Tag 目标 Commit SHA missing in {receipt_zh.relative_to(repo_root)}",
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
            message=f"Publication timestamp missing or pending in {receipt_en.relative_to(repo_root)}",
        )
    if not ts_m_zh or not ts_m_zh.group(1).strip() or "PENDING" in ts_m_zh.group(1).upper():
        return VerificationResult(
            passed=False,
            status="RECEIPT_TIMESTAMP_MISSING",
            message=f"公开发布时间戳 missing or pending in {receipt_zh.relative_to(repo_root)}",
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
                message=f"Required evidence row '{gate_name}' ({gate_desc}) missing in {receipt_en.relative_to(repo_root)}",
            )
        if st in ("PENDING", "TODO", "CANDIDATE"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_PENDING",
                message=f"Evidence row '{gate_name}' in {receipt_en.relative_to(repo_root)} is '{st}', not final PASS/SUCCESS.",
            )
        if st not in ("PASS", "SUCCESS"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_INCOMPLETE",
                message=f"Evidence row '{gate_name}' in {receipt_en.relative_to(repo_root)} has non-passing status '{st}'.",
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
                message=f"Required evidence row '{gate_name}' ({gate_desc}) missing in {receipt_zh.relative_to(repo_root)}",
            )
        if st in ("PENDING", "TODO", "CANDIDATE"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_PENDING",
                message=f"Evidence row '{gate_name}' in {receipt_zh.relative_to(repo_root)} is '{st}', not final PASS/SUCCESS.",
            )
        if st not in ("PASS", "SUCCESS"):
            return VerificationResult(
                passed=False,
                status="RECEIPT_EVIDENCE_INCOMPLETE",
                message=f"Evidence row '{gate_name}' in {receipt_zh.relative_to(repo_root)} has non-passing status '{st}'.",
            )

    return VerificationResult(
        passed=True,
        status="PASS",
        message=f"Release receipt for {tag} verified: valid dual receipts, verified {actual_pkg_count} packages, and all required evidence confirmed.",
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
        evidence_dir = repo_root / "docs" / "evidence" / "releases" / tag
        receipt_file = evidence_dir / "RELEASE_RECEIPT.md"
        if receipt_file.is_file():
            stage = "attested"
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
        res_tree = check_working_tree(repo_root)
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

        res_absence = check_receipt_absence_in_candidate(tag, repo_root=repo_root)
        print(f"[{res_absence.status}] Candidate Receipt Absence: {res_absence.message}")
        if not res_absence.passed:
            all_passed = False

        res_manifest = check_release_manifest_consistency(tag, repo_root=repo_root)
        print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
        if not res_manifest.passed:
            all_passed = False

        res_notes = check_release_notes_consistency(tag, repo_root=repo_root)
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

        res_absence = check_receipt_absence_in_candidate(tag, repo_root=repo_root)
        print(f"[{res_absence.status}] Candidate Receipt Absence: {res_absence.message}")
        if not res_absence.passed:
            all_passed = False

        res_manifest = check_release_manifest_consistency(tag, repo_root=repo_root)
        print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
        if not res_manifest.passed:
            all_passed = False

        res_nav = check_manifest_navigation(tag, repo_root=repo_root)
        print(f"[{res_nav.status}] Manifest Navigation: {res_nav.message}")
        if not res_nav.passed:
            all_passed = False

        res_notes = check_release_notes_consistency(tag, repo_root=repo_root)
        print(f"[{res_notes.status}] Notes Consistency: {res_notes.message}")
        if not res_notes.passed:
            all_passed = False

    elif stage == "attested":
        if candidate_sha:
            res_tag = check_tag_immutability(tag, candidate_sha, check_remote=args.check_remote, stage="attested", cwd=repo_root)
            print(f"[{res_tag.status}] Tag Immutability: {res_tag.message}")
            if not res_tag.passed:
                all_passed = False

        res_manifest = check_release_manifest_consistency(tag, repo_root=repo_root)
        print(f"[{res_manifest.status}] Manifest Consistency: {res_manifest.message}")
        if not res_manifest.passed:
            all_passed = False

        res_nav = check_manifest_navigation(tag, repo_root=repo_root)
        print(f"[{res_nav.status}] Manifest Navigation: {res_nav.message}")
        if not res_nav.passed:
            all_passed = False

        res_notes = check_release_notes_consistency(tag, repo_root=repo_root)
        print(f"[{res_notes.status}] Notes Consistency: {res_notes.message}")
        if not res_notes.passed:
            all_passed = False

        res_receipt = check_release_receipt_consistency(tag, release_commit=candidate_sha, repo_root=repo_root)
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
