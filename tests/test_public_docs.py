"""Unit and regression tests for scripts/check_public_docs.py."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_public_docs import (
    run_checks,
    check_anti_patterns,
    check_catalog_inventory,
    check_category_readmes,
    check_catalog_parity,
    normalize_invocation,
    extract_status_tokens,
    get_skill_invocation_authority,
    get_public_surface_files,
    FORBIDDEN_PATTERNS,
)


class PublicDocsQualityTests(unittest.TestCase):
    def test_current_repo_passes_public_doc_checks(self) -> None:
        """The repository's public documentation passes all consistency and style gates."""
        result = run_checks(ROOT)
        self.assertTrue(result.passed, f"Public doc check failed with errors: {result.errors}")

    def test_public_surface_files_discovered(self) -> None:
        """Ensure all required root, category, and workflow documentation files are scanned."""
        files = get_public_surface_files(ROOT)
        rel_files = {p.relative_to(ROOT).as_posix() for p in files}

        # Root files
        self.assertIn("README.md", rel_files)
        self.assertIn("README.zh-CN.md", rel_files)
        self.assertIn("CATALOG.md", rel_files)
        self.assertIn("CATALOG.zh-CN.md", rel_files)

        # Category READMEs
        self.assertIn("skills/project/README.md", rel_files)
        self.assertIn("skills/project/README.zh-CN.md", rel_files)
        self.assertIn("skills/engineering/README.md", rel_files)
        self.assertIn("skills/review/README.md", rel_files)
        self.assertIn("skills/thinking/README.md", rel_files)

        # Workflow docs
        self.assertIn("docs/workflows/project-workflow.md", rel_files)
        self.assertIn("docs/zh-CN/workflows/project-workflow.md", rel_files)

    def test_anti_pattern_regression_fixtures(self) -> None:
        """Verify each forbidden implementation anti-pattern triggers detection on public docs."""
        fixtures = [
            ("frontier-round", "This skill uses a frontier-round interview style."),
            ("tracer-bullet ticket graph", "Generates a tracer-bullet ticket graph with dependencies."),
            ("下游 ... 消费", "幂等建立供下游 Project Skills 消费的结构。"),
            ("有界 handoff", "输出给下游组件的有界 handoff 产物。"),
            ("稳定 ... 契约", "建立初始稳定 tracker 契约。"),
            ("工具经济性", "分析执行中的工具经济性问题。"),
            ("守护线", "检查执行流程中缺失的守护线。"),
            ("注入证据", "向追问过程中注入证据信息。"),
        ]

        with tempfile.TemporaryDirectory(prefix="public-doc-fixture-") as tmp:
            tmp_root = Path(tmp)
            for label, offensive_text in fixtures:
                dummy_file = tmp_root / f"doc_{label.replace(' ', '_')}.md"
                dummy_file.write_text(f"# Title\n\n{offensive_text}\n", encoding="utf-8")
                errors = check_anti_patterns(tmp_root, files=[dummy_file])
                self.assertTrue(
                    any(label in err for err in errors),
                    f"Expected detection of [{label}] in '{offensive_text}', got: {errors}",
                )

    def test_missing_catalog_package_fails(self) -> None:
        """If a package is missing from CATALOG.md or CATALOG.zh-CN.md, check fails."""
        with tempfile.TemporaryDirectory(prefix="catalog-test-") as tmp:
            tmp_root = Path(tmp)
            # Create a mock admitted package
            pkg_dir = tmp_root / "skills" / "project" / "mock-skill"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Mock", encoding="utf-8")

            # Create catalog missing mock-skill
            (tmp_root / "CATALOG.md").write_text("# Catalog\n\n### other-skill\n", encoding="utf-8")
            (tmp_root / "CATALOG.zh-CN.md").write_text("# 目录\n\n### other-skill\n", encoding="utf-8")

            errors = check_catalog_inventory(tmp_root)
            self.assertTrue(any("missing admitted packages" in err for err in errors))

    def test_category_readme_missing_skill_link_fails(self) -> None:
        """If a category README omits a skill in its directory, check fails."""
        with tempfile.TemporaryDirectory(prefix="category-test-") as tmp:
            tmp_root = Path(tmp)
            cat_dir = tmp_root / "skills" / "project"
            pkg_dir = cat_dir / "mock-pkg"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "SKILL.md").write_text("# Mock", encoding="utf-8")

            (cat_dir / "README.md").write_text("# Project\n\nNo link here.", encoding="utf-8")
            (cat_dir / "README.zh-CN.md").write_text("# 项目\n\nNo link here.", encoding="utf-8")

            errors = check_category_readmes(tmp_root)
            self.assertTrue(any("missing link to mock-pkg/SKILL.md" in err for err in errors))

    def test_root_readme_stable_package_count_matches_catalog(self) -> None:
        """Root READMEs package count claim must match catalog inventory and admitted packages."""
        admitted = {p.parent.name for p in ROOT.glob("skills/*/*/SKILL.md")}
        admitted_count = len(admitted)

        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        m_en = re.search(r"provides\s+(\d+)\s+first-party\s+Agent\s+Skills", readme_en)
        self.assertIsNotNone(m_en, "README.md missing package count statement.")
        self.assertEqual(int(m_en.group(1)), admitted_count)

        m_zh = re.search(r"包含\s*(\d+)\s*个第一方\s*Agent\s*Skill", readme_zh)
        self.assertIsNotNone(m_zh, "README.zh-CN.md missing package count statement.")
        self.assertEqual(int(m_zh.group(1)), admitted_count)

    def test_root_readme_has_no_unreleased_claim_for_tagged_packages(self) -> None:
        """Root READMEs must not claim that admitted tagged packages are unreleased."""
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        self.assertNotRegex(
            readme_en,
            r"available on `?main`? as an unreleased addition",
            "README.md contains stale unreleased claim.",
        )
        self.assertNotIn("尚未包含在版本标签中", readme_zh, "README.zh-CN.md contains stale unreleased claim.")
        self.assertNotIn("尚未发布版本标签", readme_zh, "README.zh-CN.md contains stale unreleased claim.")

    def test_english_chinese_skill_inventory_matches(self) -> None:
        """CATALOG.md, CATALOG.zh-CN.md, and skills/*/*/SKILL.md must list identical package sets."""
        admitted = {p.parent.name for p in ROOT.glob("skills/*/*/SKILL.md")}

        cat_en = (ROOT / "CATALOG.md").read_text(encoding="utf-8")
        cat_zh = (ROOT / "CATALOG.zh-CN.md").read_text(encoding="utf-8")

        skills_en = set(re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_en, re.MULTILINE))
        skills_zh = set(re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_zh, re.MULTILINE))

        self.assertEqual(skills_en, admitted)
        self.assertEqual(skills_zh, admitted)

    def test_english_chinese_agent_config_adapter_count_matches(self) -> None:
        """EN and ZH README adapter counts must match each other and the canonical authority."""
        # Canonical authority: harness-support.md
        harness_doc = (ROOT / "skills" / "engineering" / "agent-config" / "references" / "harness-support.md").read_text(encoding="utf-8")
        m_auth = re.search(r"native host adapters for\s+(\d+)\s+primary coding-agent harnesses", harness_doc)
        self.assertIsNotNone(m_auth, "Authority doc harness-support.md missing adapter count.")
        canonical_count = int(m_auth.group(1))

        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

        m_en = re.search(r"(\d+)\s+native\s+adapters", readme_en)
        self.assertIsNotNone(m_en, "README.md missing native adapters count.")
        self.assertEqual(int(m_en.group(1)), canonical_count)

        m_zh = re.search(r"(\d+)\s*种原生适配器", readme_zh)
        self.assertIsNotNone(m_zh, "README.zh-CN.md missing native adapters count.")
        self.assertEqual(int(m_zh.group(1)), canonical_count)

    def test_catalog_en_zh_entries_have_equivalent_required_fields(self) -> None:
        """Every skill entry in English and Chinese catalogs must provide equivalent required fields."""
        cat_en = (ROOT / "CATALOG.md").read_text(encoding="utf-8")
        cat_zh = (ROOT / "CATALOG.zh-CN.md").read_text(encoding="utf-8")

        skills = re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_en, re.MULTILINE)
        self.assertEqual(len(skills), 36)

        en_fields = ["Purpose", "When to use", "Invocation", "Package", "Status"]
        zh_fields = ["作用", "什么时候用", "调用方式", "包位置", "状态"]

        for skill in skills:
            block_en = re.search(r"^###\s+" + skill + r"\n(.*?)(?=\n###|\Z)", cat_en, re.DOTALL | re.MULTILINE).group(1)
            block_zh = re.search(r"^###\s+" + skill + r"\n(.*?)(?=\n###|\Z)", cat_zh, re.DOTALL | re.MULTILINE).group(1)

            for ef in en_fields:
                self.assertIn(
                    f"**{ef}:**",
                    block_en,
                    f"CATALOG.md entry '{skill}' is missing required field '**{ef}:**'",
                )

            for zf in zh_fields:
                self.assertIn(
                    f"**{zf}：**",
                    block_zh,
                    f"CATALOG.zh-CN.md entry '{skill}' is missing required field '**{zf}：**'",
                )

    def test_catalog_en_zh_invocation_semantic_parity(self) -> None:
        """Every skill must have identical invocation semantics across EN, ZH, and authority."""
        cat_en = (ROOT / "CATALOG.md").read_text(encoding="utf-8")
        cat_zh = (ROOT / "CATALOG.zh-CN.md").read_text(encoding="utf-8")

        skills = re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_en, re.MULTILINE)
        self.assertEqual(len(skills), 36)

        mismatches: list[str] = []
        for s in skills:
            auth_inv = get_skill_invocation_authority(s, ROOT)

            block_en = re.search(r"^###\s+" + s + r"\n(.*?)(?=\n###|\Z)", cat_en, re.DOTALL | re.MULTILINE).group(1)
            m_inv_en = re.search(r"-\s+\*\*Invocation:\*\s*(.*?)$", block_en, re.MULTILINE)
            inv_en = normalize_invocation(m_inv_en.group(1).strip() if m_inv_en else "")

            block_zh = re.search(r"^###\s+" + s + r"\n(.*?)(?=\n###|\Z)", cat_zh, re.DOTALL | re.MULTILINE).group(1)
            m_inv_zh = re.search(r"-\s+\*\*调用(?:方式)?(?:\*\*：|\*\*:\s*|：\*\*)\s*(.*?)$", block_zh, re.MULTILINE)
            inv_zh = normalize_invocation(m_inv_zh.group(1).strip() if m_inv_zh else "")

            if not (auth_inv == inv_en == inv_zh):
                mismatches.append(f"{s}: authority='{auth_inv}', EN='{inv_en}', ZH='{inv_zh}'")

        self.assertEqual(mismatches, [], f"Invocation semantic mismatches found: {mismatches}")

    def test_catalog_en_zh_status_semantic_parity(self) -> None:
        """Every skill must have identical status semantic tokens between English and Chinese catalogs."""
        cat_en = (ROOT / "CATALOG.md").read_text(encoding="utf-8")
        cat_zh = (ROOT / "CATALOG.zh-CN.md").read_text(encoding="utf-8")

        skills = re.findall(r"^###\s+([a-zA-Z0-9_-]+)", cat_en, re.MULTILINE)
        self.assertEqual(len(skills), 36)

        mismatches: list[str] = []
        for s in skills:
            block_en = re.search(r"^###\s+" + s + r"\n(.*?)(?=\n###|\Z)", cat_en, re.DOTALL | re.MULTILINE).group(1)
            m_stat_en = re.search(r"-\s+\*\*Status:\*\*\s*(.*?)$", block_en, re.MULTILINE)
            stat_en = m_stat_en.group(1).strip() if m_stat_en else ""
            tok_en = extract_status_tokens(stat_en)

            block_zh = re.search(r"^###\s+" + s + r"\n(.*?)(?=\n###|\Z)", cat_zh, re.DOTALL | re.MULTILINE).group(1)
            m_stat_zh = re.search(r"-\s+\*\*状态(?:\*\*：|\*\*:\s*|：\*\*)\s*(.*?)$", block_zh, re.MULTILINE)
            stat_zh = m_stat_zh.group(1).strip() if m_stat_zh else ""
            tok_zh = extract_status_tokens(stat_zh)

            if tok_en != tok_zh:
                mismatches.append(f"{s}: EN={sorted(tok_en)} vs ZH={sorted(tok_zh)}")

        self.assertEqual(mismatches, [], f"Status semantic token mismatches found: {mismatches}")

    def test_structured_facts_protected_from_humanizer(self) -> None:
        """Structured facts (Invocation, Status, package counts) are protected from prose alteration."""
        # 1. Negative test: changing invocation in catalog causes check_catalog_parity to fail
        with tempfile.TemporaryDirectory(prefix="parity-guard-") as tmp:
            tmp_root = Path(tmp)
            # Copy real catalogs into temp dir
            (tmp_root / "CATALOG.md").write_text((ROOT / "CATALOG.md").read_text(encoding="utf-8"), encoding="utf-8")
            # Mutate Chinese catalog to change kanban-worker invocation to 'user'
            zh_corrupted = (ROOT / "CATALOG.zh-CN.md").read_text(encoding="utf-8").replace(
                "### kanban-worker\n\n- **作用：** 在定时运行中认领并执行一张看板任务，优先处理已有修改意见或进行中的工作。\n- **什么时候用：** 调度执行 Light-Kanban 看板任务时。\n- **调用方式：** Model-invoked；支持手动入口。",
                "### kanban-worker\n\n- **作用：** 在定时运行中认领并执行一张看板任务，优先处理已有修改意见或进行中的工作。\n- **什么时候用：** 调度执行 Light-Kanban 看板任务时。\n- **调用方式：** 仅 user-invoked。",
            )
            (tmp_root / "CATALOG.zh-CN.md").write_text(zh_corrupted, encoding="utf-8")
            # Symlink skills directory for authority discovery
            (tmp_root / "skills").symlink_to(ROOT / "skills", target_is_directory=True)

            errs = check_catalog_parity(tmp_root)
            self.assertTrue(any("kanban-worker" in e and "contradicts authority" in e for e in errs),
                            f"Expected invocation mismatch error, got: {errs}")

        # 2. Negative test: degrading status to 'NEW' causes check_catalog_parity to fail
        with tempfile.TemporaryDirectory(prefix="parity-guard-status-") as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "CATALOG.md").write_text((ROOT / "CATALOG.md").read_text(encoding="utf-8"), encoding="utf-8")
            zh_status_degraded = (ROOT / "CATALOG.zh-CN.md").read_text(encoding="utf-8").replace(
                "- **状态：** 第一方已准入（通过 full path review-loop agent-skill PASS）；随 v0.1.6 发布。",
                "- **状态：** 第一方已准入；NEW。",
            )
            (tmp_root / "CATALOG.zh-CN.md").write_text(zh_status_degraded, encoding="utf-8")
            (tmp_root / "skills").symlink_to(ROOT / "skills", target_is_directory=True)

            errs = check_catalog_parity(tmp_root)
            self.assertTrue(any("kb-init" in e and "mismatch" in e for e in errs),
                            f"Expected status mismatch error, got: {errs}")


if __name__ == "__main__":
    unittest.main()
