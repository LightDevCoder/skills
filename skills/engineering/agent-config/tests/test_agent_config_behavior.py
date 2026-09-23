"""Behavior checks against the shipped agent-config CLI and installed package."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"


class AgentConfigBehaviorTest(unittest.TestCase):
    def invoke(self, host: dict, profile: dict) -> dict:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/agent_config.py"),
             "--host-json", json.dumps(host), "--profile-json", json.dumps(profile),
             "--task-json", json.dumps({"difficulty": "high", "difficulty_source": "explicit-user"}),
             "--no-jev"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_empty_host_and_profile_never_return_ready(self) -> None:
        result = self.invoke({}, {})
        self.assertEqual(result["readiness"], "NEED_INPUT")
        self.assertIsNone(result["execution_config"])

    def test_canonical_host_and_profile_drive_real_cli(self) -> None:
        host = json.loads((FIXTURES / "case-a-tiered-single-pass.json").read_text())
        profile = json.loads((FIXTURES / "profile-multi-model.json").read_text())
        now = datetime.now(timezone.utc).isoformat()
        host["observed_at"] = now
        host["workspace"] = profile["scope"]["workspace"]
        for model in host["available_models"]:
            model["evidence"]["observed_at"] = now
        for capability in host["capabilities"].values():
            if capability.get("evidence"):
                capability["evidence"]["observed_at"] = now
        result = self.invoke(host, profile)
        self.assertEqual(result["readiness"], "READY")
        self.assertEqual(result["execution_config"]["model"], "model-gamma")

    @unittest.skipIf(os.environ.get("AGENT_CONFIG_INSTALLED_COPY") == "1", "already running in isolated copy")
    def test_isolated_installed_copy_runs_the_full_package_suite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="agent-config-installed-") as directory:
            destination = Path(directory) / "skills/engineering/agent-config"
            destination.parent.mkdir(parents=True)
            shutil.copytree(ROOT, destination)
            environment = dict(os.environ, AGENT_CONFIG_INSTALLED_COPY="1")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(destination / "tests"), "-p", "test_*.py"],
                capture_output=True, text=True, check=False, env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
