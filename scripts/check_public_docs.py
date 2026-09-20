#!/usr/bin/env python3
"""Public Documentation Quality Guard.

Validates that public/human-facing documentation remains accessible, well-linked,
and free of internal implementation-only anti-patterns and jargon leaks:
1. Exact package inventory consistency across skills/, CATALOG.md, and CATALOG.zh-CN.md.
2. Category READMEs completely cover all skills in their category without omissions.
3. Skill links in catalogs and category READMEs exist on disk.
4. Public surface does not leak implementation-only anti-patterns:
   - frontier-round
   - tracer-bullet ticket graph
   - 下游 ... 消费
   - 有界 handoff
   - 稳定 ... 契约
   - 工具经济性
   - 守护线
   - 注入证据
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# Implementation-only anti-pattern signatures forbidden on the public surface
FORBIDDEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"frontier-round", re.IGNORECASE), "frontier-round"),
    (re.compile(r"tracer-bullet ticket graph", re.IGNORECASE), "tracer-bullet ticket graph"),
    (re.compile(r"下游.*消费"), "下游 ... 消费"),
    (re.compile(r"有界\s*handoff", re.IGNORECASE), "有界 handoff"),
    (re.compile(r"稳定.*契约"), "稳定 ... 契约"),
    (re.compile(r"工具经济性"), "工具经济性"),
    (re.compile(r"守护线"), "守护线"),
    (re.compile(r"注入证据"), "注入证据"),
]


class PublicDocCheckResult(NamedTuple):
    passed: bool
    errors: list[str]


def get_admitted_packages(repo_root: Path = REPO_ROOT) -> set[str]:
    """Retrieve set of admitted skill package names from skills/*/*/SKILL.md."""
    return {p.parent.name for p in repo_root.glob("skills/*/*/SKILL.md")}


def get_public_surface_files(repo_root: Path = REPO_ROOT) -> list[Path]:
    """Collect all human-facing public documentation files."""
    files: list[Path] = []
    # Root level public docs
    for name in ["README.md", "README.zh-CN.md", "CATALOG.md", "CATALOG.zh-CN.md"]:
        p = repo_root / name
        if p.is_file():
            files.append(p)

    # Category and skills level READMEs
    for name in ["skills/README.md", "skills/README.zh-CN.md"]:
        p = repo_root / name
        if p.is_file():
            files.append(p)

    for p in repo_root.glob("skills/*/README*.md"):
        if p.is_file():
            files.append(p)

    # Public workflow guides
    for p in repo_root.glob("docs/workflows/*.md"):
        if p.is_file():
            files.append(p)
    for p in repo_root.glob("docs/zh-CN/workflows/*.md"):
        if p.is_file():
            files.append(p)

    return sorted(set(files))


def check_catalog_inventory(repo_root: Path = REPO_ROOT) -> list[str]:
    """Verify that CATALOG.md and CATALOG.zh-CN.md match the admitted packages exactly."""
    errors: list[str] = []
    admitted = get_admitted_packages(repo_root)

    for cat_name in ["CATALOG.md", "CATALOG.zh-CN.md"]:
        cat_file = repo_root / cat_name
        if not cat_file.is_file():
            errors.append(f"Catalog file missing: {cat_name}")
            continue

        text = cat_file.read_text(encoding="utf-8")
        catalog_packages = set(re.findall(r"^###\s+([a-zA-Z0-9_-]+)", text, re.MULTILINE))

        missing = admitted - catalog_packages
        if missing:
            errors.append(f"{cat_name} is missing admitted packages: {sorted(missing)}")

        extra = catalog_packages - admitted
        if extra:
            errors.append(f"{cat_name} contains unadmitted packages: {sorted(extra)}")

    return errors


def check_category_readmes(repo_root: Path = REPO_ROOT) -> list[str]:
    """Verify category READMEs list all packages in their category and links resolve."""
    errors: list[str] = []
    category_dirs = [d for d in (repo_root / "skills").iterdir() if d.is_dir() and d.name != "docs"]

    for cat_dir in sorted(category_dirs):
        packages_in_cat = sorted([p.name for p in cat_dir.iterdir() if (p / "SKILL.md").is_file()])
        if not packages_in_cat:
            continue

        for readme_name in ["README.md", "README.zh-CN.md"]:
            readme_path = cat_dir / readme_name
            if not readme_path.is_file():
                errors.append(f"Missing category README: {readme_path.relative_to(repo_root)}")
                continue

            text = readme_path.read_text(encoding="utf-8")
            for pkg in packages_in_cat:
                expected_link = f"{pkg}/SKILL.md"
                if expected_link not in text:
                    errors.append(
                        f"{readme_path.relative_to(repo_root)} is missing link to {expected_link}"
                    )
                target_skill = cat_dir / expected_link
                if not target_skill.is_file():
                    errors.append(
                        f"Resolved link target does not exist: {target_skill.relative_to(repo_root)}"
                    )

    return errors


def check_anti_patterns(
    repo_root: Path = REPO_ROOT,
    files: list[Path] | None = None,
) -> list[str]:
    """Scan public documentation surface for forbidden implementation-only leakages."""
    errors: list[str] = []
    target_files = files if files is not None else get_public_surface_files(repo_root)

    for path in target_files:
        try:
            rel_path = path.relative_to(repo_root)
        except ValueError:
            rel_path = path

        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            for pattern, pattern_label in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    errors.append(
                        f"{rel_path}:{idx} contains forbidden implementation anti-pattern [{pattern_label}]: {line.strip()}"
                    )

    return errors


def run_checks(repo_root: Path = REPO_ROOT) -> PublicDocCheckResult:
    """Execute all public doc checks."""
    errors: list[str] = []
    errors.extend(check_catalog_inventory(repo_root))
    errors.extend(check_category_readmes(repo_root))
    errors.extend(check_anti_patterns(repo_root))
    return PublicDocCheckResult(passed=len(errors) == 0, errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public documentation quality and anti-patterns.")
    parser.add_argument("--root", default=str(REPO_ROOT), help="Repository root path.")
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    print(f"=== Public Documentation Quality Gate ===")
    print(f"Repository Root: {repo_root}")
    print("------------------------------------------")

    result = run_checks(repo_root)
    if result.passed:
        print("RESULT: PASS — Public documentation is consistent and human-facing.")
        return 0

    print(f"RESULT: FAIL — {len(result.errors)} documentation issues detected:")
    for err in result.errors:
        print(f"  - {err}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
