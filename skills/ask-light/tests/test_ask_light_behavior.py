from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch
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
# Category A Tests: Deterministic Evidence Tests (SPEC §5, §28, §29, §37-A)
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

    def test_canonical_flow_spec_no_tickets_recommends_project_tickets(self) -> None:
        """SPEC §5: Active SPEC without tickets routes to project-tickets without review gate."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            write_effort_state(proj, "feature-a", spec_status="active")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["stage"], "spec-no-tickets")
            self.assertFalse(ev["tickets"]["exists"])
            self.assertTrue(ev["spec"]["active"])

            # Validating project-tickets under current-workflow succeeds without hard constraint blocker
            val = ASK_LIGHT.validate_recommendation(
                "project-tickets", evidence=ev, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "VALIDATED")
            self.assertEqual(val["selectedSkill"], "project-tickets")
            self.assertTrue(val["checks"]["hardConstraintsRespected"])

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

    def test_research_artifact_discovery_conservative(self) -> None:
        """SPEC §30: Research existence means candidate exists, not sufficient or clarified."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            rdir = proj / "docs" / "research"
            rdir.mkdir(parents=True)
            (rdir / "tech-landscape.md").write_text("# Research\n", encoding="utf-8")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertIn("docs/research/tech-landscape.md", ev["artifactSignals"]["research"])
            self.assertEqual(ev["stage"], "initialized")

    def test_clarification_handoff_content_classification(self) -> None:
        """SPEC §28, §29: Content-validated clarification signals with readyFor."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            agents = proj / "docs" / "agents"

            # 1. Valid ready handoff with project-spec recommendation
            (agents / "clarification-handoff.md").write_text(
                "Project clarification handoff\n- Status: ready-for-next-stage\n- Recommended next explicit invocation: project-spec\n",
                encoding="utf-8",
            )
            # 2. Irrelevant file with 'clarif' in name but no contract content
            (agents / "clarification-scratchpad.md").write_text(
                "# Just some notes\nNo status or handoff here.\n", encoding="utf-8",
            )
            # 3. Blocked handoff
            (agents / "blocked-handoff.md").write_text(
                "Project clarification handoff\n- Status: blocked\n- Recommended next explicit invocation: none\n",
                encoding="utf-8",
            )
            # 4. Ready status but missing recommended invocation (incomplete readiness)
            (agents / "incomplete-handoff.md").write_text(
                "Project clarification handoff\n- Status: ready-for-next-stage\n",
                encoding="utf-8",
            )

            signals = ASK_LIGHT._classify_clarification_signals(proj, None)
            paths = {s["path"]: s for s in signals}

            # 1. ready -> ready: True, readyFor: "project-spec"
            self.assertIn("docs/agents/clarification-handoff.md", paths)
            self.assertTrue(paths["docs/agents/clarification-handoff.md"]["ready"])
            self.assertEqual(paths["docs/agents/clarification-handoff.md"]["state"], "ready")
            self.assertEqual(paths["docs/agents/clarification-handoff.md"]["readyFor"], "project-spec")

            # 2. notes -> not classified
            self.assertNotIn("docs/agents/clarification-scratchpad.md", paths)

            # 3. blocked -> ready: False
            self.assertIn("docs/agents/blocked-handoff.md", paths)
            self.assertFalse(paths["docs/agents/blocked-handoff.md"]["ready"])
            self.assertEqual(paths["docs/agents/blocked-handoff.md"]["state"], "blocked")

            # 4. incomplete -> ready: False, state: incomplete-readiness
            self.assertIn("docs/agents/incomplete-handoff.md", paths)
            self.assertFalse(paths["docs/agents/incomplete-handoff.md"]["ready"])
            self.assertEqual(paths["docs/agents/incomplete-handoff.md"]["state"], "incomplete-readiness")

    def test_skill_catalog_generation(self) -> None:
        packet = ASK_LIGHT.next_evidence(self.roots, {}, host="codex")
        catalog = packet["catalog"]
        self.assertEqual(len(catalog), 34)
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
# Strict Scope Validation & Skill: none Tests (SPEC §6, §7, §8, §9)
# ---------------------------------------------------------------------------

class StrictScopeAndNoneValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-scope-val-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_scope_vocabulary(self) -> None:
        for scope in ("current-workflow", "independent", "standalone"):
            with self.subTest(scope=scope):
                val = ASK_LIGHT.validate_recommendation(
                    "eli5", roots=self.roots, host="codex", scope=scope
                )
                self.assertEqual(val["status"], "VALIDATED")
                self.assertEqual(val["scope"], scope)

    def test_invalid_scope_rejected_immediately(self) -> None:
        """SPEC §6: validator rejects unknown/typo scopes."""
        for invalid in ("independant", "foo", "custom", "workflow", "", None):
            with self.subTest(scope=invalid):
                val = ASK_LIGHT.validate_recommendation(
                    "eli5", roots=self.roots, host="codex", scope=invalid
                )
                self.assertEqual(val["status"], "BLOCKED")
                self.assertIn("scope must be one of", val["reason"])

    def test_invalid_scope_cannot_bypass_hard_constraints(self) -> None:
        """SPEC §7: Invalid scope never bypasses active hard constraints."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = proj / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(proj, reviewed_effort="effort", status="READY", verdict=None)
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            val = ASK_LIGHT.validate_recommendation(
                "code-review", evidence=ev, roots=self.roots, host="codex", scope="independant"
            )
            self.assertEqual(val["status"], "BLOCKED")
            self.assertIn("scope must be one of", val["reason"])

    def test_skill_none_valid_for_accepted_effort(self) -> None:
        """SPEC §8: Legitimate terminal accepted effort returns valid Skill none."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = proj / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(proj, reviewed_effort="effort", verdict="PASS")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["stage"], "accepted")

            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "VALIDATED")
            self.assertTrue(val["checks"]["noSkillSelected"])
            self.assertTrue(val["checks"]["hardConstraintsRespected"])
            self.assertIn("current effort accepted", val["reason"])

    def test_skill_none_invalid_for_all_non_terminal_current_workflow_stages(self) -> None:
        """SPEC §8, §9: Reject Skill: none for any non-terminal current-workflow state."""
        # 1. Uninitialized project
        with tempfile.TemporaryDirectory() as tmp:
            p_uninit = Path(tmp) / "uninit"
            p_uninit.mkdir()
            ev_uninit = ASK_LIGHT.inspect_project_evidence(p_uninit)
            self.assertEqual(ev_uninit["stage"], "uninitialized")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_uninit, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")
            self.assertFalse(val["checks"]["hardConstraintsRespected"])

        # 2. Initialized (no SPEC)
        with tempfile.TemporaryDirectory() as tmp:
            p_init = Path(tmp) / "init"
            write_project_state(p_init, initialized=True, spec=False)
            ev_init = ASK_LIGHT.inspect_project_evidence(p_init)
            self.assertEqual(ev_init["stage"], "initialized")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_init, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 3. Initialized with research
        with tempfile.TemporaryDirectory() as tmp:
            p_res = Path(tmp) / "init_res"
            write_project_state(p_res, initialized=True, spec=False)
            docs_res = p_res / "docs" / "research"
            docs_res.mkdir(parents=True)
            (docs_res / "findings.md").write_text("# Research\n", encoding="utf-8")
            ev_res = ASK_LIGHT.inspect_project_evidence(p_res)
            self.assertEqual(ev_res["stage"], "initialized")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_res, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 4. Clarification ready but no SPEC (stage is initialized, artifactSignals.clarification has readyFor project-spec)
        with tempfile.TemporaryDirectory() as tmp:
            p_clar = Path(tmp) / "clar_ready"
            write_project_state(p_clar, initialized=True, spec=False)
            docs_agents = p_clar / "docs" / "agents"
            docs_agents.mkdir(parents=True, exist_ok=True)
            (docs_agents / "clarification-handoff.md").write_text(
                "Project clarification handoff\n- Status: ready-for-next-stage\n- Recommended next explicit invocation: project-spec\n",
                encoding="utf-8",
            )
            ev_clar = ASK_LIGHT.inspect_project_evidence(p_clar)
            self.assertEqual(ev_clar["stage"], "initialized")
            self.assertTrue(any(s.get("readyFor") == "project-spec" for s in ev_clar.get("artifactSignals", {}).get("clarification", [])))
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_clar, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 5. SPEC ready without tickets
        with tempfile.TemporaryDirectory() as tmp:
            p_spec = Path(tmp) / "spec_ready"
            write_project_state(p_spec, initialized=True, spec=True)
            ev_spec = ASK_LIGHT.inspect_project_evidence(p_spec)
            self.assertEqual(ev_spec["stage"], "spec-no-tickets")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_spec, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 6. Ready implementation ticket
        with tempfile.TemporaryDirectory() as tmp:
            p_wip = Path(tmp) / "wip"
            write_project_state(p_wip, initialized=True, spec=True)
            issues = p_wip / ".scratch" / "effort" / "issues"
            issues.mkdir(parents=True, exist_ok=True)
            (issues / "01-ticket.md").write_text("- Status: open\n", encoding="utf-8")
            ev_wip = ASK_LIGHT.inspect_project_evidence(p_wip)
            self.assertEqual(ev_wip["stage"], "work-in-progress")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_wip, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 7. Active project review
        with tempfile.TemporaryDirectory() as tmp:
            p_rev = Path(tmp) / "rev_active"
            write_project_state(p_rev, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = p_rev / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(p_rev, reviewed_effort="effort", status="READY", verdict=None)
            ev_rev = ASK_LIGHT.inspect_project_evidence(p_rev)
            self.assertEqual(ev_rev["stage"], "project-review")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_rev, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 8. Stale review
        with tempfile.TemporaryDirectory() as tmp:
            p_stale = Path(tmp) / "rev_stale"
            write_project_state(p_stale, initialized=True, spec=True)
            write_effort_state(p_stale, "current", spec_status="active", ticket_statuses=["resolved"])
            ensure_git_baseline(p_stale)
            write_project_review_state(p_stale, reviewed_effort="current", verdict="PASS")
            spec_file = p_stale / ".scratch" / "current" / "spec.md"
            spec_file.write_text(spec_file.read_text(encoding="utf-8") + "\nDirty drift\n", encoding="utf-8")
            ev_stale = ASK_LIGHT.inspect_project_evidence(p_stale)
            self.assertEqual(ev_stale["stage"], "review-stale")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_stale, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 9. Ambiguous current effort
        with tempfile.TemporaryDirectory() as tmp:
            p_amb = Path(tmp) / "amb_effort"
            write_project_state(p_amb, initialized=True, spec=True)
            write_effort_state(p_amb, "alpha", spec_status="active")
            write_effort_state(p_amb, "beta", spec_status="active")
            ev_amb = ASK_LIGHT.inspect_project_evidence(p_amb)
            self.assertEqual(ev_amb["stage"], "ambiguous-current-effort")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_amb, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

        # 10. Tickets unknown (unrecognized status)
        with tempfile.TemporaryDirectory() as tmp:
            p_tkn = Path(tmp) / "tickets_unknown"
            write_project_state(p_tkn, initialized=True, spec=True)
            issues = p_tkn / ".scratch" / "effort" / "issues"
            issues.mkdir(parents=True, exist_ok=True)
            (issues / "01.md").write_text("- Status: foobar\n", encoding="utf-8")
            ev_tkn = ASK_LIGHT.inspect_project_evidence(p_tkn)
            self.assertEqual(ev_tkn["stage"], "tickets-unknown")
            val = ASK_LIGHT.validate_recommendation(
                "none", evidence=ev_tkn, roots=self.roots, host="codex", scope="current-workflow"
            )
            self.assertEqual(val["status"], "BLOCKED")

    def test_skill_none_valid_for_standalone_and_independent(self) -> None:
        val_sa = ASK_LIGHT.validate_recommendation(
            "none", roots=self.roots, host="codex", scope="standalone"
        )
        self.assertEqual(val_sa["status"], "VALIDATED")

        val_indep = ASK_LIGHT.validate_recommendation(
            "none", roots=self.roots, host="codex", scope="independent"
        )
        self.assertEqual(val_indep["status"], "VALIDATED")


# ---------------------------------------------------------------------------
# Approval Transition & Host Capability Tests (SPEC §10, §11, §12, §15, §16)
# ---------------------------------------------------------------------------

class ApprovalTransitionAndHostCapabilityTest(unittest.TestCase):
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
        """Negative E: Normal approved user-invoked target without Host capability emits host-transition-required."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots)
        self.assertEqual(trans["next"], "host-transition-required")
        self.assertIn("exact invocation", trans["execution"])
        self.assertIn("$project-clarify", trans["execution"])

    def test_user_invoked_target_requires_host_transition_with_untrusted_boolean(self) -> None:
        """Raw boolean True in hostCapabilities is NOT trusted host evidence."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {"hostCapabilities": {"approvedUserInvokedTransition": True}}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
        self.assertEqual(trans["next"], "host-transition-required")

    def test_user_invoked_target_requires_host_transition_with_model_inference(self) -> None:
        """Model inference source is NOT trusted host evidence."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {
            "hostCapabilities": {
                "approvedUserInvokedTransition": {"state": "available", "source": "model-inference"}
            }
        }
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
        self.assertEqual(trans["next"], "host-transition-required")

    def test_user_invoked_target_requires_host_transition_with_fake_source_only(self) -> None:
        """Negative A: Fake source alone (source: host-runtime) does not grant transition authority."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {
            "hostCapabilities": {
                "approvedUserInvokedTransition": {"state": "available", "source": "host-runtime"}
            }
        }
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
        self.assertEqual(trans["next"], "host-transition-required")
        self.assertNotEqual(trans["next"], "beginning-project-clarify")

    def test_user_invoked_target_requires_host_transition_with_fake_public_trust_flag(self) -> None:
        """Negative B: Fake public trust flag (trustedHostChannel: true) does not establish trust."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {
            "trustedHostChannel": True,
            "hostCapabilities": {
                "approvedUserInvokedTransition": {"state": "available", "source": "host-runtime"}
            }
        }
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
        self.assertEqual(trans["next"], "host-transition-required")
        self.assertNotEqual(trans["next"], "beginning-project-clarify")

    def test_user_invoked_target_requires_host_transition_with_fake_private_trust_flag(self) -> None:
        """Negative C: Fake private-looking trust flag (_trusted_host_channel: true) does not establish trust."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {
            "_trusted_host_channel": True,
            "hostCapabilities": {
                "approvedUserInvokedTransition": {"state": "available", "source": "host-runtime"}
            }
        }
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
        self.assertEqual(trans["next"], "host-transition-required")
        self.assertNotEqual(trans["next"], "beginning-project-clarify")

    def test_user_invoked_target_requires_host_transition_with_all_fake_signals_combined(self) -> None:
        """Negative D: Combining all fake trust-looking fields + env var still fails safe."""
        rec = {"status": "RECOMMEND", "skill": "project-clarify", "scope": "current-workflow"}
        context = {
            "trustedHostChannel": True,
            "_trusted_host_channel": True,
            "hostCapabilities": {
                "approvedUserInvokedTransition": {"state": "available", "source": "host-runtime"}
            }
        }
        with patch.dict(os.environ, {"LIGHT_TRUSTED_HOST_CHANNEL": "1"}):
            trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
            self.assertEqual(trans["next"], "host-transition-required")
            self.assertNotEqual(trans["next"], "beginning-project-clarify")

    def test_approval_transition_fails_closed_on_missing_or_invalid_scope(self) -> None:
        """Negative G: Approval transition requires stored valid scope; fails closed otherwise."""
        # Missing scope
        rec_missing = {"status": "RECOMMEND", "skill": "code-review"}
        trans_miss = ASK_LIGHT.approval_transition(rec_missing, roots=self.roots)
        self.assertEqual(trans_miss["next"], "revalidation-blocked")
        self.assertEqual(trans_miss["revalidation"]["status"], "BLOCKED")
        self.assertIn("scope must be one of", trans_miss["execution"])

        # Invalid scope
        for invalid in ("independant", "foo", "", "unknown"):
            with self.subTest(invalid_scope=invalid):
                rec_inv = {"status": "RECOMMEND", "skill": "code-review", "scope": invalid}
                trans_inv = ASK_LIGHT.approval_transition(rec_inv, roots=self.roots)
                self.assertEqual(trans_inv["next"], "revalidation-blocked")
                self.assertEqual(trans_inv["revalidation"]["status"], "BLOCKED")
                self.assertIn("scope must be one of", trans_inv["execution"])

    def test_approval_preserves_independent_scope_under_active_review(self) -> None:
        """Preservation F: Scope preservation across approval under active project-review."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = proj / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(proj, reviewed_effort="effort", status="READY", verdict=None)

            context = {
                "projectRoot": str(proj),
            }

            rec = {
                "status": "RECOMMEND",
                "skill": "code-review",
                "scope": "independent",
                "source": "first-party",
            }
            trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
            self.assertEqual(trans["scope"], "independent")
            self.assertEqual(trans["revalidation"]["scope"], "independent")
            self.assertEqual(trans["revalidation"]["status"], "VALIDATED")
            self.assertEqual(trans["next"], "beginning-code-review")

    def test_approval_preserves_independent_scope_for_user_invoked_target_fallback(self) -> None:
        """Preservation F: Scope survives fallback transition for user-invoked skill."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True, ticket_statuses=["resolved"])
            effort_spec = proj / ".scratch" / "effort" / "spec.md"
            effort_spec.write_text("# SPEC\nStatus: active\n", encoding="utf-8")
            write_project_review_state(proj, reviewed_effort="effort", status="READY", verdict=None)

            context = {
                "projectRoot": str(proj),
            }

            rec = {
                "status": "RECOMMEND",
                "skill": "project-clarify",
                "scope": "independent",
                "source": "first-party",
            }
            trans = ASK_LIGHT.approval_transition(rec, roots=self.roots, context=context)
            self.assertEqual(trans["scope"], "independent")
            self.assertEqual(trans["revalidation"]["scope"], "independent")
            self.assertEqual(trans["revalidation"]["status"], "VALIDATED")
            self.assertEqual(trans["next"], "host-transition-required")
            self.assertIn("$project-clarify", trans["execution"])

    def test_revalidation_blocks_stale_advice(self) -> None:
        rec = {"status": "RECOMMEND", "skill": "nonexistent-skill", "scope": "independent"}
        trans = ASK_LIGHT.approval_transition(rec, roots=self.roots)
        self.assertEqual(trans["next"], "revalidation-blocked")
        self.assertIn("cannot be executed", trans["execution"])


# ---------------------------------------------------------------------------
# Router Boundary Tests (SPEC §37-B)
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
# Hard-State Scope Tests (SPEC §37-C)
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

            val_wf = ASK_LIGHT.validate_recommendation(
                "implement", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_wf["status"], "BLOCKED")
            self.assertIn("ambiguous-current-effort", val_wf["reason"])

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

            val_owner = ASK_LIGHT.validate_recommendation(
                "project-review", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_owner["status"], "VALIDATED")

            val_other = ASK_LIGHT.validate_recommendation(
                "project-spec", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_other["status"], "BLOCKED")
            self.assertIn("active-review", val_other["reason"])

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

            self.assertFalse(any(c["blocking"] for c in ev["hardConstraints"]))

            val_new = ASK_LIGHT.validate_recommendation(
                "project-clarify", evidence=ev, roots=self.roots, scope="independent"
            )
            self.assertEqual(val_new["status"], "VALIDATED")

    def test_uninitialized_repo_permits_standalone_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            proj.mkdir()
            ev = ASK_LIGHT.inspect_project_evidence(proj)

            val_wf = ASK_LIGHT.validate_recommendation(
                "project-init", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_wf["status"], "VALIDATED")

            val_wf_bad = ASK_LIGHT.validate_recommendation(
                "project-spec", evidence=ev, roots=self.roots, scope="current-workflow"
            )
            self.assertEqual(val_wf_bad["status"], "BLOCKED")

            val_sa = ASK_LIGHT.validate_recommendation(
                "eli5", evidence=ev, roots=self.roots, scope="standalone"
            )
            self.assertEqual(val_sa["status"], "VALIDATED")


# ---------------------------------------------------------------------------
# agent-config / implement Relationship Tests (SPEC §31, §34, §35)
# ---------------------------------------------------------------------------

class AgentConfigImplementRelationshipTest(unittest.TestCase):
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

            context = {"hostCapabilities": {"modelSelector": False, "multiAgent": False}}
            val = ASK_LIGHT.validate_recommendation(
                "implement", evidence=ev, roots=self.roots, scope="current-workflow", context=context
            )
            self.assertEqual(val["status"], "VALIDATED")

    def test_explicit_routing_request_validates_agent_config(self) -> None:
        val = ASK_LIGHT.validate_recommendation(
            "agent-config", roots=self.roots, scope="independent"
        )
        self.assertEqual(val["status"], "VALIDATED")


# ---------------------------------------------------------------------------
# Review Transaction Coherence & Full Matrix Tests (SPEC §19)
# ---------------------------------------------------------------------------

class ReviewTransactionRegressionMatrixTest(unittest.TestCase):
    """Exhaustive transaction coherence matrix covering Charter/State/Verdict fields and formats."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-tx-mat-")
        self.host_root = Path(self.temp.name) / "host"
        self.host_root.mkdir()
        self.roots = install_host_fixture_skills(self.host_root)
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
        state_round: str = "1",
        verdict_round: str = "round-01 (final)",
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
            f"- Round: {state_round}\n",
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
                + f"- Round: {verdict_round}\n\n"
                "## Conclusion\nBaseline accepted.\n",
                encoding="utf-8",
            )
        return root, base_sha, cand_sha

    def test_missing_or_duplicate_charter_fields_fail_closed(self) -> None:
        # missing Charter revision
        p1, _, _ = self.build_project()
        (p1 / ".project-review" / "charter.md").write_text("# Charter\n- Source: `.scratch/current/spec.md`\n- Profile: generic\n", encoding="utf-8")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p1)["stage"], "review-state-unknown")

        # duplicate Charter revision
        p2, _, _ = self.build_project()
        append_durable_field(p2 / ".project-review" / "charter.md", "- Charter revision: 2")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p2)["stage"], "review-state-unknown")

        # duplicate Profile
        p3, _, _ = self.build_project()
        append_durable_field(p3 / ".project-review" / "charter.md", "- Profile: software")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p3)["stage"], "review-freshness-unknown")

    def test_missing_or_duplicate_state_fields_fail_closed(self) -> None:
        fields = ("Status", "Charter revision", "Profile", "Round")
        for field in fields:
            with self.subTest(missing_field=field):
                p, _, _ = self.build_project()
                lines = [line for line in (p / ".project-review" / "state.md").read_text(encoding="utf-8").splitlines() if not line.startswith(f"- {field}:")]
                (p / ".project-review" / "state.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "review-state-unknown")

            with self.subTest(duplicate_field=field):
                p, _, _ = self.build_project()
                append_durable_field(p / ".project-review" / "state.md", f"- {field}: extra-value")
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "review-state-unknown")

    def test_state_round_invalid_forms_fail_closed(self) -> None:
        for bad_round in ("0", "00", "-1", "round-00", "abc", "round-final"):
            with self.subTest(bad_round=bad_round):
                p, _, _ = self.build_project(state_round=bad_round)
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "review-state-unknown")

    def test_state_charter_revision_and_profile_mismatch_fail_closed(self) -> None:
        p_rev, _, _ = self.build_project(charter_rev="1", state_rev="2")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_rev)["stage"], "review-state-unknown")

        p_prof, _, _ = self.build_project(profile="generic")
        (p_prof / ".project-review" / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 1\n", encoding="utf-8"
        )
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_prof)["stage"], "review-state-unknown")

    def test_missing_or_duplicate_verdict_fields_fail_closed(self) -> None:
        fields = ("Verdict", "Charter revision", "Profile", "Round")
        for field in fields:
            with self.subTest(missing_verdict_field=field):
                p, _, _ = self.build_project()
                lines = [line for line in (p / ".project-review" / "verdict.md").read_text(encoding="utf-8").splitlines() if not line.startswith(f"- {field}:")]
                (p / ".project-review" / "verdict.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "acceptance-unknown")

            with self.subTest(duplicate_verdict_field=field):
                p, _, _ = self.build_project()
                append_durable_field(p / ".project-review" / "verdict.md", f"- {field}: PASS")
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "acceptance-unknown")

    def test_verdict_aliases_and_semantic_pass_fail_closed(self) -> None:
        # Alias field lines instead of canonical Verdict:
        aliases = ("Result: PASS", "Outcome: PASS", "Acceptance: PASS", "Status: PASS", "State: PASS")
        for alias in aliases:
            with self.subTest(alias=alias):
                p, _, _ = self.build_project(verdict=None)
                (p / ".project-review" / "verdict.md").write_text(
                    f"# Verdict\n- Charter revision: 1\n- Profile: generic\n- {alias}\n- Round: 1\n", encoding="utf-8"
                )
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "acceptance-unknown")

        # Non-canonical semantic verdicts
        bad_verdicts = ("PASSED", "ACCEPTED", "SUCCESS", "APPROVED", "OK", "COMPLETE", "FAILED", "REJECTED")
        for bad in bad_verdicts:
            with self.subTest(bad_verdict=bad):
                p, _, _ = self.build_project(verdict=bad)
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "acceptance-unknown")

    def test_state_verdict_mismatches_fail_closed(self) -> None:
        # Round mismatch
        p_round, _, _ = self.build_project(state_round="1", verdict_round="2")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_round)["stage"], "acceptance-unknown")

        # Charter revision mismatch
        p_rev, _, _ = self.build_project(charter_rev="1", verdict_rev="2")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_rev)["stage"], "acceptance-unknown")

        # Profile mismatch
        p_prof, _, _ = self.build_project(profile="generic", verdict_profile="software")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_prof)["stage"], "acceptance-unknown")

        # Status conflict (State PASS vs Verdict FAIL)
        p_conf, _, _ = self.build_project(status="PASS", verdict="FAIL")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_conf)["stage"], "acceptance-unknown")

    def test_positive_round_forms_accepted(self) -> None:
        for r_state, r_verdict in (
            ("1", "1"),
            ("01", "01"),
            ("round-01", "round-01"),
            ("round-1", "round-1"),
            ("round-01 (final)", "round-01 (final)"),
            ("round-01 (closed)", "round-01 (closed)"),
        ):
            with self.subTest(r_state=r_state, r_verdict=r_verdict):
                p, _, _ = self.build_project(state_round=r_state, verdict_round=r_verdict)
                self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "accepted")


