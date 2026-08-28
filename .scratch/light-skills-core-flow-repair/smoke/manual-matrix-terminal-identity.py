#!/usr/bin/env python3
"""Manual smoke test matrix for SPEC: Final Terminal Transaction Identity Repair.
Covers all 24 scenarios specified in SPEC §21.
"""

from __future__ import annotations

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

ROOTS = [{"category": "first-party", "path": str(Path(__file__).resolve().parents[3] / "skills")}]

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "smoke-fixture",
    "GIT_AUTHOR_EMAIL": "smoke-fixture@example.com",
    "GIT_COMMITTER_NAME": "smoke-fixture",
    "GIT_COMMITTER_EMAIL": "smoke-fixture@example.com",
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
        root, "-c", "commit.gpgsign=false", "-c", "user.name=smoke-fixture",
        "-c", "user.email=smoke-fixture@example.com",
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


def build_base(root: Path, effort: str = "core-repair") -> tuple[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    agents = root / "docs" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / "light-project.md").write_text(
        "<!-- light-project:managed:start -->\n# Light Project Configuration\n- Goal: Test\n"
        "- Outputs: tests\n- Relevant Skills: project-review\n<!-- light-project:managed:end -->\n",
        encoding="utf-8",
    )
    e_dir = root / ".scratch" / effort
    e_dir.mkdir(parents=True, exist_ok=True)
    (e_dir / "spec.md").write_text("# SPEC\nStatus: active\n", encoding="utf-8")
    issues = e_dir / "issues"
    issues.mkdir(parents=True, exist_ok=True)
    (issues / "01.md").write_text("- Status: resolved\n", encoding="utf-8")

    src = root / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "app.py").write_text("print('base')\n", encoding="utf-8")
    base_sha = ensure_git_baseline(root)

    r_dir = root / ".project-review"
    r_dir.mkdir(parents=True, exist_ok=True)
    return base_sha, r_dir


def route(root: Path) -> dict:
    context = {"projectRoot": str(root), "invocationControl": "explicit-only", "availability": "codex"}
    return ASK_LIGHT.route(ROOTS, context, host="codex", mode="next")


