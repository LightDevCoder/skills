"""Port of tests/quick-start-smoke-tests.ps1."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_helpers import Checks  # noqa: E402


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    for path in ("examples/quick-start/README.md", "examples/quick-start/README.zh-CN.md", "examples/quick-start/brief.md", "examples/quick-start/AGENTS.md"):
        c.check((root / path).is_file(), f"Quick Start file is missing: {path}")

    en = (root / "examples/quick-start/README.md").read_text(encoding="utf-8", errors="replace")
    zh = (root / "examples/quick-start/README.zh-CN.md").read_text(encoding="utf-8", errors="replace")
    brief = (root / "examples/quick-start/brief.md").read_text(encoding="utf-8", errors="replace")
    agents = (root / "examples/quick-start/AGENTS.md").read_text(encoding="utf-8", errors="replace")

    c.check(
        "npx skills add LightDevCoder/skills --yes --copy --agent '*'" in en
        and "npx skills add LightDevCoder/skills --skill ask-light" in en
        and "$ask-light next" in en
        and "$project-init" in en
        and "$review-loop" in en,
        "English Quick Start is missing a required command.",
    )
    c.check(
        "illustrative" in en and "nothing was invoked, installed, or orchestrated" in en,
        "English Quick Start must label output and preserve non-execution boundary.",
    )
    c.check("README.md" in zh and "Illustrative output" in zh, "Chinese Quick Start is missing pairing or illustrative output.")
    c.check("Goal" in brief and "Boundary" in brief and "Stop at each handoff" in agents, "Quick Start fixture lacks a minimal brief or explicit stop rule.")

    return c.assertions, c.failures


class QuickStartSmokeTest(unittest.TestCase):
    def test_quick_start_smoke(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"QUICK_START=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
