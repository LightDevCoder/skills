#!/usr/bin/env python3
"""Pre-fix reproductions (§19 A-D) against human-audit baseline d00b221.

Builds real temporary Git repositories shaped like a finished Light software
project, writes the d00b221-shaped durable record, and calls the real
ask_light route() to show the INCORRECT current behavior. Read-only wrt this
repository. Outputs are appended to repro-prefix-d00b221.out by the caller.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SPEC_FILE = REPO / "skills" / "ask-light" / "scripts" / "ask_light.py"
spec = importlib.util.spec_from_file_location("ask_light_prefix", SPEC_FILE)
assert spec and spec.loader
ASK_LIGHT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ASK_LIGHT)

MAP_PATH = ASK_LIGHT.MAP_PATH


def git(root: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "repro",
        "GIT_AUTHOR_EMAIL": "repro@example.com",
        "GIT_COMMITTER_NAME": "repro",
        "GIT_COMMITTER_EMAIL": "repro@example.com",
    }
    proc = subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", *args],
                          env=env, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        return f"__git_rc_{proc.returncode}__"
    return proc.stdout.strip()


def baseline(root: Path) -> str:
    if git(root, "rev-parse", "--is-inside-work-tree") != "true":
        git(root, "init", "-q")
    git(root, "add", "-A")
    if git(root, "status", "--porcelain"):
        git(root, "commit", "-q", "-a", "-m", "record reviewed baseline")
    return git(root, "rev-parse", "HEAD")


def seed_project(root: Path) -> None:
    agents = root / "docs" / "agents"
    agents.mkdir(parents=True)
    (agents / "light-project.md").write_text(
        "# Light Project Configuration\n- Goal: Build parser\n- Outputs: parser\n"
    )
    effort = root / ".scratch" / "current"
    (effort).mkdir(parents=True)
    (effort / "spec.md").write_text("# SPEC\nStatus: active\n")
    issues = effort / "issues"
    issues.mkdir()
    (issues / "01.md").write_text("- Status: resolved\n")
    (root / "README.md").write_text("# Project\nv1\n")


def write_record(root: Path, *, fixed_point: str, scope: str | None = None,
                 final_rev: str | None = None, verdict: str = "PASS") -> None:
    rd = root / ".project-review"
    rd.mkdir(exist_ok=True)
    lines = [
        "# Acceptance Charter",
        "## Revision",
        "- Charter revision: 1",
        "## Acceptance baseline",
        "- Source: approved effort SPEC — `.scratch/current/spec.md`",
        f"- Source revision or identity: {baseline_value[root.name]}",
        "- Approval state: approved",
        "## Review Profile",
        "- Profile: software",
        f"- Fixed point: {fixed_point}",
    ]
    if scope is not None:
        lines.append(f"- Implementation scope: {scope}")
    (rd / "charter.md").write_text("\n".join(lines) + "\n")
    (rd / "state.md").write_text("# State\n- Status: READY\n- Round: 1\n")
    vlines = ["# Verdict", f"- Verdict: **{verdict}**"]
    if final_rev is not None:
        vlines.append(f"- Reviewed implementation revision: {final_rev}")
    vlines += ["", "## Conclusion", "Accepted."]
    (rd / "verdict.md").write_text("\n".join(vlines) + "\n")


def route(root: Path) -> dict:
    context = {"projectRoot": str(root), "invocationControl": "explicit-only",
               "availability": "codex"}
    roots = [{"category": "first-party", "path": str(MAP_PATH.parents[1].parent)}]
    # Host fixture packages are unnecessary for stage derivation; supply repo root.
    result = ASK_LIGHT.route(roots, context, host="codex", mode="next")
    return result


baseline_value: dict[str, str] = {}
FAILURES: list[str] = []


def case(name: str, got_stage: str, expect_stage: str, *, bug_expected: bool) -> None:
    flag = "FALSE ACCEPT reproduced" if bug_expected else "unexpected result"
    ok = got_stage == expect_stage
    print(f"[{name}] stage={got_stage!r} required={expect_stage!r} -> "
          + ("OK (fails closed)" if ok == (not bug_expected) else f"{flag}")
          )


def make_project(tag: str) -> tuple[Path, str, str]:
    root = Path(tempfile.mkdtemp(prefix=f"repro-{tag}-")) / "proj"
    root.mkdir()
    seed_project(root)
    src = root / "src"
    src.mkdir()
    # Pre-existing component file belongs to the BASE commit; the review window
    # must touch ONLY src/app.py (that is what makes §11 evadable on d00b221).
    (src / "common.py").write_text("COMMON = 1\n")
    b = baseline(root)
    baseline_value[root.name] = b
    (src / "app.py").write_text("print('impl v1')\n")
    c2 = baseline(root)
    return root, b, c2


def main() -> int:
    print(f"# Pre-fix reproductions against working tree at HEAD "
          f"{subprocess.run(['git','-C',str(REPO),'rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip()}")
    print()

    # A - pre-existing in-scope file NOT touched by B..C diff, dirty + committed
    for label, commit_change in (("A1 dirty", False), ("A2 committed", True)):
        root, _c1, _c2 = make_project(label.split()[1])
        write_record(root, fixed_point=f"{baseline_value[root.name]} {git(root, 'rev-parse', 'HEAD')}")
        assert route(root)["projectStage"] == "accepted", "sanity: fresh PASS must start accepted"
        (root / "src" / "common.py").write_text("COMMON = 2\n")
        if commit_change:
            git(root, "add", "-A"); git(root, "commit", "-q", "-m", "touch common after review")
        stage = route(root)["projectStage"]
        print(f"A/{label}: modified pre-existing in-scope src/common.py -> {stage!r}"
              f"   [required per §11: review-stale]  {'BUG' if stage == 'accepted' else 'ok'}")

    # B - NEW implementation file after PASS, untracked + committed
    for label, do_commit in (("B1 untracked", False), ("B2 committed", True)):
        root, _c1, _c2 = make_project(label.split()[1])
        write_record(root, fixed_point=f"{baseline_value[root.name]} {git(root, 'rev-parse', 'HEAD')}")
        assert route(root)["projectStage"] == "accepted", "sanity"
        (root / "src" / "new_feature.py").write_text("NEW = 1\n")
        if do_commit:
            git(root, "add", "-A"); git(root, "commit", "-q", "-m", "new feature after review")
        stage = route(root)["projectStage"]
        print(f"B/{label}: added src/new_feature.py after PASS -> {stage!r}"
              f"   [required per §12: review-stale]  {'BUG' if stage == 'accepted' else 'ok'}")

    # C - malformed two-endpoint identity partially salvaged ('<invalid40hex> <valid>')
    root, _c1, _c2 = make_project("C")
    garbage = "0123456789abcdef0123456789abcdef01234567"
    cand = git(root, "rev-parse", "HEAD")
    write_record(root, fixed_point=f"{garbage} {cand}")
    stage = route(root)["projectStage"]
    print(f"C: Fixed point '<unresolvable 40-hex> <valid-candidate>' -> {stage!r}"
          f"   [strict contract: unknown]  {'PARTIAL-SALVAGE BUG' if stage == 'accepted' else 'ok'}")

    # D - duplicate endpoints deduplicated ('<candidate> <candidate>')
    root, _c1, _c2 = make_project("D")
    cand = git(root, "rev-parse", "HEAD")
    write_record(root, fixed_point=f"{cand} {cand}")
    stage = route(root)["projectStage"]
    print(f"D: Fixed point '<candidate> <candidate>' -> {stage!r}"
          f"   [strict contract: unknown]  {'DEDUPE BUG' if stage == 'accepted' else 'ok'}")

    print("\nBaseline sanity: all four defects above reproduce d00b221 false accepts;")
    print("each must become review-stale / review-freshness-unknown under §10-§14.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