# ---------------------------------------------------------------------------
# Freshness Regression Matrix Tests (SPEC §20)
# ---------------------------------------------------------------------------

class FreshnessRegressionMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-fresh-mat-")
        self.host_root = Path(self.temp.name) / "host"
        self.host_root.mkdir()
        self.roots = install_host_fixture_skills(self.host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build_project(self, verdict: str = "PASS") -> Path:
        self._count += 1
        project = Path(self.temp.name) / f"fresh-{self._count}"
        write_project_state(project, initialized=True, spec=True)
        write_effort_state(project, "current", spec_status="active", ticket_statuses=["resolved"])
        ensure_git_baseline(project)
        write_project_review_state(project, reviewed_effort="current", verdict=verdict)
        return project

    def test_fresh_pass_fail_and_blocked_verdicts(self) -> None:
        p_pass = self.build_project("PASS")
        ev_pass = ASK_LIGHT.inspect_project_evidence(p_pass)
        self.assertEqual(ev_pass["stage"], "accepted")
        self.assertTrue(ev_pass["review"]["accepted"])

        p_fail = self.build_project("FAIL")
        ev_fail = ASK_LIGHT.inspect_project_evidence(p_fail)
        self.assertEqual(ev_fail["stage"], "acceptance-not-passed")
        self.assertFalse(ev_fail["review"]["accepted"])

        p_blk = self.build_project("BLOCKED")
        ev_blk = ASK_LIGHT.inspect_project_evidence(p_blk)
        self.assertEqual(ev_blk["stage"], "acceptance-not-passed")
        self.assertFalse(ev_blk["review"]["accepted"])

    def test_stale_pass_fail_blocked_on_committed_change(self) -> None:
        for verdict in ("PASS", "FAIL", "BLOCKED"):
            with self.subTest(verdict=verdict):
                p = self.build_project(verdict)
                spec = p / ".scratch" / "current" / "spec.md"
                spec.write_text(spec.read_text(encoding="utf-8") + "\nModification\n", encoding="utf-8")
                commit_all(p, "modify spec")
                ev = ASK_LIGHT.inspect_project_evidence(p)
                self.assertEqual(ev["stage"], "review-stale")
                self.assertEqual(ev["review"]["freshness"], "stale")

    def test_stale_pass_on_working_tree_and_staged_drift(self) -> None:
        # unstaged dirty
        p_dirty = self.build_project("PASS")
        spec_d = p_dirty / ".scratch" / "current" / "spec.md"
        spec_d.write_text(spec_d.read_text(encoding="utf-8") + "\nUnstaged dirty\n", encoding="utf-8")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_dirty)["stage"], "review-stale")

        # staged change
        p_staged = self.build_project("PASS")
        spec_s = p_staged / ".scratch" / "current" / "spec.md"
        spec_s.write_text(spec_s.read_text(encoding="utf-8") + "\nStaged\n", encoding="utf-8")
        _git(p_staged, "add", "-A")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_staged)["stage"], "review-stale")

        # tracked deletion
        p_del = self.build_project("PASS")
        (p_del / ".scratch" / "current" / "spec.md").unlink()
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_del)["stage"], "review-stale")

    def test_untracked_and_ignored_in_scope_additions_stale(self) -> None:
        # Directory baseline source
        p_dir = Path(self.temp.name) / "dir-proj"
        write_project_state(p_dir, initialized=True, spec=True)
        write_effort_state(p_dir, "current", spec_status="active", ticket_statuses=["resolved"])
        base = ensure_git_baseline(p_dir)
        write_project_review_state(p_dir, charter_source="`.scratch/current`", verdict="PASS", revision_identity=base)

        # untracked file inside reviewed dir stales
        (p_dir / ".scratch" / "current" / "untracked.md").write_text("untracked\n", encoding="utf-8")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_dir)["stage"], "review-stale")

        # git-ignored file inside reviewed dir stales
        p_ign = Path(self.temp.name) / "ign-proj"
        write_project_state(p_ign, initialized=True, spec=True)
        write_effort_state(p_ign, "current", spec_status="active", ticket_statuses=["resolved"])
        base_ign = ensure_git_baseline(p_ign)
        write_project_review_state(p_ign, charter_source="`.scratch/current`", verdict="PASS", revision_identity=base_ign)
        add_ignore_rule(p_ign, "ignored.txt")
        (p_ign / ".scratch" / "current" / "ignored.txt").write_text("ignored content\n", encoding="utf-8")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_ign)["stage"], "review-stale")

    def test_unrelated_out_of_scope_change_keeps_fresh_acceptance(self) -> None:
        p = self.build_project("PASS")
        (p / "README.md").write_text("# New Title\n", encoding="utf-8")
        _git(p, "add", "-A")
        commit_all(p, "change readme")
        ev = ASK_LIGHT.inspect_project_evidence(p)
        self.assertEqual(ev["stage"], "accepted")

    def test_unresolvable_and_ambiguous_source_revision_fails_closed(self) -> None:
        # unresolvable
        p_unres = self.build_project("PASS")
        (p_unres / ".project-review" / "charter.md").write_text(
            "# Charter\n- Charter revision: 1\n- Source: `.scratch/current/spec.md`\n- Source revision or identity: commit 0123456789abcdef0123456789abcdef01234567\n- Profile: generic\n",
            encoding="utf-8",
        )
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_unres)["stage"], "review-freshness-unknown")

        # ambiguous (two hashes)
        p_amb = self.build_project("PASS")
        (p_amb / ".project-review" / "charter.md").write_text(
            "# Charter\n- Charter revision: 1\n- Source: `.scratch/current/spec.md`\n- Source revision or identity: 1111111111111111111111111111111111111111 2222222222222222222222222222222222222222\n- Profile: generic\n",
            encoding="utf-8",
        )
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_amb)["stage"], "review-freshness-unknown")

    def test_duplicate_charter_source_fails_closed(self) -> None:
        """SPEC §17: Duplicate Charter Source violates producer singleton contract."""
        p = self.build_project("PASS")
        charter = p / ".project-review" / "charter.md"
        charter.write_text(
            "# Charter\n- Charter revision: 1\n- Source: `.scratch/current/spec.md`\n- Source: `.scratch/other/spec.md`\n- Source revision or identity: 1111111111111111111111111111111111111111\n- Profile: generic\n",
            encoding="utf-8",
        )
        ev = ASK_LIGHT.inspect_project_evidence(p)
        self.assertEqual(ev["stage"], "review-ownership-unknown")
        self.assertEqual(ev["review"]["ownership"], "unresolvable")
        self.assertFalse(ev["review"]["accepted"])
        self.assertTrue(any(c.get("ownerSkill") == "project-review" for c in ev.get("hardConstraints", [])))
        val = ASK_LIGHT.validate_recommendation("none", evidence=ev, roots=self.roots, scope="current-workflow")
        self.assertEqual(val["status"], "BLOCKED")

    def test_duplicate_charter_source_revision_fails_closed(self) -> None:
        """SPEC §17: Duplicate Charter Source revision or identity fails closed."""
        p = self.build_project("PASS")
        charter = p / ".project-review" / "charter.md"
        charter.write_text(
            "# Charter\n- Charter revision: 1\n- Source: `.scratch/current/spec.md`\n- Source revision or identity: 1111111111111111111111111111111111111111\n- Source revision or identity: 2222222222222222222222222222222222222222\n- Profile: generic\n",
            encoding="utf-8",
        )
        ev = ASK_LIGHT.inspect_project_evidence(p)
        self.assertEqual(ev["stage"], "review-freshness-unknown")
        self.assertEqual(ev["review"]["freshness"], "unknown")
        val = ASK_LIGHT.validate_recommendation("none", evidence=ev, roots=self.roots, scope="current-workflow")
        self.assertEqual(val["status"], "BLOCKED")


