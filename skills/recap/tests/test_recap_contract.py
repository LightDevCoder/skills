"""Port of skills/recap/tests/recap-contract-tests.ps1."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_helpers import Checks  # noqa: E402


def test_recap_safety_contract(text: str) -> bool:
    forbids_compaction = bool(re.search(r"(?is)(do not|does not|never)[^\r\n]{0,120}compact", text))
    forbids_implicit_handoff = "`recap` never invokes either capability" in text
    return forbids_compaction and forbids_implicit_handoff


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill = (root / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    metadata = (root / "agents" / "openai.yaml").read_text(encoding="utf-8", errors="replace")

    c.check(bool(re.search(r"(?m)^name:\s*recap\s*$", skill)), "frontmatter name is recap")
    c.check(bool(re.search(r"(?m)^disable-model-invocation:\s*true\s*$", skill)), "Claude metadata disables model invocation")
    c.check(bool(re.search(r"explicit `\$recap`|explicit \$recap", skill)), "contract requires explicit invocation")
    c.check("exactly one non-empty line" in skill, "contract requires one non-empty line")
    c.check("Do not call tools" in skill, "contract forbids tool calls")
    c.check(test_recap_safety_contract(skill), "contract forbids compaction and implicit handoffs")
    unsafe_mutation = skill.replace("`recap` never invokes either capability", "`recap` invokes either capability automatically")
    c.check(not test_recap_safety_contract(unsafe_mutation), "opposite-polarity handoff mutation is rejected")
    c.check("`review-loop`" in skill, "contract preserves explicit final-review handoff")
    c.check(bool(re.search(r'display_name:\s*"Session Recap"', metadata)), "metadata has display name")
    c.check(bool(re.search(r'short_description:\s*"[^"]{25,64}"', metadata)), "metadata has bounded short description")
    c.check(bool(re.search(r'default_prompt:\s*"Use \$recap', metadata)), "metadata default prompt invokes recap explicitly")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", metadata)), "Codex metadata disables implicit invocation")

    return c.assertions, c.failures


class RecapContractTest(unittest.TestCase):
    def test_recap_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertFalse(failures, f"RECAP_CONTRACT=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
