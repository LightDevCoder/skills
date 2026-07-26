import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "skills" / "learn-anything" / "hooks" / "skill_candidate_builder.py"
GOOD = ROOT / "tests" / "fixtures" / "learn-anything-method.md"
BAD = ROOT / "tests" / "fixtures" / "learn-anything-incomplete.md"


class LearnAnythingHookTests(unittest.TestCase):
    assertions = 0

    def check(self, condition: bool, message: str) -> None:
        type(self).assertions += 1
        self.assertTrue(condition, message)

    def run_hook(self, source: Path) -> dict:
        result = subprocess.run(
            [sys.executable, str(HOOK), "--source-file", str(source)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_complete_source_returns_internal_contract(self) -> None:
        result = self.run_hook(GOOD)
        self.check(result["outcome"] == "method_contract", "complete source must produce a Method Contract")
        self.check(result["contract_visibility"] == "internal", "Method Contract remains internal")
        self.check(result["promotion_status"] == "eligible_for_package_build", "complete source reaches package-build boundary")
        self.check(result["method_contract"]["invocation_type"] == "user-invoked", "invocation type is preserved")

    def test_incomplete_source_blocks_without_invention(self) -> None:
        result = self.run_hook(BAD)
        self.check(result["outcome"] == "blocked", "incomplete source must block")
        self.check("triggers" in result["missing_information"], "missing trigger evidence is named")
        self.check(result["promotion_status"] == "not_promoted", "blocked source is not promoted")

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"LEARN_ANYTHING_HOOK_ASSERTIONS={cls.assertions}")


if __name__ == "__main__":
    unittest.main()
