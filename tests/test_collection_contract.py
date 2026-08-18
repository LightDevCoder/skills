from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"ask-light", "kb-init", "language-learning", "learn-anything", "light-kanban-worker", "manuscript-ops", "project-init", "recap", "review-loop"}


class CollectionContractTests(unittest.TestCase):
    assertions = 0

    def check(self, condition: bool, message: str) -> None:
        type(self).assertions += 1
        self.assertTrue(condition, message)

    def test_exact_packages_and_metadata_policy(self) -> None:
        actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir() and path.name != "docs"}
        self.check(actual == EXPECTED, f"unexpected first-party package set: {sorted(actual)}")
        for name in sorted(EXPECTED):
            skill = ROOT / "skills" / name
            body = (skill / "SKILL.md").read_text(encoding="utf-8")
            metadata = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.check(re.search(rf"^name:\s*{re.escape(name)}\s*$", body, re.M) is not None, f"{name} frontmatter name")
            for field in ("display_name:", "short_description:", "default_prompt:", "allow_implicit_invocation:"):
                self.check(field in metadata, f"{name} metadata field {field}")
            explicit = re.search(r"^disable-model-invocation:\s*true\s*$", body, re.M) is not None
            expected = "false" if explicit else "true"
            self.check(re.search(rf"allow_implicit_invocation:\s*{expected}\s*$", metadata, re.M) is not None, f"{name} invocation policy")

    def test_release_docs_and_quick_start(self) -> None:
        paths = [
            "README.md", "README.zh-CN.md", "CATALOG.md", "CATALOG.zh-CN.md",
            "CHANGELOG.md", "CHANGELOG.zh-CN.md", "docs/INSTALLATION.md",
            "docs/INSTALLATION.zh-CN.md", "docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md",
            "docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md",
            "docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md",
            "docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.md",
            "docs/workflows/recipes.md", "docs/zh-CN/workflows/recipes.md",
            "examples/quick-start/README.md", "examples/quick-start/README.zh-CN.md",
        ]
        for relative in paths:
            self.check((ROOT / relative).is_file(), f"missing required file {relative}")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        catalog = (ROOT / "CATALOG.md").read_text(encoding="utf-8")
        installation = (ROOT / "docs/INSTALLATION.md").read_text(encoding="utf-8")
        admission = (ROOT / "docs/SKILL_ADMISSION.md").read_text(encoding="utf-8")
        admission_zh = (ROOT / "docs/SKILL_ADMISSION.zh-CN.md").read_text(encoding="utf-8")
        review_policy = (ROOT / "docs/REVIEW_POLICY.md").read_text(encoding="utf-8")
        review_policy_zh = (ROOT / "docs/REVIEW_POLICY.zh-CN.md").read_text(encoding="utf-8")
        self.check("npx skills add LightDevCoder/skills --yes --copy --agent '*'" in readme, "README generic latest whole install")
        self.check("npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'" in installation, "installation generic latest per-Skill install")
        self.check("npx skills add LightDevCoder/skills#v0.1.2" in installation, "installation historical pinned v0.1.2 install")
        self.check("npx skills add LightDevCoder/skills#v0.1.3" in installation, "installation historical pinned v0.1.3 install")
        self.check("npx skills add LightDevCoder/skills#v0.1.4" in installation, "installation historical pinned v0.1.4 install")
        self.check("npx skills add LightDevCoder/skills#v0.1.5" in installation, "installation pinned v0.1.5 install")
        self.check("default revision" in installation and "#ref" in installation, "installation revision semantics")
        self.check("LightDevCoder/skills" in readme and "Drive your creativity" in readme, "homepage about copy")
        self.check(re.search(r"v0\.1\.5.{0,160}is published from", readme, re.I | re.S) is not None, "README published v0.1.5 release")
        self.check(re.search(r"v0\.1\.2.{0,200}seven", readme, re.I | re.S) is not None, "README v0.1.2 seven-package history")
        self.check("9 admitted first-party Skills" in catalog, "catalog nine-package boundary")
        self.check("Released v0.1.5" in catalog, "catalog released v0.1.5 framing")
        for label, text in (("admission", admission), ("admission zh-CN", admission_zh),
                            ("review policy", review_policy), ("review policy zh-CN", review_policy_zh)):
            self.check(re.search(r"prompt-only|纯提示型", text) is not None, f"{label} prompt-only fast track")
            self.check("fresh independent Evaluator" in text, f"{label} independent evaluator boundary")
            self.check("Critic" in text and "code-review" in text, f"{label} omitted specialist boundaries")

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"COLLECTION_PYTHON_ASSERTIONS={cls.assertions}")


if __name__ == "__main__":
    unittest.main()
