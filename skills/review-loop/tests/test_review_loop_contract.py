"""Contract, invocation, and boundary assertions for review-loop (lightweight Review Engine)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
REFS = "\n".join(
    (ROOT / "references" / name).read_text(encoding="utf-8")
    for name in ("reviewer-contract.md", "finding-schema.md", "migration.md")
)
COMBINED = SKILL + "\n" + REFS


def frontmatter(text: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def model_invoked(skill: str, metadata: str) -> bool:
    return (
        bool(re.search(r"(?m)^name:\s*review-loop\s*$", frontmatter(skill)))
        and "disable-model-invocation" not in frontmatter(skill)
        and bool(re.search(r"(?m)^\s*allow_implicit_invocation:\s*true\s*$", metadata))
    )


class ReviewLoopContractTest(unittest.TestCase):
    def test_package_shape_and_model_invocation(self) -> None:
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "agents" / "openai.yaml").is_file())
        self.assertTrue(model_invoked(SKILL, METADATA))
        self.assertIn("model-invoked", SKILL)
        self.assertIn("manually invoked", normalized(SKILL))

    def test_responsibilities_are_the_five_steps(self) -> None:
        text = normalized(SKILL).lower()
        for marker in ("resolve reviewer", "invoke reviewer", "receive findings", "return repair", "re-run reviewer"):
            self.assertIn(marker, text)
        self.assertIn("at the limit", text)
        self.assertIn("stop", text)

    def test_input_packet_is_the_four_fields(self) -> None:
        for marker in ("Target:", "Requirements:", "Relevant context:", "Previous findings:"):
            self.assertIn(marker, COMBINED)
        self.assertIn("reviewer-contract", SKILL.lower())
        self.assertIn("REVIEW-ERROR", COMBINED)

    def test_reviewer_resolution_is_explicit(self) -> None:
        self.assertIn("generic-review", SKILL)
        self.assertIn("code-review", SKILL)
        self.assertIn("domain reviewer", normalized(SKILL).lower())

    def test_normalized_findings_contract(self) -> None:
        for marker in ("id:", "severity:", "location:", "problem:", "reason:"):
            self.assertIn(marker, COMBINED)
        self.assertIn("suggestion", COMBINED.lower())
        self.assertIn("Findings: []", COMBINED)
        for state in ("new", "persists", "fixed", "duplicate"):
            self.assertIn(state, COMBINED)
        self.assertIn("never reuse", normalized(COMBINED).lower())
        self.assertIn("duplicate_of", COMBINED)

    def test_bounded_convergence_and_handoff(self) -> None:
        self.assertIn("3 rounds", SKILL)
        self.assertIn("handoff", normalized(SKILL).lower())
        self.assertIn("hand the outstanding", normalized(SKILL).lower())

    def test_legacy_note_points_to_project_review(self) -> None:
        self.assertIn("project-review", SKILL)
        self.assertIn("migrated", normalized(REFS).lower())
        self.assertIn("frozen", normalized(REFS).lower())
        self.assertIn("PASS", COMBINED)
        self.assertIn("FAIL", COMBINED)
        self.assertIn("BLOCKED", COMBINED)

    def test_read_only_and_no_final_verdict_boundary(self) -> None:
        # review-loop engine must not claim final project verdict
        self.assertIn("owns no project final acceptance", normalized(SKILL))
        self.assertIn("belong to `project-review`", SKILL)
        # engine itself is not the verdict owner
        self.assertTrue("project-review" in SKILL and "PASS" in SKILL)

    def test_invocation_mutation_is_rejected(self) -> None:
        self.assertTrue(model_invoked(SKILL, METADATA))
        disabled = SKILL.replace("name: review-loop\n", "name: review-loop\ndisable-model-invocation: true\n", 1)
        implicit_off = METADATA.replace("allow_implicit_invocation: true", "allow_implicit_invocation: false")
        self.assertFalse(model_invoked(disabled, METADATA))
        self.assertFalse(model_invoked(SKILL, implicit_off))

    def test_references_resolve(self) -> None:
        # All links in SKILL.md must resolve
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", SKILL)
        for link in links:
            if link.startswith("http") or link.startswith("#") or not link:
                continue
            link_path = link.split("#")[0]
            resolved = (ROOT / link_path).resolve()
            self.assertTrue(resolved.exists(), f"unresolved link {link} -> {resolved}")

    def test_no_heavy_acceptance_ownership(self) -> None:
        self.assertNotIn("The Core owns the final verdict", SKILL)
        self.assertIn("project-review", SKILL)


if __name__ == "__main__":
    unittest.main(verbosity=2)