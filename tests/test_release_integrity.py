"""Unit and behavior tests for scripts/verify_release_integrity.py."""

from __future__ import annotations

import json
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
    resolve_tag_object_sha,
    resolve_annotated_tag_identity,
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
            "bypass_actors": [],
            "current_user_can_bypass": "never",
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

    def test_canonical_vstar_ruleset_passes(self) -> None:
        """Canonical ruleset protecting refs/tags/v* with deletion/update rules passes."""
        valid_ruleset = {
            "id": 23728847,
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
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([valid_ruleset])
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")

    def test_exact_single_version_include_fails(self) -> None:
        """Ruleset including only a single version tag fails because it does not protect the namespace."""
        rs = {
            "id": 1,
            "name": "Single Version Only",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v0.2.4"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_missing_update_rule_fails(self) -> None:
        """Ruleset missing the update restriction fails."""
        rs = {
            "id": 1,
            "name": "Missing Update",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}],
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("update", res.message)

    def test_missing_deletion_rule_fails(self) -> None:
        """Ruleset missing the deletion restriction fails."""
        rs = {
            "id": 1,
            "name": "Missing Deletion",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "update"}],
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("deletion", res.message)

    def test_inactive_ruleset_fails(self) -> None:
        """Ruleset with disabled enforcement fails."""
        rs = {
            "id": 1,
            "name": "Disabled Protection",
            "target": "tag",
            "enforcement": "disabled",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_branch_target_fails(self) -> None:
        """Ruleset targeting branch instead of tag fails."""
        rs = {
            "id": 1,
            "name": "Branch Protection",
            "target": "branch",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_release_namespace_excluded_fails(self) -> None:
        """Ruleset excluding refs/tags/v* fails."""
        rs = {
            "id": 1,
            "name": "Namespace Excluded",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": ["refs/tags/v*"]}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_narrow_release_exclude_fails(self) -> None:
        """Ruleset excluding a specific release tag fails."""
        rs = {
            "id": 1,
            "name": "Narrow Release Excluded",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": ["refs/tags/v0.2.4"]}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_bypass_actor_fails(self) -> None:
        """Ruleset with bypass actors fails."""
        rs = {
            "id": 1,
            "name": "Bypass Actor Present",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [{"actor_id": 1, "actor_type": "Integration"}],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_current_user_bypass_fails(self) -> None:
        """Ruleset allowing current user bypass fails."""
        rs = {
            "id": 1,
            "name": "Current User Bypass",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [],
            "current_user_can_bypass": "always",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")

    def test_missing_bypass_actors_blocks(self) -> None:
        """Ruleset missing bypass_actors information must fail closed and be BLOCKED."""
        rs = {
            "id": 1,
            "name": "Missing Bypass Actors",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("bypass_actors", res.message)

    def test_missing_current_user_can_bypass_blocks(self) -> None:
        """Ruleset missing current_user_can_bypass must fail closed and be BLOCKED."""
        rs = {
            "id": 1,
            "name": "Missing Current User Bypass",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [],
        }
        res = verify_ruleset_payload([rs])
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "BLOCKED")
        self.assertIn("current_user_can_bypass", res.message)

    def test_empty_bypass_and_never_pass(self) -> None:
        """Ruleset with empty bypass_actors and never current_user_can_bypass passes."""
        rs = {
            "id": 1,
            "name": "Strict Zero Bypass",
            "target": "tag",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "rules": [{"type": "deletion"}, {"type": "update"}],
            "bypass_actors": [],
            "current_user_can_bypass": "never",
        }
        res = verify_ruleset_payload([rs])
        self.assertTrue(res.passed)
        self.assertEqual(res.status, "PASS")

    def test_single_version_include_blocks(self) -> None:
        """Single version include blocks publication gate."""
        self.test_exact_single_version_include_fails()

    def test_release_namespace_exclude_blocks(self) -> None:
        """Release namespace exclude blocks publication gate."""
        self.test_release_namespace_excluded_fails()

    def test_inactive_ruleset_blocks(self) -> None:
        """Inactive ruleset blocks publication gate."""
        self.test_inactive_ruleset_fails()

    def test_missing_update_blocks(self) -> None:
        """Missing update rule blocks publication gate."""
        self.test_missing_update_rule_fails()

    def test_missing_deletion_blocks(self) -> None:
        """Missing deletion rule blocks publication gate."""
        self.test_missing_deletion_rule_fails()


def make_valid_receipt_en(
    tag: str = "v0.2.4",
    tag_obj: str = "1111111111111111111111111111111111111111",
    tag_target: str = "2222222222222222222222222222222222222222",
    pkg_count: int = 1,
    status: str = "VERIFIED",
    ci_status: str = "PASS",
    pinned_status: str = "PASS",
    latest_status: str = "PASS",
    release_pub_status: str = "PASS",
    release_url: str | None = None,
    timestamp: str = "2026-09-21T00:00:00Z",
) -> str:
    url = release_url or f"https://github.com/LightDevCoder/skills/releases/tag/{tag}"
    return f"""# LightDevCoder/skills {tag} Release Receipt

[中文收据](RELEASE_RECEIPT.zh-CN.md)

Status: `{status}` — Formally published and attested on `main`.

## Identity

| Field | Value |
| :--- | :--- |
| **Repository** | `LightDevCoder/skills` (public) |
| **Release** | `{tag}` |
| **Release Tag** | `{tag}` |
| **Annotated Tag Object** | `{tag_obj}` |
| **Tag Target Commit** | `{tag_target}` |
| **Release URL** | {url} |
| **Publication Timestamp** | `{timestamp}` |
| **Collection Package Count** | {pkg_count} admitted packages |
| **Policy Status** | `PROVISIONAL` |

## Verification Checklist

| Gate | Status | Evidence |
| :--- | :--- | :--- |
| **GitHub Actions CI (`collection-quality`)** | `{ci_status}` | Clean run |
| **Pinned Fresh Install** | `{pinned_status}` | All packages installed |
| **Generic Latest Fresh Install** | `{latest_status}` | All packages installed |
| **GitHub Release Publication** | `{release_pub_status}` | Published |
"""


def make_valid_receipt_zh(
    tag: str = "v0.2.4",
    tag_obj: str = "1111111111111111111111111111111111111111",
    tag_target: str = "2222222222222222222222222222222222222222",
    pkg_count: int = 1,
    status: str = "VERIFIED",
    ci_status: str = "PASS",
    pinned_status: str = "PASS",
    latest_status: str = "PASS",
    release_pub_status: str = "PASS",
    release_url: str | None = None,
    timestamp: str = "2026-09-21T00:00:00Z",
) -> str:
    url = release_url or f"https://github.com/LightDevCoder/skills/releases/tag/{tag}"
    return f"""# LightDevCoder/skills {tag} 发布收据

[English Version](RELEASE_RECEIPT.md)

状态：`{status}` — 已正式公开发布，并在 `main` 完成事实证明。

## 发布身份

| 属性 | 记录值 |
| :--- | :--- |
| **代码仓库** | `LightDevCoder/skills`（公开仓库） |
| **发布版本** | `{tag}` |
| **发布 Tag** | `{tag}` |
| **Annotated Tag 对象** | `{tag_obj}` |
| **Tag 目标 Commit** | `{tag_target}` |
| **发布 URL** | {url} |
| **公开发布时间戳** | `{timestamp}` |
| **集合包总数** | {pkg_count} admitted packages |
| **政策状态** | `PROVISIONAL` |

## 验证核对清单

| 检查门禁 | 状态 | 验证证据 |
| :--- | :--- | :--- |
| **GitHub Actions CI (`collection-quality`)** | `{ci_status}` | 全绿通过 |
| **锁定版本全量全新安装** | `{pinned_status}` | 全部成功安装 |
| **最新主干全量全新安装** | `{latest_status}` | 全部成功安装 |
| **GitHub Release 发布** | `{release_pub_status}` | 已发布 |
"""


class ReceiptStrictValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="receipt-strict-test-")
        self.tmp_root = Path(self.tmp.name)
        # Create a mock admitted package so admitted package count is 1
        pkg_dir = self.tmp_root / "skills" / "cat" / "pkg"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "SKILL.md").write_text("# Mock", encoding="utf-8")
        self.rel_dir = self.tmp_root / "docs" / "evidence" / "releases" / "v0.2.4"
        self.rel_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_attested_receipt_candidate_status_rejected(self) -> None:
        """CANDIDATE status in receipt is strictly rejected in attested stage (v0.2.4+)."""
        en = make_valid_receipt_en(status="CANDIDATE")
        zh = make_valid_receipt_zh(status="CANDIDATE")
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_STATUS_INVALID")

    def test_attested_receipt_missing_tag_object_rejected(self) -> None:
        """Missing Annotated Tag Object in receipt is rejected."""
        en = make_valid_receipt_en().replace("| **Annotated Tag Object** | `1111111111111111111111111111111111111111` |\n", "")
        zh = make_valid_receipt_zh()
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_TAG_OBJECT_MISSING")

    def test_attested_receipt_missing_tag_target_rejected(self) -> None:
        """Missing Tag Target Commit in receipt is rejected."""
        en = make_valid_receipt_en().replace("| **Tag Target Commit** | `2222222222222222222222222222222222222222` |\n", "")
        zh = make_valid_receipt_zh()
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_TAG_TARGET_MISSING")

    def test_attested_receipt_missing_publication_timestamp_rejected(self) -> None:
        """Missing Publication Timestamp in receipt is rejected."""
        en = make_valid_receipt_en().replace("| **Publication Timestamp** | `2026-09-21T00:00:00Z` |\n", "")
        zh = make_valid_receipt_zh()
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_TIMESTAMP_MISSING")

    def test_attested_receipt_pending_ci_rejected(self) -> None:
        """Pending CI conclusion in receipt is rejected."""
        en = make_valid_receipt_en(ci_status="PENDING")
        zh = make_valid_receipt_zh(ci_status="PENDING")
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_EVIDENCE_PENDING")

    def test_attested_receipt_pending_pinned_install_rejected(self) -> None:
        """Pending pinned install in receipt is rejected."""
        en = make_valid_receipt_en(pinned_status="PENDING")
        zh = make_valid_receipt_zh(pinned_status="PENDING")
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_EVIDENCE_PENDING")

    def test_attested_receipt_pending_latest_install_rejected(self) -> None:
        """Pending latest install in receipt is rejected."""
        en = make_valid_receipt_en(latest_status="PENDING")
        zh = make_valid_receipt_zh(latest_status="PENDING")
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_EVIDENCE_PENDING")

    def test_attested_receipt_wrong_tag_object_rejected(self) -> None:
        """Mismatched tag object SHA in receipt is rejected."""
        subprocess.run(["git", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.tmp_root, capture_output=True, check=True)
        (self.tmp_root / "dummy.txt").write_text("v1", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "tag", "-a", "v0.2.4", "-m", "v0.2.4"], cwd=self.tmp_root, capture_output=True, check=True)

        actual_peel = resolve_tag_sha("v0.2.4", cwd=self.tmp_root)
        bogus_obj = "0000000000000000000000000000000000000000"

        en = make_valid_receipt_en(tag_obj=bogus_obj, tag_target=actual_peel)
        zh = make_valid_receipt_zh(tag_obj=bogus_obj, tag_target=actual_peel)
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_TAG_OBJECT_MISMATCH")

    def test_attested_receipt_wrong_tag_target_rejected(self) -> None:
        """Mismatched target commit SHA in receipt is rejected."""
        subprocess.run(["git", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.tmp_root, capture_output=True, check=True)
        (self.tmp_root / "dummy.txt").write_text("v1", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "tag", "-a", "v0.2.4", "-m", "v0.2.4"], cwd=self.tmp_root, capture_output=True, check=True)

        actual_obj = resolve_tag_object_sha("v0.2.4", cwd=self.tmp_root)
        bogus_target = "0000000000000000000000000000000000000000"

        en = make_valid_receipt_en(tag_obj=actual_obj, tag_target=bogus_target)
        zh = make_valid_receipt_zh(tag_obj=actual_obj, tag_target=bogus_target)
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_TAG_TARGET_MISMATCH")

    def test_attested_receipt_wrong_release_url_rejected(self) -> None:
        """Wrong release URL in receipt is rejected."""
        bogus_url = "https://github.com/LightDevCoder/skills/releases/tag/v0.2.3"
        en = make_valid_receipt_en(release_url=bogus_url)
        zh = make_valid_receipt_zh(release_url=bogus_url)
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", repo_root=self.tmp_root)
        self.assertFalse(res.passed)
        self.assertEqual(res.status, "RECEIPT_URL_MISMATCH")

    def test_annotated_release_tag_passes(self) -> None:
        """Annotated release tag passes receipt verification when SHAs match."""
        subprocess.run(["git", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.tmp_root, capture_output=True, check=True)
        (self.tmp_root / "test.txt").write_text("ok", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "candidate"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "tag", "-a", "v0.2.4", "-m", "release v0.2.4"], cwd=self.tmp_root, capture_output=True, check=True)

        tag_ident = resolve_annotated_tag_identity("v0.2.4", cwd=self.tmp_root)
        self.assertTrue(tag_ident.is_annotated)
        self.assertEqual(tag_ident.tag_type, "tag")

        en = make_valid_receipt_en(tag_obj=tag_ident.tag_object_sha, tag_target=tag_ident.peeled_commit_sha)
        zh = make_valid_receipt_zh(tag_obj=tag_ident.tag_object_sha, tag_target=tag_ident.peeled_commit_sha)
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        res = check_release_receipt_consistency("v0.2.4", release_commit=tag_ident.peeled_commit_sha, repo_root=self.tmp_root)
        self.assertTrue(res.passed, f"Expected PASS but got {res.status}: {res.message}")
        self.assertEqual(res.status, "PASS")

    def test_lightweight_release_tag_rejected(self) -> None:
        """Lightweight release tag (git tag without -a) is rejected as RELEASE_TAG_NOT_ANNOTATED."""
        subprocess.run(["git", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.tmp_root, capture_output=True, check=True)
        (self.tmp_root / "test.txt").write_text("ok", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "candidate"], cwd=self.tmp_root, capture_output=True, check=True)
        cand_sha = resolve_commit_sha("HEAD", cwd=self.tmp_root)

        # Create LIGHTWEIGHT tag (no -a)
        subprocess.run(["git", "tag", "v0.2.4"], cwd=self.tmp_root, capture_output=True, check=True)

        tag_ident = resolve_annotated_tag_identity("v0.2.4", cwd=self.tmp_root)
        self.assertFalse(tag_ident.is_annotated)
        self.assertEqual(tag_ident.tag_type, "commit")

        en = make_valid_receipt_en(tag_obj=cand_sha, tag_target=cand_sha)
        zh = make_valid_receipt_zh(tag_obj=cand_sha, tag_target=cand_sha)
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh, encoding="utf-8")

        # check_release_receipt_consistency rejects lightweight tag
        res_receipt = check_release_receipt_consistency("v0.2.4", release_commit=cand_sha, repo_root=self.tmp_root)
        self.assertFalse(res_receipt.passed)
        self.assertEqual(res_receipt.status, "RELEASE_TAG_NOT_ANNOTATED")

        # check_tag_immutability also rejects lightweight tag in stage=tagged
        res_immut = check_tag_immutability("v0.2.4", cand_sha, stage="tagged", cwd=self.tmp_root)
        self.assertFalse(res_immut.passed)
        self.assertEqual(res_immut.status, "LIGHTWEIGHT_TAG_FORBIDDEN")

    def test_receipt_tag_object_must_match_real_annotated_tag_object(self) -> None:
        """Receipt Annotated Tag Object must match real tag object SHA."""
        self.test_attested_receipt_wrong_tag_object_rejected()

    def test_receipt_target_commit_must_match_peeled_commit(self) -> None:
        """Receipt Tag Target Commit must match actual peeled commit SHA."""
        self.test_attested_receipt_wrong_tag_target_rejected()

    def test_attested_main_head_may_differ_from_release_candidate(self) -> None:
        """Crucial regression: attested gate passes when main HEAD is an attestation commit later than the candidate commit."""
        subprocess.run(["git", "init"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.tmp_root, capture_output=True, check=True)

        # 1. Candidate commit A with Manifest and Notes
        manifest_en = (
            "# Manifest v0.2.4\nRelease: `v0.2.4`\nRelease identity: `refs/tags/v0.2.4^{commit}`\n"
            "Collection package count: 1 admitted packages\nPolicy status: `PROVISIONAL`\n"
        )
        manifest_zh = (
            "# 清单 v0.2.4\n发布版本：`v0.2.4`\n发布身份：`refs/tags/v0.2.4^{commit}`\n"
            "集合包总数：1 个\n政策状态：`PROVISIONAL`\n"
        )
        (self.rel_dir / "RELEASE_MANIFEST.md").write_text(manifest_en, encoding="utf-8")
        (self.rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(manifest_zh, encoding="utf-8")
        (self.rel_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
        (self.rel_dir / "RELEASE_NOTES.zh-CN.md").write_text("# 说明", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "release: prepare v0.2.4"], cwd=self.tmp_root, capture_output=True, check=True)
        commit_a = resolve_commit_sha("HEAD", cwd=self.tmp_root)

        # 2. Tag v0.2.4 -> Commit A
        subprocess.run(["git", "tag", "-a", "v0.2.4", "-m", "v0.2.4"], cwd=self.tmp_root, capture_output=True, check=True)
        tag_obj_a = resolve_tag_object_sha("v0.2.4", cwd=self.tmp_root)
        self.assertIsNotNone(tag_obj_a)

        # 3. Attestation commit B: create verified receipts and update docs
        en_receipt = make_valid_receipt_en(tag_obj=tag_obj_a, tag_target=commit_a)
        zh_receipt = make_valid_receipt_zh(tag_obj=tag_obj_a, tag_target=commit_a)
        (self.rel_dir / "RELEASE_RECEIPT.md").write_text(en_receipt, encoding="utf-8")
        (self.rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh_receipt, encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=self.tmp_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "docs(release): attest v0.2.4 publication"], cwd=self.tmp_root, capture_output=True, check=True)
        commit_b = resolve_commit_sha("HEAD", cwd=self.tmp_root)

        # Prove Commit B != Commit A
        self.assertNotEqual(commit_a, commit_b)

        # 4. Verify stage=attested with release_commit=commit_a
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_release_integrity.py"),
                "--tag", "v0.2.4",
                "--release-commit", commit_a,
                "--stage", "attested",
            ],
            cwd=self.tmp_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Expected PASS but got exit {proc.returncode}:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("RESULT: PASS", proc.stdout)

    def test_synthetic_future_release_lifecycle_e2e(self) -> None:
        """Full synthetic lifecycle: PREPARED -> TAGGED -> ATTESTED, plus negative controls."""
        with tempfile.TemporaryDirectory(prefix="e2e-synthetic-") as tmp:
            tmp_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_root, capture_output=True, check=True)

            # Setup 1 admitted package
            pkg_dir = tmp_root / "skills" / "cat" / "pkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Synthetic Skill", encoding="utf-8")

            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v9.9.9"
            rel_dir.mkdir(parents=True)

            manifest_en = (
                "# Manifest v9.9.9\n"
                "[中文清单](RELEASE_MANIFEST.zh-CN.md) · [Release Notes](RELEASE_NOTES.md)\n\n"
                "Release: `v9.9.9`\nRelease identity: `refs/tags/v9.9.9^{commit}`\n"
                "Collection package count: 1 admitted packages\nPolicy status: `PROVISIONAL`\n\n"
                "Post-publication verification is attested on main in RELEASE_RECEIPT.md.\n"
            )
            manifest_zh = (
                "# 清单 v9.9.9\n"
                "发布版本：`v9.9.9`\n发布身份：`refs/tags/v9.9.9^{commit}`\n"
                "集合包总数：1 个\n政策状态：`PROVISIONAL`\n"
            )
            (rel_dir / "RELEASE_MANIFEST.md").write_text(manifest_en, encoding="utf-8")
            (rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(manifest_zh, encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.zh-CN.md").write_text("# 说明", encoding="utf-8")

            # Commit A: candidate commit
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "release: prepare v9.9.9"], cwd=tmp_root, capture_output=True, check=True)
            commit_a = resolve_commit_sha("HEAD", cwd=tmp_root)

            # 1. Stage PREPARED on Commit A passes
            proc_prep = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", "HEAD",
                    "--stage", "prepared",
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_prep.returncode, 0, f"PREPARED failed:\n{proc_prep.stdout}\n{proc_prep.stderr}")
            self.assertIn("RESULT: PASS", proc_prep.stdout)

            # 2. Tag v9.9.9 -> Commit A
            subprocess.run(["git", "tag", "-a", "v9.9.9", "-m", "v9.9.9"], cwd=tmp_root, capture_output=True, check=True)
            tag_obj_a = resolve_tag_object_sha("v9.9.9", cwd=tmp_root)

            # Stage TAGGED on tag->A passes
            proc_tagged = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", commit_a,
                    "--stage", "tagged",
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_tagged.returncode, 0, f"TAGGED failed:\n{proc_tagged.stdout}\n{proc_tagged.stderr}")
            self.assertIn("RESULT: PASS", proc_tagged.stdout)

            # 3. Create Receipt on main and Commit B
            en_receipt = make_valid_receipt_en(tag="v9.9.9", tag_obj=tag_obj_a, tag_target=commit_a)
            zh_receipt = make_valid_receipt_zh(tag="v9.9.9", tag_obj=tag_obj_a, tag_target=commit_a)
            (rel_dir / "RELEASE_RECEIPT.md").write_text(en_receipt, encoding="utf-8")
            (rel_dir / "RELEASE_RECEIPT.zh-CN.md").write_text(zh_receipt, encoding="utf-8")

            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "docs(release): attest v9.9.9 publication"], cwd=tmp_root, capture_output=True, check=True)
            commit_b = resolve_commit_sha("HEAD", cwd=tmp_root)
            self.assertNotEqual(commit_a, commit_b)

            # Stage ATTESTED on HEAD=B with release_commit=commit_a passes
            proc_attested = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", commit_a,
                    "--stage", "attested",
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_attested.returncode, 0, f"ATTESTED failed:\n{proc_attested.stdout}\n{proc_attested.stderr}")
            self.assertIn("RESULT: PASS", proc_attested.stdout)

            # Negative Control 1: candidate Receipt
            (rel_dir / "RELEASE_RECEIPT.md").write_text(
                make_valid_receipt_en(tag="v9.9.9", tag_obj=tag_obj_a, tag_target=commit_a, status="CANDIDATE"),
                encoding="utf-8",
            )
            res_cand = check_release_receipt_consistency("v9.9.9", release_commit=commit_a, repo_root=tmp_root)
            self.assertFalse(res_cand.passed)
            self.assertEqual(res_cand.status, "RECEIPT_STATUS_INVALID")

            # Negative Control 2: missing Receipt field
            (rel_dir / "RELEASE_RECEIPT.md").write_text(
                en_receipt.replace(f"| **Annotated Tag Object** | `{tag_obj_a}` |\n", ""),
                encoding="utf-8",
            )
            res_missing = check_release_receipt_consistency("v9.9.9", release_commit=commit_a, repo_root=tmp_root)
            self.assertFalse(res_missing.passed)
            self.assertEqual(res_missing.status, "RECEIPT_TAG_OBJECT_MISSING")

            # Negative Control 3: wrong tag SHA
            (rel_dir / "RELEASE_RECEIPT.md").write_text(
                make_valid_receipt_en(tag="v9.9.9", tag_obj="0000000000000000000000000000000000000000", tag_target=commit_a),
                encoding="utf-8",
            )
            res_wrong_sha = check_release_receipt_consistency("v9.9.9", release_commit=commit_a, repo_root=tmp_root)
            self.assertFalse(res_wrong_sha.passed)
            self.assertEqual(res_wrong_sha.status, "RECEIPT_TAG_OBJECT_MISMATCH")

            # Negative Control 4: wrong target commit
            (rel_dir / "RELEASE_RECEIPT.md").write_text(
                make_valid_receipt_en(tag="v9.9.9", tag_obj=tag_obj_a, tag_target="0000000000000000000000000000000000000000"),
                encoding="utf-8",
            )
            res_wrong_target = check_release_receipt_consistency("v9.9.9", release_commit=commit_a, repo_root=tmp_root)
            self.assertFalse(res_wrong_target.passed)
            self.assertEqual(res_wrong_target.status, "RECEIPT_TAG_TARGET_MISMATCH")

            # Negative Control 5: relative Receipt link in Manifest
            (rel_dir / "RELEASE_MANIFEST.md").write_text(
                manifest_en + "\n[Receipt](RELEASE_RECEIPT.md)\n",
                encoding="utf-8",
            )
            res_rel_link = check_manifest_navigation("v9.9.9", repo_root=tmp_root)
            self.assertFalse(res_rel_link.passed)
            self.assertEqual(res_rel_link.status, "RELATIVE_RECEIPT_LINK_FORBIDDEN")


