"""Unit and behavior tests for scripts/verify_release_integrity.py."""

from __future__ import annotations

import sys
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
        # v0.2.1 is an existing tag
        v021_sha = resolve_tag_sha("v0.2.1", cwd=ROOT)
        self.assertIsNotNone(v021_sha)

        res = check_tag_immutability("v0.2.1", v021_sha, cwd=ROOT)
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "IDEMPOTENT_PASS")
        self.assertIn("Safe for CI retry", res.message)

    def test_existing_tag_different_target_is_hard_fail(self) -> None:
        """An existing tag pointing to a different commit returns HARD_FAIL, blocking retargeting."""
        # v0.2.1 points to 6f9d173, while HEAD is a subsequent commit (61402e1 or similar)
        head_sha = resolve_commit_sha("HEAD", cwd=ROOT)
        v021_sha = resolve_tag_sha("v0.2.1", cwd=ROOT)
        self.assertNotEqual(head_sha, v021_sha)

        res = check_tag_immutability("v0.2.1", "HEAD", cwd=ROOT)
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
