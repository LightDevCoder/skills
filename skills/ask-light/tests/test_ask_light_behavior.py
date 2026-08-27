from __future__ import annotations

import importlib.util
import json
import os
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


def write_effort_state(
    root: Path,
    name: str,
    *,
    spec_status: str | None = None,
    ticket_statuses: list[str] | None = None,
    acceptance_verdict: str | None = None,
    acceptance_status: str | None = None,
) -> None:
    """Write one `.scratch/<name>` effort for multi-effort regression tests."""
    effort = root / ".scratch" / name
    effort.mkdir(parents=True, exist_ok=True)
    if spec_status is not None:
        if spec_status == "active":
            (effort / "spec.md").write_text("# SPEC\nStatus: active\n", encoding="utf-8")
        else:
            (effort / "spec.md").write_text(f"# SPEC\nStatus: {spec_status}\n", encoding="utf-8")
    if ticket_statuses is not None:
        issues = effort / "issues"
        issues.mkdir(parents=True, exist_ok=True)
        for index, status in enumerate(ticket_statuses, start=1):
            (issues / f"{index:02d}.md").write_text(f"- Status: {status}\n", encoding="utf-8")
    if acceptance_verdict is not None:
        (effort / "acceptance.md").write_text(f"Verdict: {acceptance_verdict}\n", encoding="utf-8")
    if acceptance_status is not None:
        (effort / "acceptance.md").write_text(f"Status: {acceptance_status}\n", encoding="utf-8")


