"""Deterministic contract tests for the kb-init first-party Skill ."""

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

REQUIRED_REFS = [
    "base-discovery.md",
    "connection-setup.md",
    "design-guide.md",
    "human-navigation.md",
    "interview-contract.md",
    "readiness-check.md",
    "research-contract.md",
    "spec-guide.md",
]

SKILL_MARKERS = [
    "Interview before architecture",
    "The user owns decisions",
    "The user owns the end of the interview",
    "User questions interrupt the interview",
    "No silent gap-filling",
    "Depth before settlement",
    "Surface architecture-shaping open decisions",
    "Decision provenance matters",
    "No platform recipes in the skill",
    "Computer use is optional, never foundational",
    "Maintenance is part of the knowledge base",
    "Design for both human and Agent use when both exist",
    "Stay inside the knowledge-base boundary",
    "External skill policy",
    "research",
    "readiness-check",
    "Connection Setup",
    "Connection Validation",
    "Approval gate",
    "Implementation begins only after explicit approval of the SPEC",
    "At minimum, verify representative end-to-end scenarios",
]


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_path = root / "SKILL.md"
    metadata_path = root / "agents" / "openai.yaml"
    evals_path = root / "evals" / "evals.json"

    for path in [skill_path, metadata_path, evals_path] + [root / "references" / r for r in REQUIRED_REFS]:
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

    for marker in SKILL_MARKERS:
        c.check(marker in skill, f"SKILL.md marker: {marker}")

    interview = (root / "references" / "interview-contract.md").read_text(encoding="utf-8", errors="replace")
    for marker in [
        "## 1. Purpose, users, and outcomes",
        "## 2. Content and record types",
        "## 3. Base and storage environment",
        "## 4. Knowledge structure and human navigation",
        "## 5. How new knowledge enters and how sources are traced",
        "## 6. Retrieval, analysis, and outputs",
        "## 7. Maintenance and Agent autonomy",
        "## 8. Boundaries, history, migration, and growth",
    ]:
        c.check(marker in interview, f"interview contract section: {marker}")

    base = (root / "references" / "base-discovery.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Discover the storage model", "Discover programmatic access", "Discover authentication and permissions", "Discover export, backup, and portability", "Base fitness check", "Separate product capability from current Agent capability"]:
        c.check(marker in base, f"base discovery marker: {marker}")

    design = (root / "references" / "design-guide.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Keep the models separate", "Human navigation model", "Make operational mechanisms explicit", "Backup claims match recovery reality"]:
        c.check(marker in design, f"design guide marker: {marker}")

    spec = (root / "references" / "spec-guide.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Problem and objective", "Exact destination", "Connection plan", "Operational mechanism matrix", "Backup/versioning and recovery semantics", "Approval gate"]:
        c.check(marker in spec, f"spec guide marker: {marker}")

    readiness = (root / "references" / "readiness-check.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Open decision surfacing", "Decision provenance", "Decision depth", "Human navigation when people directly use the base", "Exact destination", "Pre-approval side effects"]:
        c.check(marker in readiness, f"readiness check marker: {marker}")

    research = (root / "references" / "research-contract.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Before dispatch", "Dispatch verification", "Research artifact isolation", "Completion verification", "After research"]:
        c.check(marker in research, f"research contract marker: {marker}")

    connection = (root / "references" / "connection-setup.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["Validate the connection", "Handle failure gracefully", "Record reconnection guidance", "Never ask the user to paste secrets"]:
        c.check(marker in connection, f"connection setup marker: {marker}")

    navigation = (root / "references" / "human-navigation.md").read_text(encoding="utf-8", errors="replace")
    for marker in ["First establish the human role", "Design the entry point", "Design browse dimensions", "Test old-knowledge retrieval"]:
        c.check(marker in navigation, f"human navigation marker: {marker}")

    evals = json.loads(evals_path.read_text(encoding="utf-8"))
    c.check(evals.get("skill") == "kb-init", "evals metadata names kb-init")
    c.check(isinstance(evals.get("cases"), list) and len(evals["cases"]) >= 30, "evals has at least thirty regression cases")
    for case in evals["cases"]:
        c.check("id" in case and "prompt" in case and "expect" in case, f"eval case fields: {case.get('id')}")

    c.check(not re.search(r"TODO|\[TODO", skill), "no template placeholders remain")

    mutated = skill.replace("The user owns the end of the interview", "The Agent may end the interview whenever enough information exists")
    c.check("The Agent may end the interview whenever enough information exists" in mutated, "mutation applied for user-owns-end")
    c.check("The user owns the end of the interview" not in mutated, "mutation removed the required marker")
    mutated2 = skill.replace("Do not choose a base, structure, schema, or maintenance model before the user's workflow supports that choice.", "Choose a generic structure immediately.")
    c.check("Choose a generic structure immediately." in mutated2, "interview-first mutation applied")
    c.check("Interview before architecture" not in mutated2.split("## Core principles")[0], "interview-first mutation is detectable")

    return c.assertions, c.failures


class KBInitContractTest(unittest.TestCase):
    def test_kb_init_contract(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"KB_INIT_CONTRACT=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
