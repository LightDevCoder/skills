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
    check_manifest_navigation,
    check_release_notes_consistency,
    check_receipt_absence_in_candidate,
    get_admitted_package_count,
    detect_candidate_tag,
    resolve_tag_sha,
    resolve_commit_sha,
)
from check_release_tag_protection import verify_ruleset_payload


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

    def test_candidate_lifecycle_requirements(self) -> None:
        """Candidate stage (v0.2.4+) requires Manifest and Notes, and strictly forbids Receipt."""
        with tempfile.TemporaryDirectory(prefix="candidate-test-") as tmp:
            tmp_root = Path(tmp)
            pkg_dir = tmp_root / "skills" / "category" / "pkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")

            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v0.2.4"
            rel_dir.mkdir(parents=True)

            # 1. Manifest exists
            (rel_dir / "RELEASE_MANIFEST.md").write_text(
                "# Manifest v0.2.4\nRelease: `v0.2.4`\nRelease identity: `refs/tags/v0.2.4^{commit}`\n"
                "Collection package count: 1 admitted packages\nPolicy status: `PROVISIONAL`\n",
                encoding="utf-8",
            )
            (rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(
                "# 清单 v0.2.4\n发布版本：`v0.2.4`\n发布身份：`refs/tags/v0.2.4^{commit}`\n"
                "集合包总数：1 个\n政策状态：`PROVISIONAL`\n",
                encoding="utf-8",
            )
            # 2. Notes exist
            (rel_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.zh-CN.md").write_text("# 说明", encoding="utf-8")

            # Check candidate receipt absence passes
            res_absence = check_receipt_absence_in_candidate("v0.2.4", repo_root=tmp_root)
            self.assertTrue(res_absence.passed)
            self.assertEqual(res_absence.status, "PASS")

            # Notes check passes
            res_notes = check_release_notes_consistency("v0.2.4", repo_root=tmp_root)
            self.assertTrue(res_notes.passed)

            # If a candidate receipt is prematurely added, check fails
            (rel_dir / "RELEASE_RECEIPT.md").write_text("# Candidate receipt", encoding="utf-8")
            res_fail = check_receipt_absence_in_candidate("v0.2.4", repo_root=tmp_root)
            self.assertFalse(res_fail.passed)
            self.assertEqual(res_fail.status, "CANDIDATE_RECEIPT_FORBIDDEN")

    def test_tag_lifecycle_requirements(self) -> None:
        """Tag stage requires Manifest without relative link to Receipt."""
        with tempfile.TemporaryDirectory(prefix="tag-nav-test-") as tmp:
            tmp_root = Path(tmp)
            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v0.2.4"
            rel_dir.mkdir(parents=True)

            # Valid manifest explaining post-publication attestation without relative receipt link
            valid_manifest = (
                "# Manifest v0.2.4\n"
                "[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)\n\n"
                "Post-publication verification facts are attested on main in RELEASE_RECEIPT.md.\n"
            )
            (rel_dir / "RELEASE_MANIFEST.md").write_text(valid_manifest, encoding="utf-8")
            (rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(valid_manifest, encoding="utf-8")

            res_nav = check_manifest_navigation("v0.2.4", repo_root=tmp_root)
            self.assertTrue(res_nav.passed)
            self.assertEqual(res_nav.status, "PASS")

            # Invalid manifest with relative link to RELEASE_RECEIPT.md
            invalid_manifest = (
                "# Manifest v0.2.4\n"
                "[Release Receipt](RELEASE_RECEIPT.md)\n"
            )
            (rel_dir / "RELEASE_MANIFEST.md").write_text(invalid_manifest, encoding="utf-8")
            res_fail = check_manifest_navigation("v0.2.4", repo_root=tmp_root)
            self.assertFalse(res_fail.passed)
            self.assertEqual(res_fail.status, "RELATIVE_RECEIPT_LINK_FORBIDDEN")

    def test_historical_v023_legacy_compatibility(self) -> None:
        """v0.2.3 is recognized as a known legacy lifecycle artifact."""
        res_nav = check_manifest_navigation("v0.2.3", repo_root=ROOT)
        self.assertTrue(res_nav.passed)
        self.assertEqual(res_nav.status, "SKIPPED_HISTORICAL")

        res_absence = check_receipt_absence_in_candidate("v0.2.3", repo_root=ROOT)
        self.assertTrue(res_absence.passed)
        self.assertEqual(res_absence.status, "SKIPPED_HISTORICAL")

    def test_attested_lifecycle_v023_on_main(self) -> None:
        """On main, v0.2.3 has final attested receipts matching local tag and package count."""
        res_receipt = check_release_receipt_consistency("v0.2.3", repo_root=ROOT)
        self.assertTrue(res_receipt.passed)
        self.assertEqual(res_receipt.status, "PASS")

        # Verify peeled commit matches
        tag_target = resolve_tag_sha("v0.2.3", cwd=ROOT)
        self.assertEqual(tag_target, "398e30627c18d9bffe877bb69695d38dcd5e7633")

    def test_remote_tag_protection_ruleset_validation(self) -> None:
        """verify_ruleset_payload accurately validates GitHub ruleset structures."""
        valid_ruleset = {
            "id": 12345,
            "name": "Protect Release Tags",
            "target": "tag",
            "enforcement": "active",
            "conditions": {
                "ref_name": {
                    "include": ["refs/tags/v*"],
                    "exclude": [],
                }
            },
            "rules": [
                {"type": "deletion"},
                {"type": "update"},
            ],
        }

        # 1. Valid ruleset passes
        res = verify_ruleset_payload([valid_ruleset])
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")

        # 2. Inactive enforcement is BLOCKED
        inactive_rs = dict(valid_ruleset, enforcement="disabled")
        res = verify_ruleset_payload([inactive_rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

        # 3. Missing deletion restriction is BLOCKED
        no_del_rs = dict(valid_ruleset, rules=[{"type": "update"}])
        res = verify_ruleset_payload([no_del_rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("deletion", res.message)

        # 4. Missing update restriction is BLOCKED
        no_upd_rs = dict(valid_ruleset, rules=[{"type": "deletion"}])
        res = verify_ruleset_payload([no_upd_rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("update", res.message)

        # 5. Non-matching pattern is BLOCKED
        wrong_pat_rs = dict(
            valid_ruleset,
            conditions={"ref_name": {"include": ["refs/tags/release-*"], "exclude": []}},
        )
        res = verify_ruleset_payload([wrong_pat_rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")



if __name__ == "__main__":
    unittest.main()
