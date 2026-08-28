#!/usr/bin/env python3
"""Pre-fix reproductions for SPEC: Final Terminal Transaction Identity Repair
Baseline: d414a3b
"""

import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

ASK_LIGHT_PATH = Path(__file__).resolve().parents[3] / "skills" / "ask-light" / "scripts" / "ask_light.py"
SPEC = importlib.util.spec_from_file_location("ask_light", ASK_LIGHT_PATH)
assert SPEC and SPEC.loader
ASK_LIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASK_LIGHT)
inspect_project_state = ASK_LIGHT.inspect_project_state

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


def setup_base_repo(root: Path) -> tuple[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    agents = root / "docs" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    content = "<!-- light-project:managed:start -->\n# Light Project Configuration\n- Goal: Build a parser\n- Outputs: parser, tests\n- Relevant Skills: project-spec, project-tickets, implement, project-review\n<!-- light-project:managed:end -->\n"
    (agents / "light-project.md").write_text(content, encoding="utf-8")
    
    effort = root / ".scratch" / "test-effort"
    effort.mkdir(parents=True, exist_ok=True)
    (effort / "spec.md").write_text("# SPEC\nStatus: active\n", encoding="utf-8")
    issues = effort / "issues"
    issues.mkdir(parents=True, exist_ok=True)
    (issues / "01.md").write_text("- Status: resolved\n", encoding="utf-8")
    
    src = root / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.py").write_text("print(1)\n", encoding="utf-8")
    base_sha = ensure_git_baseline(root)
    
    rdir = root / ".project-review"
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / "charter.md").write_text(
        f"# Acceptance Charter\n\n"
        f"## Revision\n- Charter revision: 1\n- Supersedes: none\n\n"
        f"## Acceptance baseline\n- Source: approved effort SPEC — `.scratch/test-effort/spec.md`\n"
        f"- Source revision or identity: commit {base_sha}\n- Approval state: approved\n\n"
        f"## Review Profile\n- Profile: generic\n",
        encoding="utf-8",
    )
    return base_sha, rdir


def run_repro():
    print("=== Running Pre-Fix Reproductions against d414a3b ===")
    
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        base_sha, rdir = setup_base_repo(root)
        
        # A — Round mismatch
        (rdir / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n",
            encoding="utf-8",
        )
        res_a = inspect_project_state(root)
        print(f"Repro A (Round mismatch): stage={res_a['stage']} (expected post-fix: acceptance-unknown)")

        # B — missing State Round
        (rdir / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n",
            encoding="utf-8",
        )
        res_b = inspect_project_state(root)
        print(f"Repro B (missing State Round): stage={res_b['stage']} (expected post-fix: review-state-unknown)")

        # C — duplicate State Round
        (rdir / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n- Round: 2\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n",
            encoding="utf-8",
        )
        res_c = inspect_project_state(root)
        print(f"Repro C (duplicate State Round): stage={res_c['stage']} (expected post-fix: review-state-unknown)")

        # D — missing Verdict Round
        (rdir / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n",
            encoding="utf-8",
        )
        res_d = inspect_project_state(root)
        print(f"Repro D (missing Verdict Round): stage={res_d['stage']} (expected post-fix: acceptance-unknown)")

        # E — missing Verdict Charter revision
        (rdir / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n",
            encoding="utf-8",
        )
        res_e = inspect_project_state(root)
        print(f"Repro E (missing Verdict Charter revision): stage={res_e['stage']} (expected post-fix: acceptance-unknown)")

        # F — missing Verdict Profile
        (rdir / "state.md").write_text(
            "# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Verdict: **PASS**\n- Round: 1\n",
            encoding="utf-8",
        )
        res_f = inspect_project_state(root)
        print(f"Repro F (missing Verdict Profile): stage={res_f['stage']} (expected post-fix: acceptance-unknown)")

        # G — terminal semantic conflict (FAIL + BLOCKED)
        (rdir / "state.md").write_text(
            "# State\n- Status: FAIL\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: FAIL\n- Verdict: BLOCKED\n- Round: 1\n",
            encoding="utf-8",
        )
        res_g1 = inspect_project_state(root)
        print(f"Repro G1 (FAIL State, Verdict FAIL+BLOCKED): stage={res_g1['stage']} (expected post-fix: acceptance-unknown)")

        (rdir / "state.md").write_text(
            "# State\n- Status: BLOCKED\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n",
            encoding="utf-8",
        )
        (rdir / "verdict.md").write_text(
            "# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: BLOCKED\n- Verdict: FAIL\n- Round: 1\n",
            encoding="utf-8",
        )
        res_g2 = inspect_project_state(root)
        print(f"Repro G2 (BLOCKED State, Verdict BLOCKED+FAIL): stage={res_g2['stage']} (expected post-fix: acceptance-unknown)")


if __name__ == "__main__":
    run_repro()
