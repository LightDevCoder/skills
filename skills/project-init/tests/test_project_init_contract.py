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
    for marker in ("project type", "user-visible goal", "expected outputs", "collaboration mode", "important constraints"):
        c.check(marker in skill, f"lightweight question captured: {marker}")
    c.check(bool(re.search(r"required\s+review\s+level", skill)), "lightweight question captured: required review level")
    for marker in ("existing `AGENTS.md`", "existing `CLAUDE.md`", "research", "confirm", "reject", "created path", "Project Initialization"):
        c.check(marker in (skill + contract), f"initialization contract marker: {marker}")
    c.check(bool(re.search(r"declared capabilit", skill + contract)), "initialization contract marker: declared capability")
    # The boundary lives as a positive execution rule: only `research` is
    # available as a model-invoked fallback and later user-invoked stages are
    # not executed by this initializer.
    c.check("`research` is the only model-invoked" in contract, "research-only model capability boundary")
    c.check("never executes or orchestrates them" in contract, "initializer does not invoke user-invoked stages")
    for old in ("to-spec", "to-tickets", "final review"):
        c.check(old not in skill, f"old name removed: {old}")
    c.check(not re.search(r"TODO|\[TODO", skill), "no template placeholders remain")

    return c.assertions, c.failures


class ProjectInitContractTest(unittest.TestCase):
    def test_project_init_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"project-init contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)