"""Composition tests for the 33-package Light workflow (SPEC §24).

Covers: clarify→socratic, project-clarify→socratic,
decision-map→socratic/research/prototype/to-questionnaire,
project-spec→project-tickets, implement→review path,
review-loop→generic-review/code-review, project-review→review-loop+reviewers,
ask-light→existing first-party Skills.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Helper
def read_skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8", errors="replace")

def read_doc(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")

class CompositionTests(unittest.TestCase):
    def test_clarify_to_socratic(self):
        text = read_skill("clarify")
        self.assertIn("socratic", text, "clarify must compose with socratic")
        # Ensure it does not claim to reimplement socratic's logic verbatim
        self.assertNotIn("Fixed questionnaire", text, "clarify should not contain stale fixed questionnaire prose")

    def test_project_clarify_to_socratic(self):
        text = read_skill("project-clarify")
        self.assertIn("socratic", text, "project-clarify must compose with socratic")
        self.assertIn("inspect" , text.lower(), "project-clarify must mention inspecting project facts before asking")

    def test_decision_map_composition(self):
        text = read_skill("decision-map")
        for dep in ("socratic", "research", "prototype", "to-questionnaire"):
            self.assertIn(dep, text, f"decision-map must mention {dep} per unknown-routing")
        # workflow doc should also mention them
        wf = read_doc("docs/workflows/clarification-system.md")
        for dep in ("socratic", "research", "prototype", "to-questionnaire"):
            self.assertIn(dep, wf, f"clarification-system workflow must mention {dep}")

    def test_project_spec_to_tickets(self):
        text = read_skill("project-spec")
        self.assertIn("project-tickets", text, "project-spec must handoff to project-tickets")
        wf = read_doc("docs/workflows/project-workflow.md")
        self.assertIn("project-spec", wf)
        self.assertIn("project-tickets", wf)

    def test_implement_review_path(self):
        text = read_skill("implement")
        self.assertIn("review-loop", text, "implement must hand to review-loop")
        # Should mention at least one reviewer
        self.assertTrue("generic-review" in text or "code-review" in text, "implement must mention appropriate reviewer path")
        wf = read_doc("docs/workflows/execution.md")
        self.assertIn("implement", wf)
        self.assertIn("review-loop", wf)
        # agent-config is optional routing
        self.assertIn("agent-config", text, "implement should reference agent-config as optional routing")
        self.assertIn("offer the user a choice", text, "implement must offer optional agent-config choice")

    def test_agent_config_composition_boundaries(self):
        ac_text = read_skill("agent-config")
        # agent-config does not steal formal decomposition from project-tickets
        self.assertIn("needs-project-tickets", ac_text, "decomposed tasks without tickets hand off to project-tickets")
        self.assertNotIn("publish to the issue tracker", ac_text.lower())
        # agent-config does not bypass review-loop or project-review
        self.assertIn("review-loop", ac_text)
        self.assertIn("project-review", ac_text)
        # Setup Gate and references presence
        self.assertIn("Setup Gate", ac_text)
        self.assertIn("references/setup.md", ac_text)
        self.assertIn("references/profile-schema.md", ac_text)
        self.assertIn("references/companion-contract.md", ac_text)
        # Invariants: profile-driven, no intelligence guessing, single-model is first-class peer
        self.assertIn("No intelligence guessing", ac_text)
        self.assertIn("Single-model is first-class", ac_text)
        # 4 execution modes presence
        for mode in ("Tiered Multi-model + Single-pass", "Tiered Multi-model + Decomposed", "Fixed Single-model + Single-pass", "Fixed Single-model + Decomposed"):
            self.assertIn(mode, ac_text)

    def test_review_loop_to_reviewers(self):
        text = read_skill("review-loop")
        self.assertIn("generic-review", text, "review-loop must reference generic-review")
        self.assertIn("code-review", text, "review-loop must reference code-review")
        # review-loop must not present itself as the final acceptance owner; project-review owns verdicts
        self.assertIn("project-review", text, "review-loop must point final acceptance to project-review")
        self.assertIn("never writes", text, "review-loop must state it never writes PASS/FAIL/BLOCKED")
        self.assertNotIn("owns `PASS`", text, "review-loop must not claim verdict ownership")
        wf = read_doc("docs/workflows/review-system.md")
        self.assertIn("review-loop", wf)
        self.assertIn("generic-review", wf)
        self.assertIn("code-review", wf)

    def test_project_review_to_loop_and_reviewers(self):
        text = read_skill("project-review")
        self.assertIn("review-loop", text, "project-review must use review-loop as engine")
        self.assertIn("generic-review", text, "project-review must compose generic-review")
        self.assertIn("code-review", text, "project-review must compose code-review")
        # Must own verdict
        self.assertIn("PASS", text)
        self.assertIn("FAIL", text)
        self.assertIn("BLOCKED", text)
        wf = read_doc("docs/workflows/review-system.md")
        self.assertIn("project-review", wf)

    def test_ask_light_routes_to_real_skills(self):
        text = read_skill("ask-light")
        import json
        skill_map = json.loads(read_doc("skills/ask-light/references/light-skill-map.json"))
        names = {entry["name"] for entry in skill_map["skills"]}
        real_skills = {"project-init", "project-clarify", "project-spec", "project-tickets", "implement", "project-review", "clarify", "socratic", "research", "prototype", "review-loop"}
        self.assertTrue(real_skills.issubset(names))
        # Ensure it does not promise to execute
        self.assertIn("read-only", text.lower(), "ask-light must be read-only router")
        # Workflow doc
        wf = read_doc("docs/workflows/project-workflow.md")
        self.assertIn("ask-light", wf)

    def test_specialized_workflows_standalone(self):
        for skill in ("manuscript-ops", "kb-init", "learn-anything", "language-learning", "kanban-worker", "recap"):
            text = read_skill(skill)
            self.assertGreater(len(text), 100, f"{skill} SKILL.md should be non-empty standalone skill")
            # Should not force project workflow membership
            self.assertNotIn("project-workflow is required", text)

    def test_workflow_docs_composition_not_copied(self):
        # Workflow docs should describe handoff, not copy internal workflows verbatim
        for doc in ("docs/workflows/clarification-system.md", "docs/workflows/execution.md", "docs/workflows/review-system.md"):
            text = read_doc(doc)
            self.assertIn("→", text, f"{doc} should show composition arrows")
            self.assertIn("Entry", text or "entry", f"{doc} should explain entry")
            self.assertIn("stop", text.lower(), f"{doc} should explain stop")

if __name__ == "__main__":
    unittest.main(verbosity=2)
