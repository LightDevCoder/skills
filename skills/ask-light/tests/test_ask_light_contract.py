"""Port of skills/ask-light/tests/ask-light-contract-tests.ps1."""

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
    reference_path = root / "references" / "discovery-contract.md"
    script_path = root / "scripts" / "ask-light.ps1"
    for path in (skill_path, metadata_path, reference_path, script_path):
        c.check(path.is_file(), f"required path exists: {path}")

    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")
    reference = reference_path.read_text(encoding="utf-8", errors="replace")
    script = script_path.read_text(encoding="utf-8", errors="replace")

    c.check(bool(re.search(r"(?ms)^---\s*\r?\nname: ask-light\s*\r?\ndescription: .+?\r?\n---", skill)), "frontmatter has name and description only")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", metadata)), "Skill is explicit-only")
    c.check("first-party" in (skill + reference), "source category first-party supported")
    for old_category in ("upstream", "modified-third-party"):
        c.check(old_category not in (skill + reference), f"non-first-party source category removed: {old_category}")
    for field in ("goal", "artifacts", "blockers", "projectType", "taskKind", "availability", "invocationControl"):
        c.check(field in (reference + skill), f"context field supported: {field}")
    for marker in (
        "metadata[- ]first", "frontmatter", "agents/openai.yaml", "shortlist", "duplicate", "unreadable",
        "Alternative", "NEED-INPUT", "BLOCKED", "installation", "never execute", "never.*install",
        "body/reference", "availability", "hosts", "readStatus", "metadataStatus: unavailable",
        "metadataReadable", "materially different next actions", "equivalent", "next", "workflow",
        "entryCondition", "expectedInput", "expectedOutput", "stopCondition", "missingDependency",
        "finalAuthority", "nothing was invoked, installed, or orchestrated",
    ):
        c.check(bool(re.search(marker, skill + reference, flags=re.IGNORECASE)), f"contract marker: {marker}")
    c.check(not re.search(r"TODO|\[TODO", skill), "no template placeholders remain")
    c.check(not re.search(r"(?i)Start-Process|Invoke-Expression|Invoke-RestMethod|Install-Module", script), "scanner has no execution or installation primitive")
    c.check(bool(re.search(r"Get-Content -Raw.*SKILL\.md", script)) and "ShortlistLimit" in script, "scanner reads bodies after shortlist only")
    c.check("ConvertTo-Json" in script, "scanner returns a structured result")
    c.check("Test-CandidateAvailability" in script and "Get-ActionFingerprint" in script and "readableShortlist" in script, "scanner filters availability, distinguishes actions, and rejects unreadable reads")
    c.check(bool(re.search(r"ValidateSet\('next', 'workflow'\)", script)) and "Get-WorkflowRecipes" in script and "Get-WorkflowRecommendation" in script, "scanner exposes explicit next and workflow modes with recipe output")
    c.check("missingDependency" in skill + reference, "workflow exposes missing dependency gaps")
    c.check("project-review" in skill and "finalAuthority" in reference + skill, "final authority belongs to project-review")

    return c.assertions, c.failures


class AskLightContractTest(unittest.TestCase):
    def test_ask_light_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"ask-light contract failed: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)