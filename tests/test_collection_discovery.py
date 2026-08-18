"""Port of tests/collection-discovery-tests.ps1 (1064 assertions).

Also composes the recap and language-learning contract suites exactly like the
PowerShell version dot-sourced them.
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "skills" / "recap" / "tests"))
sys.path.insert(0, str(ROOT / "skills" / "language-learning" / "tests"))
sys.path.insert(0, str(ROOT / "skills" / "light-kanban-worker" / "tests"))

from check_helpers import Checks, read  # noqa: E402
from test_recap_contract import run_checks as recap_checks  # noqa: E402
from test_recap_output_contract import run_checks as recap_output_checks  # noqa: E402
from test_language_learning_contract import run_checks as ll_checks  # noqa: E402
from test_light_kanban_worker_contract import run_checks as worker_contract_checks  # noqa: E402
from test_light_kanban_worker_behavior import run_checks as worker_behavior_checks  # noqa: E402

EXPECTED = [
    "ask-light",
    "kb-init",
    "language-learning",
    "learn-anything",
    "light-kanban-worker",
    "manuscript-ops",
    "project-init",
    "recap",
    "review-loop",
]


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_root = root / "skills"
    actual = sorted(d.name for d in skill_root.iterdir() if d.is_dir() and d.name != "docs")
    c.check(actual == EXPECTED, "skills/ must contain exactly the nine admitted package directories.")

    readme = read(root, "README.md")
    catalog = read(root, "CATALOG.md")
    installation = read(root, "docs/INSTALLATION.md")
    readme_zh = (root / "README.zh-CN.md").read_text(encoding="utf-8", errors="replace")
    catalog_zh = (root / "CATALOG.zh-CN.md").read_text(encoding="utf-8", errors="replace")

    c.check("skills/docs/assets/skills-header.png" in readme, "README must display the repository-local header image.")
    first_non_empty = next((ln for ln in readme.splitlines() if ln.strip()), "")
    c.check(
        bool(re.match(r"^!\[[^\]]+\]\(skills/docs/assets/skills-header\.png\)", first_non_empty)),
        "README header image must be the first non-empty line with alt text.",
    )
    svg_path = root / "skills/docs/assets/skills-header.svg"
    png_path = root / "skills/docs/assets/skills-header.png"
    c.check(svg_path.is_file(), "Editable skills-header.svg is missing.")
    c.check(png_path.is_file(), "Rendered skills-header.png is missing.")
    if svg_path.is_file() and png_path.is_file():
        svg_text = svg_path.read_text(encoding="utf-8", errors="replace")
        png_bytes = png_path.read_bytes()
        c.check(bool(re.search(r"<svg\b", svg_text)) and svg_path.stat().st_size > 100, "Header SVG is not a non-empty SVG document.")
        c.check(
            len(png_bytes) > 100 and png_bytes[0] == 137 and png_bytes[1] == 80 and png_bytes[2] == 78 and png_bytes[3] == 71,
            "Header PNG does not have a valid PNG signature.",
        )
    c.check("npx skills add LightDevCoder/skills --yes --copy --agent '*'" in installation, "Installation guide is missing the generic whole-repository latest install command.")
    c.check("npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'" in installation, "Installation guide is missing the generic per-Skill latest install command.")
    c.check(bool(re.search(r"npx skills add LightDevCoder/skills#v0\.1\.2", installation)), "Installation guide is missing the historical pinned v0.1.2 release command.")
    c.check(bool(re.search(r"npx skills add LightDevCoder/skills#v0\.1\.3", installation)), "Installation guide is missing the historical pinned v0.1.3 release command.")
    c.check(bool(re.search(r"npx skills add LightDevCoder/skills#v0\.1\.4", installation)), "Installation guide is missing the historical pinned v0.1.4 release command.")
    c.check(bool(re.search(r"npx skills add LightDevCoder/skills#v0\.1\.5", installation)), "Installation guide is missing the pinned v0.1.5 release command.")
    c.check(bool(re.search(r"#ref|fragment|default revision", installation)), "Installation guide must explain revision semantics rather than overclaim shorthand immutability.")
    c.check("commands target the immutable v0.1.0 release" not in installation, "Installation guide must not claim the old shorthand is permanently immutable.")
    c.check(not re.search(r"not a verified command|<owner>/<repository>", installation), "Installation guide still contains unresolved pre-release command wording.")
    c.check("Manual fallback" in installation, "Installation guide must retain a manual fallback.")
    c.check(
        all(token in installation for token in ("source_root", "skill_name", "destination_root")),
        "Manual fallback must use valid shell variables.",
    )
    c.check(bool(re.search(r"(?is)v0\.1\.5.{0,160}is published from", readme)), "README must present v0.1.5 as the published release.")
    c.check(bool(re.search(r"(?is)v0\.1\.2.{0,200}seven", readme)), "README must retain the v0.1.2 seven-package history.")
    c.check("9 admitted first-party Skills" in catalog, "Catalog must present the nine-package collection.")
    c.check("Released v0.1.5" in catalog, "Catalog must present v0.1.5 as released.")
    c.check(bool(re.search(r"(?is)v0\.1\.1[^\r\n]{0,80}five", readme)), "README must retain the v0.1.1 five-package history.")
    c.check(bool(re.search(r"light-kanban-worker.{0,200}scheduled", readme, re.IGNORECASE | re.DOTALL)), "README must present light-kanban-worker as the scheduled Light-Kanban worker Skill.")

    for package in EXPECTED:
        package_root = skill_root / package
        skill_file = package_root / "SKILL.md"
        metadata_file = package_root / "agents" / "openai.yaml"
        body = ""
        c.check(skill_file.is_file(), f"{package} is missing SKILL.md.")
        c.check(metadata_file.is_file(), f"{package} is missing agents/openai.yaml.")

        if skill_file.is_file():
            body = skill_file.read_text(encoding="utf-8", errors="replace")
            c.check(
                bool(re.search(rf"(?m)^name:\s*{re.escape(package)}\s*$", body)),
                f"{package} SKILL.md name metadata is inconsistent.",
            )

        if metadata_file.is_file():
            metadata = metadata_file.read_text(encoding="utf-8", errors="replace")
            for field in ("display_name:", "short_description:", "default_prompt:", "allow_implicit_invocation:"):
                c.check(field in metadata, f"{package} metadata is missing {field}.")
            front_explicit = bool(re.search(r"(?m)^disable-model-invocation:\s*true\s*$", body))
            expected_policy = "false" if front_explicit else "true"
            c.check(
                bool(re.search(rf"allow_implicit_invocation:\s*{expected_policy}", metadata)),
                f"{package} invocation policy disagrees with SKILL.md.",
            )

        c.check(f"skills/{package}/" in readme, f"{package} is missing from README.")
        c.check(f"skills/{package}/" in catalog, f"{package} is missing from CATALOG.md.")
        section_match = re.search(rf"(?ms)^### {re.escape(package)}\r?\n(?P<section>.*?)(?=^### |\Z)", catalog)
        section = section_match.group("section") if section_match else ""
        c.check(section_match is not None, f"{package} is missing a catalog section.")
        c.check("- **Invocation:**" in section, f"{package} catalog invocation field is missing.")
        c.check("- **Status:**" in section, f"{package} catalog status field is missing.")
        c.check("- **Installation path:**" in section, f"{package} catalog installation field is missing.")
        c.check("- **Evidence:**" in section, f"{package} catalog evidence field is missing.")
        c.check(
            bool(re.search(rf"\| \[{re.escape(package)}\].*\| (User-invoked|Model-invoked)", readme)),
            f"{package} README invocation type is missing.",
        )

    markdown_files = sorted(str(p.relative_to(root)).replace(os.sep, "/") for p in root.rglob("*.md") if p.is_file())
    for file in markdown_files:
        path = root / file
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            link = m.group(1).split("#")[0]
            if re.match(r"^https?://", link) or not link:
                continue
            resolved = path.parent / link
            c.check(resolved.exists(), f"{file} contains an unresolved Markdown link: {link}")

    retired = 0
    for p in (root / "skills").rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8", errors="replace")
            if "project-workflow" in text or "to-manuscript-spec" in text:
                retired += 1
    c.check(retired == 0, "Retired orchestration references remain under skills/.")

    for required in [
        "AGENTS.md",
        "CATALOG.md",
        "CHANGELOG.md",
        "docs/INSTALLATION.md",
        "docs/MAINTENANCE.md",
        "docs/REVIEW_POLICY.md",
        "docs/SKILL_ADMISSION.md",
        "docs/workflows/README.md",
        "skills/docs/assets/skills-header.json",
        "README.zh-CN.md",
        "CATALOG.zh-CN.md",
        "CHANGELOG.zh-CN.md",
        "docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.md",
        "docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.md",
        "docs/evidence/releases/v0.1.3/RELEASE_RECEIPT.md",
        "docs/evidence/releases/v0.1.4/RELEASE_RECEIPT.md",
        "docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.md",
        "docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.md",
        "docs/evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.md",
        ".github/workflows/quality.yml",
    ]:
        c.check((root / required).is_file(), f"Required documentation path is missing: {required}")

    for en, zh in [
        ("README.md", "README.zh-CN.md"),
        ("CATALOG.md", "CATALOG.zh-CN.md"),
        ("CHANGELOG.md", "CHANGELOG.zh-CN.md"),
        ("docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md"),
        ("docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md"),
        ("docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md"),
        ("docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md"),
    ]:
        en_path, zh_path = root / en, root / zh
        c.check(en_path.is_file(), f"English/Chinese pair is missing: {en}")
        c.check(zh_path.is_file(), f"English/Chinese pair is missing: {zh}")
        if en_path.is_file() and zh_path.is_file():
            en_text = en_path.read_text(encoding="utf-8", errors="replace")
            zh_text = zh_path.read_text(encoding="utf-8", errors="replace")
            c.check(zh.split("/")[-1] in en_text, f"{en} does not link its Chinese counterpart.")
            c.check(en.split("/")[-1] in zh_text, f"{zh} does not link its English counterpart.")

    parity_matrix = [
        ("README.md", "README.zh-CN.md", ["Quick Start", "ask-light", "v0.1.1"]),
        ("CATALOG.md", "CATALOG.zh-CN.md", ["review-loop", "v0.1.1", "skills/"]),
        ("CHANGELOG.md", "CHANGELOG.zh-CN.md", ["v0.1.1", "0.1.0", "release"]),
        ("docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", ["npx skills add", "fresh-install", "SKILL.md"]),
        ("docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md", ["README", "review-loop", "release"]),
        ("docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md", ["review-loop", "PASS", "BLOCKED"]),
        ("docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md", ["review-loop", "PASS", "BLOCKED"]),
    ]
    for en, zh, markers in parity_matrix:
        en_text = read(root, en)
        zh_text = read(root, zh)
        for marker in markers:
            c.check(marker in en_text and marker in zh_text, f"{en} and {zh} are missing the synchronized semantic marker: {marker}")

    for path in ("docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md", "docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md"):
        text = read(root, path)
        c.check(bool(re.search(r"prompt-only|纯提示型", text)), "Admission/review policy must describe the prompt-only fast track.")
        c.check("fresh independent Evaluator" in text, "Fast-track policy must preserve one fresh independent Evaluator.")
        c.check("Critic" in text, "Fast-track policy must state the separate Critic boundary.")
        c.check("code-review" in text, "Fast-track policy must state the code-review boundary.")

    semantic_matrix = [
        ("README.md", "README.zh-CN.md", [("Install the published first-party collection", "安装已发布的第一方集合"), ("Install one Skill at the same published revision", "安装同一已发布版本下的一个 Skill"), ("fresh-install evidence", "fresh-install 证据")]),
        ("CATALOG.md", "CATALOG.zh-CN.md", [("Current state", "当前状态"), ("Stable release", "稳定版本"), ("Installation authority", "安装权威")]),
        ("CHANGELOG.md", "CHANGELOG.zh-CN.md", [("Release evidence", "Release 证据"), ("Historical installation details", "历史安装明细")]),
        ("docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", [("Revision semantics", "Revision 语义"), ("Historical v0.1.0 verification", "历史 v0.1.0 验证"), ("Manual fallback", "手动 fallback")]),
        ("docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md", [("Authoritative records", "权威记录"), ("Synchronization matrix", "变更流程与同步矩阵"), ("closeout", "closeout")]),
        ("docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md", [("Review triggers", "Review triggers"), ("final acceptance", "final acceptance"), ("BLOCKED", "BLOCKED")]),
        ("docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md", [("Admission questions", "Admission questions"), ("Required evidence", "必需 evidence"), ("review-loop", "review-loop")]),
    ]
    for en, zh, pairs in semantic_matrix:
        en_text = read(root, en)
        zh_text = read(root, zh)
        for a, b in pairs:
            c.check(a in en_text and b in zh_text, f"{en} and {zh} are missing the semantic pair: {a} / {b}")

    for name in EXPECTED:
        en_path = root / f"docs/skills/{name}.md"
        zh_path = root / f"docs/zh-CN/skills/{name}.md"
        c.check(en_path.is_file(), f"Skill guide is missing: docs/skills/{name}.md")
        c.check(zh_path.is_file(), f"Chinese Skill guide is missing: docs/zh-CN/skills/{name}.md")
        if en_path.is_file() and zh_path.is_file():
            c.check(f"../zh-CN/skills/{name}.md" in en_path.read_text(encoding="utf-8", errors="replace"), f"{name} English guide does not link its Chinese guide.")
            c.check(f"../../skills/{name}.md" in zh_path.read_text(encoding="utf-8", errors="replace"), f"{name} Chinese guide does not link its English guide.")

    workflow_pairs = [
        ("docs/workflows/README.md", "docs/zh-CN/workflows/README.md"),
        ("docs/workflows/first-party-composition.md", "docs/zh-CN/workflows/first-party-composition.md"),
        ("docs/workflows/recipes.md", "docs/zh-CN/workflows/recipes.md"),
    ]
    for en, zh in workflow_pairs:
        en_path, zh_path = root / en, root / zh
        c.check(en_path.is_file(), f"Workflow document is missing: {en}")
        c.check(zh_path.is_file(), f"Chinese workflow document is missing: {zh}")
        if en_path.is_file() and zh_path.is_file():
            c.check(zh.split("/")[-1] in en_path.read_text(encoding="utf-8", errors="replace"), f"{en} does not link its Chinese counterpart.")
            c.check(en.split("/")[-1] in zh_path.read_text(encoding="utf-8", errors="replace"), f"{zh} does not link its English counterpart.")

    guide_parity = ["SKILL.md", "BLOCKED", "review-loop", "user-invoked"]
    for name in EXPECTED:
        en_path = root / f"docs/skills/{name}.md"
        zh_path = root / f"docs/zh-CN/skills/{name}.md"
        if en_path.is_file() and zh_path.is_file():
            en_text = en_path.read_text(encoding="utf-8", errors="replace")
            zh_text = zh_path.read_text(encoding="utf-8", errors="replace")
            for marker in guide_parity:
                c.check(marker in en_text and marker in zh_text, f"{name} Skill guides are missing the synchronized semantic marker: {marker}")

    secondary_parity = [
        ("docs/workflows/first-party-composition.md", "docs/zh-CN/workflows/first-party-composition.md", ["review-loop", "ask-light"]),
        ("docs/workflows/recipes.md", "docs/zh-CN/workflows/recipes.md", ["review-loop", "ask-light", "PASS", "FAIL", "BLOCKED", "handoff", "stop"]),
    ]
    for en, zh, markers in secondary_parity:
        en_text = read(root, en)
        zh_text = read(root, zh)
        for marker in markers:
            c.check(marker in en_text and marker in zh_text, f"{en} and {zh} are missing the synchronized semantic marker: {marker}")

    for revision in ("v0.1.1", "v0.1.2"):
        for name in ("RELEASE_RECEIPT", "TEST_SUMMARY", "INSTALLATION_VERIFICATION", "DISCOVERY_VERIFICATION", "LIMITATIONS"):
            en_text = read(root, f"docs/evidence/releases/{revision}/{name}.md")
            zh_text = read(root, f"docs/evidence/releases/{revision}/{name}.zh-CN.md")
            markers = [revision, "VERIFIED", "fresh"] if name == "RELEASE_RECEIPT" else [revision, "PASS", "fresh"]
            for marker in markers:
                c.check(marker in en_text and marker in zh_text, f"{name} {revision} release evidence is missing the synchronized semantic marker: {marker}")

    c.check("Drive your creativity" in readme, "README About description is missing.")

    workflow_text = read(root, "skills/ask-light/SKILL.md")
    workflow_script = read(root, "skills/ask-light/scripts/ask-light.ps1")
    c.check("$ask-light next" in workflow_text and "$ask-light workflow" in workflow_text, "ask-light must document both explicit modes.")
    c.check("entryCondition" in workflow_text and "missing dependency" in workflow_text and "finalAuthority" in workflow_text, "ask-light workflow output contract is incomplete.")
    c.check(bool(re.search(r"ValidateSet\('next', 'workflow'\)", workflow_script)) and "Get-WorkflowRecipes" in workflow_script, "ask-light scanner lacks explicit workflow mode implementation.")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", read(root, "skills/learn-anything/agents/openai.yaml"))), "learn-anything must declare explicit-only metadata policy.")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", read(root, "skills/recap/agents/openai.yaml"))), "recap must declare explicit-only metadata policy.")

    documentation_files = ["README.md", "CATALOG.md", "CHANGELOG.md", "AGENTS.md"]
    documentation_files += sorted(
        str(p.relative_to(root)).replace(os.sep, "/") for p in (root / "docs").rglob("*.md") if p.is_file()
    )
    for file in documentation_files:
        path = root / file
        if not path.is_file():
            c.check(False, f"Required documentation file is missing: {file}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            link = m.group(1).split("#")[0]
            if re.match(r"^https?://", link) or not link:
                continue
            resolved = path.parent / link
            c.check(resolved.exists(), f"{file} contains an unresolved relative link: {link}")

    return c.assertions, c.failures


class CollectionDiscoveryTest(unittest.TestCase):
    def test_collection_discovery(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"COLLECTION_DISCOVERY=FAIL: {failures}")


class RecapContractCompositionTest(unittest.TestCase):
    def test_recap_contract_composition(self) -> None:
        assertions, failures = recap_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"RECAP_CONTRACT=FAIL: {failures}")

    def test_recap_output_contract_composition(self) -> None:
        assertions, failures = recap_output_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"RECAP_OUTPUT_CONTRACT=FAIL: {failures}")


class LanguageLearningContractCompositionTest(unittest.TestCase):
    def test_language_learning_contract_composition(self) -> None:
        assertions, failures = ll_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LANGUAGE_LEARNING_CONTRACT=FAIL: {failures}")


class LightKanbanWorkerContractCompositionTest(unittest.TestCase):
    def test_worker_contract_composition(self) -> None:
        assertions, failures = worker_contract_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LIGHT_KANBAN_WORKER_CONTRACT=FAIL: {failures}")


class LightKanbanWorkerBehaviorCompositionTest(unittest.TestCase):
    def test_worker_behavior_composition(self) -> None:
        assertions, failures = worker_behavior_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"LIGHT_KANBAN_WORKER_BEHAVIOR=FAIL: {failures}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
