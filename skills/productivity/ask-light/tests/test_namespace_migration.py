"""Public discovery and routing boundaries for the v0.2.6 canonical names."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
SCRIPTS = PACKAGE / "scripts"
sys.path.insert(0, str(SCRIPTS))
from ask_light_models import CompactProjectState
from state_extractor import compute_legal_actions

spec = importlib.util.spec_from_file_location("namespace_ask_light", SCRIPTS / "ask_light.py")
assert spec and spec.loader
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)

RENAMES = {
    "implement": "light-implement", "code-review": "light-code-review",
    "research": "light-research", "prototype": "light-prototype", "tdd": "light-tdd",
    "diagnosing-bugs": "light-diagnosing-bugs", "wizard": "light-wizard",
    "handoff": "light-handoff", "teach": "light-teach",
    "to-questionnaire": "light-to-questionnaire", "wait-what": "light-wait-what",
    "writing-for-agents": "light-writing-for-agents",
}


def write_package(root: Path, name: str) -> Path:
    p = root / name
    p.mkdir(parents=True)
    (p / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test capability identity.\n---\n\nRead-only fixture.\n"
    )
    return p.resolve()


class NamespaceMigrationTests(unittest.TestCase):
    def test_old_same_name_capabilities_do_not_satisfy_light_dependencies(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for old, canonical in RENAMES.items():
                with self.subTest(skill=canonical):
                    write_package(root, old)
                    result = ask.validate_recommendation(
                        canonical, roots=[{"category": "first-party", "path": str(root)}],
                        scope="independent",
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertEqual(result["logicalRecommendation"], canonical)
                    self.assertFalse(result["checks"]["available"])
                    self.assertEqual(result["source"], "")

    def test_mixed_installation_resolves_only_the_light_canonical_path(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for old, canonical in RENAMES.items():
                write_package(root, old)
                expected = write_package(root, canonical)
                with self.subTest(skill=canonical):
                    result = ask.validate_recommendation(
                        canonical, roots=[{"category": "first-party", "path": str(root)}],
                        scope="independent",
                    )
                    self.assertEqual(result["status"], "VALIDATED")
                    self.assertEqual(Path(result["source"].removeprefix("first-party: ")), expected)
                    self.assertEqual(result["invocation"], "$" + canonical)
                    old_result = ask.validate_recommendation(
                        old, roots=[{"category": "first-party", "path": str(root)}], scope="independent",
                    )
                    self.assertEqual(old_result["status"], "BLOCKED")
                    self.assertFalse(old_result["checks"]["inLightMap"])

    def test_ready_ticket_remains_a_recommendation_until_approval(self):
        state = CompactProjectState(
            initialized=True, spec_exists=True, spec_active=True, tickets_exist=True,
            ready_tickets=["issue-01.md"],
        )
        result = compute_legal_actions(state, "What comes next?")
        self.assertEqual(result.allowed_actions, ["light-implement"])
        self.assertEqual(result.fallback_action, "light-implement")
        self.assertFalse(result.is_authorized)
        approved = compute_legal_actions(state, "start executing")
        self.assertEqual(approved.allowed_actions, ["light-implement"])
        self.assertTrue(approved.is_authorized)

    def test_business_types_and_artifact_keys_remain_research(self):
        mapping = ask.load_map()
        recipe = next(w for w in mapping["workflows"] if w["id"] == "new-project-initialization")
        self.assertIn("research", recipe["projectTypes"])
        self.assertNotIn("light-research", recipe["projectTypes"])
        self.assertEqual(mapping["skillFamilies"]["light-research"], "research")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs/agents").mkdir(parents=True)
            (root / "docs/agents/light-project.md").write_text("# Light project\n")
            (root / "docs/research").mkdir(parents=True)
            (root / "docs/research/source.md").write_text("# Source\n")
            evidence = ask.inspect_project_evidence(root)
            self.assertIn("docs/research/source.md", evidence["artifactSignals"]["research"])
            self.assertNotIn("light-research", evidence["artifactSignals"])
