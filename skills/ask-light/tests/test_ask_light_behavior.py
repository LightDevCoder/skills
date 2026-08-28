from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

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
    text = path.read_text(encoding="utf-8").rstrip("\n")
    path.write_text(f"{text}\n{line}\n", encoding="utf-8")


def add_ignore_rule(root: Path, pattern: str, *, mechanism: str = "gitignore") -> None:
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


# ---------------------------------------------------------------------------
# Category A Tests: Deterministic Evidence Tests (SPEC §37-A)
# ---------------------------------------------------------------------------

class DeterministicEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-ev-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_uninitialized_project_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            proj.mkdir()
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertFalse(ev["initialized"])
            self.assertEqual(ev["stage"], "uninitialized")
            self.assertEqual(len(ev["hardConstraints"]), 1)
            self.assertEqual(ev["hardConstraints"][0]["type"], "uninitialized-project")
            self.assertEqual(ev["hardConstraints"][0]["ownerSkill"], "project-init")

    def test_current_effort_resolution_and_active_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            write_effort_state(proj, "feature-a", spec_status="active")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertTrue(ev["initialized"])
            self.assertEqual(ev["currentEffort"]["name"], "feature-a")
            self.assertEqual(ev["currentEffort"]["resolution"], "current")
            self.assertTrue(ev["spec"]["active"])

    def test_ticket_frontier_classification_all_buckets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            issues = proj / ".scratch" / "effort" / "issues"
            issues.mkdir(parents=True, exist_ok=True)
            (issues / "01-ready.md").write_text("- Status: ready-for-agent\n- Blocked by: None\n", encoding="utf-8")
            (issues / "02-blocked.md").write_text("- Status: open\n- Blocked by: 01\n", encoding="utf-8")
            (issues / "03-claimed.md").write_text("- Status: claimed\n- Blocked by: None\n", encoding="utf-8")
            (issues / "04-resolved.md").write_text("- Status: resolved\n", encoding="utf-8")
            (issues / "05-unknown.md").write_text("- Status: bogus-status\n", encoding="utf-8")

            ev = ASK_LIGHT.inspect_project_evidence(proj)
            tickets = ev["tickets"]
            self.assertTrue(tickets["exists"])
            self.assertTrue(tickets["frontierReady"])
            self.assertFalse(tickets["allResolved"])
            self.assertEqual(len(tickets["ready"]), 1)
            self.assertEqual(len(tickets["blocked"]), 1)
            self.assertEqual(len(tickets["claimed"]), 1)
            self.assertEqual(len(tickets["resolved"]), 1)
            self.assertEqual(len(tickets["unknown"]), 1)
            self.assertIn(".scratch/effort/issues/01-ready.md", tickets["readyTicketPaths"])

    def test_research_artifact_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            rdir = proj / "docs" / "research"
            rdir.mkdir(parents=True)
            (rdir / "tech-landscape.md").write_text("# Research\n", encoding="utf-8")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertIn("docs/research/tech-landscape.md", ev["artifactSignals"]["research"])

    def test_clarification_handoff_content_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            agents = proj / "docs" / "agents"

            # Valid ready handoff
            (agents / "clarification-handoff.md").write_text(
                "Project clarification handoff\n- Status: ready-for-next-stage\n- Recommended next explicit invocation: project-spec\n",
                encoding="utf-8",
            )
            # Irrelevant file with 'clarif' in name but no contract content
            (agents / "clarification-scratchpad.md").write_text(
                "# Just some notes\nNo status or handoff here.\n", encoding="utf-8",
            )
            # Blocked handoff
            (agents / "blocked-handoff.md").write_text(
                "Project clarification handoff\n- Status: blocked\n- Recommended next explicit invocation: none\n",
                encoding="utf-8",
            )

            signals = ASK_LIGHT._classify_clarification_signals(proj, None)
            paths = {s["path"]: s for s in signals}
            self.assertIn("docs/agents/clarification-handoff.md", paths)
            self.assertTrue(paths["docs/agents/clarification-handoff.md"]["ready"])
            self.assertEqual(paths["docs/agents/clarification-handoff.md"]["state"], "ready")

            self.assertIn("docs/agents/blocked-handoff.md", paths)
            self.assertFalse(paths["docs/agents/blocked-handoff.md"]["ready"])
            self.assertEqual(paths["docs/agents/blocked-handoff.md"]["state"], "blocked")

            self.assertNotIn("docs/agents/clarification-scratchpad.md", paths)

    def test_skill_catalog_generation(self) -> None:
        packet = ASK_LIGHT.next_evidence(self.roots, {}, host="codex")
        catalog = packet["catalog"]
        self.assertEqual(len(catalog), 33)
        names = {item["name"] for item in catalog}
        self.assertIn("project-clarify", names)
        self.assertIn("project-spec", names)
        self.assertIn("implement", names)
        self.assertIn("project-review", names)
        self.assertIn("eli5", names)
        for item in catalog:
            self.assertEqual(item["availability"], "available")
            self.assertTrue(item["description"])

    def test_selection_validation_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            val = ASK_LIGHT.validate_recommendation(
                "project-clarify",
                evidence=ev,
                roots=self.roots,
                host="codex",
                scope="current-workflow",
            )
            self.assertEqual(val["status"], "VALIDATED")
            self.assertEqual(val["selectedSkill"], "project-clarify")
            self.assertEqual(val["invocation"], "$project-clarify")
            self.assertEqual(val["invocationType"], "user-invoked")
            self.assertTrue(val["checks"]["inLightMap"])
            self.assertTrue(val["checks"]["available"])
            self.assertTrue(val["checks"]["uniqueCopy"])
            self.assertTrue(val["checks"]["metadataReadable"])
            self.assertTrue(val["checks"]["hostPermits"])
            self.assertTrue(val["checks"]["invocationCompatible"])
            self.assertTrue(val["checks"]["provenanceFirstParty"])
            self.assertTrue(val["checks"]["localPointersResolve"])
            self.assertTrue(val["checks"]["hardConstraintsRespected"])

    def test_selection_validation_blocked_does_not_substitute(self) -> None:
        val = ASK_LIGHT.validate_recommendation(
            "unknown-skill",
            evidence={},
            roots=self.roots,
            host="codex",
            scope="current-workflow",
        )
        self.assertEqual(val["status"], "BLOCKED")
        self.assertEqual(val["logicalRecommendation"], "unknown-skill")
        self.assertIn("not a Light Skill", val["reason"])


