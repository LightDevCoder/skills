"""Unit and behavior tests for scripts/verify_release_integrity.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from verify_release_integrity import (
    check_tag_immutability,
    check_release_manifest_consistency,
    check_release_receipt_consistency,
    get_admitted_package_count,
    detect_candidate_tag,
    resolve_tag_sha,
    resolve_commit_sha,
)


class ReleaseIntegrityTests(unittest.TestCase):
    def test_admitted_package_count_is_36(self) -> None:
        """Exactly 36 admitted Skill packages must be counted under skills/*/*."""
        count = get_admitted_package_count(ROOT)
        self.assertEqual(count, 36)

    def test_detect_candidate_tag(self) -> None:
        """Infers latest candidate release tag from docs/evidence/releases/."""
        tag = detect_candidate_tag(ROOT)
        self.assertEqual(tag, "v0.2.3")

    def test_new_tag_passes_ready_for_creation(self) -> None:
        """A tag that does not exist locally or remotely passes ready for creation."""
        res = check_tag_immutability("v9.9.9-nonexistent", "HEAD", cwd=ROOT)
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")
        self.assertIn("does not exist yet", res.message)

    def test_existing_tag_same_target_is_idempotent_pass(self) -> None:
        """An existing tag pointing to the exact same target commit returns IDEMPOTENT_PASS."""
        with tempfile.TemporaryDirectory(prefix="git-tag-test-") as tmp:
            tmp_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_root, capture_output=True, check=True)
            (tmp_root / "file.txt").write_text("v1", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "tag", "-a", "v1.0.0", "-m", "v1.0.0"], cwd=tmp_root, capture_output=True, check=True)

            c1_sha = resolve_tag_sha("v1.0.0", cwd=tmp_root)
            self.assertIsNotNone(c1_sha)

            res = check_tag_immutability("v1.0.0", c1_sha, cwd=tmp_root)
            self.assertTrue(res.passed)
            self.assertEqual(res.status, "IDEMPOTENT_PASS")
            self.assertIn("Safe for CI retry", res.message)

    def test_existing_tag_different_target_is_hard_fail(self) -> None:
        """An existing tag pointing to a different commit returns HARD_FAIL, blocking retargeting."""
        with tempfile.TemporaryDirectory(prefix="git-tag-test-") as tmp:
            tmp_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_root, capture_output=True, check=True)
            (tmp_root / "file.txt").write_text("v1", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "tag", "-a", "v1.0.0", "-m", "v1.0.0"], cwd=tmp_root, capture_output=True, check=True)

            # Second commit
            (tmp_root / "file.txt").write_text("v2", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "second"], cwd=tmp_root, capture_output=True, check=True)

            res = check_tag_immutability("v1.0.0", "HEAD", cwd=tmp_root)
            self.assertFalse(res.passed)
            self.assertEqual(res.status, "HARD_FAIL")
            self.assertIn("Tag retargeting/force-moving is strictly forbidden", res.message)

    def test_receipt_consistency_v022(self) -> None:
        """v0.2.2 release receipts match dual-language requirements and package count."""
        res = check_release_receipt_consistency("v0.2.2", repo_root=ROOT)
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")
        self.assertIn("36 packages", res.message)

    def test_manifest_consistency_v023(self) -> None:
        """v0.2.3 release manifest matches dual-language requirements, package count, and policy."""
        res = check_release_manifest_consistency("v0.2.3", repo_root=ROOT)
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")
        self.assertIn("36 packages", res.message)

    def test_receipt_consistency_v023(self) -> None:
        """v0.2.3 release receipt matches dual-language requirements and package count."""
        res = check_release_receipt_consistency("v0.2.3", repo_root=ROOT)
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")
        self.assertIn("36 packages", res.message)

    def test_missing_receipt_fails_cleanly(self) -> None:
        """Missing receipt for an unreleased version returns RECEIPT_MISSING."""
        res = check_release_receipt_consistency("v9.9.9-bogus", repo_root=ROOT)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_MISSING")

    def test_historical_v022_skips_manifest(self) -> None:
        """v0.2.2 precedes manifest architecture and returns SKIPPED_HISTORICAL."""
        res = check_release_manifest_consistency("v0.2.2", repo_root=ROOT)
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "SKIPPED_HISTORICAL")

    def test_missing_manifest_fails_for_v023(self) -> None:
        """Missing manifest for v0.2.3+ returns MANIFEST_MISSING."""
        with tempfile.TemporaryDirectory(prefix="manifest-test-") as tmp:
            tmp_root = Path(tmp)
            res = check_release_manifest_consistency("v0.2.3", repo_root=tmp_root)
            self.assertFalse(res.passed)
            self.assertEqual(res.status, "MANIFEST_MISSING")

    def test_manifest_consistency_hermetic_pass(self) -> None:
        """Hermetic verification of valid dual manifests."""
        with tempfile.TemporaryDirectory(prefix="manifest-test-") as tmp:
            tmp_root = Path(tmp)
            # Create a mock admitted package
            pkg_dir = tmp_root / "skills" / "category" / "pkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")

            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v0.2.3"
            rel_dir.mkdir(parents=True)

            manifest_content_en = (
                "# Manifest v0.2.3\n"
                "Release: `v0.2.3`\n"
                "Release identity: `refs/tags/v0.2.3^{commit}`\n"
                "Collection package count: 1 admitted packages\n"
                "Policy status: `PROVISIONAL`\n"
            )
            manifest_content_zh = (
                "# 清单 v0.2.3\n"
                "发布版本：`v0.2.3`\n"
                "发布身份：`refs/tags/v0.2.3^{commit}`\n"
                "集合包总数：1 个\n"
                "政策状态：`PROVISIONAL`\n"
            )
            (rel_dir / "RELEASE_MANIFEST.md").write_text(manifest_content_en, encoding="utf-8")
            (rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(manifest_content_zh, encoding="utf-8")

            res = check_release_manifest_consistency("v0.2.3", repo_root=tmp_root)
            self.assertTrue(res.passed)
            self.assertEqual(res.status, "PASS")

    def test_receipt_target_mismatch_fails(self) -> None:
        """Receipt target commit mismatching local tag peeled commit returns RECEIPT_TARGET_MISMATCH."""
        with tempfile.TemporaryDirectory(prefix="receipt-mismatch-test-") as tmp:
            tmp_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_root, capture_output=True, check=True)
            (tmp_root / "file.txt").write_text("v1", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "commit 1"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "tag", "-a", "v0.2.3", "-m", "v0.2.3"], cwd=tmp_root, capture_output=True, check=True)

            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v0.2.3"
            rel_dir.mkdir(parents=True)
            # Receipt records a different target commit SHA
            bogus_sha = "0123456789012345678901234567890123456789"
            receipt_en = (
                "# Receipt v0.2.3\n"
                f"Tag target commit | `{bogus_sha}`\n"
                "Collection package count | 0 admitted packages\n"
                "https://github.com/LightDevCoder/skills/releases/tag/v0.2.3\n"
            )
            receipt_zh = (
                "# 收据 v0.2.3\n"
                f"Tag 目标 commit | `{bogus_sha}`\n"
                "集合包总数 | 0 个\n"
            )
            (rel_dir / "RELEASE_RECEIPT.md").write_text(receipt_en, encoding="utf-8")
            (rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(receipt_zh, encoding="utf-8")

            res = check_release_receipt_consistency("v0.2.3", repo_root=tmp_root)
            self.assertFalse(res.passed)
            self.assertEqual(res.status, "RECEIPT_TARGET_MISMATCH")



if __name__ == "__main__":
    unittest.main()
