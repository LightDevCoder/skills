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


def get_canonical_adapter_count(repo_root: Path = REPO_ROOT) -> int:
    """Retrieve canonical native harness adapter count from agent-config documentation."""
    harness_doc = repo_root / "skills" / "engineering" / "agent-config" / "references" / "harness-support.md"
    if harness_doc.is_file():
        text = harness_doc.read_text(encoding="utf-8")
        m = re.search(r"native host adapters for\s+(\d+)\s+primary coding-agent harnesses", text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return 10


def check_readme_facts(repo_root: Path = REPO_ROOT) -> list[str]:
    """Validate root README facts against repository canonical state."""
    errors: list[str] = []
    admitted = get_admitted_packages(repo_root)
    pkg_count = len(admitted)
    canonical_adapters = get_canonical_adapter_count(repo_root)

    readme_en = repo_root / "README.md"
    readme_zh = repo_root / "README.zh-CN.md"

    if readme_en.is_file():
        text_en = readme_en.read_text(encoding="utf-8")
        # Check package count claim
        m_count = re.search(r"provides\s+(\d+)\s+first-party\s+Agent\s+Skills", text_en, re.IGNORECASE)
        if m_count and int(m_count.group(1)) != pkg_count:
            errors.append(f"README.md package count claim {m_count.group(1)} differs from admitted count {pkg_count}.")
        # Check unreleased claims for tagged packages
        if re.search(r"available on `?main`? as an unreleased addition", text_en, re.IGNORECASE):
            errors.append("README.md contains stale claim stating admitted package is an unreleased addition.")
        # Check adapter count
        m_adapt = re.search(r"(\d+)\s+native\s+adapters", text_en, re.IGNORECASE)
        if m_adapt and int(m_adapt.group(1)) != canonical_adapters:
            errors.append(f"README.md reports {m_adapt.group(1)} native adapters, expected {canonical_adapters}.")

    if readme_zh.is_file():
        text_zh = readme_zh.read_text(encoding="utf-8")
        # Check package count claim
        m_count = re.search(r"包含\s*(\d+)\s*个第一方\s*Agent\s*Skill", text_zh, re.IGNORECASE)
        if m_count and int(m_count.group(1)) != pkg_count:
            errors.append(f"README.zh-CN.md package count claim {m_count.group(1)} differs from admitted count {pkg_count}.")
        # Check unreleased claims
        if "尚未包含在版本标签中" in text_zh or "尚未发布版本标签" in text_zh:
            errors.append("README.zh-CN.md contains stale claim stating admitted package is not included in version tag.")
        # Check adapter count
        m_adapt = re.search(r"(\d+)\s*种原生适配器", text_zh)
        if m_adapt and int(m_adapt.group(1)) != canonical_adapters:
            errors.append(f"README.zh-CN.md reports {m_adapt.group(1)} native adapters, expected {canonical_adapters}.")

    return errors


def check_catalog_parity(repo_root: Path = REPO_ROOT) -> list[str]:
    """Validate that English and Chinese catalogs provide equivalent required fields for each skill."""
    errors: list[str] = []
    cat_en_path = repo_root / "CATALOG.md"
    cat_zh_path = repo_root / "CATALOG.zh-CN.md"

    if not cat_en_path.is_file() or not cat_zh_path.is_file():
        return errors

    cat_en = cat_en_path.read_text(encoding="utf-8")
    cat_zh = cat_zh_path.read_text(encoding="utf-8")

    skills_en = re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_en, re.MULTILINE)
    skills_zh = re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_zh, re.MULTILINE)

    if set(skills_en) != set(skills_zh):
        errors.append(f"Catalog skill sets differ between EN and ZH: {set(skills_en) ^ set(skills_zh)}")

    en_required = ["Purpose", "When to use", "Invocation", "Package", "Status"]
    zh_required = ["作用", "什么时候用", "调用", "包", "状态"]

    for s in skills_en:
        block_en_m = re.search(r"^###\s+" + s + r"\n(.*?)(?=\n###|\Z)", cat_en, re.DOTALL | re.MULTILINE)
        if block_en_m:
            block = block_en_m.group(1)
            for req in en_required:
                if f"**{req}:**" not in block:
                    errors.append(f"CATALOG.md entry '{s}' missing required field: **{req}:**")

        block_zh_m = re.search(r"^###\s+" + s + r"\n(.*?)(?=\n###|\Z)", cat_zh, re.DOTALL | re.MULTILINE)
        if block_zh_m:
            block = block_zh_m.group(1)
            for req in zh_required:
                if f"**{req}" not in block:
                    errors.append(f"CATALOG.zh-CN.md entry '{s}' missing required field: **{req}**")

    return errors


def run_checks(repo_root: Path = REPO_ROOT) -> PublicDocCheckResult:
    """Execute all public doc checks."""
    errors: list[str] = []
    errors.extend(check_catalog_inventory(repo_root))
    errors.extend(check_category_readmes(repo_root))
    errors.extend(check_anti_patterns(repo_root))
    errors.extend(check_readme_facts(repo_root))
    errors.extend(check_catalog_parity(repo_root))
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
        print("RESULT: PASS — Public documentation structural and terminology checks passed.")
        return 0

    print(f"RESULT: FAIL — {len(result.errors)} documentation issues detected:")
    for err in result.errors:
        print(f"  - {err}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
