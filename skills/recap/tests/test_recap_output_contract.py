"""Port of skills/recap/tests/recap-output-contract-tests.ps1."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402


def test_recap_line(text: str) -> bool:
    if not text or not text.strip():
        return False
    if re.search(r"[\r\n]", text):
        return False
    if re.search(r"^\s*(#|[-*+]\s)", text):
        return False
    if re.search(r"^\s*(?:\*\*)?[A-Za-z][A-Za-z -]{0,30}:(?:\*\*)?\s*", text):
        return False
    return True


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    success = "The recap Skill is installed with manual-only metadata, and repository admission checks are now in progress."
    no_context = "No prior session activity is available to recap."
    multiline = "Repository files were updated.\nNext: run the test suite."
    labeled = [
        "Recap: Repository files were updated.",
        "Status: Repository files were updated.",
        "Result: Repository files were updated.",
        "**Recap:** Repository files were updated.",
    ]

    c.check(test_recap_line(success), "success output is one unlabeled line")
    c.check("installed" in success and "in progress" in success, "success output includes outcome and current state")
    c.check(test_recap_line(no_context), "no-context boundary is a safe one-line result")
    c.check(not test_recap_line(multiline), "multiline output is rejected")
    for candidate in labeled:
        c.check(not test_recap_line(candidate), f"leading label is rejected: {candidate}")

    return c.assertions, c.failures


class RecapOutputContractTest(unittest.TestCase):
    def test_recap_output_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"RECAP_OUTPUT_CONTRACT=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