# ---------------------------------------------------------------------------
# Software Baseline Matrix Tests (SPEC §21)
# ---------------------------------------------------------------------------

class SoftwareReviewBaselineMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-soft-mat-")
        self.host_root = Path(self.temp.name) / "host"
        self.host_root.mkdir()
        self.roots = install_host_fixture_skills(self.host_root)
        self._count = 0

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build_software_project(
        self,
        *,
        fixed_point_override: str | None = None,
        scope_override: str | None = "src/",
        final_revision_override: str | None = None,
        omit_fixed_point: bool = False,
        omit_scope: bool = False,
        omit_final_rev: bool = False,
    ) -> tuple[Path, str, str]:
        self._count += 1
        root = Path(self.temp.name) / f"soft-proj-{self._count}"
        write_project_state(root, initialized=True, spec=True)
        write_effort_state(root, "current", spec_status="active", ticket_statuses=["resolved"])
        src = root / "src"
        src.mkdir(parents=True)
        (src / "app.py").write_text("print(1)\n", encoding="utf-8")
        base = ensure_git_baseline(root)

        (src / "app.py").write_text("print(2)\n", encoding="utf-8")
        _git(root, "add", "-A")
        commit_all(root, "candidate commit")
        candidate = _git(root, "rev-parse", "HEAD").stdout.strip()

        fp_val = base if fixed_point_override is None else fixed_point_override
        cand_val = candidate if final_revision_override is None else final_revision_override

        write_project_review_state(
            root,
            reviewed_effort="current",
            verdict="PASS",
            revision_identity=base,
            profile="software",
            fixed_point=None if omit_fixed_point else fp_val,
            implementation_scope=None if omit_scope else scope_override,
            final_revision=None if omit_final_rev else cand_val,
        )
        return root, base, candidate

    def test_valid_software_baseline_accepts(self) -> None:
        p, _, _ = self.build_software_project()
        ev = ASK_LIGHT.inspect_project_evidence(p)
        self.assertEqual(ev["stage"], "accepted")
        self.assertTrue(ev["review"]["accepted"])

    def test_fixed_point_validation_matrix(self) -> None:
        # missing fixed point
        p_miss, _, _ = self.build_software_project(omit_fixed_point=True)
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_miss)["stage"], "review-freshness-unknown")

        # invalid/short SHA
        p_inv, _, _ = self.build_software_project(fixed_point_override="1234abc")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_inv)["stage"], "review-freshness-unknown")

        # unresolvable SHA
        p_unres, _, _ = self.build_software_project(fixed_point_override="0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_unres)["stage"], "review-freshness-unknown")

        # duplicate fixed point
        p_dup, _, _ = self.build_software_project()
        append_durable_field(p_dup / ".project-review" / "charter.md", "- Fixed point: 0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_dup)["stage"], "review-freshness-unknown")

    def test_base_equals_final_revision_fails_closed(self) -> None:
        """SPEC §19: Fixed point == reviewed final revision fails closed."""
        p_eq, b, _ = self.build_software_project(final_revision_override="SAME")
        # Overwrite final revision to equal base
        verdict_text = (p_eq / ".project-review" / "verdict.md").read_text(encoding="utf-8")
        verdict_text = verdict_text.replace("SAME", b)
        (p_eq / ".project-review" / "verdict.md").write_text(verdict_text, encoding="utf-8")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_eq)["stage"], "review-freshness-unknown")

    def test_fixed_point_not_ancestor_fails_closed(self) -> None:
        """SPEC §19: Fixed point is not an ancestor of reviewed final revision fails closed."""
        self._count += 1
        root = Path(self.temp.name) / f"not-ancestor-{self._count}"
        write_project_state(root, initialized=True, spec=True)
        write_effort_state(root, "current", spec_status="active", ticket_statuses=["resolved"])
        src = root / "src"
        src.mkdir(parents=True)
        (src / "app.py").write_text("print(1)\n", encoding="utf-8")
        base = ensure_git_baseline(root)

        # Create branch A for fixed point
        _git(root, "checkout", "-b", "branch-a")
        (src / "app.py").write_text("print('branch A')\n", encoding="utf-8")
        _git(root, "add", "-A")
        commit_all(root, "commit on branch A")
        branch_a_rev = _git(root, "rev-parse", "HEAD").stdout.strip()

        # Create diverged branch B from base
        _git(root, "checkout", base)
        _git(root, "checkout", "-b", "branch-b")
        (src / "app.py").write_text("print('branch B')\n", encoding="utf-8")
        _git(root, "add", "-A")
        commit_all(root, "commit on branch B")
        branch_b_rev = _git(root, "rev-parse", "HEAD").stdout.strip()

        # Review with fixed_point = branch_a_rev and final_revision = branch_b_rev (branch_a is not ancestor of branch_b)
        write_project_review_state(
            root,
            reviewed_effort="current",
            verdict="PASS",
            revision_identity=base,
            profile="software",
            fixed_point=branch_a_rev,
            implementation_scope="src/",
            final_revision=branch_b_rev,
        )
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(root)["stage"], "review-freshness-unknown")

    def test_nested_and_out_of_scope_ignored_drift(self) -> None:
        """SPEC §18: In-scope nested ignored drift stales software review; out-of-scope ignored drift does not."""
        p, _, _ = self.build_software_project()
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "accepted")

        # 1. Out-of-scope ignored file does NOT invalidate review
        doc_dir = p / "doc"
        doc_dir.mkdir(parents=True, exist_ok=True)
        add_ignore_rule(p, "doc/ignored.txt")
        (doc_dir / "ignored.txt").write_text("out-of-scope ignored\n", encoding="utf-8")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "accepted")

        # 2. Nested in-scope ignored file DOES invalidate software review
        nested_dir = p / "src" / "nested" / "sub"
        nested_dir.mkdir(parents=True, exist_ok=True)
        add_ignore_rule(p, "src/nested/sub/ignored.py")
        (nested_dir / "ignored.py").write_text("print('nested ignored')\n", encoding="utf-8")
        ev_stale = ASK_LIGHT.inspect_project_evidence(p)
        self.assertEqual(ev_stale["stage"], "review-stale")
        self.assertEqual(ev_stale["review"]["freshness"], "stale")

    def test_software_current_in_scope_and_out_of_scope_drift(self) -> None:
        """SPEC §20: Current in-scope drift stales software review; out-of-scope drift does not."""
        p, _, _ = self.build_software_project()
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "accepted")

        # Out-of-scope modification
        (p / "notes.txt").write_text("some note\n", encoding="utf-8")
        _git(p, "add", "-A")
        commit_all(p, "out of scope commit")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p)["stage"], "accepted")

        # In-scope modification
        (p / "src" / "app.py").write_text("print('drift')\n", encoding="utf-8")
        _git(p, "add", "-A")
        commit_all(p, "in scope drift commit")
        ev_stale = ASK_LIGHT.inspect_project_evidence(p)
        self.assertEqual(ev_stale["stage"], "review-stale")
        self.assertEqual(ev_stale["review"]["freshness"], "stale")

    def test_implementation_scope_validation_matrix(self) -> None:
        # missing scope
        p_miss, _, _ = self.build_software_project(omit_scope=True)
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_miss)["stage"], "review-freshness-unknown")

        # absolute scope
        p_abs, _, _ = self.build_software_project(scope_override="/src/app.py")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_abs)["stage"], "review-freshness-unknown")

        # path traversal
        p_trav, _, _ = self.build_software_project(scope_override="src/../src/app.py")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_trav)["stage"], "review-freshness-unknown")

        # wildcard / forbidden chars
        p_wild, _, _ = self.build_software_project(scope_override="src/*.py")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_wild)["stage"], "review-freshness-unknown")

        # pathspec magic
        p_spec, _, _ = self.build_software_project(scope_override=":(top)src/")
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(p_spec)["stage"], "review-freshness-unknown")

    def test_empty_in_scope_diff_window_fails_closed(self) -> None:
        # Diff was only in doc/, but scope was src/
        self._count += 1
        root = Path(self.temp.name) / f"empty-diff-{self._count}"
        write_project_state(root, initialized=True, spec=True)
        write_effort_state(root, "current", spec_status="active", ticket_statuses=["resolved"])
        src = root / "src"
        src.mkdir(parents=True)
        (src / "app.py").write_text("print(1)\n", encoding="utf-8")
        (root / "doc.txt").write_text("v1\n", encoding="utf-8")
        base = ensure_git_baseline(root)

        (root / "doc.txt").write_text("v2\n", encoding="utf-8")
        _git(root, "add", "-A")
        commit_all(root, "change doc outside scope")
        candidate = _git(root, "rev-parse", "HEAD").stdout.strip()

        write_project_review_state(
            root,
            reviewed_effort="current",
            verdict="PASS",
            revision_identity=base,
            profile="software",
            fixed_point=base,
            implementation_scope="src/",
            final_revision=candidate,
        )
        self.assertEqual(ASK_LIGHT.inspect_project_evidence(root)["stage"], "review-freshness-unknown")


