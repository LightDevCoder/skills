#!/usr/bin/env python3
"""Post-fix manual smoke matrix (§22) — real Git repos through the real CLI.

Every row builds a real temporary Git repository, writes canonical durable
records, and invokes the actual ask_light.py command line (route() path) to
record the observed ProjectStage. The caller redirects stdout into
manual-matrix-hardening.out.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CLI = REPO / "skills" / "ask-light" / "scripts" / "ask_light.py"
ROOTS_JSON = json.dumps([{"category": "first-party", "path": str(REPO / "skills")}])
GARBAGE = "0f1e2d3c4b5a9876543210fedcba9876543210ab"


def git(root: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "smoke",
        "GIT_AUTHOR_EMAIL": "smoke@example.com",
        "GIT_COMMITTER_NAME": "smoke",
        "GIT_COMMITTER_EMAIL": "smoke@example.com",
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


def seed_project(root: Path, *, with_map: bool = False) -> None:
    agents = root / "docs" / "agents"
    agents.mkdir(parents=True)
    (agents / "light-project.md").write_text(
        "# Light Project Configuration\n- Goal: Build parser\n- Outputs: parser\n"
    )
    effort = root / ".scratch" / "current"
    effort.mkdir(parents=True)
    (effort / "spec.md").write_text("# SPEC\nStatus: active\n")
    if with_map:
        (effort / "map.md").write_text("# Map\n")
    issues = effort / "issues"
    issues.mkdir()
    (issues / "01.md").write_text("- Status: resolved\n")
    (root / "README.md").write_text("# Project\nv1\n")


def make_software_project(tag: str, *, scope: str = "src/") -> tuple[Path, str, str]:
    root = Path(tempfile.mkdtemp(prefix=f"smoke-{tag}-")) / "proj"
    root.mkdir()
    seed_project(root)
    src = root / "src"
    src.mkdir()
    (src / "common.py").write_text("COMMON = 1\n")
    base = baseline(root)
    (src / "app.py").write_text("print('impl v1')\n")
    baseline(root)
    candidate = git(root, "rev-parse", "HEAD")
    write_software_record(root, base=base, candidate=candidate, scope=scope)
    return root, base, candidate


def write_software_record(
    root: Path,
    *,
    base: str,
    candidate: str,
    scope: str = "src/",
    profile_line: str = "- Profile: software",
    fixed_line: str | None = None,
    source_revision_line: str | None = None,
    final_line: str | None = None,
) -> None:
    rd = root / ".project-review"
    rd.mkdir(exist_ok=True)
    if source_revision_line is None:
        source_revision_line = f"- Source revision or identity: {base}"
    (rd / "charter.md").write_text(
        "\n".join([
            "# Acceptance Charter",
            "## Acceptance baseline",
            "- Source: approved effort SPEC — `.scratch/current/spec.md`",
            source_revision_line,
            "- Approval state: approved",
            "## Review Profile",
            profile_line,
            fixed_line if fixed_line is not None else f"- Fixed point: {base}",
            f"- Implementation scope: {scope}",
        ]) + "\n"
    )
    (rd / "state.md").write_text("# State\n- Status: READY\n- Round: 1\n")
    if final_line is None:
        final_line = f"- Reviewed implementation revision: {candidate}"
    (rd / "verdict.md").write_text(
        f"# Verdict\n- Verdict: **PASS**\n{final_line}\n\n## Conclusion\nAccepted.\n"
    )


def write_directory_record(root: Path, *, revision: str, source: str) -> None:
    rd = root / ".project-review"
    rd.mkdir(exist_ok=True)
    (rd / "charter.md").write_text(
        "# Acceptance Charter\n"
        "## Acceptance baseline\n"
        f"- Source: {source}\n"
        f"- Source revision or identity: {revision}\n"
        "- Approval state: approved\n"
        "## Review Profile\n"
        "- Profile: generic\n"
    )
    (rd / "state.md").write_text("# State\n- Status: READY\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Verdict: **PASS**\n")


def cli_stage(root: Path) -> str:
    context = json.dumps({
        "projectRoot": str(root),
        "invocationControl": "explicit-only",
        "availability": "codex",
    })
    proc = subprocess.run(
        [sys.executable, str(CLI), "--roots-json", ROOTS_JSON,
         "--context-json", context, "--host-name", "codex", "--mode", "next"],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        return f"__cli_rc_{proc.returncode}__"
    return json.loads(proc.stdout).get("projectStage", "")


def replace_field(root: Path, record: str, field: str, value: str | None) -> None:
    path = root / ".project-review" / record
    prefix = f"- {field}: "
    lines = path.read_text(encoding="utf-8").splitlines()
    if value is None:
        kept = [line for line in lines if not line.startswith(prefix)]
    else:
        kept = [f"{prefix}{value}" if line.startswith(prefix) else line for line in lines]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def add_line(root: Path, record: str, line: str) -> None:
    path = root / ".project-review" / record
    text = path.read_text(encoding="utf-8").rstrip("\n")
    path.write_text(f"{text}\n{line}\n", encoding="utf-8")


def add_ignore_rule(root: Path, pattern: str, *, mechanism: str = "gitignore") -> None:
    if mechanism == "gitignore":
        target = root / ".gitignore"
    else:
        target = root / ".git" / "info" / "exclude"
        target.parent.mkdir(exist_ok=True)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    separator = "" if not existing or existing.endswith("\n") else "\n"
    target.write_text(f"{existing}{separator}{pattern}\n", encoding="utf-8")


RESULTS: list[tuple[str, str, str, bool]] = []


def row(number: int, description: str, expected: str, observed: str) -> None:
    ok = (
        observed == expected
        or (expected == "not accepted" and observed in {
            "review-freshness-unknown", "review-ownership-unknown"})
    )
    RESULTS.append((f"{number:02d}", description, observed, ok))
    print(f"{number:02d}. {description}\n    expected={expected!r} observed={observed!r} -> {'OK' if ok else 'MISMATCH'}")


def main() -> int:
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    print(f"# Post-fix manual smoke matrix (§22) — real CLI against working tree at {head}")
    print()

    # 1. fresh software PASS -> accepted
    root, base, candidate = make_software_project("01")
    row(1, "fresh software PASS", "accepted", cli_stage(root))

    # 2. duplicate Profile + implementation drift -> not accepted
    root, base, candidate = make_software_project("02")
    add_line(root, "charter.md", "- Profile: generic")
    (root / "src" / "app.py").write_text("print('impl v2')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "drift")
    row(2, "duplicate Profile + implementation drift", "not accepted", cli_stage(root))

    # 3. missing Profile + implementation drift -> not accepted
    root, base, candidate = make_software_project("03")
    replace_field(root, "charter.md", "Profile", None)
    (root / "src" / "app.py").write_text("print('impl v2')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "drift")
    row(3, "missing Profile + implementation drift", "not accepted", cli_stage(root))

    # 4. duplicate Source -> unknown
    root, base, candidate = make_software_project("04")
    add_line(root, "charter.md", "- Source: `.scratch/other/spec.md`")
    row(4, "duplicate Source", "review-ownership-unknown", cli_stage(root))

    # 5. duplicate Fixed point -> unknown
    root, base, candidate = make_software_project("05")
    add_line(root, "charter.md", f"- Fixed point: {base}")
    row(5, "duplicate Fixed point", "review-freshness-unknown", cli_stage(root))

    # 6. duplicate Implementation scope -> unknown
    root, base, candidate = make_software_project("06")
    add_line(root, "charter.md", "- Implementation scope: docs/")
    row(6, "duplicate Implementation scope", "review-freshness-unknown", cli_stage(root))

    # 7. duplicate Reviewed implementation revision -> unknown
    root, base, candidate = make_software_project("07")
    add_line(root, "verdict.md", f"- Reviewed implementation revision: {candidate}")
    row(7, "duplicate Reviewed implementation revision", "review-freshness-unknown", cli_stage(root))

    # 8. Source revision invalid + valid -> unknown
    root, base, candidate = make_software_project("08")
    replace_field(root, "charter.md", "Source revision or identity", f"{GARBAGE} {base}")
    row(8, "Source revision invalid+valid", "review-freshness-unknown", cli_stage(root))

    # 9. Source revision valid A + valid B -> unknown
    root, base, candidate = make_software_project("09")
    (root / "README.md").write_text("# Project\nunrelated second commit\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "unrelated second commit")
    other = git(root, "rev-parse", "HEAD")
    replace_field(root, "charter.md", "Source revision or identity", f"{base} {other}")
    row(9, "Source revision validA+validB", "review-freshness-unknown", cli_stage(root))

    # 10/11. ignored in-scope implementation file -> stale
    for number, mechanism in ((10, "gitignore"), (11, "info-exclude")):
        root, base, candidate = make_software_project(f"{number:02d}")
        add_ignore_rule(root, "new_hidden.py", mechanism=mechanism)
        (root / "src" / "new_hidden.py").write_text("HIDDEN = 1\n")
        row(number, f"ignored in-scope src/new_hidden.py via {mechanism}", "review-stale", cli_stage(root))

    # 12. ignored out-of-scope file -> current
    root, base, candidate = make_software_project("12")
    add_ignore_rule(root, "*.tmp")
    (root / "build.tmp").write_text("cache\n")
    row(12, "ignored out-of-scope root build.tmp", "accepted", cli_stage(root))

    # 13. ignored directory Source child -> stale
    root = Path(tempfile.mkdtemp(prefix="smoke-13-")) / "proj"
    root.mkdir()
    seed_project(root, with_map=True)
    revision = baseline(root)
    write_directory_record(root, revision=revision, source="`.scratch/current`")
    add_ignore_rule(root, "hidden.md")
    (root / ".scratch" / "current" / "hidden.md").write_text("hidden child\n")
    row(13, "ignored .scratch/current/hidden.md child", "review-stale", cli_stage(root))

    # 14. ignored file outside directory Source -> current
    root = Path(tempfile.mkdtemp(prefix="smoke-14-")) / "proj"
    root.mkdir()
    seed_project(root, with_map=True)
    revision = baseline(root)
    write_directory_record(root, revision=revision, source="`.scratch/current`")
    add_ignore_rule(root, "*.tmp")
    (root / "loose.tmp").write_text("outside\n")
    row(14, "ignored file outside directory Source", "accepted", cli_stage(root))

    # 15. file-only Source + ignored sibling -> current
    root, base, candidate = make_software_project("15")
    add_ignore_rule(root, "random-note.md")
    (root / ".scratch" / "current" / "random-note.md").write_text("sibling\n")
    row(15, "file-only Source + ignored sibling", "accepted", cli_stage(root))

    # 16. exact-file implementation scope + ignored sibling -> current
    root, base, candidate = make_software_project("16", scope="src/app.py")
    add_ignore_rule(root, "sibling.py")
    (root / "src" / "sibling.py").write_text("SIB = 1\n")
    row(16, "exact-file scope + ignored sibling", "accepted", cli_stage(root))

    # 17. whole-repository scope + ignored file -> stale. With scope "." the
    # durable records are in-scope files (documented §16 born-stale), so the
    # ignored file is named with a sort-first filename to keep it visible in
    # the reported names.
    root, base, candidate = make_software_project("17", scope=".")
    add_ignore_rule(root, "!priority.data")
    (root / "!priority.data").write_text("ignored in whole-repo scope\n")
    row(17, "whole-repository scope + ignored file", "review-stale", cli_stage(root))

    # 18. previous C1 -> repair -> C2 lifecycle -> still accepted at C2
    root, base, c1 = make_software_project("18")
    (root / "src" / "app.py").write_text("print('impl v2 repaired')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "bounded in-scope repair")
    c2 = git(root, "rev-parse", "HEAD")
    replace_field(root, "verdict.md", "Reviewed implementation revision", c2)
    row(18, "C1 -> repair -> C2 lifecycle accepted at C2", "accepted", cli_stage(root))

    # 19. post-C2 in-scope normal tracked drift -> stale
    (root / "src" / "common.py").write_text("COMMON = 9\n")
    row(19, "post-C2 in-scope tracked drift", "review-stale", cli_stage(root))

    # 20. unrelated README outside scope -> current
    root2, base2, cand2 = make_software_project("20")
    (root2 / "README.md").write_text("# Project\ndocs only\n", encoding="utf-8")
    git(root2, "add", "-A")
    git(root2, "commit", "-q", "-m", "docs only")
    row(20, "unrelated README outside scope", "accepted", cli_stage(root2))

    ok = sum(1 for item in RESULTS if item[3])
    print(f"\n{ok}/{len(RESULTS)} rows OK")
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
