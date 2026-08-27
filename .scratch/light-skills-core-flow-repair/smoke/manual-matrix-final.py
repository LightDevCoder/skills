#!/usr/bin/env python3
"""Manual smoke matrix (§26) — real temporary Git repositories through the REAL
ask_light route() entry point. Every case prints REQUIRED vs OBSERVED stage.
Read-only wrt this repository."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("ask_light_smoke", REPO / "skills" / "ask-light" / "scripts" / "ask_light.py")
assert spec and spec.loader
ASK_LIGHT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ASK_LIGHT)
ROOTS = [{"category": "first-party", "path": str(REPO / "skills")}]

ENV = {**os.environ,
       "GIT_AUTHOR_NAME": "smoke", "GIT_AUTHOR_EMAIL": "smoke@example.com",
       "GIT_COMMITTER_NAME": "smoke", "GIT_COMMITTER_EMAIL": "smoke@example.com"}


def git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", *args],
                       env=ENV, capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return f"__rc{p.returncode}__"
    return p.stdout.strip()


def commit_all(root: Path, msg: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


def head(root: Path) -> str:
    return git(root, "rev-parse", "HEAD")


def new_project(tag: str) -> Path:
    root = Path(tempfile.mkdtemp(prefix=f"mx-{tag}-")) / "proj"
    root.mkdir()
    agents = root / "docs" / "agents"; agents.mkdir(parents=True)
    (agents / "light-project.md").write_text("# Light Project Configuration\n- Goal: parser\n- Outputs: parser\n")
    effort = root / ".scratch" / "current"; effort.mkdir(parents=True)
    (effort / "spec.md").write_text("# SPEC\nStatus: active\n")
    (effort / "issues").mkdir()
    (effort / "issues" / "01.md").write_text("- Status: resolved\n")
    (root / "README.md").write_text("# Project\nv1\n")
    src = root / "src"; src.mkdir()
    (src / "common.py").write_text("COMMON = 1\n")  # pre-existing component member at base
    return root


def freeze_base(root: Path) -> str:
    if git(root, "rev-parse", "--is-inside-work-tree") != "true":
        git(root, "init", "-q")
    commit_all(root, "baseline")
    return head(root)


def write_impl(root: Path) -> str:
    (root / "src" / "app.py").write_text("print('impl v1')\n")
    commit_all(root, "implement feature")
    return head(root)


def record(root: Path, base: str, cand: str, *, fp: str | None, scope: str | None,
           final: str | None, verdict: str = "PASS",
           source_dir: bool = False) -> None:
    rd = root / ".project-review"; rd.mkdir(exist_ok=True)
    src_line = "`" + ".scratch/current`" if source_dir else ("approved effort SPEC — `.scratch/current/spec.md`")
    lines = ["# Acceptance Charter", "## Revision", "- Charter revision: 1",
             "## Acceptance baseline", f"- Source: {src_line}",
             f"- Source revision or identity: {base}", "- Approval state: approved",
             "## Review Profile", "- Profile: software"]
    if fp is not None:
        lines.append(f"- Fixed point: {fp}")
    if scope is not None:
        lines.append(f"- Implementation scope: {scope}")
    (rd / "charter.md").write_text("\n".join(lines) + "\n")
    (rd / "state.md").write_text("# State\n- Status: READY\n- Round: 1\n")
    vlines = ["# Verdict", f"- Verdict: **{verdict}**"]
    if final is not None:
        vlines.append(f"- Reviewed implementation revision: {final}")
    vlines += ["", "## Conclusion", "Recorded."]
    (rd / "verdict.md").write_text("\n".join(vlines) + "\n")


RESULTS: list[tuple[str, str, str]] = []


def check(no: int, label: str, required: str, project: Path) -> None:
    context = {"projectRoot": str(project), "invocationControl": "explicit-only", "availability": "codex"}
    observed = ASK_LIGHT.route(ROOTS, context, host="codex", mode="next")["projectStage"]
    ok = "OK" if observed == required else "**MISMATCH**"
    RESULTS.append((f"{no:02d}", label, ""))
    print(f"{no:02d}. {label:<58} required={required:<24} observed={observed:<24} {ok}")


GARBAGE = "0f1e2d3c4b5a9876543210fedcba9876543210ab"


def standard_fixture(tag: str, scope: str = "src/") -> tuple[Path, str, str]:
    p = new_project(tag)
    b = freeze_base(p)
    c = write_impl(p)
    record(p, b, c, fp=b, scope=scope, final=c)
    return p, b, c


def main() -> None:
    # 1 fresh software PASS
    p, _b, _c = standard_fixture("fresh")
    check(1, "fresh software PASS", "accepted", p)

    # 2/3 changed-path drift dirty & committed
    for i, do_commit in ((2, False), (3, True)):
        p, _b, _c = standard_fixture(f"cp{i}")
        (p / "src/app.py").write_text("print('v2')\n")
        if do_commit:
            commit_all(p, "post pass change")
        check(i, f"changed-path drift ({'committed' if do_commit else 'dirty'})", "review-stale", p)

    # 4/5 pre-existing in-scope file untouched by B..C diff
    for i, do_commit in ((4, False), (5, True)):
        p, _b, _c = standard_fixture(f"pre{i}")
        (p / "src/common.py").write_text("COMMON = 2\n")
        if do_commit:
            commit_all(p, "touch common")
        check(i, f"pre-existing in-scope file ({'committed' if do_commit else 'dirty'})", "review-stale", p)

    # 6 new in-scope file untracked (+6b staged)
    p, _b, _c = standard_fixture("new-untracked")
    (p / "src/new_feature.py").write_text("NEW = 1\n")
    check(6, "new untracked in-scope implementation file", "review-stale", p)

    p, _b, _c = standard_fixture("new-staged")
    (p / "src/staged_feature.py").write_text("S = 1\n")
    git(p, "add", "-A")
    check(6, "new STAGED in-scope implementation file", "review-stale", p)

    # 7 committed new in-scope file
    p, _b, _c = standard_fixture("new-committed")
    (p / "src/new_feature.py").write_text("NEW = 1\n")
    commit_all(p, "new impl file")
    check(7, "committed new in-scope implementation file", "review-stale", p)

    # 8 in-scope deletion
    p, _b, _c = standard_fixture("del")
    (p / "src/app.py").unlink()
    check(8, "in-scope deletion (dirty)", "review-stale", p)

    # 9/10 outside-scope changes
    p, _b, _c = standard_fixture("readme-dirty")
    (p / "README.md").write_text("# v2 docs\n")
    check(9, "dirty README outside scope", "accepted", p)

    p, _b, _c = standard_fixture("readme-committed")
    (p / "README.md").write_text("# v2 docs\n")
    commit_all(p, "docs only")
    check(10, "committed README outside scope", "accepted", p)

    # 11 whole-repo scope catches README (no hidden exception)
    p, _b, _c = standard_fixture("whole", scope=".")
    (p / "README.md").write_text("# v2 docs\n")
    commit_all(p, "docs only whole-scope")
    check(11, "whole-repo scope '.' + committed README change", "review-stale", p)

    # 12 exact-file scope isolates untracked sibling
    p, _b, _c = standard_fixture("exact", scope="src/app.py")
    (p / "src/sibling.py").write_text("SIB = 1\n")
    check(12, "exact-file scope + untracked sibling stays current", "accepted", p)

    # 13 missing scope
    p, b, c = new_project("noscope"), None, None
    b = freeze_base(p); c = write_impl(p)
    record(p, b, c, fp=b, scope=None, final=c)
    check(13, "missing Implementation scope", "review-freshness-unknown", p)

    # 14 malformed mixed-validity scope
    p, b, c = standard_fixture("badscope")
    rec = p / ".project-review/charter.md"
    rec.write_text(rec.read_text().replace("- Implementation scope: src/", "- Implementation scope: src/; ../escape"), )
    check(14, "mixed valid/invalid scope rejects WHOLE field", "review-freshness-unknown", p)

    # 15 legacy two-SHA fixed point (d00b221 shape, no scope, no final rev)
    p, b, c = new_project("legacy"), "", ""
    b = freeze_base(p); c = write_impl(p)
    record(p, b, c, fp=f"{b} {c}", scope=None, final=None)
    check(15, "legacy d00b221 two-value record never accepts", "review-freshness-unknown", p)

    # 16 malformed + valid SHA in Fixed point
    p, b, c = standard_fixture("mixedsha")
    record(p, b, c, fp=f"{GARBAGE} {b}", scope="src/", final=c)
    check(16, "Fixed point '<invalid-40hex> <valid>' no salvage", "review-freshness-unknown", p)

    # 17 missing final revision
    p, b, c = standard_fixture("nofinal")
    record(p, b, c, fp=b, scope="src/", final=None)
    check(17, "missing Reviewed implementation revision", "review-freshness-unknown", p)

    # 18 invalid final revision (unresolvable full-length sha)
    p, b, c = standard_fixture("badfinal")
    record(p, b, c, fp=b, scope="src/", final=GARBAGE)
    check(18, "unresolvable Reviewed implementation revision", "review-freshness-unknown", p)

    # 19/20 FAIL / BLOCKED bind to evaluated revision; drift stales to project-review
    for no, verdict_name in ((19, "FAIL"), (20, "BLOCKED")):
        p, b, c = standard_fixture(f"{verdict_name.lower()}")
        record(p, b, c, fp=b, scope="src/", final=c, verdict=verdict_name)
        (p / "src/common.py").write_text("COMMON = 9\n")
        commit_all(p, "in-scope drift after non-pass")
        check(no, f"{verdict_name} then in-scope drift", "review-stale", p)

    # 21 §21 lifecycle: C1 -> bounded repair -> C2 -> PASS binds C2
    p, b, c1 = standard_fixture("repair")
    (p / "src/app.py").write_text("print('impl v2 repaired')\n")
    commit_all(p, "bounded repair inside frozen scope")
    c2 = head(p)
    record(p, b, c2, fp=b, scope="src/", final=c2, verdict="PASS")
    ctx = {"projectRoot": str(p), "invocationControl": "explicit-only", "availability": "codex"}
    observed = ASK_LIGHT.route(ROOTS, ctx, host="codex", mode="next")["projectStage"]
    ok = "OK" if observed == "accepted" else "**MISMATCH**"
    print(f"21. review->repair C1({c1[:8]})->C2({c2[:8]})->PASS binds C2{'':<16} required=accepted            "
          f"observed={observed:<24} {ok}")
    RESULTS.append(("21", "lifecycle binds evaluated revision C2", ""))

    # 22 post-C2 in-scope change stales
    (p / "src/common.py").write_text("COMMON = 42\n")
    check(22, "in-scope change after accepted C2", "review-stale", p)

    # out-of-scope change after accepted C2 must remain accepted (extra guard)
    p2, b2, _c = standard_fixture("repair-oos")
    record(p2, b2, b2, fp=b2, scope="src/", final=head(p2))
    ctx2 = {"projectRoot": str(p2), "invocationControl": "explicit-only", "availability": "codex"}
    assert ASK_LIGHT.route(ROOTS, ctx2, host="codex", mode="next")["projectStage"] == "accepted"
    (p2 / "README.md").write_text("# unrelated doc update\n")
    commit_all(p2, "out of scope update after pass")
    observed = ASK_LIGHT.route(ROOTS, ctx2, host="codex", mode="next")["projectStage"]
    ok = "OK" if observed == "accepted" else "**MISMATCH**"
    print(f"22b. out-of-scope change after accepted C2{'':<28} required=accepted            observed={observed:<24} {ok}")

    # 23/24/25 Source layer: directory vs file baselines (generic profile record)
    def source_fixture(tag: str, *, dir_source: bool):
        root = Path(tempfile.mkdtemp(prefix=f"mx-{tag}-")) / "proj"
        root.mkdir()
        agents = root / "docs" / "agents"; agents.mkdir(parents=True)
        (agents / "light-project.md").write_text("# Light Project Configuration\n- Goal: g\n- Outputs: o\n")
        effort = root / ".scratch" / "current"; effort.mkdir(parents=True)
        (effort / "spec.md").write_text("# SPEC\nStatus: active\n")
        (effort / "issues").mkdir(); (effort / "issues" / "01.md").write_text("- Status: resolved\n")
        (effort / "map.md").write_text("# Map\nv1\n")
        (root / "README.md").write_text("# R\n")
        base = freeze_base(root)
        rd = root / ".project-review"; rd.mkdir()
        source_value = "`.scratch/current`" if dir_source else "`.scratch/current/spec.md`"
        (rd / "charter.md").write_text(
            "# Acceptance Charter\n## Acceptance baseline\n"
            f"- Source: {source_value}\n- Source revision or identity: {base}\n"
            "- Approval state: approved\n## Review Profile\n- Profile: generic\n")
        (rd / "state.md").write_text("- Status: READY\n- Round: 1\n")
        (rd / "verdict.md").write_text("# Verdict\n- Verdict: **PASS**\n")
        return root

    p = source_fixture("diradd", dir_source=True)
    (p / ".scratch/current/notes.md").write_text("new child\n")
    check(23, "directory Source + new untracked child", "review-stale", p)

    p = source_fixture("outside", dir_source=True)
    (p / "STRAY.txt").write_text("outside the cited dir\n")
    check(24, "untracked outside directory Source", "accepted", p)

    p = source_fixture("sibling", dir_source=False)
    (p / ".scratch/current/map.md").write_text("# sibling of file source\n")
    check(25, "file Source + untracked sibling", "accepted", p)

    print("\nManual smoke complete.")


if __name__ == "__main__":
    main()
