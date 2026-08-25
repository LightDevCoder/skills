"""Contract checks for the model-invoked agent-config package.

These are deterministic package checks.  They do not claim that a live Agent
Host was queried or that a host executed the returned plan.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
HOST_SCHEMA = (ROOT / "references" / "host-evidence-schema.md").read_text(encoding="utf-8")
PLAN_SCHEMA = (ROOT / "references" / "plan-schema.md").read_text(encoding="utf-8")


class AgentConfigContractTest(unittest.TestCase):
    def test_package_shape_and_model_invocation_are_explicit(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "references" / "host-evidence-schema.md").is_file())
        self.assertTrue((ROOT / "references" / "plan-schema.md").is_file())
        self.assertRegex(SKILL, r"(?m)^name:\s*agent-config\s*$")
        self.assertRegex(SKILL, r"(?m)^description:\s*.+")
        self.assertNotRegex(SKILL, r"(?m)^disable-model-invocation:")
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")

    def test_current_evidence_not_memory_controls_availability(self) -> None:
        for marker in (
            "current,\ninspectable Agent Host evidence",
            "Never guess a model inventory from memory",
            "unknown",
            "Do not promote unknown to available",
            "concurrency cap",
            "subagents do not prove parallelism",
            "parallelism does not prove isolated worktrees",
        ):
            self.assertIn(marker, SKILL, marker)
        for marker in (
            "available`, `unavailable`, or `unknown",
            "host-runtime",
            "positive integer",
            "Reject a false inventory claim",
        ):
            self.assertIn(marker, HOST_SCHEMA, marker)

    def test_all_three_safe_route_shapes_are_defined(self) -> None:
        for marker in (
            "Multi-model, multi-agent",
            "Single-model, multi-agent",
            "Single-model, single-agent",
            "per-agent model selection",
            "fresh session/thread",
            "self-check",
            "no selectable model",
        ):
            self.assertIn(marker, SKILL, marker)

        self.assertNotIn(
            "session/thread, or parallelism are unavailable or unknown",
            SKILL,
        )
        self.assertIn(
            "subagents or an independent\n   session/thread are unavailable or unknown",
            SKILL,
        )
        self.assertRegex(
            SKILL,
            r"(?s)Multi-model, multi-agent.*?parallelism, and\n\s+the needed independent session/thread are all available",
        )

    def test_role_independence_ownership_and_merge_rules_are_bounded(self) -> None:
        for marker in (
            "Controller",
            "Explorer",
            "Implementer",
            "Reviewer",
            "Merger",
            "exact file ownership",
            "read-only",
            "fresh session/thread distinct\n  from every Implementer",
            "one active change\n  unit",
            "Do not issue duplicate",
            "exactly one named role",
            "unreviewed conflict resolution",
        ):
            self.assertIn(marker, SKILL, marker)

    def test_output_schema_has_no_hidden_assignments_or_unbounded_workers(self) -> None:
        for marker in (
            "Status: READY | NEED-INPUT | BOUNDARY",
            "## Evidence ledger",
            "## Role assignment",
            "## Ownership matrix",
            "## Execution waves",
            "## Review and merge gates",
            "every active Explorer, Implementer,\nReviewer, and Merger appears",
            "more concurrent workers than the evidenced cap",
            "does not show as available",
        ):
            self.assertIn(marker, PLAN_SCHEMA, marker)

    def test_invocation_mutation_is_rejected(self) -> None:
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        mutated_metadata = METADATA.replace(
            "allow_implicit_invocation: true", "allow_implicit_invocation: false"
        )
        self.assertNotRegex(mutated_metadata, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        mutated_skill = SKILL.replace("name: agent-config\n", "name: agent-config\ndisable-model-invocation: true\n", 1)
        self.assertRegex(mutated_skill, r"(?m)^disable-model-invocation:\s*true\s*$")

    def test_live_package_is_self_contained_and_provider_neutral(self) -> None:
        package_text = "\n".join((SKILL, METADATA, HOST_SCHEMA, PLAN_SCHEMA))
        self.assertNotRegex(
            package_text,
            r"(?i)sol-advisor|\bsol\b|\bterra\b|\bluna\b|mattpocock|github\.com",
        )
        self.assertNotRegex(package_text, r"https?://|/Users/|\\.codex")
        self.assertIn("no required companion", SKILL)
        self.assertIn("no external Skill", SKILL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