class ReleaseWorkflowSequenceTests(unittest.TestCase):
    """Synthetic E2E testing matching the exact SKILL.md execution order."""

    def test_synthetic_prepared_sequence_real_order(self) -> None:
        """PREPARED sequence: pre-commit checks -> commit candidate -> verify prepared PASS.

        Negative control: calling verify prepared before commit must FAIL DIRTY_TREE.
        """
        with tempfile.TemporaryDirectory(prefix="e2e-prepared-seq-") as tmp:
            tmp_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_root, capture_output=True, check=True)

            # Base commit tracking docs
            (tmp_root / "README.md").write_text("# Collection\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_root, capture_output=True, check=True)

            # Prepare candidate files: update candidate docs, write Manifest, write Notes
            (tmp_root / "README.md").write_text("# Collection (Candidate v9.9.9)\n", encoding="utf-8")
            pkg_dir = tmp_root / "skills" / "cat" / "pkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")

            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v9.9.9"
            rel_dir.mkdir(parents=True)
            manifest_en = (
                "# Manifest v9.9.9\nRelease: `v9.9.9`\nRelease identity: `refs/tags/v9.9.9^{commit}`\n"
                "Collection package count: 1 admitted packages\nPolicy status: `PROVISIONAL`\n"
            )
            manifest_zh = (
                "# 清单 v9.9.9\n发布版本：`v9.9.9`\n发布身份：`refs/tags/v9.9.9^{commit}`\n"
                "集合包总数：1 个\n政策状态：`PROVISIONAL`\n"
            )
            (rel_dir / "RELEASE_MANIFEST.md").write_text(manifest_en, encoding="utf-8")
            (rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(manifest_zh, encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.zh-CN.md").write_text("# 说明", encoding="utf-8")

            # Assert working tree is dirty
            proc_diff = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_root, capture_output=True, text=True)
            self.assertTrue(proc_diff.stdout.strip())

            # NEGATIVE: calling verify --stage prepared before commit must FAIL (DIRTY_TREE)
            proc_neg = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", "HEAD",
                    "--stage", "prepared",
                    "--root", str(tmp_root),
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_neg.returncode, 0)
            self.assertIn("DIRTY_TREE", proc_neg.stdout)

            # Pre-commit checks run, then commit candidate
            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "release: prepare v9.9.9"], cwd=tmp_root, capture_output=True, check=True)
            candidate_a = resolve_commit_sha("HEAD", cwd=tmp_root)

            # POSITIVE: on clean working tree with committed candidate, verify prepared PASSES
            proc_pos = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", candidate_a,
                    "--stage", "prepared",
                    "--root", str(tmp_root),
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_pos.returncode, 0, f"PREPARED failed:\n{proc_pos.stdout}\n{proc_pos.stderr}")
            self.assertIn("RESULT: PASS", proc_pos.stdout)

    def test_synthetic_tagged_sequence_real_order(self) -> None:
        """TAGGED sequence: candidate commit -> tag preflight -> create annotated tag -> verify tagged PASS.

        Negative control: calling verify tagged before tag exists must FAIL TAG_MISSING.
        Negative control: lightweight tag must FAIL LIGHTWEIGHT_TAG_FORBIDDEN.
        """
        with tempfile.TemporaryDirectory(prefix="e2e-tagged-seq-") as tmp:
            tmp_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_root, capture_output=True, check=True)

            pkg_dir = tmp_root / "skills" / "cat" / "pkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Skill", encoding="utf-8")

            rel_dir = tmp_root / "docs" / "evidence" / "releases" / "v9.9.9"
            rel_dir.mkdir(parents=True)
            manifest_en = (
                "# Manifest v9.9.9\nRelease: `v9.9.9`\nRelease identity: `refs/tags/v9.9.9^{commit}`\n"
                "Collection package count: 1 admitted packages\nPolicy status: `PROVISIONAL`\n"
            )
            manifest_zh = (
                "# 清单 v9.9.9\n发布版本：`v9.9.9`\n发布身份：`refs/tags/v9.9.9^{commit}`\n"
                "集合包总数：1 个\n政策状态：`PROVISIONAL`\n"
            )
            (rel_dir / "RELEASE_MANIFEST.md").write_text(manifest_en, encoding="utf-8")
            (rel_dir / "RELEASE_MANIFEST.zh-CN.md").write_text(manifest_zh, encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.md").write_text("# Notes", encoding="utf-8")
            (rel_dir / "RELEASE_NOTES.zh-CN.md").write_text("# 说明", encoding="utf-8")

            subprocess.run(["git", "add", "."], cwd=tmp_root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "release: prepare v9.9.9"], cwd=tmp_root, capture_output=True, check=True)
            candidate_a = resolve_commit_sha("HEAD", cwd=tmp_root)

            # NEGATIVE 1: calling verify tagged before tag exists must FAIL (TAG_MISSING)
            proc_neg_notag = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", candidate_a,
                    "--stage", "tagged",
                    "--root", str(tmp_root),
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_neg_notag.returncode, 0)
            self.assertIn("TAG_MISSING", proc_neg_notag.stdout)

            # Fixture ruleset with strict compliance
            valid_ruleset = {
                "id": 1,
                "name": "Protect Release Tags",
                "target": "tag",
                "enforcement": "active",
                "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
                "rules": [{"type": "deletion"}, {"type": "update"}],
                "bypass_actors": [],
                "current_user_can_bypass": "never",
            }
            fixture_file = tmp_root / "ruleset_fixture.json"
            fixture_file.write_text(json.dumps([valid_ruleset]), encoding="utf-8")

            # Run tag preflight
            proc_preflight = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "check_release_tag_preflight.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", candidate_a,
                    "--fixture", str(fixture_file),
                    "--root", str(tmp_root),
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_preflight.returncode, 0, f"Preflight failed:\n{proc_preflight.stdout}\n{proc_preflight.stderr}")
            self.assertIn("RESULT: PASS", proc_preflight.stdout)

            # Create annotated tag
            subprocess.run(["git", "tag", "-a", "v9.9.9", "-m", "v9.9.9"], cwd=tmp_root, capture_output=True, check=True)

            # Validate tagged state
            proc_pos_tagged = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9",
                    "--release-commit", candidate_a,
                    "--stage", "tagged",
                    "--root", str(tmp_root),
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_pos_tagged.returncode, 0, f"TAGGED failed:\n{proc_pos_tagged.stdout}\n{proc_pos_tagged.stderr}")
            self.assertIn("RESULT: PASS", proc_pos_tagged.stdout)

            # Verify tag object is annotated ('tag') and peeled commit is candidate_a
            ident = resolve_annotated_tag_identity("v9.9.9", cwd=tmp_root)
            self.assertTrue(ident.is_annotated)
            self.assertEqual(ident.tag_type, "tag")
            self.assertEqual(ident.peeled_commit_sha, candidate_a)

            # NEGATIVE 2: lightweight tag is rejected in stage=tagged
            subprocess.run(["git", "tag", "v9.9.9-light"], cwd=tmp_root, capture_output=True, check=True)
            proc_neg_light = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify_release_integrity.py"),
                    "--tag", "v9.9.9-light",
                    "--release-commit", candidate_a,
                    "--stage", "tagged",
                    "--root", str(tmp_root),
                ],
                cwd=tmp_root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_neg_light.returncode, 0)
            self.assertIn("LIGHTWEIGHT_TAG_FORBIDDEN", proc_neg_light.stdout)

    def test_workflow_contract_skill_md_action_order(self) -> None:
        """Contract test for release-workflow/SKILL.md ensuring correct action sequence."""
        skill_text = (ROOT / "skills" / "project" / "release-workflow" / "SKILL.md").read_text(encoding="utf-8")

        # 1. Stage PREPARED: git commit candidate must appear BEFORE verify_release_integrity --stage prepared
        idx_prep_commit = skill_text.find('git commit -m "release: prepare vX.Y.Z"')
        idx_prep_verify = skill_text.find("--stage prepared")
        self.assertNotEqual(idx_prep_commit, -1, "Missing candidate commit in SKILL.md")
        self.assertNotEqual(idx_prep_verify, -1, "Missing verify --stage prepared in SKILL.md")
        self.assertLess(
            idx_prep_commit,
            idx_prep_verify,
            "In Stage PREPARED, candidate commit must be executed BEFORE verify --stage prepared",
        )

        # 2. Stage TAGGED: check_release_tag_preflight < git tag -a < verify --stage tagged < git push origin
        idx_preflight = skill_text.find("check_release_tag_preflight.py")
        idx_tag_a = skill_text.find('git tag -a vX.Y.Z -m "vX.Y.Z — <title>"')
        idx_tagged_verify = skill_text.find("--stage tagged")
        idx_tag_push = skill_text.find("git push origin vX.Y.Z")

        self.assertNotEqual(idx_preflight, -1, "Missing check_release_tag_preflight.py in SKILL.md")
        self.assertNotEqual(idx_tag_a, -1, "Missing git tag -a in SKILL.md")
        self.assertNotEqual(idx_tagged_verify, -1, "Missing verify --stage tagged in SKILL.md")
        self.assertNotEqual(idx_tag_push, -1, "Missing git push origin vX.Y.Z in SKILL.md")

        self.assertLess(idx_preflight, idx_tag_a, "check_release_tag_preflight must precede git tag -a")
        self.assertLess(idx_tag_a, idx_tagged_verify, "git tag -a must precede verify --stage tagged")
        self.assertLess(idx_tagged_verify, idx_tag_push, "verify --stage tagged must precede git push origin <tag>")

        # 3. Stage ATTESTED: verify --stage attested < push attestation commit
        idx_attested_verify = skill_text.find("--stage attested")
        idx_attest_push = skill_text.find("push the attestation commit to `origin/main`")
        self.assertNotEqual(idx_attested_verify, -1, "Missing verify --stage attested in SKILL.md")
        self.assertNotEqual(idx_attest_push, -1, "Missing push attestation commit in SKILL.md")
        self.assertLess(idx_attested_verify, idx_attest_push, "verify --stage attested must precede push attestation commit")



if __name__ == "__main__":
    unittest.main()
