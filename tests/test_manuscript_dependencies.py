"""Real package interface and exact-ref checks for manuscript handoffs."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "skills/writing/manuscript-ops/scripts/check_dependencies.py"
CATALOGS = [ROOT / "skills/thinking", ROOT / "skills/review", ROOT / "skills/engineering"]


class ManuscriptDependencyTests(unittest.TestCase):
    def run_check(self, *extra: str) -> tuple[int, dict]:
        args = [sys.executable, str(CHECKER)]
        for catalog in CATALOGS:
            args.extend(["--catalog", str(catalog)])
        args.extend(extra)
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        return result.returncode, json.loads(result.stdout)

    def test_current_categorized_packages_are_ready_offline(self) -> None:
        code, result = self.run_check()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "READY")
        self.assertIn("catalog:socratic", result["checks"])

    def test_exact_ref_is_required_for_online_byte_comparison(self) -> None:
        code, result = self.run_check("--online")
        self.assertEqual(code, 2)
        self.assertIn("--online requires --ref", result["errors"][0])
        code, result = self.run_check("--online", "--ref", "main")
        self.assertEqual(code, 2)
        self.assertIn("exact commit SHA or release tag", result["errors"][0])

    def test_missing_required_interface_blocks(self) -> None:
        registry = json.loads((ROOT / "skills/writing/manuscript-ops/assets/dependency-contracts.json").read_text())
        registry["dependencies"][0]["required_files"].append("scripts/nonexistent.py")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(registry))
            code, result = self.run_check("--registry", str(path))
        self.assertEqual(code, 2)
        self.assertTrue(any("nonexistent.py" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
