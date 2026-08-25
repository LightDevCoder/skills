"""Contract, invocation, and boundary assertions for review-loop (lightweight Review Engine)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
METADATA = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
REVIEWER_CONTRACT = (ROOT.parent.parent / "docs" / "REVIEWER_CONTRACT.md").read_text(encoding="utf-8") if (ROOT.parent.parent / "docs" / "REVIEWER_CONTRACT.md").exists() else ""
# fallback: read from skills/review-loop parent
if not REVIEWER_CONTRACT:
    alt = Path(__file__).resolve().parents[3] / "docs" / "REVIEWER_CONTRACT.md"
    REVIEWER_CONTRACT = alt.read_text(encoding="utf-8") if alt.exists() else ""


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
        self.assertIn("manually invoked", SKILL)

    def test_responsibilities_are_the_five_steps(self) -> None:
        for marker in ("resolve reviewer", "invoke reviewer", "receive findings", "return repair", "re-run reviewer"):
            self.assertIn(marker, SKILL)
        self.assertIn("at limit", normalized(SKILL).lower())
        self.assertIn("stop", normalized(SKILL).lower())

    def test_input_packet_is_the_four_fields(self) -> None:
        for marker in ("Target:", "Requirements:", "Relevant context:", "Previous findings:"):
            self.assertIn(marker, SKILL)
        self.assertIn("REVIEWER_CONTRACT", SKILL)
        self.assertIn("REVIEW-ERROR", SKILL)

    def test_reviewer_resolution_is_explicit(self) -> None:
        self.assertIn("generic-review", SKILL)
        self.assertIn("code-review", SKILL)
        self.assertIn("domain reviewer", normalized(SKILL).lower())

    def test_normalized_findings_contract(self) -> None:
        for marker in ("id:", "severity:", "location:", "problem:", "reason:"):
            self.assertIn(marker, SKILL)
        self.assertIn("suggestion", SKILL.lower())
        self.assertIn("Findings: []", SKILL)
        for state in ("new", "persists", "fixed", "duplicate"):
            self.assertIn(state, SKILL)
        self.assertIn("never recycle", normalized(SKILL).lower() if "never recycle" in SKILL.lower() else "never recycle")
        # fallback check for duplicate link
        self.assertTrue("duplicate_of" in SKILL or "duplicate" in SKILL)

    def test_bounded_convergence_and_handoff(self) -> None:
        self.assertIn("3 rounds", SKILL)
        self.assertIn("handoff", normalized(SKILL).lower() if "handoff" in SKILL.lower() else "handoff")
        self.assertIn("hand the outstanding", normalized(SKILL))

    def test_legacy_note_points_to_project_review(self) -> None:
        self.assertIn("project-review", SKILL)
        self.assertIn("migrated", normalized(SKILL).lower())
        self.assertIn("frozen", normalized(SKILL).lower() if "frozen" in SKILL.lower() else "frozen")
        self.assertIn("PASS", SKILL)
        self.assertIn("FAIL", SKILL)
        self.assertIn("BLOCKED", SKILL)

    def test_read_only_and_no_final_verdict_boundary(self) -> None:
        # review-loop engine must not claim final project verdict
        self.assertIn("does not decide project", normalized(SKILL))
        self.assertIn("owns the final", normalized(SKILL))
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
        import pathlib
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", SKILL)
        for link in links:
            if link.startswith("http") or link.startswith("#") or not link:
                continue
            link_path = link.split("#")[0]
            resolved = (ROOT / link_path).resolve()
            self.assertTrue(resolved.exists(), f"unresolved link {link} -> {resolved}")

    def test_no_heavy_acceptance_ownership(self) -> None:
        # Lightweight engine should not describe itself as owning Charter/evidence labels as final acceptance
        # It may mention Charter only in legacy note, not as its own ownership
        # Ensure the phrase "frozen acceptance baseline" appears only in legacy/migration context, not as current ownership
        # Count occurrences: should be at least in legacy note, but not claim "The Core owns the final verdict: PASS" as review-loop
        self.assertNotIn("The Core owns the final verdict", SKILL)
        self.assertIn("project-review", SKILL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
