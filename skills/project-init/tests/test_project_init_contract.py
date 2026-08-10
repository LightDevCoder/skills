"""Port of skills/project-init/tests/project-init-contract-tests.ps1."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_path = root / "SKILL.md"
    metadata_path = root / "agents" / "openai.yaml"
    preset_path = root / "references" / "presets.md"
    contract_path = root / "references" / "initialization-contract.md"
    for path in (skill_path, metadata_path, preset_path, contract_path):
        c.check(path.is_file(), f"required path exists: {path}")
    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    presets = preset_path.read_text(encoding="utf-8", errors="replace")
    contract = contract_path.read_text(encoding="utf-8", errors="replace")

    c.check(bool(re.search(r"(?ms)^---\s*\r?\nname: project-init\s*\r?\ndescription: .+?\r?\n---", skill)), "frontmatter has name and description only")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", metadata)), "Skill is explicit-only")
    for preset in ("generic", "software", "manuscript", "skill-development", "research", "knowledge-base", "data-analysis"):
        c.check(bool(re.search(rf"\| {re.escape(preset)} \|", presets)), f"preset supported: {preset}")
    for marker in ("project type", "user-visible goal", "expected outputs", "collaboration mode", "important constraints", "required review level"):
        c.check(marker in skill, f"lightweight question captured: {marker}")
    for marker in ("existing `AGENTS.md`", "existing `CLAUDE.md`", "research", "confirm", "reject", "created path", "declared capability", "Project Initialization"):
        c.check(marker in (skill + contract), f"initialization contract marker: {marker}")
    for forbidden in ("to-spec", "to-tickets", "implement", "final review", "another user-invoked Skill"):
        c.check(forbidden in skill, f"boundary names forbidden operation: {forbidden}")
    c.check("does not run" in skill and ("never invoke" in skill or "must not invoke" in skill), "boundaries prohibit execution")
    c.check(not re.search(r"TODO|\[TODO", skill), "no template placeholders remain")

    return c.assertions, c.failures


class ProjectInitContractTest(unittest.TestCase):
    def test_project_init_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertFalse(failures, f"project-init contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
