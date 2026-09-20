"""Unit and regression tests for scripts/check_public_docs.py."""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
