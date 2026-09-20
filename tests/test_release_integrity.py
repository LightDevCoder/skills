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
        self.assertEqual(tag, "v0.2.2")

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

    def test_missing_receipt_fails_cleanly(self) -> None:
        """Missing receipt for an unreleased version returns RECEIPT_MISSING."""
        res = check_release_receipt_consistency("v9.9.9-bogus", repo_root=ROOT)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_MISSING")


if __name__ == "__main__":
    unittest.main()