# ---------------------------------------------------------------------------
# Category B Tests: Router Boundary Tests (SPEC §37-B)
# ---------------------------------------------------------------------------

class RouterBoundaryTest(unittest.TestCase):
    """Prove that Python does NOT make semantic workflow decisions."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-bnd-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_chinese_next_question_reaches_evidence_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            context = {"projectRoot": str(proj), "goal": "我已经对项目进行了初始化，接下来我该怎么做"}
            packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(packet["routingState"], "needs-model-judgment")
            self.assertIn("evidence", packet)
            self.assertNotIn("skill", packet["evidence"])

    def test_english_next_question_reaches_same_evidence_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            context = {"projectRoot": str(proj), "goal": "What should I do next?"}
            packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(packet["routingState"], "needs-model-judgment")
            self.assertIn("evidence", packet)

    def test_goal_mentioning_spec_does_not_select_project_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            context = {"projectRoot": str(proj), "goal": "I want to write a spec for this project"}
            packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(packet["routingState"], "needs-model-judgment")
            self.assertNotIn("skill", packet["evidence"])

    def test_task_kind_specification_does_not_select_project_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            context = {"projectRoot": str(proj), "taskKind": "specification"}
            packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(packet["routingState"], "needs-model-judgment")
            self.assertNotIn("skill", packet["evidence"])

    def test_research_artifact_does_not_select_project_clarify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            rdir = proj / "docs" / "research"
            rdir.mkdir(parents=True)
            (rdir / "landscape.md").write_text("# Research\n", encoding="utf-8")
            context = {"projectRoot": str(proj)}
            packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(packet["routingState"], "needs-model-judgment")
            self.assertNotIn("skill", packet["evidence"])

    def test_clarification_readiness_does_not_produce_project_spec_from_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            agents = proj / "docs" / "agents"
            (agents / "clarification-handoff.md").write_text(
                "Project clarification handoff\n- Status: ready-for-next-stage\n- Recommended next explicit invocation: project-spec\n",
                encoding="utf-8",
            )
            context = {"projectRoot": str(proj)}
            packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="next")
            self.assertEqual(packet["routingState"], "needs-model-judgment")
            self.assertNotIn("skill", packet["evidence"])

    def test_workflow_mode_publishes_recipes_without_choosing_winner(self) -> None:
        context = {"projectType": "software", "taskKind": "feature"}
        packet = ASK_LIGHT.route(self.roots, context, host="codex", mode="workflow")
        self.assertEqual(packet["routingState"], "needs-model-judgment")
        self.assertIn("recipes", packet)
        self.assertGreater(len(packet["recipes"]), 0)
        self.assertNotIn("workflow", packet.get("evidence", {}))


# ---------------------------------------------------------------------------
# Category C Tests: Hard-State Scope Tests (SPEC §37-C)
# ---------------------------------------------------------------------------

class HardStateScopeTest(unittest.TestCase):
    """Verify that hard constraints bind only current-workflow scope."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-scope-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_ambiguous_effort_blocks_current_workflow_but_permits_standalone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            write_effort_state(proj, "alpha", spec_status="active")
            write_effort_state(proj, "beta", spec_status="active")
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            # current-workflow: blocked by ambiguous-current-effort constraint
            val_wf = ASK_LIGHT.validate_recommendation(
                "implement", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_wf["status"], "BLOCKED")
            self.assertIn("ambiguous-current-effort", val_wf["reason"])

            # standalone: permits eli5
            val_sa = ASK_LIGHT.validate_recommendation(
                "eli5", evidence=ev, roots=self.roots, scope="standalone"
            )
            self.assertEqual(val_sa["status"], "VALIDATED")

    def test_active_review_binds_current_workflow_but_permits_independent_code_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = proj / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(proj, reviewed_effort="effort", status="READY", verdict=None)
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            # current-workflow: project-review is permitted because it owns the constraint
            val_owner = ASK_LIGHT.validate_recommendation(
                "project-review", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_owner["status"], "VALIDATED")

            # current-workflow: other skills (e.g. project-spec) blocked by active review constraint
            val_other = ASK_LIGHT.validate_recommendation(
                "project-spec", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_other["status"], "BLOCKED")
            self.assertIn("active-review", val_other["reason"])

            # independent task: user asks for independent diff review -> code-review validated
            val_indep = ASK_LIGHT.validate_recommendation(
                "code-review", evidence=ev, roots=self.roots, scope="independent"
            )
            self.assertEqual(val_indep["status"], "VALIDATED")

    def test_accepted_effort_permits_new_work_routing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = proj / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(proj, reviewed_effort="effort", verdict="PASS")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["stage"], "accepted")

            # Non-blocking constraint on accepted effort
            self.assertFalse(any(c["blocking"] for c in ev["hardConstraints"]))

            # New effort request routes cleanly under independent/current-workflow
            val_new = ASK_LIGHT.validate_recommendation(
                "project-clarify", evidence=ev, roots=self.roots, scope="independent"
            )
            self.assertEqual(val_new["status"], "VALIDATED")

    def test_uninitialized_repo_permits_standalone_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            proj.mkdir()
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            # current-workflow: uninitialized project requires project-init
            val_wf = ASK_LIGHT.validate_recommendation(
                "project-init", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_wf["status"], "VALIDATED")

            val_wf_bad = ASK_LIGHT.validate_recommendation(
                "project-spec", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_wf_bad["status"], "BLOCKED")

            # standalone: ELI5 validated without issue
            val_sa = ASK_LIGHT.validate_recommendation(
                "eli5", evidence=ev, roots=self.roots, scope="standalone"
            )
            self.assertEqual(val_sa["status"], "VALIDATED")


