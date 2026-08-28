from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ask_light", ROOT / "scripts" / "ask_light.py")
assert SPEC and SPEC.loader
ASK_LIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASK_LIGHT)

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "ask-light-fixture",
    "GIT_AUTHOR_EMAIL": "ask-light-fixture@example.com",
    "GIT_COMMITTER_NAME": "ask-light-fixture",
    "GIT_COMMITTER_EMAIL": "ask-light-fixture@example.com",
}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=_GIT_ENV,
        capture_output=True,
        text=True,
        timeout=60,
    )


def commit_all(root: Path, message: str) -> None:
    committed = _git(
        root, "-c", "commit.gpgsign=false", "-c", "user.name=ask-light-fixture",
        "-c", "user.email=ask-light-fixture@example.com",
        "commit", "-q", "-a", "-m", message,
    )
    assert committed.returncode == 0, committed.stderr


def ensure_git_baseline(root: Path) -> str:
    """Commit the current project tree like a real Light workflow would before
    a review freezes its baseline, and return the recorded HEAD revision."""
    inside = _git(root, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        initialized = _git(root, "init", "-q")
        assert initialized.returncode == 0, initialized.stderr
    added = _git(root, "add", "-A")
    assert added.returncode == 0, added.stderr
    status = _git(root, "status", "--porcelain")
    if status.stdout.strip():
        commit_all(root, "record reviewed baseline")
    head = _git(root, "rev-parse", "HEAD")
    assert head.returncode == 0, head.stderr
    return head.stdout.strip()


def install_host_fixture_skills(root: Path) -> list[dict[str, object]]:
    """Write every mapped Skill as an available host package and return roots."""
    for entry in ASK_LIGHT.load_map()["skills"]:
        fields, error = ASK_LIGHT.read_frontmatter(ROOT.parent / entry["name"] / "SKILL.md")
        assert not error, entry["name"]
        write_skill(
            root,
            entry["name"],
            metadata=entry["name"] != "eli5",
            user_invoked=fields.get("disable-model-invocation", "").lower() == "true",
        )
    return [{"category": "first-party", "path": str(root)}]


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
    charter_revision: str = "1",
    status: str | None = None,
    state_content: str | None = None,
    include_state: bool = True,
    verdict: str | None = "PASS",
    verdict_content: str | None = None,
    include_charter: bool = True,
    include_revision: bool = True,
    revision_identity: str | None = "auto",
    dir_name: str = ".project-review",
    profile: str = "generic",
    fixed_point: str | None = None,
    implementation_scope: str | None = None,
    final_revision: str | None = None,
) -> Path:
    """Write a durable record with the REAL project-review layout.

    Mirrors skills/project-review/references/WORKFLOW.md (charter/state/verdict)
    and the Charter fields from acceptance-charter.md (`Source:` identifies what
    was reviewed; `Source revision or identity:` freezes its baseline). With
    ``revision_identity="auto"`` the current project tree is committed first —
    exactly how a real Light workflow freezes a repository source — and the
    recorded value is that resolvable commit. ``profile`` plus ``fixed_point``
    (immutable review base), ``implementation_scope`` (reviewed software
    target), and ``final_revision`` (verdict `- Reviewed implementation
    revision:`) mirror the software Profile's three-field baseline
    (references/profiles/software.md).
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
        if not include_revision:
            revision_line = ""
        elif revision_identity == "auto":
            revision_line = f"- Source revision or identity: commit {ensure_git_baseline(root)}\n"
        else:
            revision_line = f"- Source revision or identity: {revision_identity}\n"
        (review_dir / "charter.md").write_text(
            "# Acceptance Charter\n\n"
            "## Revision\n"
            f"- Charter revision: {charter_revision}\n"
            "- Supersedes: none\n"
            "\n"
            "## Acceptance baseline\n"
            f"- Source: {source_value}\n"
            + revision_line
            + "- Approval state: approved\n"
            "\n"
            "## Review Profile\n"
            f"- Profile: {profile}\n"
            + (f"- Fixed point: {fixed_point}\n" if fixed_point is not None else "")
            + (f"- Implementation scope: {implementation_scope}\n" if implementation_scope is not None else ""),
            encoding="utf-8",
        )
    if state_content is not None:
        (review_dir / "state.md").write_text(state_content, encoding="utf-8")
    elif include_state:
        state_status = (
            status
            if status is not None
            else (verdict if verdict in ("PASS", "FAIL", "BLOCKED") else "PASS")
        )
        (review_dir / "state.md").write_text(
            "# Project-review State\n"
            f"- Status: {state_status}\n"
            f"- Charter revision: {charter_revision}\n"
            f"- Profile: {profile}\n"
            "- Round: 1\n",
            encoding="utf-8",
        )
    if verdict_content is not None:
        (review_dir / "verdict.md").write_text(verdict_content, encoding="utf-8")
    elif verdict is not None:
        # Real produced records wrap the value in markdown emphasis.
        (review_dir / "verdict.md").write_text(
            "# Verdict\n\n"
            f"- Charter revision: {charter_revision}\n"
            f"- Profile: {profile}\n"
            f"- Verdict: **{verdict}**\n"
            + (f"- Reviewed implementation revision: {final_revision}\n" if final_revision is not None else "")
            + "- Round: round-01 (final)\n"
            "\n"
            "## Conclusion\n"
            "The frozen baseline is accepted.\n",
            encoding="utf-8",
        )
    return review_dir


def append_durable_field(path: Path, line: str) -> None:
    """Tamper helper (§21): append one canonical field line to a durable record.

    Normal producer fixtures never generate duplicate canonical fields, so
    adversarial tests must mutate otherwise-valid records explicitly.
    """
    text = path.read_text(encoding="utf-8").rstrip("\n")
    path.write_text(f"{text}\n{line}\n", encoding="utf-8")


def add_ignore_rule(root: Path, pattern: str, *, mechanism: str = "gitignore") -> None:
    """Hide `pattern` from git status via .gitignore or .git/info/exclude."""
    if mechanism == "gitignore":
        target = root / ".gitignore"
    elif mechanism == "info-exclude":
        target = root / ".git" / "info" / "exclude"
        target.parent.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError(mechanism)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    separator = "" if not existing or existing.endswith("\n") else "\n"
    target.write_text(f"{existing}{separator}{pattern}\n", encoding="utf-8")


class AskLightBehaviorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

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
                write_project_state(project, initialized=True, spec=True, ticket_statuses=["resolved"])
                # The real Charter contract freezes the reviewed SPEC itself;
                # give the effort's cited source a physical presence and commit
                # it BEFORE the review records its baseline revision.
                effort_spec = project / ".scratch" / "effort" / "spec.md"
                effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
                if verdict is None:
                    write_project_review_state(
                        project,
                        reviewed_effort="effort",
                        verdict_content="# Verdict\n- Charter revision: 1\n- Profile: generic\n- Round: 1\nAcceptance record exists.\n",
                    )
                else:
                    write_project_review_state(project, reviewed_effort="effort", verdict=verdict)
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
                verdict_content="- Charter revision: 1\n- Profile: generic\n- Round: 1\nStatus: complete\nVerdict: **PASS**\n",
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
            write_project_review_state(project, reviewed_effort="current", status="READY", verdict=None)
            context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
            result = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(result["projectStage"], "project-review")
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


class ReviewFreshnessRegressionTest(unittest.TestCase):
    """A project-review verdict applies only to the reviewed baseline.

    The Charter freezes BOTH a source location and its revision; ask-light must
    prove the reviewed source still matches the recorded identity before any
    verdict (PASS, FAIL, or BLOCKED) remains authoritative for the current
    effort. Unverifiable or missing identities fail closed.
    """

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-fresh-")
        self.host_root = Path(self.temp.name) / "host"
        self.host_root.mkdir()
        self.roots = install_host_fixture_skills(self.host_root)
        self._build_count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build_reviewed_project(
        self,
        *,
        effort: str = "current",
        verdict: str | None = "PASS",
        **charter_kwargs: object,
    ) -> Path:
        self._build_count += 1
        project = Path(self.temp.name) / f"project-{self._build_count}"
        write_project_state(project, initialized=True, spec=True)
        write_effort_state(project, effort, spec_status="active", ticket_statuses=["resolved"])
        write_project_review_state(project, reviewed_effort=effort, verdict=verdict, **charter_kwargs)
        return project

    def route_project(self, project: Path) -> dict[str, object]:
        context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
        return ASK_LIGHT.route(self.roots, context, host="codex", mode="next")

    def modify_reviewed_source(self, project: Path, *, commit: bool) -> None:
        spec = project / ".scratch" / "current" / "spec.md"
        spec.write_text(spec.read_text(encoding="utf-8") + "\nPost-review change.\n", encoding="utf-8")
        if commit:
            commit_all(project, "post-review change")

    # A: unchanged baseline keeps a fresh PASS authoritative.
    def test_fresh_pass_on_unchanged_baseline_is_accepted(self) -> None:
        for label, mutate in (("no-change", False), ("untracked-noise-added", True)):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp) / "project"
                write_project_state(project, initialized=True, spec=True)
                write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
                if mutate:
                    (project / "notes").mkdir()
                    (project / "notes" / "scratchpad.md").write_text("unrelated\n", encoding="utf-8")
                    ensure_git_baseline(project)
                else:
                    ensure_git_baseline(project)
                write_project_review_state(project, reviewed_effort="current", verdict="PASS")
                result = self.route_project(project)
                self.assertEqual(result["status"], "RECOMMEND", result)
                self.assertEqual(result["projectStage"], "accepted")
                self.assertEqual(result["skill"], "")
                self.assertEqual(result["next"], "no-execution")
                self.assertIn("acceptance passed", result["completed"])

    # B: committed change after the recorded revision stales the PASS.
    def test_committed_change_after_pass_routes_back_to_project_review(self) -> None:
        project = self.build_reviewed_project(verdict="PASS")
        self.modify_reviewed_source(project, commit=True)
        result = self.route_project(project)
        self.assertNotEqual(result["projectStage"], "accepted")
        self.assertEqual(result["status"], "RECOMMEND", result)
        self.assertEqual(result["projectStage"], "review-stale")
        self.assertEqual(result["skill"], "project-review")
        self.assertIn("changed since the recorded", str(result["reason"]))

    # C: uncommitted working-tree edits also invalidate the PASS.
    def test_dirty_working_tree_after_pass_stales_the_review(self) -> None:
        project = self.build_reviewed_project(verdict="PASS")
        self.modify_reviewed_source(project, commit=False)
        result = self.route_project(project)
        self.assertEqual(result["projectStage"], "review-stale", result)
        self.assertEqual(result["skill"], "project-review")
        self.assertIn("working-tree", str(result["reason"]))

    # D: unrelated files never invalidate the review.
    def test_unrelated_file_change_keeps_fresh_acceptance(self) -> None:
        for label, commit_unrelated in (("untracked-readme", False), ("committed-readme", True)):
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS")
                readme = project / "README.md"
                readme.write_text("# Project\n\nUnrelated documentation change.\n", encoding="utf-8")
                if commit_unrelated:
                    _git(project, "add", "-A")
                    commit_all(project, "docs only")
                result = self.route_project(project)
                self.assertEqual(result["status"], "RECOMMEND", result)
                self.assertEqual(result["projectStage"], "accepted", result)

    # E: FAIL/BLOCKED applies to its baseline too — a changed baseline needs a
    # fresh review instead of keeping the old failure authoritative forever.
    def test_stale_nonpass_verdict_requires_fresh_review(self) -> None:
        for verdict in ("FAIL", "BLOCKED"):
            with self.subTest(verdict=verdict):
                project = self.build_reviewed_project(verdict=verdict)
                self.modify_reviewed_source(project, commit=True)
                result = self.route_project(project)
                self.assertEqual(result["projectStage"], "review-stale", result)
                self.assertEqual(result["skill"], "project-review")
                self.assertNotEqual(result["projectStage"], "acceptance-not-passed")

    # F: a non-resolvable revision identity must never grant acceptance.
    def test_unresolvable_revision_identity_fails_closed(self) -> None:
        project = self.build_reviewed_project(verdict="PASS", revision_identity="nonsense-or-unavailable")
        result = self.route_project(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "review-freshness-unknown", result)
        self.assertEqual(result["skill"], "")
        self.assertEqual(result["next"], "no-execution")
        self.assertNotEqual(result["projectStage"], "accepted")
        combined = str(result["reason"]) + " ".join(str(gap) for gap in result["gaps"])
        self.assertIn("Source revision or identity", combined)

    # G: blank or missing revision identity also fails closed.
    def test_missing_revision_identity_fails_closed(self) -> None:
        for label, kwargs in (
            ("blank-value", {"revision_identity": ""}),
            ("field-omitted", {"include_revision": False}),
        ):
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS", **kwargs)
                result = self.route_project(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-freshness-unknown", result)
                self.assertEqual(result["next"], "no-execution")
                self.assertIn("revision", str(result["reason"]).lower())

    # §20: exactly one unambiguous Git commit identity in one field is usable.
    def test_single_valid_source_revision_is_accepted(self) -> None:
        project = self.build_reviewed_project(verdict="PASS")
        sha = _git(project, "rev-parse", "HEAD").stdout.strip()
        charter = (project / ".project-review" / "charter.md").read_text(encoding="utf-8")
        self.assertIn(f"- Source revision or identity: commit {sha}", charter)
        result = self.route_project(project)
        self.assertEqual((result["status"], result["projectStage"]), ("RECOMMEND", "accepted"))

    # §20: multi-candidate Source revision values are never salvaged.
    def test_ambiguous_source_revision_value_fails_closed(self) -> None:
        garbage = "0f1e2d3c4b5a9876543210fedcba9876543210ab"
        probe = self.build_reviewed_project(verdict="PASS")
        sha = _git(probe, "rev-parse", "HEAD").stdout.strip()
        # A second locally resolvable commit for the valid+valid case.
        (probe / "README.md").write_text("# Project\nsecond commit\n", encoding="utf-8")
        _git(probe, "add", "-A")
        commit_all(probe, "unrelated second commit")
        other_sha = _git(probe, "rev-parse", "HEAD").stdout.strip()
        cases = (
            ("invalid-only", garbage),
            ("invalid-plus-valid", f"{garbage} {sha}"),
            ("valid-plus-invalid", f"{sha} {garbage}"),
            ("valid-a-plus-valid-b", f"{sha} {other_sha}"),
            ("same-valid-sha-twice", f"{sha} {sha}"),
        )
        for label, value in cases:
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS", revision_identity=value)
                result = self.route_project(project)
                self.assertNotEqual(result["projectStage"], "accepted", result)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-freshness-unknown", result)
                self.assertEqual(result["skill"], "", result)
                self.assertEqual(result["next"], "no-execution", result)

    # §20: duplicate canonical Source revision fields are ambiguous even when
    # the duplicated values are identical, in either field order.
    def test_duplicate_source_revision_fields_fail_closed(self) -> None:
        garbage = "0f1e2d3c4b5a9876543210fedcba9876543210ab"
        for label, first_kwargs, appended in (
            ("identical-duplicate", {}, None),
            ("valid-first-invalid-second", {}, f"- Source revision or identity: {garbage}"),
            ("invalid-first-valid-second", {"revision_identity": garbage}, None),
        ):
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS", **first_kwargs)
                if appended is None:
                    appended = (
                        "- Source revision or identity: "
                        + _git(project, "rev-parse", "HEAD").stdout.strip()
                    )
                append_durable_field(
                    project / ".project-review" / "charter.md", appended
                )
                result = self.route_project(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-freshness-unknown", result)
                self.assertEqual(result["skill"], "", result)
                self.assertEqual(result["next"], "no-execution", result)

    # §6/§20: duplicate canonical Source fields make review ownership
    # unresolvable even when one of them matches the current effort.
    def test_duplicate_source_fields_fail_closed(self) -> None:
        for label, base_kwargs, appended in (
            ("current-effort-first", {}, "- Source: `.scratch/other/spec.md`"),
            ("other-effort-first", {"charter_source": "`.scratch/other/spec.md`"},
             "- Source: `.scratch/current/spec.md`"),
            ("identical-duplicate", {}, "- Source: `.scratch/current/spec.md`"),
        ):
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS", **base_kwargs)
                append_durable_field(project / ".project-review" / "charter.md", appended)
                result = self.route_project(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-ownership-unknown", result)
                self.assertEqual(result["skill"], "", result)
                self.assertEqual(result["next"], "no-execution", result)
                self.assertNotEqual(result["projectStage"], "accepted")
                self.assertNotEqual(result["projectStage"], "implementation-complete")

    # §5/§20: a durable Charter without exactly one Profile never falls back
    # to the generic contract — the Profile selects the freshness contract.
    def test_missing_or_duplicate_profile_fails_closed(self) -> None:
        for label, mutate in (
            ("missing-profile", "remove"),
            ("duplicate-identical", "duplicate"),
        ):
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS")
                charter = project / ".project-review" / "charter.md"
                if mutate == "remove":
                    kept = [
                        line for line in charter.read_text(encoding="utf-8").splitlines()
                        if not line.startswith("- Profile: ")
                    ]
                    charter.write_text("\n".join(kept) + "\n", encoding="utf-8")
                else:
                    append_durable_field(charter, "- Profile: generic")
                result = self.route_project(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-freshness-unknown", result)
                self.assertEqual(result["skill"], "", result)
                self.assertEqual(result["next"], "no-execution", result)
                self.assertNotEqual(result["projectStage"], "accepted")

    # Canonical producer template layout stays consumable end-to-end.
    def test_canonical_charter_template_layout_reaches_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            sha = ensure_git_baseline(project)
            review_dir = project / ".project-review"
            review_dir.mkdir(parents=True)
            (review_dir / "charter.md").write_text(
                "# Acceptance Charter\n"
                "\n"
                "## Revision\n"
                "- Charter revision: 1\n"
                "- Supersedes: none\n"
                f"- Created at: 2026-08-27T00:00:00Z\n"
                "\n"
                "## Acceptance baseline\n"
                "- Source: `.scratch/current/spec.md`\n"
                f"- Source revision or identity: {sha}\n"
                "- Approval state: approved\n"
                "\n"
                "## Review Profile\n"
                "- Profile: generic\n"
                "\n"
                "## Original goal\n"
                "Prove the canonical producer layout is consumed faithfully.\n"
                "\n"
                "## User-visible outcome\n"
                "The router accepts only when the frozen baseline is intact.\n"
                "\n"
                "## Acceptance criteria\n"
                "- AC-1: baseline freshness verifiable from recorded revision\n"
                "\n"
                "## Approved exceptions\n"
                "- None\n",
                encoding="utf-8",
            )
            (review_dir / "state.md").write_text(
                "# Project-review State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n",
                encoding="utf-8",
            )
            (review_dir / "verdict.md").write_text(
                "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Round: round-01 (final)\nVerdict: **PASS**\n",
                encoding="utf-8",
            )
            result = self.route_project(project)
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted", result)


class SoftwareBaselineFreshnessTest(unittest.TestCase):
    """Software Profile baseline contract (producer owner:
    skills/project-review references/profiles/software.md).

    A software verdict binds to THREE frozen identities: Charter
    `- Fixed point:` (immutable code-review base, exactly one full SHA),
    Charter `- Implementation scope:` (the reviewed software target as
    repository-relative literal paths), and the verdict's
    `- Reviewed implementation revision:` (the final evaluated candidate).
    Freshness holds only while, inside that scope, the tree exactly matches
    the reviewed revision (tracked/committed/staged/unstaged drift and
    untracked additions alike); the base must delimit the final revision with
    non-empty in-scope change; malformed/missing identities are never
    salvaged; FAIL/BLOCKED bind equally; legacy d00b221-shaped records never
    accept.
    """

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-fixed-")
        host_root = Path(self.temp.name) / "host"
        host_root.mkdir()
        self.roots = install_host_fixture_skills(host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def route(self, project: Path) -> dict[str, object]:
        context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
        return ASK_LIGHT.route(self.roots, context, host="codex", mode="next")

    def garbage_sha(self) -> str:
        return "0f1e2d3c4b5a9876543210fedcba9876543210ab"

    def build_reviewed_software_project(
        self,
        *,
        verdict: str = "PASS",
        include_fixed_point: bool = True,
        fixed_point_override: str | None = None,
        include_scope: bool = True,
        scope_value: str = "src/",
        include_final_revision: bool = True,
        final_revision_override: str | None = None,
    ) -> tuple[Path, str, str]:
        """Base commit B (holds pre-existing src/common.py) -> implementation
        commit C1 (adds src/app.py), then a software record whose Source is the
        approved SPEC at B and whose three-field baseline names B/C1 by default."""
        self._count += 1
        project = Path(self.temp.name) / f"soft-{self._count}"
        write_project_state(project, initialized=True, spec=True)
        write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
        (project / "README.md").write_text("# Project\nv1\n", encoding="utf-8")
        src = project / "src"
        src.mkdir()
        # Pre-existing component member: deliberately untouched by the B..C
        # review diff so §11-style evasion attempts are exercised directly.
        (src / "common.py").write_text("VALUE_COMMON = 1\n", encoding="utf-8")
        base = ensure_git_baseline(project)
        (src / "app.py").write_text("print('implementation v1')\n", encoding="utf-8")
        _git(project, "add", "-A")
        commit_all(project, "implement feature v1")
        candidate = _git(project, "rev-parse", "HEAD").stdout.strip()
        if fixed_point_override == "LEGACY_TWO_VALUE":
            fixed_value: str | None = f"{base} {candidate}"  # exact d00b221 shape
        elif fixed_point_override is not None:
            fixed_value = fixed_point_override
        else:
            fixed_value = base
        write_project_review_state(
            project,
            reviewed_effort="current",
            verdict=verdict,
            revision_identity=base,
            profile="software",
            fixed_point=fixed_value if include_fixed_point else None,
            implementation_scope=scope_value if include_scope else None,
            final_revision=(final_revision_override if final_revision_override is not None else candidate)
            if include_final_revision else None,
        )
        return project, base, candidate

    # -- mutation helpers ---------------------------------------------------
    def modify(self, project: Path, relative: str, content: str, *, commit: bool = False) -> None:
        target = project / relative
        target.write_text(content, encoding="utf-8")
        if commit:
            _git(project, "add", "-A")
            commit_all(project, f"modify {relative}")

    def add_file(self, project: Path, relative: str, content: str, *, staged: bool = False, commit: bool = False) -> None:
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if staged or commit:
            _git(project, "add", "-A")
        if commit:
            commit_all(project, f"add {relative}")

    def delete(self, project: Path, relative: str, *, commit: bool = False) -> None:
        (project / relative).unlink()
        if commit:
            _git(project, "add", "-A")
            commit_all(project, f"delete {relative}")

    def replace_field(self, project: Path, field: str, value: str | None) -> None:
        charter = project / ".project-review" / "charter.md"
        prefix = f"- {field}: "
        kept = [line for line in charter.read_text(encoding="utf-8").splitlines() if not line.startswith(prefix)]
        if value is not None:
            kept.append(f"{prefix}{value}")
        charter.write_text("\n".join(kept) + "\n", encoding="utf-8")

    def assert_accepted(self, project: Path) -> dict[str, object]:
        result = self.route(project)
        self.assertEqual(result["status"], "RECOMMEND", result)
        self.assertEqual(result["projectStage"], "accepted", result)
        self.assertEqual(result["skill"], "", result)
        return result

    def assert_unknown(self, project: Path, fragment: str) -> dict[str, object]:
        result = self.route(project)
        self.assertNotEqual(result["projectStage"], "accepted", result)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "review-freshness-unknown", result)
        self.assertEqual(result["skill"], "", result)
        self.assertEqual(result["next"], "no-execution", result)
        combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
        self.assertIn(fragment, combined)
        return result

    def assert_stale(self, project: Path) -> dict[str, object]:
        result = self.route(project)
        self.assertEqual(result["projectStage"], "review-stale", result)
        self.assertEqual(result["skill"], "project-review", result)
        return result

    # -- §20 matrix ---------------------------------------------------------
    def test_valid_baseline_accepts(self) -> None:
        for scope in ("src/", "src/; README.md"):
            with self.subTest(scope=scope):
                project, _base, _candidate = self.build_reviewed_software_project(scope_value=scope)
                result = self.assert_accepted(project)
                self.assertIn("acceptance passed", result["completed"])

    def test_changed_path_drift_stales_the_review(self) -> None:
        for label, commit_change in (("dirty", False), ("committed", True)):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.modify(project, "src/app.py", "print('v2')\n", commit=commit_change)
                result = self.assert_stale(project)
                combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
                self.assertIn("src/app.py", combined)

    def test_preexisting_in_scope_file_outside_original_diff_stales(self) -> None:
        # §11 regression: src/common.py predates the review window and was not
        # touched by B..C, yet it belongs to the frozen component scope.
        for label, commit_change in (("dirty", False), ("committed", True)):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.modify(project, "src/common.py", "VALUE_COMMON = 2\n", commit=commit_change)
                result = self.assert_stale(project)
                combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
                self.assertIn("src/common.py", combined)

    def test_new_in_scope_file_after_pass_stales(self) -> None:
        for label, kwargs in (
            ("untracked", {}),
            ("staged", {"staged": True}),
            ("committed", {"commit": True}),
        ):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.add_file(project, "src/new_feature.py", "NEW = 1\n", **kwargs)
                result = self.assert_stale(project)
                combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
                self.assertIn("new_feature.py", combined)

    def test_in_scope_deletion_stales(self) -> None:
        for label, commit_deletion in (("dirty-deletion", False), ("committed-deletion", True)):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.delete(project, "src/app.py", commit=commit_deletion)
                self.assert_stale(project)

    def test_outside_scope_changes_keep_acceptance(self) -> None:
        for label, action in (
            ("dirty-readme", "dirty"),
            ("committed-readme", "committed"),
            ("untracked-note", "untracked"),
        ):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                if action == "untracked":
                    (project / "SIDE-NOTES.txt").write_text("note\n", encoding="utf-8")
                else:
                    readme = project / "README.md"
                    readme.write_text(readme.read_text(encoding="utf-8") + "\ndocs update\n", encoding="utf-8")
                    if action == "committed":
                        _git(project, "add", "-A")
                        commit_all(project, "docs-only change")
                self.assert_accepted(project)

    def test_exact_file_scope_isolates_siblings(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project(scope_value="src/app.py")
        self.modify(project, "src/app.py", "print('v2')\n")
        self.assert_stale(project)

        sibling_project, _base, _candidate = self.build_reviewed_software_project(scope_value="src/app.py")
        self.add_file(sibling_project, "src/sibling.py", "SIB = 1\n")
        self.assert_accepted(sibling_project)

    def test_whole_repo_scope_has_no_readme_exception(self) -> None:
        for label, commit_change in (("dirty", False), ("committed", True)):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project(scope_value=".")
                self.modify(project, "README.md", "# Project\nv2\n", commit=commit_change)
                self.assert_stale(project)

    def test_missing_implementation_scope_fails_closed(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project(include_scope=False)
        self.assert_unknown(project, "Implementation scope")

    def test_invalid_scope_entries_fail_closed_whole_field(self) -> None:
        cases = ("../outside", "/absolute/path", ":(glob)src/**", "src/*",
                 "src/app[1].py", "src/{a,b}", "src/; ../mixed-invalid")
        for scope in cases:
            with self.subTest(scope=scope):
                project, _base, _candidate = self.build_reviewed_software_project(scope_value=scope)
                result = self.assert_unknown(project, "Implementation scope")
                combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
                self.assertIn("fails closed", combined)

    def test_mixed_valid_invalid_scope_has_no_partial_salvage(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project(scope_value="src/; ../escape")
        result = self.assert_unknown(project, "../escape")
        self.assertIn("whole field fails closed" if False else "partially salvaging", str(result["gaps"]) + str(result["reason"]))

    def test_missing_final_revision_fails_closed(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project(include_final_revision=False)
        self.assert_unknown(project, "Reviewed implementation revision")

    def set_final_revision(self, project: Path, value: str) -> None:
        verdict = project / ".project-review" / "verdict.md"
        prefix = "- Reviewed implementation revision: "
        lines = [
            f"{prefix}{value}" if line.startswith(prefix) else line
            for line in verdict.read_text(encoding="utf-8").splitlines()
        ]
        verdict.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_invalid_final_revision_fails_closed(self) -> None:
        garbage = self.garbage_sha()
        values = {
            "short-sha": ("abc1234", "exactly one full 40-character"),
            "sha-plus-prose": ("<C1> final", "exactly one full 40-character"),
            "prose-plus-sha": ("reviewed <C1>", "exactly one full 40-character"),
            "two-resolvable-shas": ("<C1> <G>", "exactly one full 40-character"),
            "unresolvable-sha": ("<G>", "does not resolve to a local Git commit"),
        }
        for label, (raw_value, fragment) in values.items():
            with self.subTest(label=label):
                project, _base, candidate = self.build_reviewed_software_project()
                final_value = (raw_value
                               .replace("<C1>", candidate)
                               .replace("<G>", garbage))
                self.set_final_revision(project, final_value)
                self.assert_unknown(project, fragment)

    def test_strict_fixed_point_matrix(self) -> None:
        garbage = self.garbage_sha()
        for label, override, fragment in self.fixed_point_cases(garbage):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project(
                    include_fixed_point=override is not None,
                    fixed_point_override=override or "",
                )
                self.assert_unknown(project, fragment)

    def fixed_point_cases(self, garbage: str):
        """Build strict fixed-point cases from one live fixture's SHAs."""
        probe, base, candidate = self.build_reviewed_software_project()
        del probe
        return (
            ("missing", None, "no `- Fixed point:`"),
            ("short-sha-plus-prose", f"window {base[:12]}", "exactly one full 40-character"),
            ("sha-plus-prose", f"{base} review base", "exactly one full 40-character"),
            ("two-valid-shas-legacy-form", f"{base} {candidate}", "exactly one full 40-character"),
            ("invalid-plus-valid", f"{garbage} {base}", "exactly one full 40-character"),
            ("valid-plus-invalid", f"{base} {garbage}", "exactly one full 40-character"),
            ("same-sha-twice", f"{base} {base}", "exactly one full 40-character"),
            ("unresolvable-single-sha", garbage, "does not resolve to a local Git commit"),
        )

    def test_base_equals_final_revision_fails_closed(self) -> None:
        project, _base, candidate = self.build_reviewed_software_project()
        self.replace_field(project, "Fixed point", candidate)
        result = self.assert_unknown(project, "equals the reviewed implementation revision")
        combined = str(result["reason"]) + " ".join(str(gap) for gap in result["gaps"])
        self.assertIn("cannot delimit any reviewed implementation", combined)

    def test_non_ancestor_base_fails_closed(self) -> None:
        # A LATER commit cannot have delimited an EARLIER reviewed revision;
        # the consumer verifies the relationship instead of guessing a base.
        project, _base, _candidate = self.build_reviewed_software_project(scope_value=".")
        self.modify(project, "README.md", "# Project\nv2\n", commit=True)
        later = _git(project, "rev-parse", "HEAD").stdout.strip()
        self.replace_field(project, "Fixed point", later)
        self.assert_unknown(project, "does not delimit the reviewed implementation revision")

    def test_empty_in_scope_window_fails_closed(self) -> None:
        # Implementation changed only src/, but the frozen scope names docs/:
        # the review window holds no in-scope software change. Never broaden.
        project, _base, _candidate = self.build_reviewed_software_project(scope_value="docs/")
        self.assert_unknown(project, "no change inside")

    def test_fail_and_blocked_verdicts_stale_on_in_scope_drift(self) -> None:
        for verdict_name in ("FAIL", "BLOCKED"):
            with self.subTest(verdict=verdict_name):
                project, _base, _candidate = self.build_reviewed_software_project(verdict=verdict_name)
                self.modify(project, "src/app.py", "print('v2')\n", commit=True)
                result = self.assert_stale(project)
                self.assertNotEqual(result["projectStage"], "acceptance-not-passed")
                self.assertNotEqual(result["projectStage"], "accepted")

    def test_legacy_d00b221_record_never_accepts(self) -> None:
        # Exact old producer shape: two-value Fixed point, no Implementation
        # scope, no Reviewed implementation revision. Intentional break of an
        # unreleased unsafe record format; never silently migrated at read time.
        project, _base, _candidate = self.build_reviewed_software_project(
            include_scope=False,
            include_final_revision=False,
            fixed_point_override="LEGACY_TWO_VALUE",
        )
        self.assert_unknown(project, "Implementation scope")

    def test_review_repair_lifecycle_binds_to_evaluated_revision_c2(self) -> None:
        # §21 lifecycle: review C1 -> confirmed finding -> bounded in-scope
        # repair committed as C2 -> fresh evaluator accepts C2 -> the verdict
        # records C2 (Charter stays immutable). ask-light must compare freshness
        # against C2, never against the init-era C1.
        project, _base, c1 = self.build_reviewed_software_project()
        self.modify(project, "src/app.py", "print('implementation v2 - repaired')\n", commit=True)
        c2 = _git(project, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(c1, c2)
        self.set_final_revision(project, c2)
        result = self.assert_accepted(project)

        # Post-C2 in-scope drift stales the fresh verdict immediately...
        self.modify(project, "src/common.py", "VALUE_COMMON = 9\n")
        self.assert_stale(project)

    def test_out_of_scope_change_after_repair_keeps_acceptance(self) -> None:
        project, _base, _c1 = self.build_reviewed_software_project()
        self.modify(project, "src/app.py", "print('implementation v2 - repaired')\n", commit=True)
        c2 = _git(project, "rev-parse", "HEAD").stdout.strip()
        self.set_final_revision(project, c2)
        # Unrelated, out-of-scope change after the accepted repair stays unrelated.
        self.modify(project, "README.md", "# Project\nv99\n", commit=True)
        self.assert_accepted(project)

    def test_review_metadata_writes_do_not_self_stale(self) -> None:
        # §16 guard: committing the review record itself AFTER the evaluated
        # implementation must not stale the software verdict; review metadata is
        # not implementation unless the producer froze it inside the scope.
        project, _base, _candidate = self.build_reviewed_software_project()
        _git(project, "add", "-A")
        commit_all(project, "commit durable review records after evaluation")
        self.assert_accepted(project)

    # -- §20/§21 singleton durable-field cardinality --------------------------
    # Normal producer fixtures never emit duplicate canonical fields, so these
    # tests tamper otherwise-valid accepted records and call the real route().

    def set_charter_field_lines(self, project: Path, field: str, lines: list[str]) -> None:
        """Replace the canonical `- {field}:` line with exactly `lines`."""
        charter = project / ".project-review" / "charter.md"
        prefix = f"- {field}: "
        out: list[str] = []
        for line in charter.read_text(encoding="utf-8").splitlines():
            if line.startswith(prefix):
                out.extend(lines)
            else:
                out.append(line)
        charter.write_text("\n".join(out) + "\n", encoding="utf-8")

    def set_verdict_field_lines(self, project: Path, field: str, lines: list[str]) -> None:
        verdict = project / ".project-review" / "verdict.md"
        prefix = f"- {field}: "
        out: list[str] = []
        for line in verdict.read_text(encoding="utf-8").splitlines():
            if line.startswith(prefix):
                out.extend(lines)
            else:
                out.append(line)
        verdict.write_text("\n".join(out) + "\n", encoding="utf-8")

    def test_duplicate_profile_fails_closed(self) -> None:
        for label, lines in (
            ("identical-software", ["- Profile: software", "- Profile: software"]),
            ("generic-first-software-second", ["- Profile: generic", "- Profile: software"]),
            ("software-first-generic-second", ["- Profile: software", "- Profile: generic"]),
        ):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.assert_accepted(project)
                self.set_charter_field_lines(project, "Profile", lines)
                self.assert_unknown(project, "Profile")

    def test_missing_profile_with_in_scope_drift_is_never_accepted(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project()
        self.assert_accepted(project)
        self.set_charter_field_lines(project, "Profile", [])
        self.modify(project, "src/app.py", "print('v2')\n", commit=True)
        # Missing Profile must not silently skip software freshness: fail
        # closed (review-freshness-unknown), never accepted.
        self.assert_unknown(project, "Profile")

    def test_duplicate_fixed_point_fails_closed_both_orders(self) -> None:
        garbage = self.garbage_sha()
        for label, first_valid in (
            ("valid-first-invalid-second", True),
            ("invalid-first-valid-second", False),
            ("identical", True),
        ):
            with self.subTest(label=label):
                project, base, _candidate = self.build_reviewed_software_project()
                self.assert_accepted(project)
                if label == "identical":
                    lines = [f"- Fixed point: {base}", f"- Fixed point: {base}"]
                elif first_valid:
                    lines = [f"- Fixed point: {base}", f"- Fixed point: {garbage}"]
                else:
                    lines = [f"- Fixed point: {garbage}", f"- Fixed point: {base}"]
                self.set_charter_field_lines(project, "Fixed point", lines)
                self.assert_unknown(project, "Fixed point")

    def test_duplicate_implementation_scope_fails_closed_both_orders(self) -> None:
        for label, lines in (
            ("identical", ["- Implementation scope: src/", "- Implementation scope: src/"]),
            ("valid-first", ["- Implementation scope: src/", "- Implementation scope: docs/"]),
            ("invalid-grammar-first", ["- Implementation scope: ../outside", "- Implementation scope: src/"]),
        ):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.assert_accepted(project)
                self.set_charter_field_lines(project, "Implementation scope", lines)
                self.assert_unknown(project, "Implementation scope")

    def test_duplicate_final_revision_fails_closed_both_orders(self) -> None:
        garbage = self.garbage_sha()
        for label, second_invalid in (
            ("identical", False),
            ("valid-first-invalid-second", True),
            ("invalid-first-valid-second", True),
        ):
            with self.subTest(label=label):
                project, _base, candidate = self.build_reviewed_software_project()
                self.assert_accepted(project)
                if label == "identical":
                    lines = [
                        f"- Reviewed implementation revision: {candidate}",
                        f"- Reviewed implementation revision: {candidate}",
                    ]
                elif label == "valid-first-invalid-second":
                    lines = [
                        f"- Reviewed implementation revision: {candidate}",
                        f"- Reviewed implementation revision: {garbage}",
                    ]
                else:
                    lines = [
                        f"- Reviewed implementation revision: {garbage}",
                        f"- Reviewed implementation revision: {candidate}",
                    ]
                self.set_verdict_field_lines(
                    project, "Reviewed implementation revision", lines
                )
                self.assert_unknown(project, "Reviewed implementation revision")

    # -- §20 ignored-file completeness inside the frozen scope ----------------

    def test_ignored_in_scope_new_file_stales(self) -> None:
        for label, mechanism in (("gitignore", "gitignore"), ("info-exclude", "info-exclude")):
            with self.subTest(label=label):
                project, _base, _candidate = self.build_reviewed_software_project()
                self.assert_accepted(project)
                add_ignore_rule(project, "new_hidden.py", mechanism=mechanism)
                self.add_file(project, "src/new_hidden.py", "HIDDEN = 1\n")
                result = self.assert_stale(project)
                combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
                self.assertIn("new_hidden.py", combined)

    def test_nested_ignored_in_scope_file_stales(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project()
        self.assert_accepted(project)
        add_ignore_rule(project, "generated/")
        self.add_file(project, "src/generated/new.py", "GENERATED = 1\n")
        result = self.assert_stale(project)
        combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
        self.assertIn("generated/new.py", combined)

    def test_out_of_scope_ignored_files_keep_acceptance(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project()
        self.assert_accepted(project)
        add_ignore_rule(project, "*.tmp")
        add_ignore_rule(project, "generated.md", mechanism="info-exclude")
        (project / "build.tmp").write_text("cache\n", encoding="utf-8")
        (project / "docs" / "generated.md").write_text("generated\n", encoding="utf-8")
        self.assert_accepted(project)

    def test_exact_file_scope_ignores_ignored_sibling(self) -> None:
        project, _base, _candidate = self.build_reviewed_software_project(scope_value="src/app.py")
        self.assert_accepted(project)
        add_ignore_rule(project, "sibling.py")
        self.add_file(project, "src/sibling.py", "SIB = 1\n")
        self.assert_accepted(project)

    def test_whole_repo_scope_counts_ignored_files(self) -> None:
        # With scope "." the durable records are in-scope files, so a verdict
        # recording its own commit is impossible (hash fixed point; §16
        # born-stale guidance). The ignored-file behavior is therefore checked
        # through the real classifier on a real repo whose tree is clean at
        # the recorded revision, with the verdict passed as produced text.
        project, base, candidate = self.build_reviewed_software_project(scope_value=".")
        _git(project, "add", "-A")
        commit_all(project, "commit durable review records after evaluation")
        records_commit = _git(project, "rev-parse", "HEAD").stdout.strip()
        charter = (project / ".project-review" / "charter.md").read_text(encoding="utf-8")
        verdict = (project / ".project-review" / "verdict.md").read_text(encoding="utf-8")
        verdict = verdict.replace(
            f"- Reviewed implementation revision: {candidate}",
            f"- Reviewed implementation revision: {records_commit}",
        )
        state = ASK_LIGHT._classify_software_implementation_freshness(
            project, charter, verdict
        )
        self.assertEqual(state, ("current", []), state)
        add_ignore_rule(project, "cache.data", mechanism="info-exclude")
        (project / "cache.data").write_text("junk\n", encoding="utf-8")
        state = ASK_LIGHT._classify_software_implementation_freshness(
            project, charter, verdict
        )
        self.assertEqual(state[0], "stale", state)
        self.assertIn("cache.data", state[1][0])

        # Reviewer-B adversarial case: a whitespace-only filename is a real
        # scope entry and must not be dropped by blank-line filtering.
        whitespace_file = project / " "
        whitespace_file.write_text("space named\n", encoding="utf-8")
        state = ASK_LIGHT._classify_software_implementation_freshness(
            project, charter, verdict
        )
        self.assertEqual(state[0], "stale", state)
        self.assertIn(" ", state[1][0])
        whitespace_file.unlink()
        state = ASK_LIGHT._classify_software_implementation_freshness(
            project, charter, verdict
        )
        self.assertEqual(state[0], "stale", state)  # cache.data still drifts


class DirectorySourceBaselineTest(unittest.TestCase):
    """§14: when the Charter cites a directory source, that whole directory is
    the reviewed baseline — including files appearing inside it untracked."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-dir-")
        host_root = Path(self.temp.name) / "host"
        host_root.mkdir()
        self.roots = install_host_fixture_skills(host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def route(self, project: Path) -> dict[str, object]:
        context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
        return ASK_LIGHT.route(self.roots, context, host="codex", mode="next")

    def build_directory_source_project(self) -> Path:
        self._count += 1
        project = Path(self.temp.name) / f"dir-{self._count}"
        write_project_state(project, initialized=True, spec=True)
        write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
        (project / ".scratch" / "current" / "map.md").write_text("# Map\n", encoding="utf-8")
        baseline = ensure_git_baseline(project)
        write_project_review_state(
            project,
            charter_source="`.scratch/current`",
            verdict="PASS",
            revision_identity=baseline,
        )
        return project

    # H: tracked child modification invalidates the directory baseline.
    def test_tracked_child_modification_stales_the_review(self) -> None:
        project = self.build_directory_source_project()
        map_file = project / ".scratch" / "current" / "map.md"
        map_file.write_text("# Map changed after review\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["projectStage"], "review-stale", result)
        self.assertEqual(result["skill"], "project-review")

    # I: tracked child deletion invalidates the directory baseline too.
    def test_tracked_child_deletion_stales_the_review(self) -> None:
        for label, commit_deletion in (("dirty-deletion", False), ("committed-deletion", True)):
            with self.subTest(label=label):
                project = self.build_directory_source_project()
                (project / ".scratch" / "current" / "map.md").unlink()
                if commit_deletion:
                    _git(project, "add", "-A")
                    commit_all(project, "remove reviewed map")
                result = self.route(project)
                self.assertEqual(result["projectStage"], "review-stale", result)

    # J: a brand-new untracked child changes the reviewed directory baseline.
    def test_new_untracked_child_stales_the_review(self) -> None:
        project = self.build_directory_source_project()
        (project / ".scratch" / "current" / "new-baseline-file.md").write_text(
            "brand-new content inside the reviewed directory\n", encoding="utf-8"
        )
        result = self.route(project)
        self.assertEqual(result["status"], "RECOMMEND", result)
        self.assertEqual(result["projectStage"], "review-stale", result)
        self.assertEqual(result["skill"], "project-review")
        combined = str(result["reason"]) + " ".join(str(gap) for gap in result["gaps"])
        self.assertIn(".scratch/current", combined)

    # K: untracked noise OUTSIDE the reviewed directory is unrelated.
    def test_untracked_outside_directory_keeps_the_review_current(self) -> None:
        project = self.build_directory_source_project()
        (project / ".scratch" / "elsewhere.txt").write_text("outside the baseline\n", encoding="utf-8")
        (project / "loose.txt").write_text("also outside\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["status"], "RECOMMEND", result)
        self.assertEqual(result["projectStage"], "accepted", result)

    # L: a FILE source ignores untracked siblings in the same directory.
    def test_file_only_source_ignores_untracked_sibling(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-file-src-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="PASS")
            (project / ".scratch" / "current" / "random-note.md").write_text(
                "sibling noise\n", encoding="utf-8"
            )
            result = self.route(project)
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted", result)

    # §14/§20: ignored children of a directory Source are still baseline
    # members — Git ignore rules hide them from status, not from freshness.
    def test_ignored_child_stales_the_directory_baseline(self) -> None:
        for label, mechanism in (("gitignore", "gitignore"), ("info-exclude", "info-exclude")):
            with self.subTest(label=label):
                project = self.build_directory_source_project()
                add_ignore_rule(project, "hidden.md", mechanism=mechanism)
                (project / ".scratch" / "current" / "hidden.md").write_text(
                    "hidden child\n", encoding="utf-8"
                )
                result = self.route(project)
                self.assertEqual(result["projectStage"], "review-stale", result)
                combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
                self.assertIn("hidden.md", combined)

    def test_nested_ignored_child_stales_the_directory_baseline(self) -> None:
        project = self.build_directory_source_project()
        add_ignore_rule(project, "generated/")
        nested = project / ".scratch" / "current" / "generated" / "nested.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("nested ignored child\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["projectStage"], "review-stale", result)
        combined = str(result["reason"]) + " " + " ".join(str(gap) for gap in result["gaps"])
        self.assertIn("generated/nested.md", combined)

    # §17: the ignored-file fix must not widen the baseline — an ignored file
    # outside the cited directory stays unrelated.
    def test_ignored_file_outside_directory_keeps_review_current(self) -> None:
        project = self.build_directory_source_project()
        add_ignore_rule(project, "*.tmp")
        (project / "loose.tmp").write_text("outside the baseline\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["status"], "RECOMMEND", result)
        self.assertEqual(result["projectStage"], "accepted", result)

    # §15: exact-file Sources keep file-only semantics even for ignored siblings.
    def test_file_only_source_ignores_ignored_sibling(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ask-light-file-ign-") as tmp:
            project = Path(tmp) / "project"
            write_project_state(project, initialized=True, spec=True)
            write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
            write_project_review_state(project, reviewed_effort="current", verdict="PASS")
            add_ignore_rule(project, "random-note.md")
            (project / ".scratch" / "current" / "random-note.md").write_text(
                "ignored sibling noise\n", encoding="utf-8"
            )
            result = self.route(project)
            self.assertEqual(result["status"], "RECOMMEND", result)
            self.assertEqual(result["projectStage"], "accepted", result)


class ReviewTransactionCoherenceTest(unittest.TestCase):
    """Review durable transaction coherence tests (charter.md + state.md + verdict.md)."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-tx-")
        host_root = Path(self.temp.name) / "host"
        host_root.mkdir()
        self.roots = install_host_fixture_skills(host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def route(self, project_root: Path) -> dict[str, Any]:
        context = {
            "projectRoot": str(project_root),
            "invocationControl": "explicit-only",
            "availability": "codex",
        }
        return ASK_LIGHT.route(self.roots, context, host="codex", mode="next")

    def build_project(
        self,
        *,
        profile: str = "generic",
        charter_rev: str = "1",
        state_rev: str = "1",
        status: str = "PASS",
        verdict: str | None = "PASS",
        verdict_rev: str | None = "1",
        verdict_profile: str | None = None,
        scope: str = "src/app.py",
    ) -> tuple[Path, str, str]:
        self._count += 1
        root = Path(self.temp.name) / f"tx-proj-{self._count}"
        write_project_state(root, initialized=True, spec=True)
        write_effort_state(root, "current", spec_status="active", ticket_statuses=["resolved"])
        src = root / "src"
        src.mkdir(parents=True, exist_ok=True)
        (src / "app.py").write_text("print(1)\n", encoding="utf-8")
        base_sha = ensure_git_baseline(root)

        (src / "app.py").write_text("print(2)\n", encoding="utf-8")
        _git(root, "add", "-A")
        commit_all(root, "candidate commit")
        cand_sha = _git(root, "rev-parse", "HEAD").stdout.strip()

        rdir = root / ".project-review"
        rdir.mkdir(parents=True, exist_ok=True)
        (rdir / "charter.md").write_text(
            "# Acceptance Charter\n\n"
            "## Revision\n"
            f"- Charter revision: {charter_rev}\n"
            "- Supersedes: none\n\n"
            "## Acceptance baseline\n"
            "- Source: approved effort SPEC — `.scratch/current/spec.md`\n"
            f"- Source revision or identity: commit {base_sha}\n"
            + (f"- Fixed point: {base_sha}\n- Implementation scope: {scope}\n" if profile == "software" else "")
            + "- Approval state: approved\n\n"
            "## Review Profile\n"
            f"- Profile: {profile}\n",
            encoding="utf-8",
        )
        (rdir / "state.md").write_text(
            "# Project-review State\n"
            f"- Status: {status}\n"
            f"- Charter revision: {state_rev}\n"
            f"- Profile: {profile}\n"
            "- Round: 1\n",
            encoding="utf-8",
        )
        if verdict is not None:
            v_profile = verdict_profile or profile
            (rdir / "verdict.md").write_text(
                "# Verdict\n\n"
                f"- Charter revision: {verdict_rev or charter_rev}\n"
                f"- Profile: {v_profile}\n"
                f"- Verdict: **{verdict}**\n"
                + (f"- Reviewed implementation revision: {cand_sha}\n" if profile == "software" else "")
                + "- Round: round-01 (final)\n\n"
                "## Conclusion\nBaseline accepted.\n",
                encoding="utf-8",
            )
        return root, base_sha, cand_sha

    def test_coherent_pass_software_and_generic_accepted(self) -> None:
        for profile in ("generic", "software"):
            with self.subTest(profile=profile):
                project, _b, _c = self.build_project(profile=profile, status="PASS", verdict="PASS")
                result = self.route(project)
                self.assertEqual(result["status"], "RECOMMEND", result)
                self.assertEqual(result["projectStage"], "accepted", result)

    def test_active_review_states_override_old_pass_verdict(self) -> None:
        for active_status in ("INIT", "READY", "CRITIC", "REPAIR", "EVALUATE"):
            with self.subTest(status=active_status):
                project, _b, _c = self.build_project(status=active_status, verdict="PASS")
                result = self.route(project)
                self.assertEqual(result["status"], "RECOMMEND", result)
                self.assertEqual(result["projectStage"], "project-review", result)
                self.assertEqual(result["skill"], "project-review", result)
                self.assertNotEqual(result["projectStage"], "accepted")

    def test_missing_state_file_fails_closed(self) -> None:
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        (project / ".project-review" / "state.md").unlink()
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_empty_or_whitespace_state_file_fails_closed(self) -> None:
        for empty_val in ("", "   \n\n  \t  "):
            with self.subTest(empty_val=repr(empty_val)):
                project, _b, _c = self.build_project(status="PASS", verdict="PASS")
                (project / ".project-review" / "state.md").write_text(empty_val, encoding="utf-8")
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_missing_canonical_state_fields_fail_closed(self) -> None:
        fields = ("Status", "Charter revision", "Profile", "Round")
        for field in fields:
            with self.subTest(field=field):
                project, _b, _c = self.build_project(status="PASS", verdict="PASS")
                state_file = project / ".project-review" / "state.md"
                lines = [line for line in state_file.read_text(encoding="utf-8").splitlines() if not line.startswith(f"- {field}:")]
                state_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_duplicate_canonical_state_fields_fail_closed(self) -> None:
        cases = [
            ("duplicate-status-identical", "- Status: PASS"),
            ("duplicate-status-conflicting", "- Status: READY"),
            ("duplicate-rev-identical", "- Charter revision: 1"),
            ("duplicate-rev-conflicting", "- Charter revision: 2"),
            ("duplicate-profile-identical", "- Profile: generic"),
            ("duplicate-profile-conflicting", "- Profile: software"),
            ("duplicate-round-identical", "- Round: 1"),
            ("duplicate-round-conflicting", "- Round: 2"),
        ]
        for label, extra_line in cases:
            with self.subTest(label=label):
                project, _b, _c = self.build_project(status="PASS", verdict="PASS")
                state_file = project / ".project-review" / "state.md"
                append_durable_field(state_file, extra_line)
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_state_round_malformed_fails_closed(self) -> None:
        malformed_rounds = ("invalid", "round-xyz", "2 of 3", "", "1 2")
        for bad_round in malformed_rounds:
            with self.subTest(bad_round=bad_round):
                project, _b, _c = self.build_project(status="PASS", verdict="PASS")
                state_file = project / ".project-review" / "state.md"
                lines = [
                    line if not line.startswith("- Round:") else f"- Round: {bad_round}"
                    for line in state_file.read_text(encoding="utf-8").splitlines()
                ]
                state_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_verdict_round_missing_or_duplicate_or_malformed_fails_closed(self) -> None:
        # 1. Missing Round in verdict.md
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        lines = [line for line in verdict_file.read_text(encoding="utf-8").splitlines() if not line.startswith("- Round:")]
        verdict_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # 2. Duplicate identical Round in verdict.md
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        append_durable_field(verdict_file, "- Round: round-01 (final)")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # 3. Duplicate conflicting Round in verdict.md
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        append_durable_field(verdict_file, "- Round: round-02 (final)")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # 4. Malformed Round in verdict.md
        for bad_round in ("invalid", "1 of 2", ""):
            with self.subTest(bad_round=bad_round):
                project, _b, _c = self.build_project(status="PASS", verdict="PASS")
                verdict_file = project / ".project-review" / "verdict.md"
                lines = [
                    line if not line.startswith("- Round:") else f"- Round: {bad_round}"
                    for line in verdict_file.read_text(encoding="utf-8").splitlines()
                ]
                verdict_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "acceptance-unknown", result)

    def test_round_mismatch_fails_closed(self) -> None:
        cases = [
            ("PASS", "PASS"),
            ("FAIL", "FAIL"),
            ("BLOCKED", "BLOCKED"),
        ]
        for s_status, v_verdict in cases:
            with self.subTest(state=s_status, verdict=v_verdict):
                project, _b, _c = self.build_project(status=s_status, verdict=v_verdict)
                # State round 2, Verdict round 1
                state_file = project / ".project-review" / "state.md"
                state_file.write_text(
                    f"# State\n- Status: {s_status}\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
                    encoding="utf-8",
                )
                verdict_file = project / ".project-review" / "verdict.md"
                verdict_file.write_text(
                    f"# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **{v_verdict}**\n- Round: round-01 (final)\n",
                    encoding="utf-8",
                )
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "acceptance-unknown", result)

    def test_verdict_charter_revision_missing_duplicate_mismatch_fails_closed(self) -> None:
        # Missing Charter revision on verdict
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        lines = [line for line in verdict_file.read_text(encoding="utf-8").splitlines() if not line.startswith("- Charter revision:")]
        verdict_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Duplicate identical Charter revision on verdict
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        append_durable_field(verdict_file, "- Charter revision: 1")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Duplicate conflicting Charter revision on verdict
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        append_durable_field(verdict_file, "- Charter revision: 2")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Charter revision mismatch: Charter/State rev 2, Verdict rev 1
        project, _b, _c = self.build_project(charter_rev="2", state_rev="2", status="PASS", verdict="PASS", verdict_rev="1")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

    def test_verdict_profile_missing_duplicate_mismatch_fails_closed(self) -> None:
        # Missing Profile on verdict
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        lines = [line for line in verdict_file.read_text(encoding="utf-8").splitlines() if not line.startswith("- Profile:")]
        verdict_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Duplicate identical Profile on verdict
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        append_durable_field(verdict_file, "- Profile: generic")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Duplicate conflicting Profile on verdict
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        verdict_file = project / ".project-review" / "verdict.md"
        append_durable_field(verdict_file, "- Profile: software")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Profile mismatch: Charter/State software, Verdict generic
        project, _b, _c = self.build_project(profile="software", status="PASS", verdict="PASS", verdict_profile="generic")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

        # Profile mismatch: Charter/State generic, Verdict software
        project, _b, _c = self.build_project(profile="generic", status="PASS", verdict="PASS", verdict_profile="software")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "acceptance-unknown", result)

    def test_terminal_verdict_semantic_uniqueness(self) -> None:
        # Valid singleton conclusions
        for status, verdict, exp_status, exp_stage in (
            ("PASS", "PASS", "RECOMMEND", "accepted"),
            ("FAIL", "FAIL", "NEED-INPUT", "acceptance-not-passed"),
            ("BLOCKED", "BLOCKED", "NEED-INPUT", "acceptance-not-passed"),
        ):
            with self.subTest(status=status, verdict=verdict):
                project, _b, _c = self.build_project(status=status, verdict=verdict)
                result = self.route(project)
                self.assertEqual(result["status"], exp_status, result)
                self.assertEqual(result["projectStage"], exp_stage, result)

        # Conflicting multi-verdict combinations all fail closed as acceptance-unknown
        conflict_verdict_lines = [
            ("PASS + FAIL", "- Verdict: PASS\n- Verdict: FAIL\n"),
            ("PASS + BLOCKED", "- Verdict: PASS\n- Verdict: BLOCKED\n"),
            ("FAIL + BLOCKED", "- Verdict: FAIL\n- Verdict: BLOCKED\n"),
            ("PASS + FAIL + BLOCKED", "- Verdict: PASS\n- Verdict: FAIL\n- Verdict: BLOCKED\n"),
        ]
        for label, lines in conflict_verdict_lines:
            for s_status in ("PASS", "FAIL", "BLOCKED"):
                with self.subTest(label=label, state_status=s_status):
                    project, _b, _c = self.build_project(status=s_status, verdict="PASS")
                    verdict_file = project / ".project-review" / "verdict.md"
                    verdict_file.write_text(
                        f"# Verdict\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n{lines}",
                        encoding="utf-8",
                    )
                    result = self.route(project)
                    self.assertEqual(result["status"], "NEED-INPUT", result)
                    self.assertEqual(result["projectStage"], "acceptance-unknown", result)

    def test_unknown_and_non_canonical_status_fail_closed(self) -> None:
        unknown_statuses = ("UNKNOWN", "NOT-PASS", "PASSING", "READY FOR PASS", "COMPLETE", "DONE")
        for bad_status in unknown_statuses:
            with self.subTest(status=bad_status):
                project, _b, _c = self.build_project(status=bad_status, verdict="PASS")
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_terminal_state_and_verdict_agreement(self) -> None:
        cases = [
            ("PASS", "PASS", "RECOMMEND", "accepted"),
            ("FAIL", "FAIL", "NEED-INPUT", "acceptance-not-passed"),
            ("BLOCKED", "BLOCKED", "NEED-INPUT", "acceptance-not-passed"),
        ]
        for s_status, v_verdict, exp_status, exp_stage in cases:
            with self.subTest(state=s_status, verdict=v_verdict):
                project, _b, _c = self.build_project(status=s_status, verdict=v_verdict)
                result = self.route(project)
                self.assertEqual(result["status"], exp_status, result)
                self.assertEqual(result["projectStage"], exp_stage, result)

    def test_terminal_state_and_verdict_conflicts_fail_closed(self) -> None:
        conflicts = [
            ("PASS", "FAIL"),
            ("PASS", "BLOCKED"),
            ("FAIL", "PASS"),
            ("FAIL", "BLOCKED"),
            ("BLOCKED", "PASS"),
            ("BLOCKED", "FAIL"),
        ]
        for s_status, v_verdict in conflicts:
            with self.subTest(state=s_status, verdict=v_verdict):
                project, _b, _c = self.build_project(status=s_status, verdict=v_verdict)
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "acceptance-unknown", result)

    def test_missing_or_empty_verdict_for_terminal_state_fails_closed(self) -> None:
        for s_status in ("PASS", "FAIL", "BLOCKED"):
            with self.subTest(status=s_status):
                project, _b, _c = self.build_project(status=s_status, verdict=None)
                result = self.route(project)
                self.assertEqual(result["status"], "NEED-INPUT", result)
                self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_charter_revision_mismatch_fails_closed(self) -> None:
        # Charter revision 2, State revision 1, Verdict PASS -> not accepted
        project, _b, _c = self.build_project(charter_rev="2", state_rev="1", status="PASS", verdict="PASS")
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_profile_mismatch_fails_closed(self) -> None:
        project, _b, _c = self.build_project(profile="software", status="PASS", verdict="PASS")
        # Change state profile to generic
        state_file = project / ".project-review" / "state.md"
        state_file.write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["status"], "NEED-INPUT", result)
        self.assertEqual(result["projectStage"], "review-state-unknown", result)

    def test_reopen_lifecycle_full_sequence(self) -> None:
        # 1. Start with PASS + PASS -> accepted
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        result = self.route(project)
        self.assertEqual(result["projectStage"], "accepted")

        # 2. Reopen review: State becomes READY (keeping old PASS verdict) -> project-review
        state_file = project / ".project-review" / "state.md"
        state_file.write_text(
            "# State\n- Status: READY\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "project-review")
        self.assertEqual(result["skill"], "project-review")

        # 3. Advance to CRITIC -> project-review
        state_file.write_text(
            "# State\n- Status: CRITIC\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "project-review")

        # 4. Advance to REPAIR -> project-review
        state_file.write_text(
            "# State\n- Status: REPAIR\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "project-review")

        # 5. Advance to EVALUATE -> project-review
        state_file.write_text(
            "# State\n- Status: EVALUATE\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "project-review")

        # 6. Simulate transition to terminal State before new Verdict is available:
        state_file.write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        # Old round-1 verdict remains -> fails closed as acceptance-unknown
        result = self.route(project)
        self.assertEqual(result["projectStage"], "acceptance-unknown")

        # 7. Fresh evaluation completes: State PASS + fresh Verdict PASS -> accepted
        verdict_file = project / ".project-review" / "verdict.md"
        verdict_file.write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-02 (final)\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "accepted")

    def test_charter_revision_update_lifecycle(self) -> None:
        # 1. rev1 PASS -> accepted
        project, _b, _c = self.build_project(charter_rev="1", state_rev="1", status="PASS", verdict="PASS")
        self.assertEqual(self.route(project)["projectStage"], "accepted")

        # 2. Charter updated to rev 2 (state still rev 1) -> not accepted (review-state-unknown)
        charter = project / ".project-review" / "charter.md"
        lines = [line if not line.startswith("- Charter revision:") else "- Charter revision: 2" for line in charter.read_text(encoding="utf-8").splitlines()]
        charter.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertEqual(self.route(project)["projectStage"], "review-state-unknown")

        # 3. New review starts: State READY / rev 2 -> project-review
        state_file = project / ".project-review" / "state.md"
        state_file.write_text(
            "# State\n- Status: READY\n- Charter revision: 2\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "project-review")
        self.assertEqual(result["skill"], "project-review")

        # 4. Review completes: State PASS rev 2 + new Verdict PASS rev 2 -> accepted
        state_file.write_text(
            "# State\n- Status: PASS\n- Charter revision: 2\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        verdict_file = project / ".project-review" / "verdict.md"
        verdict_file.write_text(
            "# Verdict\n- Charter revision: 2\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n",
            encoding="utf-8",
        )
        self.assertEqual(self.route(project)["projectStage"], "accepted")

    def test_c1_repair_c2_with_reopen_lifecycle(self) -> None:
        project, base_sha, c1_sha = self.build_project(profile="software", status="READY", verdict="PASS")

        # Repair to C2
        (project / "src" / "app.py").write_text("print('repair C2')\n", encoding="utf-8")
        _git(project, "add", "src/app.py")
        commit_all(project, "commit C2")
        c2_sha = _git(project, "rev-parse", "HEAD").stdout.strip()

        # Fresh evaluation completes for C2
        (project / ".project-review" / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 2\n",
            encoding="utf-8",
        )
        (project / ".project-review" / "verdict.md").write_text(
            f"# Verdict\n- Charter revision: 1\n- Profile: software\n- Verdict: **PASS**\n"
            f"- Reviewed implementation revision: {c2_sha}\n- Round: round-02 (final)\n",
            encoding="utf-8",
        )
        self.assertEqual(self.route(project)["projectStage"], "accepted")

        # Reopen review for another pass
        (project / ".project-review" / "state.md").write_text(
            "# State\n- Status: READY\n- Charter revision: 1\n- Profile: software\n- Round: 3\n",
            encoding="utf-8",
        )
        result = self.route(project)
        self.assertEqual(result["projectStage"], "project-review")
        self.assertNotEqual(result["projectStage"], "accepted")

        # Fresh PASS completes round 3
        (project / ".project-review" / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 3\n",
            encoding="utf-8",
        )
        # Before fresh round-3 verdict is written, old round-2 verdict fails closed as acceptance-unknown
        self.assertEqual(self.route(project)["projectStage"], "acceptance-unknown")

        (project / ".project-review" / "verdict.md").write_text(
            f"# Verdict\n- Charter revision: 1\n- Profile: software\n- Verdict: **PASS**\n"
            f"- Reviewed implementation revision: {c2_sha}\n- Round: round-03 (final)\n",
            encoding="utf-8",
        )
        self.assertEqual(self.route(project)["projectStage"], "accepted")




if __name__ == "__main__":
    unittest.main(verbosity=2)
