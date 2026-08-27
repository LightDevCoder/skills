from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ask_light", ROOT / "scripts" / "ask_light.py")
assert SPEC and SPEC.loader
ASK_LIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASK_LIGHT)


def write_skill(root: Path, name: str, *, metadata: bool = True, body: str = "Body", user_invoked: bool = False) -> None:
    package = root / name
    package.mkdir(parents=True, exist_ok=True)
    invocation = "disable-model-invocation: true\n" if user_invoked else ""
    (package / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Fixture for {name}.\n{invocation}---\n\n{body}\n", encoding="utf-8")
    if metadata:
        (package / "agents").mkdir(exist_ok=True)
        (package / "agents" / "openai.yaml").write_text("interface:\n  display_name: fixture\n", encoding="utf-8")


class AskLightBehaviorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        for entry in ASK_LIGHT.load_map()["skills"]:
            fields, error = ASK_LIGHT.read_frontmatter(ROOT.parent / entry["name"] / "SKILL.md")
            self.assertFalse(error, entry["name"])
            write_skill(
                self.root,
                entry["name"],
                metadata=entry["name"] != "eli5",
                user_invoked=fields.get("disable-model-invocation", "").lower() == "true",
            )
        self.roots = [{"category": "first-party", "path": str(self.root)}]

    def tearDown(self) -> None:
        self.temp.cleanup()

    def route(self, goal: str, *, host: str = "codex", task_kind: str = "", availability=None):
        context = {"goal": goal, "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": task_kind, "availability": availability or host, "invocationControl": "explicit-only"}
        return ASK_LIGHT.route(self.roots, context, host)

    def test_representative_intents_choose_the_expected_top_skill(self) -> None:
        cases = {
            "Explain this like I'm five": "eli5",
            "Practice Japanese conversation": "language-learning",
            "Give me a one-line recap": "recap",
            "I don't know which Skill to use": "ask-light",
            "Initialize this repo for a new project": "project-init",
            "Turn these requirements into a project spec": "project-spec",
            "Break this spec into implementation tickets": "project-tickets",
            "Review whether this project is actually complete": "project-review",
            "Investigate this bug": "diagnosing-bugs",
            "I need to clarify a fuzzy product idea": "clarify",
            "I need to preserve a decision map across sessions": "decision-map",
            "Set up a manuscript workflow": "manuscript-ops",
            "I have a large foggy multi-session project": "decision-map",
            "We are missing an external fact": "research",
            "We need an experiment to decide": "prototype",
            "This information is held by another person": "to-questionnaire",
            "The SPEC exists and needs slicing": "project-tickets",
            "The ticket is ready and unblocked": "implement",
            "This is a hard bug or regression": "diagnosing-bugs",
            "Implementation complete and needs acceptance": "project-review",
            "The accepted project is ready to publish": "release-workflow",
            "The previous explanation did not land": "wait-what",
            "Review the current code changes": "code-review",
            "Review this document": "generic-review",
            "Configure agents for this task": "agent-config",
            "Walk me through setting up credentials": "wizard",
        }
        for phrase, expected in cases.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(self.route(phrase)["skill"], expected)

    def test_folded_yaml_descriptions_are_parsed_from_package_frontmatter(self) -> None:
        expected = {
            "language-learning": "Language-learning tutor for any target language.",
            "release-workflow": "Run a first-party Agent Skills collection",
        }
        for name, fragment in expected.items():
            with self.subTest(name=name):
                fields, error = ASK_LIGHT.read_frontmatter(ROOT.parent / name / "SKILL.md")
                self.assertFalse(error)
                self.assertIn(fragment, fields["description"])
                self.assertNotEqual(fields["description"], ">-")

    def test_task_kind_alias_routes_without_goal_text(self) -> None:
        result = self.route("", task_kind="debugging")
        self.assertEqual((result["status"], result["skill"]), ("RECOMMEND", "diagnosing-bugs"))
        self.assertIn("taskKind:debugging->diagnosing-bugs", result["reason"])

    def test_project_scope_and_final_authority_break_material_ties(self) -> None:
        self.assertEqual(self.route("Clarify this project requirement")["skill"], "project-clarify")
        self.assertEqual(self.route("Review this branch for final acceptance")["skill"], "project-review")
        self.assertEqual(self.route("Final review this artifact")["skill"], "project-review")
        self.assertEqual(self.route("Review this artifact", task_kind="final-review")["skill"], "project-review")

    def test_precedence_does_not_create_a_route_without_a_semantic_match(self) -> None:
        for goal in ("Deploy this repository", "Archive this repo", "Create a README for this project"):
            with self.subTest(goal=goal):
                result = self.route(goal)
                self.assertEqual((result["status"], result["skill"]), ("NEED-INPUT", ""))

    def test_review_task_kind_routes_to_code_review(self) -> None:
        result = self.route("", task_kind="review")
        self.assertEqual((result["status"], result["skill"]), ("RECOMMEND", "code-review"))

    def test_unresolved_material_tie_requests_input(self) -> None:
        result = self.route("Review this artifact and branch")
        self.assertEqual(result["status"], "NEED-INPUT")
        self.assertIn("Material Light route tie", " ".join(result["gaps"]))

    def test_frozen_skill_without_optional_metadata_remains_navigable(self) -> None:
        result = self.route("Explain this like I'm five")
        self.assertEqual((result["status"], result["skill"], result["invocation"]), ("RECOMMEND", "eli5", "$eli5"))

    def test_logical_route_is_preserved_when_host_reports_skill_unavailable(self) -> None:
        availability = {"host": "codex", "unavailableSkills": ["project-review"], "readablePaths": [str(self.root)]}
        result = self.route("Review whether this project is actually complete", availability=availability)
        self.assertEqual((result["status"], result["skill"]), ("BLOCKED", "project-review"))

    def test_generic_root_and_unknown_neighbor_are_not_light_provenance(self) -> None:
        generic = Path(self.temp.name) / "generic"
        generic.mkdir()
        write_skill(generic, "project-review")
        write_skill(self.root, "third-party-helper")
        context = {"goal": "final acceptance", "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": "final-review", "availability": "codex", "invocationControl": "explicit-only"}
        self.assertEqual(ASK_LIGHT.route([{"category": "generic", "path": str(generic)}], context)["status"], "BLOCKED")
        names = {candidate["name"] for candidate in self.route("final acceptance")["candidates"]}
        self.assertNotIn("third-party-helper", names)

    def test_duplicate_first_party_copy_requires_host_precedence(self) -> None:
        duplicate = Path(self.temp.name) / "duplicate"
        duplicate.mkdir()
        write_skill(duplicate, "recap")
        context = {"goal": "one-line recap", "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": "", "availability": "codex", "invocationControl": "explicit-only"}
        result = ASK_LIGHT.route(self.roots + [{"category": "first-party", "path": str(duplicate)}], context)
        self.assertEqual((result["status"], result["skill"]), ("BLOCKED", "recap"))
        self.assertIn("multiple available first-party copies", " ".join(result["gaps"]))

    def test_overlapping_roots_deduplicate_the_same_physical_package(self) -> None:
        context = {"goal": "one-line recap", "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": "", "availability": "codex", "invocationControl": "explicit-only"}
        result = ASK_LIGHT.route(self.roots + [{"category": "first-party", "path": str(self.root / "recap")}], context)
        self.assertEqual((result["status"], result["skill"]), ("RECOMMEND", "recap"))
        self.assertEqual(len([item for item in result["candidates"] if item["name"] == "recap"]), 1)

    def test_first_party_root_requires_a_nonempty_path(self) -> None:
        context = {"goal": "one-line recap", "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": "", "availability": "codex", "invocationControl": "explicit-only"}
        for record in ({"category": "first-party"}, {"category": "first-party", "path": ""}):
            with self.subTest(record=record):
                result = ASK_LIGHT.route([record], context)
                self.assertEqual((result["status"], result["skill"]), ("BLOCKED", "recap"))
                self.assertIn("non-empty path", " ".join(result["gaps"]))

    def test_host_invocation_rendering_is_explicit(self) -> None:
        self.assertEqual(self.route("one-line recap", host="codex")["invocation"], "$recap")
        self.assertEqual(self.route("one-line recap", host="claude-code")["invocation"], "/recap")
        self.assertEqual(self.route("one-line recap", host="other")["invocation"], "Skill: recap")

    def test_supported_invocation_controls_are_checked_against_package_type(self) -> None:
        context = {"goal": "review convergence", "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": "", "availability": "codex", "invocationControl": "model-callable"}
        model_callable = ASK_LIGHT.route(self.roots, context)
        self.assertEqual((model_callable["status"], model_callable["skill"]), ("RECOMMEND", "review-loop"))

        context.update({"goal": "one-line recap", "invocationControl": "either"})
        either = ASK_LIGHT.route(self.roots, context)
        self.assertEqual((either["status"], either["skill"]), ("RECOMMEND", "recap"))

        context["invocationControl"] = "model-callable"
        incompatible = ASK_LIGHT.route(self.roots, context)
        self.assertEqual((incompatible["status"], incompatible["skill"]), ("BLOCKED", "recap"))
        self.assertIn("incompatible", " ".join(incompatible["gaps"]))

    def test_selected_local_pointer_must_resolve(self) -> None:
        (self.root / "recap" / "SKILL.md").write_text("---\nname: recap\ndescription: recap\n---\n\n[missing](references/missing.md)\n", encoding="utf-8")
        result = self.route("one-line recap")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("body/reference unreadable", " ".join(result["gaps"]))

    def test_selected_local_directory_pointer_is_a_valid_package_reference(self) -> None:
        (self.root / "recap" / "tests").mkdir()
        (self.root / "recap" / "SKILL.md").write_text("---\nname: recap\ndescription: recap\n---\n\n[tests](tests/)\n", encoding="utf-8")
        result = self.route("one-line recap")
        self.assertEqual((result["status"], result["skill"]), ("RECOMMEND", "recap"))
        self.assertEqual(result["reads"]["references"], 1)

    def test_selected_nested_markdown_pointers_resolve_recursively(self) -> None:
        references = self.root / "recap" / "references"
        references.mkdir()
        (self.root / "recap" / "SKILL.md").write_text("---\nname: recap\ndescription: recap\n---\n\n[first](references/first.md)\n", encoding="utf-8")
        (references / "first.md").write_text("[second](second.md)\n", encoding="utf-8")
        (references / "second.md").write_text("[cycle](first.md)\n", encoding="utf-8")

        valid = self.route("one-line recap")
        self.assertEqual((valid["status"], valid["reads"]["references"]), ("RECOMMEND", 2))

        (references / "second.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        broken = self.route("one-line recap")
        self.assertEqual(broken["status"], "BLOCKED")
        self.assertIn("body/reference unreadable", " ".join(broken["gaps"]))

    def test_unclosed_frontmatter_is_unavailable(self) -> None:
        (self.root / "recap" / "SKILL.md").write_text(
            "---\nname: recap\ndescription: recap\nBody without closing delimiter\n",
            encoding="utf-8",
        )
        result = self.route("one-line recap")
        self.assertEqual((result["status"], result["skill"]), ("BLOCKED", "recap"))
        self.assertIn("frontmatter is not closed", " ".join(result["gaps"]))

    def test_invalid_utf8_metadata_and_reference_return_blocked(self) -> None:
        (self.root / "recap" / "SKILL.md").write_bytes(b"\xff\xfe")
        metadata = self.route("one-line recap")
        self.assertEqual((metadata["status"], metadata["skill"]), ("BLOCKED", "recap"))

        write_skill(self.root, "recap", body="[bad](references/bad.md)")
        reference = self.root / "recap" / "references" / "bad.md"
        reference.parent.mkdir(exist_ok=True)
        reference.write_bytes(b"\xff\xfe")
        body = self.route("one-line recap")
        self.assertEqual((body["status"], body["skill"]), ("BLOCKED", "recap"))
        self.assertIn("body/reference unreadable", " ".join(body["gaps"]))

    def test_workflow_uses_map_and_validates_each_unique_step_package(self) -> None:
        context = {"goal": "build a software feature", "artifacts": ["brief.md"], "blockers": "none", "projectType": "software", "taskKind": "feature", "availability": "codex", "invocationControl": "explicit-only"}
        result = ASK_LIGHT.route(self.roots, context, mode="workflow")
        self.assertEqual((result["status"], result["workflow"], result["finalAuthority"]), ("RECOMMEND", "software-feature", "project-review"))
        self.assertEqual(result["reads"]["bodies"], len({step["skill"] for step in result["steps"]}))
        for step in result["steps"]:
            self.assertTrue({"expectedInput", "expectedOutput", "handoffArtifact", "stopCondition", "optional", "missingDependency"}.issubset(step))
            self.assertNotIn("public contract", step["expectedInput"])
            self.assertNotEqual(step["handoffArtifact"], f"{step['skill']} result")
        spec = result["steps"][0]
        self.assertEqual(spec["skill"], "project-spec")
        self.assertIn("clarified goal", spec["expectedInput"])
        self.assertIn("SPEC artifact", spec["handoffArtifact"])
        self.assertEqual(spec["invocationType"], "user-invoked")
        self.assertIn("nothing was invoked", result["execution"])
        self.assertTrue({"source", "reason", "invocation", "confidence", "alternative", "missingDependency"}.issubset(result))
        self.assertEqual(result["missingDependency"], "")

    def test_workflow_accepts_an_explicit_empty_blocker_field(self) -> None:
        context = {"goal": "build a software feature", "artifacts": ["brief.md"], "blockers": "", "projectType": "software", "taskKind": "feature", "availability": "codex", "invocationControl": "explicit-only"}

        result = ASK_LIGHT.route(self.roots, context, mode="workflow")

        self.assertEqual((result["status"], result["workflow"]), ("RECOMMEND", "software-feature"))

    def test_new_project_workflow_preserves_setup_and_discovery_aliases(self) -> None:
        for task_kind in ("setup", "discovery"):
            with self.subTest(task_kind=task_kind):
                context = {"goal": "initialize a new project", "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": task_kind, "availability": "codex", "invocationControl": "explicit-only"}
                result = ASK_LIGHT.route(self.roots, context, mode="workflow")
                self.assertEqual((result["status"], result["workflow"]), ("RECOMMEND", "new-project-initialization"))

    def test_workflow_boundary_results_keep_the_workflow_schema(self) -> None:
        required = {"workflow", "entryCondition", "steps", "stoppingBoundary", "missingDependency", "finalAuthority"}
        cases = [
            {"goal": "", "artifacts": [], "blockers": "", "projectType": "software", "taskKind": "feature", "availability": "codex", "invocationControl": "explicit-only"},
            {"goal": "build a software feature", "artifacts": [], "blockers": "", "projectType": "software", "taskKind": "feature", "availability": "codex", "invocationControl": "automatic"},
            {"goal": "archive this project", "artifacts": [], "blockers": "", "projectType": "software", "taskKind": "archive", "availability": "codex", "invocationControl": "explicit-only"},
        ]
        for context in cases:
            with self.subTest(context=context):
                result = ASK_LIGHT.route(self.roots, context, mode="workflow")
                self.assertEqual(result["status"], "NEED-INPUT")
                self.assertTrue(required.issubset(result))
                self.assertEqual(result["steps"], [])

    def test_workflow_blocks_when_a_step_has_a_broken_local_pointer(self) -> None:
        project_init = self.root / "project-init" / "SKILL.md"
        project_init.write_text(
            "---\nname: project-init\ndescription: fixture\ndisable-model-invocation: true\n---\n\n"
            "[missing](references/missing.md)\n",
            encoding="utf-8",
        )
        context = {"goal": "initialize a new project", "artifacts": ["README.md"], "blockers": "none", "projectType": "generic", "taskKind": "initialization", "availability": "codex", "invocationControl": "explicit-only"}

        result = ASK_LIGHT.route(self.roots, context, mode="workflow")

        self.assertEqual((result["status"], result["skill"]), ("BLOCKED", ""))
        self.assertIn("body/reference unreadable", " ".join(result["gaps"]))
        self.assertEqual(result["reads"]["bodies"], 1)
        self.assertEqual(result["missingDependency"], "project-init")

    def test_workflow_prefers_specific_project_recipe_and_rejects_automatic_control(self) -> None:
        context = {"goal": "initialize a manuscript project", "artifacts": ["draft.md"], "blockers": "none", "projectType": "manuscript", "taskKind": "initialization", "availability": "codex", "invocationControl": "explicit-only"}
        result = ASK_LIGHT.route(self.roots, context, mode="workflow")
        self.assertEqual(result["workflow"], "manuscript-project")
        context["invocationControl"] = "automatic"
        blocked = ASK_LIGHT.route(self.roots, context, mode="workflow")
        self.assertEqual(blocked["status"], "NEED-INPUT")
        self.assertIn("explicit-only", " ".join(blocked["gaps"]))
        self.assertEqual(blocked["steps"], [])

    def test_workflow_duplicate_required_step_requires_host_precedence(self) -> None:
        duplicate = Path(self.temp.name) / "workflow-duplicate"
        duplicate.mkdir()
        write_skill(duplicate, "project-init")
        context = {"goal": "initialize a new project", "artifacts": ["README.md"], "blockers": "none", "projectType": "generic", "taskKind": "initialization", "availability": "codex", "invocationControl": "explicit-only"}
        result = ASK_LIGHT.route(self.roots + [{"category": "first-party", "path": str(duplicate)}], context, mode="workflow")
        self.assertEqual((result["status"], result["skill"]), ("BLOCKED", ""))
        self.assertIn("Duplicate first-party workflow steps", " ".join(result["gaps"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
