"""Deterministic contract tests for the kb-init first-party Skill."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

from check_helpers import Checks  # noqa: E402

REQUIRED_MARKERS = [
    "Interview before architecture",
    "The user owns decisions",
    "The user owns the end of the interview",
    "Questions from the user interrupt the interview",
    "No silent gap-filling",
    "No platform recipes in the core skill",
    "Computer use is never a prerequisite",
    "Maintenance is part of the product",
    "Allowed external skill",
    "research",
    "user explicitly ends the interview",
    "Base Discovery",
    "Approval gate",
    "Implementation begins only after the user explicitly approves the SPEC",
    "Validation should test the user's actual workflow",
]


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_path = root / "SKILL.md"
    metadata_path = root / "agents" / "openai.yaml"
    refs = [
        "base-discovery.md",
        "design-guide.md",
        "interview-contract.md",
        "spec-guide.md",
    ]
    for path in [skill_path, metadata_path, root / "evals" / "evals.json"] + [root / "references" / r for r in refs]:
        c.check(path.is_file(), f"required path exists: {path}")

    skill = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata = metadata_path.read_text(encoding="utf-8", errors="replace")

    c.check(bool(re.search(r"(?m)^name:\s*kb-init\s*$", skill)), "frontmatter name is kb-init")
    c.check(bool(re.search(r"(?m)^disable-model-invocation:\s*true\s*$", skill)), "Skill disables model invocation")
    c.check(bool(re.search(r"(?m)^description:.*explicitly invokes kb-init", skill)), "description requires explicit invocation")
    c.check(bool(re.search(r"(?m)^description:.*start the interview automatically", skill)), "description preserves automatic interview start after explicit invocation")
    c.check(bool(re.search(r"Run only after an explicit `kb-init` request", skill)), "invocation section is explicit-only")
    c.check(bool(re.search(r"must not trigger on its own", skill)), "invocation section forbids implicit trigger")
    c.check(bool(re.search(r"must not invoke another user-invoked Skill", skill)), "invocation section forbids user-invoked chaining")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", metadata)), "Codex metadata disables implicit invocation")
    c.check("display_name:" in metadata and "short_description:" in metadata and "default_prompt:" in metadata, "metadata has required interface fields")
    c.check(bool(re.search(r'default_prompt:\s*"Use \$kb-init', metadata)), "metadata default prompt invokes kb-init explicitly")

    for marker in REQUIRED_MARKERS:
        c.check(marker in skill, f"SKILL.md marker: {marker}")

    for ref in refs:
        text = (root / "references" / ref).read_text(encoding="utf-8", errors="replace")
        c.check(len(text.strip()) > 0, f"references/{ref} is non-empty")

    interview = (root / "references" / "interview-contract.md").read_text(encoding="utf-8", errors="replace")
    c.check("## 1. Purpose, users, and outcomes" in interview, "interview contract covers purpose/users/outcomes")
    c.check("## 2. Content and record types" in interview, "interview contract covers content/record types")
    c.check("## 3. Base and storage environment" in interview, "interview contract covers base/storage")
    c.check("## 4. Knowledge structure and organization" in interview, "interview contract covers structure/organization")
    c.check("## 5. How new knowledge enters" in interview, "interview contract covers intake")
    c.check("## 6. Retrieval, analysis, and outputs" in interview, "interview contract covers retrieval/analysis")
    c.check("## 7." in interview and "## 8." in interview, "interview contract has all eight required design areas")

    spec = (root / "references" / "spec-guide.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Problem and objective", "Base decision", "Approval gate", "Remaining limitations"]:
        c.check(marker in spec, f"spec guide marker: {marker}")

    base = (root / "references" / "base-discovery.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Storage model", "Programmatic access", "Authentication and permissions", "Export, backup, and portability", "No computer-use dependency"]:
        c.check(marker in base, f"base discovery marker: {marker}")

    evals_path = root / "evals" / "evals.json"
    evals = json.loads(evals_path.read_text(encoding="utf-8"))
    c.check(evals.get("skill") == "kb-init", "evals metadata names kb-init")
    c.check(isinstance(evals.get("cases"), list) and len(evals["cases"]) >= 8, "evals has at least eight regression cases")
    for case in evals["cases"]:
        c.check("id" in case and "prompt" in case and "expect" in case, f"eval case fields: {case.get('id')}")

    c.check(not re.search(r"TODO|\[TODO", skill), "no template placeholders remain")

    # Opposite-polarity mutations: each change must be detected.
    mutated = skill.replace("The user owns the end of the interview", "The Agent may end the interview whenever enough information exists")
    c.check("The Agent may end the interview whenever enough information exists" in mutated, "mutation applied for user-owns-end")
    c.check("The user owns the end of the interview" not in mutated, "mutation removed the required marker")
    mutated2 = skill.replace("Do not choose a base, folder structure, schema, or maintenance model before the user's workflow supports that choice.", "Choose a generic folder structure immediately.")
    c.check("Choose a generic folder structure immediately." in mutated2 and "Interview before architecture." not in mutated2.split("## Core principles")[0], "interview-first mutation is detectable")

    return c.assertions, c.failures


class KBInitContractTest(unittest.TestCase):
    def test_kb_init_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"KB_INIT_CONTRACT=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
