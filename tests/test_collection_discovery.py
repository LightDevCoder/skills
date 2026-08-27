"""Port of tests/collection-discovery-tests.ps1 — updated for 33-package refactor.

Also composes the unchanged language-learning contract suite exactly like the
PowerShell version dot-sourced it. The user-amended recap contract is checked by
the functional-closure suite while its frozen historical tests remain untouched.
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "skills" / "language-learning" / "tests"))
sys.path.insert(0, str(ROOT / "skills" / "kanban-worker" / "tests"))

from check_helpers import Checks, read  # noqa: E402
from test_language_learning_contract import run_checks as ll_checks  # noqa: E402
from test_kanban_worker_contract import run_checks as worker_contract_checks  # noqa: E402
from test_kanban_worker_behavior import run_checks as worker_behavior_checks  # noqa: E402

EXPECTED = sorted(
    [
        "agent-config",
        "ask-light",
        "clarify",
        "code-review",
        "decision-map",
        "diagnosing-bugs",
        "eli5",
        "generic-review",
        "handoff",
        "implement",
        "kanban-worker",
        "kb-init",
        "language-learning",
        "learn-anything",
        "manuscript-ops",
        "project-clarify",
        "project-init",
        "project-review",
        "project-spec",
        "project-tickets",
        "prototype",
        "recap",
        "release-workflow",
        "research",
        "resolving-merge-conflicts",
        "review-loop",
        "socratic",
        "tdd",
        "teach",
        "to-questionnaire",
        "wait-what",
        "wizard",
        "writing-for-agents",
    ]
)


def run_checks(root: Path = ROOT) -> tuple[int, list[str]]:
    c = Checks()
    skill_root = root / "skills"
    actual = sorted(d.name for d in skill_root.iterdir() if d.is_dir() and d.name != "docs")
    c.check(actual == EXPECTED, f"skills/ must contain exactly the 33 admitted package directories. got {actual}")

    readme = read(root, "README.md")
    catalog = read(root, "CATALOG.md")
    installation = read(root, "docs/INSTALLATION.md")
    readme_zh = (root / "README.zh-CN.md").read_text(encoding="utf-8", errors="replace")
    catalog_zh = (root / "CATALOG.zh-CN.md").read_text(encoding="utf-8", errors="replace")

    # Hero — new Assets/header.png is the primary hero; legacy header remains for package tests
    c.check("Assets/header.png" in readme, "README must display the new repository hero Assets/header.png.")
    c.check("Assets/header.png" in readme_zh, "README.zh-CN must display the new hero Assets/header.png.")
    first_non_empty = next((ln for ln in readme.splitlines() if ln.strip()), "")
    c.check(
        bool(re.match(r"^!\[[^\]]+\]\(Assets/header\.png\)", first_non_empty)),
        "README header image must be the first non-empty line with alt text pointing to Assets/header.png.",
    )
    first_zh = next((ln for ln in readme_zh.splitlines() if ln.strip() and not ln.startswith("[English")), "")
    # allow [English README] link line before hero
    lines_zh = [ln for ln in readme_zh.splitlines() if ln.strip()]
    hero_line_zh = next((ln for ln in lines_zh if "Assets/header.png" in ln), "")
    c.check(bool(re.match(r"^!\[[^\]]+\]\(Assets/header\.png\)", hero_line_zh)), "README.zh-CN hero must point to Assets/header.png.")
    hero_path = root / "Assets/header.png"
    c.check(hero_path.is_file(), "New hero asset Assets/header.png is missing.")
    if hero_path.is_file():
        data = hero_path.read_bytes()
        c.check(
            len(data) > 100 and data[0] == 137 and data[1] == 80 and data[2] == 78 and data[3] == 71,
            "Hero PNG Assets/header.png does not have a valid PNG signature.",
        )
    # Legacy editable header still required for package-header tests
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
    c.check(bool(re.search(r"npx skills add LightDevCoder/skills#v0\.1\.6", installation)), "Installation guide is missing the pinned v0.1.6 release command.")
    c.check(bool(re.search(r"#ref|fragment|default revision", installation)), "Installation guide must explain revision semantics rather than overclaim shorthand immutability.")
    c.check("commands target the immutable v0.1.0 release" not in installation, "Installation guide must not claim the old shorthand is permanently immutable.")
    c.check(not re.search(r"not a verified command|<owner>/<repository>", installation), "Installation guide still contains unresolved pre-release command wording.")
    c.check("Manual fallback" in installation, "Installation guide must retain a manual fallback.")
    c.check(
        all(token in installation for token in ("source_root", "skill_name", "destination_root")),
        "Manual fallback must use valid shell variables.",
    )
    c.check(bool(re.search(r"(?is)v0\.1\.6.{0,160}is published from", readme)), "README must present v0.1.6 as the published release.")
    c.check("33" in catalog and "admitted" in catalog, "Catalog must present the 33-package collection.")
    c.check("v0.1.6" in catalog, "Catalog must mention v0.1.6.")
    c.check("33" in readme, "README must mention 33 Skills.")
    c.check(bool(re.search(r"ask-light", readme, re.IGNORECASE)), "README must mention ask-light entry.")
    c.check(bool(re.search(r"project-init.*project-clarify.*project-spec.*project-tickets.*implement.*project-review.*release-workflow", readme, re.DOTALL | re.IGNORECASE)), "README must present the main workflow project-init → project-clarify → project-spec → project-tickets → implement → project-review → release-workflow.")

    for package in EXPECTED:
        package_root = skill_root / package
        skill_file = package_root / "SKILL.md"
        # eli5 intentionally has no agents/openai.yaml (migrated, uses frontmatter only) — check only if present
        metadata_file = package_root / "agents" / "openai.yaml"
        body = ""
        c.check(skill_file.is_file(), f"{package} is missing SKILL.md.")
        # metadata required for all except eli5 which is a migrated explain skill without host policy
        if package != "eli5":
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

        c.check(f"skills/{package}/" in catalog, f"{package} is missing from CATALOG.md.")
        section_match = re.search(rf"(?ms)^### {re.escape(package)}\r?\n(?P<section>.*?)(?=^### |\Z)", catalog)
        section = section_match.group("section") if section_match else ""
        c.check(section_match is not None, f"{package} is missing a catalog section.")
        c.check("- **Invocation:**" in section or "- **调用：**" in section, f"{package} catalog invocation field is missing.")
        c.check("- **Status:**" in section or "- **状态：**" in section, f"{package} catalog status field is missing.")
        c.check("- **Installation path:**" in section or "- **安装路径：**" in section, f"{package} catalog installation field is missing.")
        c.check("- **Evidence:**" in section or "- **证据：**" in section, f"{package} catalog evidence field is missing.")
        # README no longer lists all 33 in a table; check that at least representative mention or catalog link covers it
        # Keep soft check: README should at least mention the main workflow skills explicitly
        if package in ("project-init", "project-clarify", "project-spec", "project-tickets", "implement", "project-review", "ask-light"):
            c.check(package in readme, f"{package} is missing from README main workflow.")

    # Link resolution — skip local workspace tracker and placeholder example links
    markdown_files = sorted(str(p.relative_to(root)).replace(os.sep, "/") for p in root.rglob("*.md") if p.is_file())
    markdown_files = [f for f in markdown_files if not f.startswith(".scratch/") and not f.startswith(".git/")]
    for file in markdown_files:
        path = root / file
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            link = m.group(1).split("#")[0].strip()
            if re.match(r"^https?://", link) or not link:
                continue
            # skip placeholder / example links that are intentionally not real files
            if "NN-" in link or link.endswith("issues/01-domain-boundary.md") or link.endswith("issues/02-clarification-family-shape.md"):
                continue
            # skip external-like references to skills-3rdParty private repo (not a local path)
            if "skills-3rdParty" in link:
                continue
            # skip template placeholders
            if link.startswith("<") or link.startswith("$"):
                continue
            # skip absolute-like assets that are handled separately
            resolved = path.parent / link
            # if link is absolute from root like Assets/header.png, resolve from root
            if link.startswith("Assets/") or link.startswith("skills/docs/assets/"):
                resolved = root / link
            # normalize
            try:
                exists = resolved.exists()
            except Exception:
                exists = False
            c.check(exists, f"{file} contains an unresolved Markdown link: {link}")

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
        "docs/REVIEWER_CONTRACT.md",
        "docs/workflows/README.md",
        "docs/workflows/project-workflow.md",
        "docs/workflows/clarification-system.md",
        "docs/workflows/execution.md",
        "docs/workflows/review-system.md",
        "docs/workflows/specialized-workflows.md",
        "skills/docs/assets/skills-header.json",
        "Assets/header.png",
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
        "docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.md",
        "docs/evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.md",
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
        ("docs/workflows/project-workflow.md", "docs/zh-CN/workflows/project-workflow.md"),
        ("docs/workflows/clarification-system.md", "docs/zh-CN/workflows/clarification-system.md"),
        ("docs/workflows/execution.md", "docs/zh-CN/workflows/execution.md"),
        ("docs/workflows/review-system.md", "docs/zh-CN/workflows/review-system.md"),
        ("docs/workflows/specialized-workflows.md", "docs/zh-CN/workflows/specialized-workflows.md"),
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
        ("README.md", "README.zh-CN.md", ["ask-light", "33", "skills/"]),
        ("CATALOG.md", "CATALOG.zh-CN.md", ["review-loop", "33", "skills/"]),
        ("CHANGELOG.md", "CHANGELOG.zh-CN.md", ["33", "ATTRIBUTION", "review-loop"]),
        ("docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", ["npx skills add", "fresh-install", "SKILL.md"]),
        ("docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md", ["ATTRIBUTION", "review-loop", "Port"]),
        ("docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md", ["review-loop", "PASS", "BLOCKED", "project-review"]),
        ("docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md", ["ATTRIBUTION", "Port", "review-loop"]),
        ("docs/workflows/project-workflow.md", "docs/zh-CN/workflows/project-workflow.md", ["project-init", "project-spec", "implement"]),
        ("docs/workflows/clarification-system.md", "docs/zh-CN/workflows/clarification-system.md", ["socratic", "clarify"]),
        ("docs/workflows/review-system.md", "docs/zh-CN/workflows/review-system.md", ["review-loop", "generic-review", "project-review"]),
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
        ("README.md", "README.zh-CN.md", [("Light Skills", "Light Skills"), ("ask-light", "ask-light"), ("Assets/header.png", "Assets/header.png")]),
        ("CATALOG.md", "CATALOG.zh-CN.md", [("Collection status", "集合状态"), ("Stable release", "稳定版本"), ("Installation authority", "安装权威")]),
        ("CHANGELOG.md", "CHANGELOG.zh-CN.md", [("Unreleased", "未发布"), ("ATTRIBUTION", "ATTRIBUTION")]),
        ("docs/INSTALLATION.md", "docs/INSTALLATION.zh-CN.md", [("Revision semantics", "Revision 语义"), ("Historical v0.1.0 verification", "历史 v0.1.0 验证"), ("Manual fallback", "手动 fallback")]),
        ("docs/MAINTENANCE.md", "docs/MAINTENANCE.zh-CN.md", [("Authoritative records", "权威记录"), ("Synchronization matrix", "同步矩阵"), ("closeout", "closeout")]),
        ("docs/REVIEW_POLICY.md", "docs/REVIEW_POLICY.zh-CN.md", [("Reviewer vs review-loop vs project-review", "Reviewer vs review-loop vs project-review"), ("project-review", "project-review"), ("BLOCKED", "BLOCKED")]),
        ("docs/SKILL_ADMISSION.md", "docs/SKILL_ADMISSION.zh-CN.md", [("Ownership gate", "ownership gate"), ("Approved PORT", "已批准"), ("review-loop", "review-loop")]),
    ]
    for en, zh, pairs in semantic_matrix:
        en_text = read(root, en)
        zh_text = read(root, zh)
        for a, b in pairs:
            c.check(a in en_text and b in zh_text, f"{en} and {zh} are missing the semantic pair: {a} / {b}")

    # Skill guides — only check those that exist; not every new skill has a docs/skills guide yet
    for name in ("ask-light", "kanban-worker", "kb-init", "language-learning", "learn-anything", "manuscript-ops", "project-init", "recap", "review-loop"):
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
        ("docs/workflows/project-workflow.md", "docs/zh-CN/workflows/project-workflow.md"),
        ("docs/workflows/clarification-system.md", "docs/zh-CN/workflows/clarification-system.md"),
        ("docs/workflows/execution.md", "docs/zh-CN/workflows/execution.md"),
        ("docs/workflows/review-system.md", "docs/zh-CN/workflows/review-system.md"),
        ("docs/workflows/specialized-workflows.md", "docs/zh-CN/workflows/specialized-workflows.md"),
    ]
    for en, zh in workflow_pairs:
        en_path, zh_path = root / en, root / zh
        c.check(en_path.is_file(), f"Workflow document is missing: {en}")
        c.check(zh_path.is_file(), f"Chinese workflow document is missing: {zh}")
        if en_path.is_file() and zh_path.is_file():
            c.check(zh.split("/")[-1] in en_path.read_text(encoding="utf-8", errors="replace"), f"{en} does not link its Chinese counterpart.")
            c.check(en.split("/")[-1] in zh_path.read_text(encoding="utf-8", errors="replace"), f"{zh} does not link its English counterpart.")

    guide_parity = ["SKILL.md", "BLOCKED", "project-review", "user-invoked"]
    for name in ("ask-light", "kanban-worker", "kb-init", "language-learning", "learn-anything", "manuscript-ops", "project-init", "recap", "review-loop"):
        en_path = root / f"docs/skills/{name}.md"
        zh_path = root / f"docs/zh-CN/skills/{name}.md"
        if en_path.is_file() and zh_path.is_file():
            en_text = en_path.read_text(encoding="utf-8", errors="replace")
            zh_text = zh_path.read_text(encoding="utf-8", errors="replace")
            markers = ["SKILL.md", "$recap", "user-invoked"] if name == "recap" else guide_parity
            for marker in markers:
                c.check(marker in en_text and marker in zh_text, f"{name} Skill guides are missing the synchronized semantic marker: {marker}")

    secondary_parity = [
        ("docs/workflows/first-party-composition.md", "docs/zh-CN/workflows/first-party-composition.md", ["review-loop", "ask-light"]),
        ("docs/workflows/recipes.md", "docs/zh-CN/workflows/recipes.md", ["review-loop", "ask-light", "PASS", "FAIL", "BLOCKED", "handoff", "stop"]),
        ("docs/workflows/project-workflow.md", "docs/zh-CN/workflows/project-workflow.md", ["project-clarify", "implement", "project-review"]),
        ("docs/workflows/clarification-system.md", "docs/zh-CN/workflows/clarification-system.md", ["socratic", "decision-map"]),
        ("docs/workflows/execution.md", "docs/zh-CN/workflows/execution.md", ["implement", "agent-config"]),
        ("docs/workflows/review-system.md", "docs/zh-CN/workflows/review-system.md", ["generic-review", "project-review"]),
        ("docs/workflows/specialized-workflows.md", "docs/zh-CN/workflows/specialized-workflows.md", ["manuscript-ops", "kb-init"]),
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

    workflow_text = read(root, "skills/ask-light/SKILL.md") + read(root, "skills/ask-light/references/discovery-contract.md")
    workflow_script = read(root, "skills/ask-light/scripts/ask_light.py")
    workflow_map = read(root, "skills/ask-light/references/light-skill-map.json")
    c.check("$ask-light next" in workflow_text and "$ask-light workflow" in workflow_text, "ask-light must document both explicit modes.")
    c.check("entryCondition" in workflow_text and "missing dependency" in workflow_text and "finalAuthority" in workflow_text, "ask-light workflow output contract is incomplete.")
    c.check('choices=("next", "workflow", "navigate")' in workflow_script and '"workflows"' in workflow_map and '"skillFamilies"' in workflow_map, "ask-light router lacks explicit workflow/navigation mode implementation.")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", read(root, "skills/learn-anything/agents/openai.yaml"))), "learn-anything must declare explicit-only metadata policy.")
    c.check(bool(re.search(r"allow_implicit_invocation:\s*false", read(root, "skills/recap/agents/openai.yaml"))), "recap must declare explicit-only metadata policy.")

    # Additional SPEC §24 checks: no Matt/sol runtime dependency, ATTRIBUTION, supporting refs resolve
    for skill in ("research", "prototype", "tdd", "handoff", "diagnosing-bugs", "wizard", "teach", "wait-what", "to-questionnaire", "writing-for-agents", "resolving-merge-conflicts"):
        c.check((root / f"skills/{skill}/ATTRIBUTION.md").is_file(), f"PORT {skill} must have ATTRIBUTION.md.")
        text = read(root, f"skills/{skill}/SKILL.md")
        # Ensure no hard requirement to install upstream at runtime
        c.check("install mattpocock/skills" not in text.lower() and "requires matt" not in text.lower(), f"{skill} must not require Matt runtime install.")

    c.check("sol-advisor" not in read(root, "skills/agent-config/SKILL.md").lower() or "sol advisor" in read(root, "skills/agent-config/SKILL.md").lower(), "agent-config should reference Sol Advisor as design reference, not a runtime dependency claim.")
    # Ensure agent-config does not hardcode Sol/Terra/Luna topology
    ac_text = read(root, "skills/agent-config/SKILL.md")
    c.check("Terra" not in ac_text and "Luna" not in ac_text, "agent-config must not hardcode Sol/Terra/Luna topology.")

    # Supporting-file reference resolution for a sample of new skills
    for pkg in ("clarify", "project-clarify", "decision-map", "project-spec", "project-tickets", "implement", "code-review", "socratic"):
        skill_md = read(root, f"skills/{pkg}/SKILL.md")
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", skill_md):
            link = m.group(2).split("#")[0].strip()
            if link.startswith("http"):
                continue
            if link.startswith("references/") or link.startswith("templates/") or link.startswith("scripts/"):
                resolved = root / f"skills/{pkg}" / link.split("#")[0]
                c.check(resolved.exists(), f"{pkg}/SKILL.md references missing file: {link}")

    # Workflow docs must reference real Skills
    workflow_text_all = " ".join(read(root, p) for p in ["docs/workflows/project-workflow.md", "docs/workflows/clarification-system.md", "docs/workflows/execution.md", "docs/workflows/review-system.md", "docs/workflows/specialized-workflows.md"])
    for required_skill in ("project-init", "project-clarify", "project-spec", "project-tickets", "implement", "project-review", "socratic", "clarify", "decision-map", "research", "prototype", "to-questionnaire", "agent-config", "review-loop", "generic-review", "code-review", "manuscript-ops", "kb-init"):
        c.check(required_skill in workflow_text_all, f"Workflow docs must reference real Skill: {required_skill}")

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
            # skip placeholder links handled above
            if "NN-" in link:
                continue
            resolved = path.parent / link
            # handle root-relative Assets
            if link.startswith("Assets/") or link.startswith("skills/docs/assets/"):
                resolved = root / link
            try:
                exists = resolved.exists()
            except Exception:
                exists = False
            c.check(exists, f"{file} contains an unresolved relative link: {link}")

    return c.assertions, c.failures


class CollectionDiscoveryTest(unittest.TestCase):
    def test_collection_discovery(self) -> None:
        assertions, failures = run_checks()
        self.assertGreater(assertions, 0)
        self.assertFalse(failures, f"COLLECTION_DISCOVERY=FAIL: {failures}")


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
