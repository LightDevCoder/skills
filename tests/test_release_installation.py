"""Behavioral checks for the released-source installation verifier."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_installation", ROOT / "scripts/verify_release_installation.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleasedSourceInstallationTests(unittest.TestCase):
    def test_stable_identity_is_accepted(self):
        module.validate_identity("v0.2.7", "a" * 40)

    def test_bad_identity_is_rejected_before_commands(self):
        for tag in ("main", "v0.2.7;echo bad", "v0.2.7\n", "v0.2.7-rc1", "../v0.2.7"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                module.validate_identity(tag, "a" * 40)
        for commit in ("a" * 39, "G" * 40, "HEAD", "a" * 40 + "\n"):
            with self.subTest(commit=commit), self.assertRaises(ValueError):
                module.validate_identity("v0.2.7", commit)

    def test_global_installation_rejects_local_environment(self):
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}), self.assertRaises(ValueError):
            module.require_fresh_runner(Path("/private/tmp/unused-global-root"))

    def test_global_installation_rejects_existing_or_redirected_destinations(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(module.sys, "platform", "linux"), patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "CODEX_HOME": ""}):
            home = Path(tmp)
            module.require_fresh_runner(home)
            (home / ".codex/skills").mkdir(parents=True)
            with self.assertRaises(ValueError):
                module.require_fresh_runner(home)
            with patch.dict(os.environ, {"CODEX_HOME": str(home / "elsewhere")}), self.assertRaises(ValueError):
                module.require_fresh_runner(home)

    def test_complete_payload_and_symlink_are_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "source/skills/project/light-implement"
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text("---\nname: light-implement\n---\nExecute.\n")
            (package / "resource.txt").write_text("source-backed resource\n")
            expected = module.source_packages(root / "source")
            destination = root / "installed"
            destination.mkdir()
            (destination / "light-implement").symlink_to(package, target_is_directory=True)
            result = module.verify_destination(destination, expected)
            self.assertEqual((result["packages"], result["files"], result["exact"]), (1, 2, True))
            (package / "resource.txt").write_text("changed\n")
            with self.assertRaises(ValueError):
                module.verify_destination(destination, expected)

    def test_missing_extra_or_misidentified_packages_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination = root / "installed"
            destination.mkdir()
            with self.assertRaises(ValueError):
                module.verify_destination(destination, {"light-tdd": {"SKILL.md": "known-source-hash"}})
            (destination / "extra").mkdir()
            with self.assertRaises(ValueError):
                module.verify_destination(destination, {})
            (destination / "broken-alias").symlink_to(root / "absent")
            with self.assertRaises(ValueError):
                module.verify_destination(destination, {})
            package = root / "source/skills/engineering/light-tdd"
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text("---\nname: tdd\n---\n")
            with self.assertRaises(ValueError):
                module.source_packages(root / "source")


if __name__ == "__main__":
    unittest.main()
