"""Contract, invocation, and boundary assertions for generic-review."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
SCHEMA = (ROOT / "references" / "output-schema.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def model_invoked(skill: str, metadata: str) -> bool:
    return (
        bool(re.search(r"(?m)^name:\s*generic-review\s*$", frontmatter(skill)))
        and "disable-model-invocation" not in frontmatter(skill)
        and bool(re.search(r"(?m)^\s*allow_implicit_invocation:\s*true\s*$", metadata))
    )


class GenericReviewContractTest(unittest.TestCase):
    def test_package_shape_and_model_invocation(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "references" / "output-schema.md").is_file())
        self.assertTrue(model_invoked(SKILL, METADATA))
        self.assertIn("model-invoked", SKILL)

    def test_required_input_and_generic_scope_are_explicit(self) -> None:
        for marker in ("Target:", "Requirements:", "Relevant context:", "Previous findings:"):
            self.assertIn(marker, SKILL)
        self.assertRegex(normalized(SKILL), r"On a first review, set Previous findings to `none`\.")
        # The generic scope is defined by what it checks, not by a permission list.
        self.assertIn("missing required output", normalized(SKILL))
        self.assertIn("internal contradiction", normalized(SKILL))
        self.assertIn("usability", normalized(SKILL))
        self.assertIn("scope added", normalized(SKILL))
        self.assertIn("specialist", SKILL)
        self.assertIn("domain rulebook", SKILL)

    def test_normalized_schema_requires_the_finding_fields_and_states(self) -> None:
        for marker in ("id:", "severity:", "location:", "problem:", "reason:", "suggestion:", "new", "persists", "fixed", "duplicate"):
            self.assertIn(marker, SCHEMA)
        self.assertIn("Findings: []", SCHEMA)
        self.assertIn("next unused number", normalized(SCHEMA))
        self.assertIn("never recycle", SCHEMA)

    def test_read_only_and_no_final_verdict_boundary(self) -> None:
        self.assertIn("Return observations, not commands", normalized(SKILL))
        self.assertIn("not a repair plan", normalized(SKILL))
        self.assertIn("do not continue into repair", normalized(SKILL))
        self.assertIn("never a final verdict", normalized(SCHEMA))
        self.assertIn("Do not include `PASS`, `FAIL`, `BLOCKED`", SCHEMA)

    def test_invocation_mutation_is_rejected(self) -> None:
        self.assertTrue(model_invoked(SKILL, METADATA))
        disabled = SKILL.replace("name: generic-review\n", "name: generic-review\ndisable-model-invocation: true\n", 1)
        implicit_off = METADATA.replace("allow_implicit_invocation: true", "allow_implicit_invocation: false")
        self.assertFalse(model_invoked(disabled, METADATA))
        self.assertFalse(model_invoked(SKILL, implicit_off))

    def test_external_runtime_and_authority_mutations_are_rejected(self) -> None:
        live = "\n".join((SKILL, METADATA, SCHEMA))
        self.assertNotRegex(live, r"(?i)github\.com|curl |npm install|subprocess|write_text\(")
        mutated = SKILL + "\nEdit the target and issue a final PASS verdict.\n"
        self.assertRegex(mutated, r"(?i)Edit the target.*final PASS")
        self.assertNotRegex(SKILL, r"(?i)issue a project.*verdict")


if __name__ == "__main__":
    unittest.main(verbosity=2)