"""Contract checks for the model-invoked agent-config package.

These are deterministic package checks validating the behavioral contracts,
schema specifications, and invariants of agent-config.
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
TASK_ASSESSMENT = (ROOT / "references" / "task-assessment.md").read_text(encoding="utf-8")
ADAPTER_CONTRACT = (ROOT / "references" / "provider-adapter-contract.md").read_text(encoding="utf-8")


class AgentConfigContractTest(unittest.TestCase):
    def test_package_shape_and_supporting_files_exist(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue((ROOT / "references" / "host-evidence-schema.md").is_file())
        self.assertTrue((ROOT / "references" / "plan-schema.md").is_file())
        self.assertTrue((ROOT / "references" / "task-assessment.md").is_file())
        self.assertTrue((ROOT / "references" / "provider-adapter-contract.md").is_file())
        self.assertRegex(SKILL, r"(?m)^name:\s*agent-config\s*$")
        self.assertRegex(SKILL, r"(?m)^description:\s*.+")
        self.assertNotRegex(SKILL, r"(?m)^disable-model-invocation:")
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")

    def test_host_evidence_schema_v2_and_backward_compatibility(self) -> None:
        for marker in (
            '"schema_version": "2"',
            "routing_rank",
            "reasoning_control",
            "levels",
            "assignment_scope",
            "available",
            "unavailable",
            "unknown",
            "host-runtime",
            "models.current",
            "models.selectable",
            "model_selection",
            "per_agent_model_selection",
            "tier routing unavailable",
            "Reject a false inventory claim",
        ):
            self.assertIn(marker, HOST_SCHEMA)

    def test_task_assessment_criteria_and_anti_wordcount_invariant(self) -> None:
        for marker in (
            "single-pass",
            "decomposed",
            "routine",
            "moderate",
            "demanding",
            "critical",
            "Anti-wordcount rule",
            "never use word count",
            "Monotonicity invariant",
        ):
            self.assertIn(marker.lower(), TASK_ASSESSMENT.lower())

    def test_adaptive_plan_schema_defines_headers_and_conditional_layouts(self) -> None:
        for marker in (
            "Status: READY | NEED-INPUT | BOUNDARY",
            "Provider mode: tiered-multi-model | fixed-single-model",
            "Task shape: single-pass | decomposed",
            "Execution readiness: executable | needs-project-tickets | waiting-on-frontier | blocked-gate",
            "Apply mode: plan-only | adapter-available-awaiting-approval | applied",
            "## Host summary",
            "## Task assessment",
            "## Execution config",
            "## Review strategy",
            "## Limitations / unknowns",
            "Controller Review",
            "Self-check",
            "Independent Review",
        ):
            self.assertIn(marker, PLAN_SCHEMA)

    def test_plan_schema_does_not_force_universal_waves_or_ownership_on_single_pass(self) -> None:
        # In the adaptive schema, single-pass tasks emit a streamlined table,
        # while ownership and waves are conditional sections for decomposed tasks.
        self.assertIn("Single-pass layout (Adaptive)", PLAN_SCHEMA)
        self.assertIn("Do not force an\nownership matrix, execution waves, or separate Explorer/Merger roles", PLAN_SCHEMA)
        self.assertIn("Conditional sections for decomposed tasks", PLAN_SCHEMA)

    def test_core_skill_defines_four_execution_modes_and_2x2_grid(self) -> None:
        for marker in (
            "tiered-multi-model",
            "fixed-single-model",
            "single-pass",
            "decomposed",
            "Mode 1 — Tiered Multi-model + Single-pass",
            "Mode 2 — Tiered Multi-model + Decomposed",
            "Mode 3 — Fixed Single-model + Single-pass",
            "Mode 4 — Fixed Single-model + Decomposed",
            "minimum sufficient model rank",
            "needs-project-tickets",
            "Roles are conditional",
        ):
            self.assertIn(marker, SKILL)

    def test_provider_adapter_contract_boundaries(self) -> None:
        for marker in (
            "Read-only by default",
            "Explicit user approval required",
            "Graceful adapter absence",
            "Non-blocking adapter failure",
            "Apply request contract",
        ):
            self.assertIn(marker, ADAPTER_CONTRACT)

    def test_invocation_mutation_is_rejected(self) -> None:
        self.assertRegex(METADATA, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        mutated_metadata = METADATA.replace(
            "allow_implicit_invocation: true", "allow_implicit_invocation: false"
        )
        self.assertNotRegex(mutated_metadata, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        mutated_skill = SKILL.replace("name: agent-config\n", "name: agent-config\ndisable-model-invocation: true\n", 1)
        self.assertRegex(mutated_skill, r"(?m)^disable-model-invocation:\s*true\s*$")

    def test_live_package_is_self_contained_and_provider_neutral(self) -> None:
        package_text = "\n".join((SKILL, METADATA, HOST_SCHEMA, PLAN_SCHEMA, TASK_ASSESSMENT, ADAPTER_CONTRACT))
        self.assertNotRegex(
            package_text,
            r"(?i)sol-advisor|\bsol\b|\bterra\b|\bluna\b|mattpocock|github\.com",
        )
        self.assertNotRegex(package_text, r"https?://|/Users/|\.codex")
        self.assertIn("no external Skill", SKILL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
