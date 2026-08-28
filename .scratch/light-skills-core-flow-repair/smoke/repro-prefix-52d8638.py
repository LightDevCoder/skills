#!/usr/bin/env python3
"""Pre-fix reproductions (§19 A-I) against human-audit baseline 52d8638.

Builds real temporary Git repositories shaped like finished Light projects,
writes the canonical durable record, then tampers exactly one thing per case
and calls the real ask_light route() to record the CURRENT behavior. Read-only
wrt this repository. The caller redirects stdout into repro-prefix-52d8638.out.

Cases:
  A  duplicate conflicting Profile fields + in-scope drift   (first-match wins)
  B  missing Profile + in-scope drift                        (generic fallback)
  C  duplicate Fixed point (identical / conflicting)
  D  duplicate Implementation scope (identical / conflicting)
  E  duplicate Reviewed implementation revision (identical / conflicting)
  F  duplicate Source fields (ownership ambiguity)
  G  ambiguous Source revision or identity (invalid+valid / valid+valid)
  H  ignored in-scope implementation file (.gitignore / .git/info/exclude)
  I  ignored directory-Source child (.gitignore / .git/info/exclude)
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
GARBAGE = "0f1e2d3c4b5a9876543210fedcba9876543210ab"


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


def make_software_project(tag: str) -> tuple[Path, str, str]:
    """Base commit B holds src/common.py; impl commit C1 adds src/app.py."""
    root = Path(tempfile.mkdtemp(prefix=f"repro-{tag}-")) / "proj"
    root.mkdir()
    seed_project(root)
    src = root / "src"
    src.mkdir()
    (src / "common.py").write_text("COMMON = 1\n")
    base = baseline(root)
    (src / "app.py").write_text("print('impl v1')\n")
    baseline(root)  # C1
    return root, base, git(root, "rev-parse", "HEAD")


def write_software_record(
    root: Path,
    *,
    base: str,
    candidate: str,
    profile_line: str = "- Profile: software",
    fixed_point_line: str | None = None,
    scope_line: str = "- Implementation scope: src/",
    final_line: str | None = None,
    source_revision_line: str | None = None,
) -> None:
    rd = root / ".project-review"
    rd.mkdir(exist_ok=True)
    if source_revision_line is None:
        source_revision_line = f"- Source revision or identity: {base}"
    (rd / "charter.md").write_text(
        "\n".join([
            "# Acceptance Charter",
            "## Revision",
            "- Charter revision: 1",
            "## Acceptance baseline",
            "- Source: approved effort SPEC — `.scratch/current/spec.md`",
            source_revision_line,
            "- Approval state: approved",
            "## Review Profile",
            profile_line,
            fixed_point_line if fixed_point_line is not None else f"- Fixed point: {base}",
            scope_line,
        ]) + "\n"
    )
    (rd / "state.md").write_text("# State\n- Status: READY\n- Round: 1\n")
    (rd / "verdict.md").write_text(
        "# Verdict\n"
        f"- Verdict: **PASS**\n"
        f"{final_line if final_line is not None else f'- Reviewed implementation revision: {candidate}'}\n"
        "\n## Conclusion\nAccepted.\n"
    )


def write_directory_source_record(root: Path, *, revision: str) -> None:
    rd = root / ".project-review"
    rd.mkdir(exist_ok=True)
    (rd / "charter.md").write_text(
        "# Acceptance Charter\n"
        "## Acceptance baseline\n"
        "- Source: `.scratch/current`\n"
        f"- Source revision or identity: {revision}\n"
        "- Approval state: approved\n"
        "## Review Profile\n"
        "- Profile: generic\n"
    )
    (rd / "state.md").write_text("# State\n- Status: READY\n- Round: 1\n")
    (rd / "verdict.md").write_text("# Verdict\n- Verdict: **PASS**\n")


def route(root: Path) -> dict:
    context = {"projectRoot": str(root), "invocationControl": "explicit-only",
               "availability": "codex"}
    roots = [{"category": "first-party", "path": str(MAP_PATH.parents[1].parent)}]
    return ASK_LIGHT.route(roots, context, host="codex", mode="next")


def stage(root: Path) -> str:
    return route(root)["projectStage"]


def replace_line(path: Path, prefix: str, replacement: str | None) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [replacement if line.startswith(prefix) else line
            for line in lines] if replacement is not None else [
        line for line in lines if not line.startswith(prefix)]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def insert_after(path: Path, prefix: str, extra: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for line in lines:
        out.append(line)
        if line.startswith(prefix):
            out.append(extra)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def report(tag: str, observed: str, required: str) -> None:
    bug = observed == "accepted" and required != "accepted"
    print(f"{tag}: observed={observed!r} required={required!r} "
          f"-> {'FALSE ACCEPT (BUG)' if bug else 'not accepted (ok)'}")


def main() -> int:
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    print(f"# Pre-fix reproductions against working tree at HEAD {head}")
    print()

    # A — duplicate conflicting Profile fields + committed in-scope drift.
    root, base, candidate = make_software_project("A")
    write_software_record(root, base=base, candidate=candidate,
                          profile_line="- Profile: generic\n- Profile: software")
    print(f"A pre-drift observation: duplicate Profile alone -> {stage(root)!r}")
    (root / "src" / "app.py").write_text("print('impl v2')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "drift after pass")
    report("A duplicate Profile (generic first) + in-scope drift", stage(root),
           "review-freshness-unknown")

    # B — missing Profile + committed in-scope drift.
    root, base, candidate = make_software_project("B")
    write_software_record(root, base=base, candidate=candidate)
    replace_line(root / ".project-review" / "charter.md", "- Profile: ", None)
    print(f"B pre-drift observation: missing Profile alone -> {stage(root)!r}")
    (root / "src" / "app.py").write_text("print('impl v2')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "drift after pass")
    report("B missing Profile + in-scope drift", stage(root), "review-freshness-unknown")

    # C — duplicate Fixed point fields.
    root, base, candidate = make_software_project("C1")
    write_software_record(root, base=base, candidate=candidate,
                          fixed_point_line=f"- Fixed point: {base}\n- Fixed point: {base}")
    report("C1 duplicate identical Fixed point", stage(root), "review-freshness-unknown")

    root, base, candidate = make_software_project("C2")
    write_software_record(root, base=base, candidate=candidate,
                          fixed_point_line=f"- Fixed point: {base}\n- Fixed point: {GARBAGE}")
    report("C2 duplicate conflicting Fixed point (valid first)", stage(root),
           "review-freshness-unknown")

    # D — duplicate Implementation scope fields.
    root, base, candidate = make_software_project("D1")
    write_software_record(root, base=base, candidate=candidate,
                          scope_line="- Implementation scope: src/\n- Implementation scope: src/")
    report("D1 duplicate identical Implementation scope", stage(root),
           "review-freshness-unknown")

    root, base, candidate = make_software_project("D2")
    write_software_record(root, base=base, candidate=candidate,
                          scope_line="- Implementation scope: src/\n- Implementation scope: docs/")
    report("D2 duplicate conflicting Implementation scope", stage(root),
           "review-freshness-unknown")

    # E — duplicate Reviewed implementation revision fields.
    root, base, candidate = make_software_project("E1")
    final = f"- Reviewed implementation revision: {candidate}"
    write_software_record(root, base=base, candidate=candidate,
                          final_line=f"{final}\n{final}")
    report("E1 duplicate identical Reviewed implementation revision", stage(root),
           "review-freshness-unknown")

    root, base, candidate = make_software_project("E2")
    write_software_record(
        root, base=base, candidate=candidate,
        final_line=(f"- Reviewed implementation revision: {candidate}\n"
                    f"- Reviewed implementation revision: {GARBAGE}"))
    report("E2 duplicate conflicting Reviewed implementation revision", stage(root),
           "review-freshness-unknown")

    # F — duplicate Source fields (ownership ambiguity, one cites current effort).
    root, base, candidate = make_software_project("F")
    write_software_record(root, base=base, candidate=candidate)
    insert_after(root / ".project-review" / "charter.md", "- Source: ",
                 "- Source: `.scratch/other/spec.md`")
    report("F duplicate Source (current effort first)", stage(root),
           "review-ownership-unknown")

    # G — ambiguous Source revision or identity values.
    root, base, candidate = make_software_project("G1")
    other = make_software_project("G1b")[1]
    write_software_record(root, base=base, candidate=candidate,
                          source_revision_line=f"- Source revision or identity: {GARBAGE} {base}")
    report("G1 Source revision '<invalid-40hex> <valid-sha>'", stage(root),
           "review-freshness-unknown")

    root, base, candidate = make_software_project("G2")
    write_software_record(root, base=base, candidate=candidate,
                          source_revision_line=f"- Source revision or identity: {base} {other}")
    report("G2 Source revision '<valid-sha-A> <valid-sha-B>'", stage(root),
           "review-freshness-unknown")

    # H — ignored in-scope implementation file after PASS.
    for tag, ignore_mechanism in (
        ("H1 .gitignore", "gitignore"),
        ("H2 .git/info/exclude", "info-exclude"),
    ):
        root, base, candidate = make_software_project(tag.split()[0])
        write_software_record(root, base=base, candidate=candidate)
        if ignore_mechanism == "gitignore":
            (root / ".gitignore").write_text("new_hidden.py\n")
        else:
            excludes = root / ".git" / "info"
            excludes.mkdir(exist_ok=True)
            (excludes / "exclude").write_text("new_hidden.py\n")
        (root / "src" / "new_hidden.py").write_text("HIDDEN = 1\n")
        report(f"{tag} ignored in-scope src/new_hidden.py", stage(root), "review-stale")

    # I — ignored directory-Source child after PASS.
    for tag, ignore_mechanism in (
        ("I1 .gitignore", "gitignore"),
        ("I2 .git/info/exclude", "info-exclude"),
    ):
        root = Path(tempfile.mkdtemp(prefix=f"repro-{tag.split()[0]}-")) / "proj"
        root.mkdir()
        seed_project(root, with_map=True)
        revision = baseline(root)
        write_directory_source_record(root, revision=revision)
        if ignore_mechanism == "gitignore":
            (root / ".gitignore").write_text("hidden.md\n")
        else:
            excludes = root / ".git" / "info"
            excludes.mkdir(exist_ok=True)
            (excludes / "exclude").write_text("hidden.md\n")
        (root / ".scratch" / "current" / "hidden.md").write_text("hidden child\n")
        report(f"{tag} ignored .scratch/current/hidden.md", stage(root), "review-stale")

    print("\nAll rows above record the PRE-FIX behavior at the stated baseline;")
    print("each 'FALSE ACCEPT (BUG)' row must become its required stage post-fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