def write_project_state(
    root: Path,
    *,
    initialized: bool = True,
    spec: bool = True,
    unresolved_ticket: bool = False,
    resolved_ticket: bool = False,
    acceptance: bool = False,
    clear_goal: bool = True,
    ticket_status: str | None = None,
    ticket_statuses: list[str] | None = None,
    spec_inactive: bool = False,
    acceptance_verdict: str | None = "PASS",
    acceptance_status: str | None = None,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if initialized:
        agents = root / "docs" / "agents"
        agents.mkdir(parents=True, exist_ok=True)
        content = "<!-- light-project:managed:start -->\n# Light Project Configuration\n"
        if clear_goal:
            content += "- Goal: Build a parser\n- Outputs: parser, tests\n"
        else:
            content += "- Goal: ?\n- Outputs: (none recorded)\n"
        content += "- Relevant Skills: project-spec, project-tickets, implement, project-review\n<!-- light-project:managed:end -->\n"
        (agents / "light-project.md").write_text(content, encoding="utf-8")
    if spec and not spec_inactive:
        (root / "docs").mkdir(exist_ok=True)
        (root / "docs" / "SPEC.md").write_text("# SPEC\n\nStable acceptance criteria.\n", encoding="utf-8")
    if spec_inactive:
        old = root / ".scratch" / "old"
        (old).mkdir(parents=True, exist_ok=True)
        (old / "spec.md").write_text("# SPEC\n\nStatus: superseded\n", encoding="utf-8")
    if ticket_statuses is not None:
        issues = root / ".scratch" / "effort" / "issues"
        issues.mkdir(parents=True, exist_ok=True)
        for index, status in enumerate(ticket_statuses, start=1):
            target = issues / f"{index:02d}-ticket.md"
            if status is None or status == "":
                target.write_text("# Ticket body\n\nNo status recorded.\n", encoding="utf-8")
            else:
                target.write_text(f"- Status: {status}\n", encoding="utf-8")
    elif ticket_status is not None:
        issues = root / ".scratch" / "effort" / "issues"
        issues.mkdir(parents=True, exist_ok=True)
        target = issues / "01-ticket.md"
        if ticket_status == "":
            target.write_text("# Ticket body\n\nNo status recorded.\n", encoding="utf-8")
        else:
            target.write_text(f"- Status: {ticket_status}\n", encoding="utf-8")
    elif unresolved_ticket or resolved_ticket:
        issues = root / ".scratch" / "effort" / "issues"
        issues.mkdir(parents=True, exist_ok=True)
        status = "resolved" if resolved_ticket else "open"
        (issues / "01-implement.md").write_text(f"- Status: {status}\n", encoding="utf-8")
    if acceptance:
        # Acceptance evidence uses the REAL project-review durable layout;
        # legacy root files were never producer-owned output.
        if acceptance_status is not None:
            write_project_review_state(
                root, reviewed_effort="effort", verdict_content=f"Status: {acceptance_status}\n"
            )
        elif acceptance_verdict is None:
            write_project_review_state(
                root, reviewed_effort="effort", verdict_content="Acceptance record exists.\n"
            )
        else:
            write_project_review_state(root, reviewed_effort="effort", verdict=acceptance_verdict)


def write_project_review_state(
    root: Path,
    *,
    reviewed_effort: str | None = None,
    charter_source: str | None = None,
    verdict: str | None = "PASS",
    verdict_content: str | None = None,
    include_charter: bool = True,
    dir_name: str = ".project-review",
) -> Path:
    """Write a durable record with the REAL project-review layout.

    Mirrors skills/project-review/references/WORKFLOW.md (charter/state/verdict)
    and the Charter fields from acceptance-charter.md (`Source:` is the
    review-ownership metadata that identifies what was reviewed).
    """
    review_dir = root / dir_name
    review_dir.mkdir(parents=True, exist_ok=True)
    if include_charter:
        if charter_source is not None:
            source_value = charter_source
        elif reviewed_effort is not None:
            source_value = f"approved effort SPEC — `.scratch/{reviewed_effort}/spec.md`"
        else:
            source_value = "direct user-provided brief (session request message)"
        (review_dir / "charter.md").write_text(
            "# Acceptance Charter\n\n"
            "## Revision\n"
            "- Charter revision: 1\n"
            "- Supersedes: none\n"
            "\n"
            "## Acceptance baseline\n"
            f"- Source: {source_value}\n"
            "- Source revision or identity: commit 4f1c9ab\n"
            "- Approval state: approved\n"
            "\n"
            "## Review Profile\n"
            "- Profile: generic\n",
            encoding="utf-8",
        )
    (review_dir / "state.md").write_text(
        "# Project-review State\n"
        "- Status: READY\n"
        "- Round: 1\n",
        encoding="utf-8",
    )
    if verdict_content is not None:
        (review_dir / "verdict.md").write_text(verdict_content, encoding="utf-8")
    elif verdict is not None:
        # Real produced records wrap the value in markdown emphasis.
        (review_dir / "verdict.md").write_text(
            "# Verdict\n\n"
            "- Charter revision: 1\n"
            "- Profile: generic\n"
            f"- Verdict: **{verdict}**\n"
            "- Round: round-01 (final)\n"
            "\n"
            "## Conclusion\n"
            "The frozen baseline is accepted.\n",
            encoding="utf-8",
        )
    return review_dir


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

    def route(self, goal: str, *, host: str = "codex", task_kind: str = "", availability=None, mode: str = "next"):
        context = {"goal": goal, "artifacts": [], "blockers": "", "projectType": "generic", "taskKind": task_kind, "availability": availability or host, "invocationControl": "explicit-only"}
        return ASK_LIGHT.route(self.roots, context, host, mode)

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
        self.assertIn("read-only", result["execution"])
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

    def test_skill_map_exposes_families_for_collection_navigation(self) -> None:
        data = ASK_LIGHT.load_map()
        self.assertEqual(set(data["skillFamilies"]), {item["name"] for item in data["skills"]})
        self.assertEqual(data["skillFamilies"]["project-init"], "project")
        self.assertEqual(data["skillFamilies"]["socratic"], "clarification")

    def test_navigation_mode_browses_families_without_project_context(self) -> None:
        result = self.route("project Skills", mode="navigate")
        self.assertEqual(result["status"], "RECOMMEND")
        self.assertIn("project", result["reason"])
        names = {item["name"] for item in result["skills"]}
        self.assertIn("project-init", names)
        self.assertIn("project-spec", names)

    def test_project_state_detection_from_real_repository_evidence(self) -> None:
        cases = {
            "init-no-spec": ({"initialized": True, "spec": False, "clear_goal": True}, "project-spec", "initialized-no-spec"),
            "init-unclear": ({"initialized": True, "spec": False, "clear_goal": False}, "project-clarify", "initialized-unclear"),
            "spec-no-tickets": ({"initialized": True, "spec": True}, "project-tickets", "spec-no-tickets"),
            "tickets-open": ({"initialized": True, "spec": True, "unresolved_ticket": True}, "implement", "work-in-progress"),
            "all-resolved": ({"initialized": True, "spec": True, "resolved_ticket": True}, "project-review", "implementation-complete"),
        }
        for label, (kwargs, expected_skill, expected_stage) in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix="ask-light-project-") as tmp:
                project = Path(tmp) / "project"
                write_project_state(project, **kwargs)
                context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
                result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
                self.assertEqual(result["status"], "RECOMMEND", result)
                self.assertEqual(result["skill"], expected_skill)
                self.assertEqual(result["projectStage"], expected_stage)
                self.assertTrue(result["completed"], "project-state result must list completed evidence")
                self.assertTrue(result["missing"], "project-state result must list missing evidence")
                self.assertTrue(result["reason"], "project-state result must include workflow reasoning")

    def test_natural_project_state_questions_use_real_repository_evidence(self) -> None:
        phrases = [
            "What's next for this project?",
            "What should I do next?",
            "Where is this project now?",
            "What stage are we at?",
            "What's missing?",
            "What have we finished?",
            "What is left?",
            "What should I work on now?",
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase), tempfile.TemporaryDirectory(prefix="ask-light-natural-") as tmp:
                project = Path(tmp) / "project"
                write_project_state(project, initialized=True, spec=True)
                context = {
                    "projectRoot": str(project),
                    "goal": phrase,
                    "invocationControl": "explicit-only",
                    "availability": "codex",
                }
                result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
                self.assertEqual(result["status"], "RECOMMEND", result)
                self.assertEqual(result["skill"], "project-tickets")
                self.assertEqual(result["projectStage"], "spec-no-tickets")
                self.assertNotIn("ticket", phrase.lower(), "prompt must not encode the expected conclusion")
                self.assertIn("SPEC", result["reason"])

    def test_ticket_state_fail_closed_regressions(self) -> None:
        cases = [
            ("missing-status", [None], "NEED-INPUT", "tickets-unknown", ""),
            ("unknown-status", ["unknown"], "NEED-INPUT", "tickets-unknown", ""),
            ("mixed-resolved-unknown", ["resolved", "unknown"], "NEED-INPUT", "tickets-unknown", ""),
            ("resolved-only", ["resolved"], "RECOMMEND", "implementation-complete", "project-review"),
            ("unresolved", ["open"], "RECOMMEND", "work-in-progress", "implement"),
        ]
        for label, statuses, expected_status, expected_stage, expected_skill in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix="ask-light-tickets-") as tmp:
                project = Path(tmp) / "project"
                write_project_state(project, initialized=True, spec=True, ticket_statuses=statuses)
                context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
                result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
                self.assertEqual(result["status"], expected_status, result)
                self.assertEqual(result["projectStage"], expected_stage)
                self.assertEqual(result["skill"], expected_skill)
                if expected_status == "NEED-INPUT":
                    self.assertIn("cannot be established", result["reason"])
                    self.assertNotEqual(result["skill"], "project-review")

    def test_superseded_scratch_spec_is_not_active_project_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-spec-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True, spec_inactive=True)
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["skill"], "project-spec")
            self.assertEqual(result["projectStage"], "initialized-no-spec")
            self.assertNotEqual(result["projectStage"], "spec-no-tickets")

    def test_acceptance_verdicts_are_fail_closed(self) -> None:
        cases = [
            ("pass", "PASS", "RECOMMEND", "accepted", ""),
            ("fail", "FAIL", "NEED-INPUT", "acceptance-not-passed", ""),
            ("blocked", "BLOCKED", "NEED-INPUT", "acceptance-not-passed", ""),
            ("unknown-verdict", "maybe", "NEED-INPUT", "acceptance-unknown", ""),
            ("missing-verdict", None, "NEED-INPUT", "acceptance-unknown", ""),
        ]
        for label, verdict, expected_status, expected_stage, expected_skill in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix="ask-light-accept-") as tmp:
                project = Path(tmp) / "project"
                write_project_state(
                    project,
                    initialized=True,
                    spec=True,
                    ticket_statuses=["resolved"],
                    acceptance=True,
                    acceptance_verdict=verdict,
                )
                context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
                result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
                self.assertEqual(result["status"], expected_status, result)
                self.assertEqual(result["projectStage"], expected_stage)
                self.assertEqual(result["skill"], expected_skill)
                if expected_status == "RECOMMEND":
                    self.assertEqual(result["next"], "no-execution")
                    self.assertIn("acceptance passed", result["completed"])
                    self.assertEqual(result["missing"], [])
                else:
                    self.assertNotEqual(result["projectStage"], "accepted")
                    self.assertIn("acceptance", result["reason"].lower())

    def test_historical_open_ticket_does_not_pollute_current_resolved_effort(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-a-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_effort_state(project, "old-effort", ticket_statuses=["open"])
            context = {"projectRoot": str(project), "goal": "Where is this project now?", "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")

    def test_historical_resolved_does_not_hide_current_open_ticket(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-b-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["open"])
            write_effort_state(project, "old-effort", ticket_statuses=["resolved"])
            context = {"projectRoot": str(project), "goal": "What should I work on now?", "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "work-in-progress")
            self.assertEqual(result["skill"], "implement")

    def test_multiple_active_efforts_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-e-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "one", spec_status="active")
            write_effort_state(project, "two", spec_status="active")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "ambiguous-current-effort")
            self.assertEqual(result["skill"], "")
            self.assertEqual(result["next"], "no-execution")
            self.assertIn("Multiple active Light efforts", result["reason"])

    def test_superseded_effort_is_not_selected_over_active_effort(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-f-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_effort_state(project, "superseded", spec_status="superseded", ticket_statuses=["open"])
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")

    def test_no_reliable_current_effort_does_not_guess(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-g-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "historical-a", spec_status="superseded", ticket_statuses=["resolved"])
            write_effort_state(project, "historical-b", spec_status="archived", ticket_statuses=["open"])
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "ambiguous-current-effort")
            self.assertEqual(result["skill"], "")
            self.assertIn("none is active/current", result["reason"])

    def test_generic_complete_acceptance_status_is_not_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-h-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(
                project,
                reviewed_effort="current",
                verdict_content="Status: complete\n",
            )
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "acceptance-unknown")
            self.assertEqual(result["skill"], "")
            self.assertNotEqual(result["projectStage"], "accepted")

    def test_explicit_verdict_pass_is_not_downgraded_by_complete_status(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-i-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(
                project,
                reviewed_effort="current",
                verdict_content="Status: complete\nVerdict: **PASS**\n",
            )
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted")
            self.assertEqual(result["skill"], "")
            self.assertEqual(result["next"], "no-execution")

    def test_explicit_pass_acceptance_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-multi-i-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="PASS")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted")
            self.assertEqual(result["skill"], "")
            self.assertEqual(result["next"], "no-execution")
            self.assertIn("acceptance passed", result["completed"])

    def test_natural_language_family_navigation(self) -> None:
        cases = [
            ("What project skills do I have?", {"family": "project", "expected": {"project-init", "project-spec", "project-tickets", "release-workflow"}}),
            ("Show me the review skills", {"family": "review", "expected": {"code-review", "generic-review", "project-review", "review-loop"}}),
            ("Which skills are for learning?", {"family": "learning", "expected": {"eli5", "language-learning", "teach"}}),
            ("What can I use for bugs?", {"skills": {"diagnosing-bugs"}}),
            ("What's the difference between clarify and project-clarify?", {"comparison": ("clarify", "project-clarify")}),
        ]
        for phrase, expected in cases:
            with self.subTest(phrase=phrase):
                result = self.route(phrase, mode="navigate")
                self.assertEqual(result["status"], "RECOMMEND", result)
                if "family" in expected:
                    self.assertEqual(result["family"], expected["family"])
                    self.assertEqual({item["name"] for item in result["skills"]}, expected["expected"])
                elif "skills" in expected:
                    self.assertEqual({item["name"] for item in result["skills"]}, expected["skills"])
                elif "comparison" in expected:
                    self.assertEqual((result["comparison"]["left"], result["comparison"]["right"]), expected["comparison"])
                    self.assertEqual({item["name"] for item in result["skills"]}, set(expected["comparison"]))

    def test_approval_transition_does_not_fake_user_invoked_start(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-approval-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True, resolved_ticket=False, unresolved_ticket=False)
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["skill"], "project-tickets")
            approved = ASK_LIGHT.approval_transition(result, ASK_LIGHT.load_map())
            self.assertEqual(approved["next"], "host-transition-required")
            self.assertIn("user-invoked", approved["execution"])
            self.assertIn("cannot begin the target itself", approved["execution"])

    def test_approval_transition_can_begin_model_invoked_target(self) -> None:
        result = self.route("Review whether this project is actually complete")
        self.assertEqual(result["skill"], "project-review")
        approved = ASK_LIGHT.approval_transition(result, ASK_LIGHT.load_map())
        self.assertEqual(approved["next"], "beginning-project-review")
        self.assertIn("model-invoked", approved["execution"])


    def test_standalone_routes_skip_project_evidence_requirements(self) -> None:
        for phrase in ("Explain this like I'm five", "Practice Japanese conversation", "Investigate this bug"):
            with self.subTest(phrase=phrase):
                result = self.route(phrase)
                self.assertEqual(result["status"], "RECOMMEND")
                self.assertEqual(result["next"], "awaiting-approval")

    def test_approval_policy_is_documented_honestly_in_skill_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "discovery-contract.md").read_text(encoding="utf-8")
        combined = skill + "\n" + contract
        for token in ("Wait for approval", "Honor the host invocation policy", "yes", "可以", "go ahead", "do it", "用这个", "user-invoked", "model-invoked", "does **not** fake execution", "exact invocation"):
            self.assertIn(token, combined)
        self.assertIn("user-invoked Skill from auto-invoking another user-invoked Skill", combined)
        self.assertIn("Do not claim a direct transition without host evidence", skill)
        self.assertIn("recommendation phase was read-only", skill)

    def test_root_discovery_from_environment(self) -> None:
        old = os.environ.get("LIGHT_SKILL_ROOTS")
        os.environ["LIGHT_SKILL_ROOTS"] = json.dumps([{"category": "first-party", "path": str(self.root)}])
        try:
            roots = ASK_LIGHT.discover_roots()
            self.assertTrue(any(Path(record["path"]).resolve() == self.root.resolve() for record in roots))
        finally:
            if old is None:
                os.environ.pop("LIGHT_SKILL_ROOTS", None)
            else:
                os.environ["LIGHT_SKILL_ROOTS"] = old

    def test_root_discovery_from_codex_home(self) -> None:
        codex_home = Path(self.temp.name) / "codex-home"
        skills_dir = codex_home / "skills"
        (skills_dir / "ask-light").mkdir(parents=True)
        (skills_dir / "ask-light" / "SKILL.md").write_text("---\nname: ask-light\ndescription: fixture\n---\n", encoding="utf-8")
        old = os.environ.get("CODEX_HOME")
        os.environ["CODEX_HOME"] = str(codex_home)
        try:
            roots = ASK_LIGHT.discover_roots()
            self.assertTrue(any(Path(record["path"]).resolve() == skills_dir.resolve() for record in roots))
        finally:
            if old is None:
                os.environ.pop("CODEX_HOME", None)
            else:
                os.environ["CODEX_HOME"] = old


    def test_results_declare_approval_boundary(self) -> None:
        result = self.route("one-line recap")
        self.assertEqual(result["next"], "awaiting-approval")
        self.assertIn("read-only", result["execution"])


    def test_project_review_integration_current_pass_is_accepted(self) -> None:
        # Case A: real .project-review record owned by the current effort, PASS.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-a-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="PASS")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted")
            self.assertEqual(result["skill"], "")
            self.assertEqual(result["next"], "no-execution")
            self.assertIn("acceptance passed", result["completed"])
            self.assertEqual(result["missing"], [])

    def test_project_review_integration_current_fail_is_not_accepted(self) -> None:
        # Case B: current-effort FAIL verdict must not complete the workflow.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-b-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="FAIL")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "acceptance-not-passed")
            self.assertNotEqual(result["projectStage"], "accepted")

    def test_project_review_integration_blocked_verdict_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-blk-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="BLOCKED")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "acceptance-not-passed")

    def test_project_review_integration_historical_pass_does_not_accept_current(self) -> None:
        # Case C: effort A's PASS must not accept current effort B.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-c-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "new-effort", spec_status="active", ticket_statuses=["resolved"])
            write_effort_state(project, "old-effort", spec_status="superseded")
            write_project_review_state(project, charter_source="`.scratch/old-effort/spec.md`", verdict="PASS")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")

    def test_project_review_integration_historical_fail_is_ignored_for_current(self) -> None:
        # Case D: a historical effort's FAIL verdict is not current evidence.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-d-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "new-effort", spec_status="active", ticket_statuses=["resolved"])
            write_effort_state(project, "old-effort", spec_status="superseded")
            write_project_review_state(project, charter_source="`.scratch/old-effort/spec.md`", verdict="FAIL")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")

    def test_project_review_integration_unresolvable_ownership_fails_closed(self) -> None:
        # Case E1: a verdict without any Charter ownership evidence.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-e1-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, include_charter=False, verdict="PASS")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "review-ownership-unknown")
            self.assertEqual(result["skill"], "")
            self.assertEqual(result["next"], "no-execution")
            self.assertIn("ownership", result["reason"].lower())

        # Case E2: a Charter whose Source cites no resolvable review target.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-e2-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, charter_source="a verbal promise from the user chat", verdict="PASS")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "review-ownership-unknown")
            self.assertNotEqual(result["projectStage"], "accepted")

    def test_stale_root_acceptance_file_cannot_contaminate_current_verdict(self) -> None:
        # Case F: legacy/root acceptance files are not authoritative evidence.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-f-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="PASS")
            agents = project / "docs" / "agents"
            (agents / "acceptance.md").write_text("Verdict: FAIL\n", encoding="utf-8")
            (agents / "review-verdict.md").write_text("Verdict: BLOCKED\n", encoding="utf-8")
            (project / "docs" / "acceptance.md").write_text("Verdict: FAIL\n", encoding="utf-8")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted")

    def test_legacy_acceptance_paths_alone_do_not_prove_acceptance(self) -> None:
        # Root-level acceptance files alone were never producer-owned output;
        # they must not complete a workflow whose review was never run.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-f2-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            (project / "docs" / "agents").mkdir(parents=True, exist_ok=True)
            (project / "docs" / "agents" / "acceptance.md").write_text("Verdict: PASS\n", encoding="utf-8")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")

    def test_review_loop_fallback_directory_is_consumed_when_primary_missing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-loop-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="FAIL", dir_name=".review-loop")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "acceptance-not-passed")

    def test_owned_charter_without_conclusion_routes_to_project_review_resume(self) -> None:
        # A review that owns the current effort but never wrote its final
        # conclusion has no acceptance verdict; project-review resume decides.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-resume-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict=None)
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")
            self.assertNotEqual(result["projectStage"], "accepted")

    def test_pointer_to_superseded_effort_with_active_effort_fails_closed(self) -> None:
        # §11-A: contradictory current-effort evidence fails closed; ask-light
        # does not choose between the pointer and the active SPEC.
        with tempfile.TemporaryDirectory(prefix="ask-light-ptr-a-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "old", spec_status="superseded", ticket_statuses=["resolved"])
            write_effort_state(project, "new", spec_status="active", ticket_statuses=["open"])
            tracker = project / "docs" / "agents" / "light-project.md"
            tracker.write_text(tracker.read_text(encoding="utf-8") + "- Current effort: old\n", encoding="utf-8")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "contradictory-current-effort")
            self.assertEqual(result["skill"], "")
            self.assertEqual(result["next"], "no-execution")
            self.assertIn("old", result["reason"])
            self.assertIn("new", result["reason"])

    def test_pointer_to_active_effort_wins_over_superseded_neighbor(self) -> None:
        # §11-B: an explicit pointer to an active effort is consistent
        # evidence and remains accepted even when another effort is superseded.
        with tempfile.TemporaryDirectory(prefix="ask-light-ptr-b-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "new", spec_status="active", ticket_statuses=["open"])
            write_effort_state(project, "old", spec_status="superseded")
            tracker = project / "docs" / "agents" / "light-project.md"
            tracker.write_text(tracker.read_text(encoding="utf-8") + "- Current effort: new\n", encoding="utf-8")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "work-in-progress")
            self.assertEqual(result["skill"], "implement")

    def test_pointer_to_missing_effort_is_not_reinterpreted(self) -> None:
        # §11-C: a dangling pointer never silently re-resolves to another
        # active effort, even when exactly one candidate exists.
        with tempfile.TemporaryDirectory(prefix="ask-light-ptr-c-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "elsewhere", spec_status="active", ticket_statuses=["open"])
            tracker = project / "docs" / "agents" / "light-project.md"
            tracker.write_text(tracker.read_text(encoding="utf-8") + "- Current effort: vanished\n", encoding="utf-8")
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["status"], "NEED-INPUT", result)
            self.assertEqual(result["projectStage"], "ambiguous-current-effort")

    def test_archive_root_citation_counts_as_historical_review(self) -> None:
        # A review citing another repo copy's archive path is clearly not the
        # current effort's review and must not accept the current effort.
        with tempfile.TemporaryDirectory(prefix="ask-light-pr-hist2-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(
                project,
                charter_source="release audit of `.scratch/archive/completed-feature/spec.md`",
                verdict="PASS",
            )
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["projectStage"], "implementation-complete")
            self.assertEqual(result["skill"], "project-review")


if __name__ == "__main__":
    unittest.main(verbosity=2)