# ---------------------------------------------------------------------------
# Current-Effort Regression Matrix Tests (SPEC §22)
# ---------------------------------------------------------------------------

class CurrentEffortRegressionMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-effort-mat-")
        self.root = Path(self.temp.name) / "light"
        self.root.mkdir()
        self.roots = install_host_fixture_skills(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_single_active_effort_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            write_effort_state(proj, "effort-1", spec_status="active")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["currentEffort"]["name"], "effort-1")
            self.assertEqual(ev["currentEffort"]["resolution"], "current")

    def test_historical_effort_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            write_effort_state(proj, "effort-active", spec_status="active")
            write_effort_state(proj, "effort-old", spec_status="superseded")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["currentEffort"]["name"], "effort-active")

    def test_multiple_active_efforts_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            write_effort_state(proj, "alpha", spec_status="active")
            write_effort_state(proj, "beta", spec_status="active")
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["stage"], "ambiguous-current-effort")
            self.assertEqual(ev["currentEffort"]["resolution"], "ambiguous")

    def test_explicit_pointer_resolution_and_missing_effort(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            write_effort_state(proj, "alpha", spec_status="active")
            write_effort_state(proj, "beta", spec_status="active")
            # Explicit pointer in docs/agents/light-project.md
            (proj / "docs" / "agents" / "light-project.md").write_text(
                "# Light Project\n- Current effort: alpha\n", encoding="utf-8"
            )
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["currentEffort"]["name"], "alpha")

            # Pointer to missing effort
            (proj / "docs" / "agents" / "light-project.md").write_text(
                "# Light Project\n- Current effort: gamma-missing\n", encoding="utf-8"
            )
            ev_missing = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev_missing["stage"], "ambiguous-current-effort")

    def test_pointer_contradicting_active_effort_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=False)
            write_effort_state(proj, "archived-effort", spec_status="superseded")
            write_effort_state(proj, "active-effort", spec_status="active")
            # Pointer points to superseded effort while active-effort exists
            (proj / "docs" / "agents" / "light-project.md").write_text(
                "# Light Project\n- Current effort: archived-effort\n", encoding="utf-8"
            )
            ev = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev["stage"], "contradictory-current-effort")
            self.assertEqual(ev["currentEffort"]["resolution"], "contradictory")

    def test_review_ownership_historical_and_unresolvable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "project"
            write_project_state(proj, initialized=True, spec=True)
            write_effort_state(proj, "current", spec_status="active", ticket_statuses=["resolved"])
            ensure_git_baseline(proj)

            # Review cites different effort `.scratch/other`
            write_project_review_state(proj, charter_source="`.scratch/other/spec.md`", verdict="PASS")
            ev_hist = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev_hist["review"]["ownership"], "historical")
            self.assertEqual(ev_hist["stage"], "implementation-complete")
            self.assertFalse(ev_hist["review"]["accepted"])

            # Review cites no single effort
            write_project_review_state(proj, charter_source="arbitrary external source", verdict="PASS")
            ev_unres = ASK_LIGHT.inspect_project_evidence(proj)
            self.assertEqual(ev_unres["review"]["ownership"], "unresolvable")
            self.assertEqual(ev_unres["stage"], "review-ownership-unknown")


