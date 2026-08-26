"""Port of skills/project-init/tests/project-init-behavior-tests.ps1."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402


def select_instruction_target(root: Path) -> Path:
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"
    if agents.is_file():
        return agents
    if claude.is_file():
        return claude
    return agents


def merge_initialization_section(existing: str, block: str) -> str:
    if re.search(r"(?ms)^## Project Initialization\s*$", existing):
        parts = re.split(r"(?ms)^## Project Initialization\s*$", existing, maxsplit=1)
        tail_match = re.search(r"(?ms)\r?\n## (?!#)", parts[1])
        if tail_match:
            suffix = parts[1][tail_match.start():].lstrip()
        else:
            suffix = ""
        return (parts[0].rstrip() + "\r\n\r\n" + block.strip() + (f"\r\n\r\n{suffix}" if suffix else "")).strip() + "\r\n"
    return (existing.rstrip() + "\r\n\r\n" + block.strip()).strip() + "\r\n"


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill = (root / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    presets = (root / "references" / "presets.md").read_text(encoding="utf-8", errors="replace")
    contract = (root / "references" / "initialization-contract.md").read_text(encoding="utf-8", errors="replace")

    for preset in ("generic", "software", "manuscript", "skill-development", "research", "knowledge-base", "data-analysis"):
        c.check(bool(re.search(rf"(?m)^\| {re.escape(preset)} \|.+\|.+\|", presets)), f"preset plan is selectable: {preset}")
    c.check("one short question at a time" in skill and "six answers" in skill, "questions stay lightweight")

    with tempfile.TemporaryDirectory(prefix="project-init-") as tmp:
        fixture = Path(tmp)
        agents = fixture / "AGENTS.md"
        claude = fixture / "CLAUDE.md"
        agents.write_text("# Existing rules\r\n\r\nKeep this line.", encoding="utf-8")
        claude.write_text("# Do not replace this file.", encoding="utf-8")
        c.check(select_instruction_target(fixture) == agents, "existing AGENTS.md is preferred without duplicate")
        c.check("When existing instruction files disagree" in skill and "If `AGENTS.md` and `CLAUDE.md` conflict" in contract, "conflicting instructions are preserved and reported")
        merged = merge_initialization_section(agents.read_text(encoding="utf-8"), "## Project Initialization\r\n\r\n- Type: software\r\n- Goal: test")
        agents.write_text(merged, encoding="utf-8")
        c.check("Keep this line." in agents.read_text(encoding="utf-8") and "Do not replace" in claude.read_text(encoding="utf-8"), "existing instructions are preserved")
        again = merge_initialization_section(agents.read_text(encoding="utf-8"), "## Project Initialization\r\n\r\n- Type: software\r\n- Goal: test")
        c.check(len(re.findall(r"(?m)^## Project Initialization\s*$", again)) == 1, "rerun keeps one initialization section")
        agents.unlink()
        c.check(select_instruction_target(fixture) == claude, "CLAUDE.md is used when AGENTS.md is absent")
        claude.unlink()
        c.check(select_instruction_target(fixture) == agents, "new AGENTS.md is default when neither exists")

    c.check("If no preset matches" in skill and "only after `confirm` may the fallback plan write" in skill, "research fallback requires confirmation")
    c.check("on `reject`, write nothing" in skill and "empty write set" in contract, "research rejection has no write set")
    c.check("requested modification" in skill and "confirmation again" in skill, "research modification re-enters confirmation")
    for marker in ("inside the requested project root", "exactly one instruction target", "existing instruction text remains present", "declared capability", "forbidden workflow"):
        c.check(marker in skill, f"validation covers {marker}")
    for forbidden in ("project-spec", "project-tickets", "implement", "project-review", "review-loop", "ask-light", "learn-anything"):
        c.check(forbidden in skill, f"boundary names {forbidden}")
    for old in ("to-spec", "to-tickets", "final review"):
        c.check(old not in skill, f"old boundary name removed: {old}")
    c.check("must not invoke another user-invoked Skill" in skill or "never invoke" in skill, "initializer does not invoke user Skills")

    return c.assertions, c.failures


class ProjectInitBehaviorTest(unittest.TestCase):
    def test_project_init_behavior(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"project-init behavior failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