# ---------------------------------------------------------------------------
# Addendum Tests: agent-config / implement Relationship Tests
# ---------------------------------------------------------------------------

class AgentConfigImplementRelationshipTest(unittest.TestCase):
    """Verify that implement is the bounded executor and agent-config is an
    optional enhancement, not a prerequisite workflow stage."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-ac-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_ready_ticket_evidence_supports_implement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            issues = proj / ".scratch" / "effort" / "issues"
            issues.mkdir(parents=True, exist_ok=True)
            (issues / "01-complex.md").write_text("- Status: ready-for-agent\n- Blocked by: None\n", encoding="utf-8")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertTrue(ev["tickets"]["frontierReady"])

            # implement validates as current-workflow
            val = ASK_LIGHT.validate_recommendation("implement", evidence=ev, roots=self.roots, scope="current-workflow")
            self.assertEqual(val["status"], "VALIDATED")

    def test_implement_remains_valid_when_agent_config_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            issues = proj / ".scratch" / "effort" / "issues"
            issues.mkdir(parents=True, exist_ok=True)
            (issues / "01-ticket.md").write_text("- Status: open\n", encoding="utf-8")
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            # agent-config listed as unavailable
            context = {"availability": {"host": "codex", "unavailableSkills": ["agent-config"]}}
            val = ASK_LIGHT.validate_recommendation(
                "implement", evidence=ev, roots=self.roots, scope="current-workflow", context=context
            )
            self.assertEqual(val["status"], "VALIDATED")

    def test_implement_remains_valid_on_fixed_model_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            issues = proj / ".scratch" / "effort" / "issues"
            issues.mkdir(parents=True, exist_ok=True)
            (issues / "01-ticket.md").write_text("- Status: open\n", encoding="utf-8")
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            # Harness with fixed model / no selector capability
            context = {"hostCapabilities": {"modelSelector": False, "multiAgent": False}}
            val = ASK_LIGHT.validate_recommendation(
                "implement", evidence=ev, roots=self.roots, scope="current-workflow", context=context
            )
            self.assertEqual(val["status"], "VALIDATED")

    def test_explicit_routing_request_validates_agent_config(self) -> None:
        # User explicitly wants execution planning
        val = ASK_LIGHT.validate_recommendation(
            "agent-config", roots=self.roots, scope="independent"
        )
        self.assertEqual(val["status"], "VALIDATED")


# ---------------------------------------------------------------------------
# Review Freshness Regression Tests (SPEC §10)
# ---------------------------------------------------------------------------

class ReviewFreshnessRegressionTest(unittest.TestCase):
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

    def inspect(self, project: Path) -> dict[str, Any]:
        return ASK_LIGHT.inspect_project_evidence(project)

    def modify_reviewed_source(self, project: Path, *, commit: bool) -> None:
        spec = project / ".scratch" / "current" / "spec.md"
        spec.write_text(spec.read_text(encoding="utf-8") + "\nPost-review change.\n", encoding="utf-8")
        if commit:
            commit_all(project, "post-review change")

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
                ev = self.inspect(project)
                self.assertEqual(ev["stage"], "accepted")
                self.assertTrue(ev["review"]["accepted"])

    def test_committed_change_after_pass_stales_review(self) -> None:
        project = self.build_reviewed_project(verdict="PASS")
        self.modify_reviewed_source(project, commit=True)
        ev = self.inspect(project)
        self.assertEqual(ev["stage"], "review-stale")
        self.assertEqual(ev["review"]["freshness"], "stale")

    def test_dirty_working_tree_after_pass_stales_review(self) -> None:
        project = self.build_reviewed_project(verdict="PASS")
        self.modify_reviewed_source(project, commit=False)
        ev = self.inspect(project)
        self.assertEqual(ev["stage"], "review-stale")
        self.assertEqual(ev["review"]["freshness"], "stale")

    def test_unrelated_file_change_keeps_fresh_acceptance(self) -> None:
        for label, commit_unrelated in (("untracked-readme", False), ("committed-readme", True)):
            with self.subTest(label=label):
                project = self.build_reviewed_project(verdict="PASS")
                readme = project / "README.md"
                readme.write_text("# Project\n\nUnrelated documentation change.\n", encoding="utf-8")
                if commit_unrelated:
                    _git(project, "add", "-A")
                    commit_all(project, "docs only")
                ev = self.inspect(project)
                self.assertEqual(ev["stage"], "accepted")

    def test_unresolvable_revision_identity_fails_closed(self) -> None:
        project = self.build_reviewed_project(verdict="PASS", revision_identity="nonsense-or-unavailable")
        ev = self.inspect(project)
        self.assertEqual(ev["stage"], "review-freshness-unknown")
        self.assertFalse(ev["review"]["accepted"])

    def test_duplicate_source_revision_fields_fail_closed(self) -> None:
        garbage = "0f1e2d3c4b5a9876543210fedcba9876543210ab"
        project = self.build_reviewed_project(verdict="PASS")
        append_durable_field(project / ".project-review" / "charter.md", f"- Source revision or identity: {garbage}")
        ev = self.inspect(project)
        self.assertEqual(ev["stage"], "review-freshness-unknown")

    def test_duplicate_source_fields_fail_closed(self) -> None:
        project = self.build_reviewed_project(verdict="PASS")
        append_durable_field(project / ".project-review" / "charter.md", "- Source: `.scratch/other/spec.md`")
        ev = self.inspect(project)
        self.assertEqual(ev["stage"], "review-ownership-unknown")


# ---------------------------------------------------------------------------
# Software Baseline Freshness Tests (SPEC §10)
# ---------------------------------------------------------------------------

class SoftwareBaselineFreshnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-soft-")
        host_root = Path(self.temp.name) / "host"
        host_root.mkdir()
        self.roots = install_host_fixture_skills(host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

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
        self._count += 1
        project = Path(self.temp.name) / f"soft-{self._count}"
        write_project_state(project, initialized=True, spec=True)
        write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
        (project / "README.md").write_text("# Project\nv1\n", encoding="utf-8")
        src = project / "src"
        src.mkdir()
        (src / "common.py").write_text("VALUE_COMMON = 1\n", encoding="utf-8")
        base = ensure_git_baseline(project)
        (src / "app.py").write_text("print('implementation v1')\n", encoding="utf-8")
        _git(project, "add", "-A")
        commit_all(project, "implement feature v1")
        candidate = _git(project, "rev-parse", "HEAD").stdout.strip()
        write_project_review_state(
            project,
            reviewed_effort="current",
            verdict=verdict,
            revision_identity=base,
            profile="software",
            fixed_point=base if include_fixed_point and fixed_point_override is None else fixed_point_override,
            implementation_scope=scope_value if include_scope else None,
            final_revision=(final_revision_override if final_revision_override is not None else candidate)
            if include_final_revision else None,
        )
        return project, base, candidate

    def test_software_baseline_accepts(self) -> None:
        project, _b, _c = self.build_reviewed_software_project()
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "accepted")
        self.assertTrue(ev["review"]["accepted"])

    def test_software_in_scope_drift_stales(self) -> None:
        project, _b, _c = self.build_reviewed_software_project()
        (project / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "review-stale")
        self.assertEqual(ev["review"]["freshness"], "stale")

    def test_software_out_of_scope_change_keeps_accepted(self) -> None:
        project, _b, _c = self.build_reviewed_software_project()
        (project / "README.md").write_text("# Project\nv2\n", encoding="utf-8")
        commit_all(project, "update readme")
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "accepted")


# ---------------------------------------------------------------------------
# Directory Source Baseline Tests (SPEC §10)
# ---------------------------------------------------------------------------

class DirectorySourceBaselineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-dir-")
        host_root = Path(self.temp.name) / "host"
        host_root.mkdir()
        self.roots = install_host_fixture_skills(host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

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

    def test_tracked_child_modification_stales_the_review(self) -> None:
        project = self.build_directory_source_project()
        map_file = project / ".scratch" / "current" / "map.md"
        map_file.write_text("# Map changed\n", encoding="utf-8")
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "review-stale")

    def test_new_untracked_child_stales_the_review(self) -> None:
        project = self.build_directory_source_project()
        (project / ".scratch" / "current" / "new.txt").write_text("new\n", encoding="utf-8")
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "review-stale")


# ---------------------------------------------------------------------------
# Review Transaction Coherence Tests (SPEC §10)
# ---------------------------------------------------------------------------

class ReviewTransactionCoherenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-tx-")
        host_root = Path(self.temp.name) / "host"
        host_root.mkdir()
        self.roots = install_host_fixture_skills(host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

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

    def test_coherent_pass_accepted(self) -> None:
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "accepted")
        self.assertTrue(ev["review"]["accepted"])

    def test_active_review_state_sets_project_review_stage(self) -> None:
        for st in ("INIT", "READY", "CRITIC", "REPAIR", "EVALUATE"):
            with self.subTest(status=st):
                project, _b, _c = self.build_project(status=st, verdict="PASS")
                ev = ASK_LIGHT.inspect_project_evidence(project)
                self.assertEqual(ev["stage"], "project-review")
                self.assertEqual(ev["review"]["status"], st)
                self.assertFalse(ev["review"]["accepted"])

    def test_round_mismatch_fails_closed(self) -> None:
        project, _b, _c = self.build_project(status="PASS", verdict="PASS")
        (project / ".project-review" / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        (project / ".project-review" / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n",
            encoding="utf-8",
        )
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "acceptance-unknown")

    def test_verdict_conflict_fails_closed(self) -> None:
        project, _b, _c = self.build_project(status="PASS", verdict="FAIL")
        ev = ASK_LIGHT.inspect_project_evidence(project)
        self.assertEqual(ev["stage"], "acceptance-unknown")


# ---------------------------------------------------------------------------
# Approval Transition Tests (SPEC §32, §33)
# ---------------------------------------------------------------------------

class ApprovalTransitionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-appr-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_model_invoked_target_begins_in_conversation(self) -> None:
        rec = {"status": "RECOMMEND", "skill": "code-review", "scope": "independent"}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots)
        self.assertEqual(trans["next"], "beginning-code-review")
        self.assertIn("model-invoked", trans["execution"])

    def test_user_invoked_target_requires_host_transition_without_capability(self) -> None:
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots)
        self.assertEqual(trans["next"], "host-transition-required")
        self.assertIn("exact invocation", trans["execution"])

    def test_user_invoked_target_transitions_with_approved_capability(self) -> None:
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {"hostCapabilities": {"approvedUserInvokedTransition": True}}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
        self.assertEqual(trans["next"], "beginning-project-clarify")
        self.assertIn("approved transition", trans["execution"])

    def test_revalidation_blocks_stale_advice(self) -> None:
        rec = {"status": "RECOMMEND", "skill": "nonexistent-skill", "scope": "independent"}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots)
        self.assertEqual(trans["next"], "revalidation-blocked")
        self.assertIn("cannot be executed", trans["execution"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