# ---------------------------------------------------------------------------
# Discovery & Provenance Matrix Tests (SPEC §23)
# ---------------------------------------------------------------------------

class DiscoveryAndProvenanceMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ask-light-disc-mat-")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_root_discovery_from_environment(self) -> None:
        skills_dir = self.root / "env_skills"
        skills_dir.mkdir()
        write_skill(skills_dir, "custom-test-skill")
        os.environ["LIGHT_SKILL_ROOTS"] = json.dumps([{"category": "first-party", "path": str(skills_dir)}])
        try:
            roots = ASK_LIGHT.discover_roots()
            paths = [r["path"] for r in roots]
            self.assertIn(str(skills_dir.resolve()), paths)
        finally:
            del os.environ["LIGHT_SKILL_ROOTS"]

    def test_duplicate_first_party_copy_requires_precedence(self) -> None:
        root1 = self.root / "root1"
        root2 = self.root / "root2"
        root1.mkdir()
        root2.mkdir()
        write_skill(root1, "eli5")
        write_skill(root2, "eli5")
        roots = [{"category": "first-party", "path": str(root1)}, {"category": "first-party", "path": str(root2)}]
        val = ASK_LIGHT.validate_recommendation("eli5", roots=roots, host="codex", scope="standalone")
        self.assertEqual(val["status"], "BLOCKED")
        self.assertIn("multiple available first-party copies", val["reason"])

    def test_third_party_same_name_isolated(self) -> None:
        root1 = self.root / "root1"
        root1.mkdir()
        write_skill(root1, "eli5")
        # Non-first-party category is skipped
        roots = [
            {"category": "first-party", "path": str(root1)},
            {"category": "third-party", "path": "/some/third/party/root"}
        ]
        candidates, gaps, _ = ASK_LIGHT.discover(roots, ASK_LIGHT.load_map(), {"host": "codex", "available": [], "unavailable": [], "readablePaths": []})
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["name"], "eli5")

    def test_missing_and_unclosed_frontmatter_unavailable(self) -> None:
        root = self.root / "bad_skills"
        root.mkdir()
        bad_pkg = root / "eli5"
        bad_pkg.mkdir()
        (bad_pkg / "SKILL.md").write_text("---\nname: eli5\nno closing fence\n", encoding="utf-8")
        roots = [{"category": "first-party", "path": str(root)}]
        candidates, gaps, _ = ASK_LIGHT.discover(roots, ASK_LIGHT.load_map(), {"host": "codex", "available": [], "unavailable": [], "readablePaths": []})
        self.assertEqual(candidates[0]["metadataStatus"], "unavailable")
        self.assertIn("not closed", candidates[0]["metadataError"])

    def test_local_pointer_integrity(self) -> None:
        root = self.root / "ptr_skills"
        root.mkdir()
        pkg = root / "eli5"
        pkg.mkdir()
        # SKILL.md linking to nonexistent reference
        (pkg / "SKILL.md").write_text("---\nname: eli5\ndescription: test\n---\n\n[missing](references/missing.md)\n", encoding="utf-8")
        roots = [{"category": "first-party", "path": str(root)}]
        val = ASK_LIGHT.validate_recommendation("eli5", roots=roots, host="codex", scope="standalone")
        self.assertEqual(val["status"], "BLOCKED")
        self.assertIn("body/reference unreadable", val["reason"])

    def test_source_checkout_root_discovery(self) -> None:
        """SPEC §21: Discover roots from source checkout containing skills/ask-light and skills/socratic."""
        repo_root = self.root / "repo"
        skills_dir = repo_root / "skills"
        write_skill(skills_dir, "ask-light")
        write_skill(skills_dir, "socratic")
        sub_dir = repo_root / "nested" / "sub"
        sub_dir.mkdir(parents=True)
        roots = ASK_LIGHT.discover_roots(cwd=sub_dir)
        paths = [r["path"] for r in roots]
        self.assertIn(str(skills_dir.resolve()), paths)

    def test_installed_host_root_discovery(self) -> None:
        """SPEC §21: Discover roots from installed host CODEX_HOME."""
        codex_home = self.root / "codex_home"
        skills_dir = codex_home / "skills"
        write_skill(skills_dir, "ask-light")
        old_env = os.environ.get("CODEX_HOME")
        os.environ["CODEX_HOME"] = str(codex_home)
        try:
            roots = ASK_LIGHT.discover_roots()
            paths = [r["path"] for r in roots]
            self.assertIn(str(skills_dir.resolve()), paths)
        finally:
            if old_env is None:
                del os.environ["CODEX_HOME"]
            else:
                os.environ["CODEX_HOME"] = old_env


# ---------------------------------------------------------------------------
# Navigation Mode Tests
# ---------------------------------------------------------------------------

class NavigationModeTest(unittest.TestCase):
    def test_natural_language_family_navigation(self) -> None:
        skill_map = ASK_LIGHT.load_map()
        res_proj = ASK_LIGHT.navigate_result(skill_map, "What project skills do I have?", host="codex")
        self.assertEqual(res_proj["status"], "RECOMMEND")
        self.assertEqual(res_proj["family"], "project")
        self.assertTrue(len(res_proj["skills"]) >= 4)

        res_comp = ASK_LIGHT.navigate_result(skill_map, "What is the difference between clarify and project-clarify?", host="codex")
        self.assertEqual(res_comp["status"], "RECOMMEND")
        self.assertEqual(res_comp["comparison"]["left"], "clarify")
        self.assertEqual(res_comp["comparison"]["right"], "project-clarify")


if __name__ == "__main__":
    unittest.main(verbosity=2)