def run_smoke():
    results = []

    def record(num: int, name: str, res: dict, exp_stage: str):
        stage = res.get("projectStage", "")
        skill = res.get("skill", "")
        status = res.get("status", "")
        ok = (stage == exp_stage)
        results.append((num, name, stage, skill, status, exp_stage, ok))

    with tempfile.TemporaryDirectory() as td:
        t_root = Path(td)

        # 1. coherent PASS same round -> accepted
        p1 = t_root / "p1"
        b1, rd1 = build_base(p1)
        (rd1 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b1}\n", encoding="utf-8")
        (rd1 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd1 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n", encoding="utf-8")
        record(1, "coherent PASS same round", route(p1), "accepted")

        # 2. PASS State round2 + PASS Verdict round1 -> acceptance-unknown
        p2 = t_root / "p2"
        b2, rd2 = build_base(p2)
        (rd2 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b2}\n", encoding="utf-8")
        (rd2 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n", encoding="utf-8")
        (rd2 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n", encoding="utf-8")
        record(2, "PASS State round2 + PASS Verdict round1", route(p2), "acceptance-unknown")

        # 3. FAIL State round2 + FAIL Verdict round1 -> acceptance-unknown
        p3 = t_root / "p3"
        b3, rd3 = build_base(p3)
        (rd3 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b3}\n", encoding="utf-8")
        (rd3 / "state.md").write_text("# State\n- Status: FAIL\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n", encoding="utf-8")
        (rd3 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **FAIL**\n- Round: round-01 (final)\n", encoding="utf-8")
        record(3, "FAIL State round2 + FAIL Verdict round1", route(p3), "acceptance-unknown")

        # 4. BLOCKED State round2 + BLOCKED Verdict round1 -> acceptance-unknown
        p4 = t_root / "p4"
        b4, rd4 = build_base(p4)
        (rd4 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b4}\n", encoding="utf-8")
        (rd4 / "state.md").write_text("# State\n- Status: BLOCKED\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n", encoding="utf-8")
        (rd4 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **BLOCKED**\n- Round: round-01 (final)\n", encoding="utf-8")
        record(4, "BLOCKED State round2 + BLOCKED Verdict round1", route(p4), "acceptance-unknown")

        # 5. missing State Round -> review-state-unknown
        p5 = t_root / "p5"
        b5, rd5 = build_base(p5)
        (rd5 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b5}\n", encoding="utf-8")
        (rd5 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n", encoding="utf-8")
        (rd5 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n", encoding="utf-8")
        record(5, "missing State Round", route(p5), "review-state-unknown")

        # 6. duplicate State Round -> review-state-unknown
        p6 = t_root / "p6"
        b6, rd6 = build_base(p6)
        (rd6 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b6}\n", encoding="utf-8")
        (rd6 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n- Round: 2\n", encoding="utf-8")
        (rd6 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n", encoding="utf-8")
        record(6, "duplicate State Round", route(p6), "review-state-unknown")

        # 7. missing Verdict Round -> acceptance-unknown
        p7 = t_root / "p7"
        b7, rd7 = build_base(p7)
        (rd7 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b7}\n", encoding="utf-8")
        (rd7 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd7 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n", encoding="utf-8")
        record(7, "missing Verdict Round", route(p7), "acceptance-unknown")

        # 8. duplicate Verdict Round -> acceptance-unknown
        p8 = t_root / "p8"
        b8, rd8 = build_base(p8)
        (rd8 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b8}\n", encoding="utf-8")
        (rd8 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd8 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n- Round: 2\n", encoding="utf-8")
        record(8, "duplicate Verdict Round", route(p8), "acceptance-unknown")

        # 9. missing Verdict Charter revision -> acceptance-unknown
        p9 = t_root / "p9"
        b9, rd9 = build_base(p9)
        (rd9 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b9}\n", encoding="utf-8")
        (rd9 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd9 / "verdict.md").write_text("# Verdict\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n", encoding="utf-8")
        record(9, "missing Verdict Charter revision", route(p9), "acceptance-unknown")

        # 10. missing Verdict Profile -> acceptance-unknown
        p10 = t_root / "p10"
        b10, rd10 = build_base(p10)
        (rd10 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b10}\n", encoding="utf-8")
        (rd10 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd10 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Verdict: **PASS**\n- Round: 1\n", encoding="utf-8")
        record(10, "missing Verdict Profile", route(p10), "acceptance-unknown")

        # 11. Verdict revision mismatch -> acceptance-unknown
        p11 = t_root / "p11"
        b11, rd11 = build_base(p11)
        (rd11 / "charter.md").write_text(f"# Charter\n- Charter revision: 2\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b11}\n", encoding="utf-8")
        (rd11 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 2\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd11 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n", encoding="utf-8")
        record(11, "Verdict revision mismatch", route(p11), "acceptance-unknown")

        # 12. Verdict profile mismatch -> acceptance-unknown
        p12 = t_root / "p12"
        b12, rd12 = build_base(p12)
        (rd12 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: software\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b12}\n- Fixed point: {b12}\n- Implementation scope: src/app.py\n", encoding="utf-8")
        (rd12 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 1\n", encoding="utf-8")
        (rd12 / "verdict.md").write_text(f"# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: 1\n", encoding="utf-8")
        record(12, "Verdict profile mismatch", route(p12), "acceptance-unknown")

        # 13. State FAIL + Verdict FAIL/BLOCKED -> acceptance-unknown
        p13 = t_root / "p13"
        b13, rd13 = build_base(p13)
        (rd13 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b13}\n", encoding="utf-8")
        (rd13 / "state.md").write_text("# State\n- Status: FAIL\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd13 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: FAIL\n- Verdict: BLOCKED\n- Round: 1\n", encoding="utf-8")
        record(13, "State FAIL + Verdict FAIL/BLOCKED", route(p13), "acceptance-unknown")

        # 14. State BLOCKED + Verdict BLOCKED/FAIL -> acceptance-unknown
        p14 = t_root / "p14"
        b14, rd14 = build_base(p14)
        (rd14 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b14}\n", encoding="utf-8")
        (rd14 / "state.md").write_text("# State\n- Status: BLOCKED\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd14 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: BLOCKED\n- Verdict: FAIL\n- Round: 1\n", encoding="utf-8")
        record(14, "State BLOCKED + Verdict BLOCKED/FAIL", route(p14), "acceptance-unknown")

        # 15. Round1 PASS -> accepted
        p15 = t_root / "p15"
        b15, rd15 = build_base(p15)
        (rd15 / "charter.md").write_text(f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n- Source revision or identity: commit {b15}\n", encoding="utf-8")
        (rd15 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd15 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n", encoding="utf-8")
        record(15, "Round1 PASS", route(p15), "accepted")

        # 16. reopen Round2 READY + old PASS -> project-review
        (rd15 / "state.md").write_text("# State\n- Status: READY\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n", encoding="utf-8")
        record(16, "reopen Round2 READY + old PASS", route(p15), "project-review")

        # 17. Round2 EVALUATE + old PASS -> project-review
        (rd15 / "state.md").write_text("# State\n- Status: EVALUATE\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n", encoding="utf-8")
        record(17, "Round2 EVALUATE + old PASS", route(p15), "project-review")

        # 18. Round2 PASS + old Round1 PASS -> acceptance-unknown
        (rd15 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 2\n", encoding="utf-8")
        record(18, "Round2 PASS + old Round1 PASS", route(p15), "acceptance-unknown")

        # 19. fresh Round2 PASS Verdict -> accepted
        (rd15 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-02 (final)\n", encoding="utf-8")
        record(19, "fresh Round2 PASS Verdict", route(p15), "accepted")

        # 20. C1->C2 current-round PASS -> accepted
        p20 = t_root / "p20"
        b20, rd20 = build_base(p20)
        # commit C1
        (p20 / "src" / "app.py").write_text("print('C1')\n", encoding="utf-8")
        _git(p20, "add", "-A")
        commit_all(p20, "commit C1")
        # commit C2
        (p20 / "src" / "app.py").write_text("print('C2')\n", encoding="utf-8")
        _git(p20, "add", "-A")
        commit_all(p20, "commit C2")
        c2_sha = _git(p20, "rev-parse", "HEAD").stdout.strip()
        (rd20 / "charter.md").write_text(
            f"# Charter\n- Charter revision: 1\n- Profile: software\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n"
            f"- Source revision or identity: commit {b20}\n- Fixed point: {b20}\n- Implementation scope: src/app.py\n",
            encoding="utf-8",
        )
        (rd20 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 2\n", encoding="utf-8")
        (rd20 / "verdict.md").write_text(
            f"# Verdict\n- Charter revision: 1\n- Profile: software\n- Verdict: **PASS**\n- Reviewed implementation revision: {c2_sha}\n- Round: round-02 (final)\n",
            encoding="utf-8",
        )
        record(20, "C1->C2 current-round PASS", route(p20), "accepted")

        # 21. post-C2 in-scope drift -> review-stale
        (p20 / "src" / "app.py").write_text("print('C2 drift')\n", encoding="utf-8")
        record(21, "post-C2 in-scope drift", route(p20), "review-stale")

        # 22. out-of-scope README -> accepted
        # restore src/app.py
        _git(p20, "checkout", "--", "src/app.py")
        (p20 / "README.md").write_text("# Updated README\n", encoding="utf-8")
        record(22, "out-of-scope README", route(p20), "accepted")

        # 23. ignored in-scope file -> review-stale
        p23 = t_root / "p23"
        b23, rd23 = build_base(p23)
        (p23 / "src" / "app.py").write_text("print('C2')\n", encoding="utf-8")
        _git(p23, "add", "-A")
        commit_all(p23, "commit C2")
        c2_23 = _git(p23, "rev-parse", "HEAD").stdout.strip()
        (rd23 / "charter.md").write_text(
            f"# Charter\n- Charter revision: 1\n- Profile: software\n- Source: approved effort SPEC — `.scratch/core-repair/spec.md`\n"
            f"- Source revision or identity: commit {b23}\n- Fixed point: {b23}\n- Implementation scope: src/\n",
            encoding="utf-8",
        )
        (rd23 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: software\n- Round: 1\n", encoding="utf-8")
        (rd23 / "verdict.md").write_text(
            f"# Verdict\n- Charter revision: 1\n- Profile: software\n- Verdict: **PASS**\n- Reviewed implementation revision: {c2_23}\n- Round: round-01 (final)\n",
            encoding="utf-8",
        )
        (p23 / ".gitignore").write_text("src/temp.py\n", encoding="utf-8")
        (p23 / "src" / "temp.py").write_text("# ignored in-scope\n", encoding="utf-8")
        record(23, "ignored in-scope file", route(p23), "review-stale")

        # 24. ignored Source child -> review-stale
        p24 = t_root / "p24"
        b24, rd24 = build_base(p24)
        (rd24 / "charter.md").write_text(
            f"# Charter\n- Charter revision: 1\n- Profile: generic\n- Source: approved effort directory — `.scratch/core-repair`\n"
            f"- Source revision or identity: commit {b24}\n",
            encoding="utf-8",
        )
        (rd24 / "state.md").write_text("# State\n- Status: PASS\n- Charter revision: 1\n- Profile: generic\n- Round: 1\n", encoding="utf-8")
        (rd24 / "verdict.md").write_text("# Verdict\n- Charter revision: 1\n- Profile: generic\n- Verdict: **PASS**\n- Round: round-01 (final)\n", encoding="utf-8")
        # Now add ignored file in .scratch/core-repair
        (p24 / ".gitignore").write_text(".scratch/core-repair/notes.tmp\n", encoding="utf-8")
        (p24 / ".scratch" / "core-repair" / "notes.tmp").write_text("temporary note\n", encoding="utf-8")
        record(24, "ignored Source child", route(p24), "review-stale")

    # Print summary table
    print(f"{'#':<3} | {'Scenario':<46} | {'Observed Stage':<22} | {'Expected Stage':<22} | {'Match'}")
    print("-" * 105)
    all_ok = True
    for num, name, stage, skill, status, exp_stage, ok in results:
        status_str = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"{num:<3} | {name:<46} | {stage:<22} | {exp_stage:<22} | {status_str}")
    print("-" * 105)
    print(f"Overall Result: {'ALL 24 PASSED' if all_ok else 'SOME FAILED'}")
    return all_ok


if __name__ == "__main__":
    import sys
    success = run_smoke()
    sys.exit(0 if success else 1)
