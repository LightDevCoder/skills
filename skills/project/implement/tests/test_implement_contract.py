"""Contract checks for the user-invoked implement package."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
WORKFLOW = (ROOT / "references" / "WORKFLOW.md").read_text(encoding="utf-8")
EXAMPLES = (ROOT / "references" / "EXAMPLES.md").read_text(encoding="utf-8")


class ImplementContractTest(unittest.TestCase):
    def test_package_shape_and_user_invocation_are_explicit(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "references" / "WORKFLOW.md").is_file())
        self.assertTrue((ROOT / "references" / "EXAMPLES.md").is_file())
        self.assertRegex(SKILL, r"(?m)^name:\s*implement\s*$")
        self.assertRegex(SKILL, r"(?m)^description:\s*.+")
        self.assertRegex(SKILL, r"(?m)^disable-model-invocation:\s*true\s*$")
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_agent_config_is_opt_in_and_user_controlled(self) -> None:
        # Core loop and workflow must offer rather than auto-call
        self.assertIn("offer agent-config", SKILL)
        self.assertIn("accept", SKILL)
        self.assertIn("decline", SKILL)
        self.assertIn("would routing materially help", SKILL)
        self.assertIn("User choice contract", WORKFLOW)
        self.assertIn("Explicit user intent overrides", WORKFLOW)
        self.assertIn("Non-blocking fallback", WORKFLOW)

    def test_implement_remains_functional_without_agent_config(self) -> None:
        self.assertIn("optional enhancement", SKILL)
        self.assertIn("declining it or running on a Host", SKILL)
        self.assertIn("does not block implementation", SKILL)
        self.assertIn("never convert into a\n`BLOCKED` implementation by default", WORKFLOW)

    def test_composition_targets_are_declared(self) -> None:
        for target in ("tdd", "review-loop", "code-review", "generic-review"):
            self.assertIn(target, SKILL)

    def test_live_package_is_self_contained_and_provider_neutral(self) -> None:
        package_text = "\n".join((SKILL, METADATA, WORKFLOW, EXAMPLES))
        self.assertNotRegex(
            package_text,
            r"(?i)sol-advisor|\bsol\b|\bterra\b|\bluna\b",
        )
        self.assertNotRegex(package_text, r"https?://|/Users/|\\.codex")


if __name__ == "__main__":
    unittest.main(verbosity=2)
