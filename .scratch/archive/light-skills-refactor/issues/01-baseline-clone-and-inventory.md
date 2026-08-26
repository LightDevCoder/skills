# 01 — Baseline clone and inventory

**What to build:** 克隆并盘点真实 Baseline，为后续所有垂直切片提供可信的起点端到端交付。

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

- [ ] `git clone https://github.com/LightDevCoder/skills.git` 到本地工作目录（本项目即是该仓库的重构目标，检查现有 packages、cross-skill references、tests、README/CATALOG/AGENTS、maintenance docs、review policy、installation docs、Assets/header.png）
- [ ] `git clone https://github.com/LightDevCoder/ELI5.git` 与 `https://github.com/LightDevCoder/release-workflow.git` 作为迁入来源，确认不修改来源仓库
- [ ] 产出 baseline 清单文档（记录当前 11 个 Light baseline Skill 列表、每个 Skill 的 SKILL.md 结构、supporting files、reference 链接、测试位置）
- [ ] 确认 `AGENTS.md:1`、`docs/agents/issue-tracker.md:1`、`docs/agents/domain.md:1` 已指向本地 tracker（`.scratch/light-skills-refactor/`）且可写

## Comments

Source: SPEC.md §2 Starting Point / §25 Phase 1 / §4 Baseline. 本票完成后所有后续票的 Blocked by 01 可解。

### 2026-08-25 — Baseline clone and inventory complete (sub-agent)

- Verified baseline clones exist: `/tmp/skills-baseline` (commit `26110c9`, shallow main, origin LightDevCoder/skills), `/tmp/eli5-src` (+ `/tmp/ELI5`), `/tmp/release-workflow-src`, `/Users/light/.agents/skill-src/mattpocock-skills` — all untouched.
- Bootstrapped working repo `/Users/light/Documents/Projects/Configurations/skills`:
  - `cp -a /tmp/skills-baseline/.git` → target `.git`
  - `rsync -a --exclude='.scratch' --exclude='.git' --exclude='.DS_Store' /tmp/skills-baseline/ → target`
  - Preserve `.scratch/light-skills-refactor/` (13 issues + spec.md), `Assets/header.png` (1767692 B skeleton hero), `docs/agents/` (issue-tracker/domain/triage)
  - Post-bootstrap: `skills/` contains 9 packages (ask-light, docs, kanban-worker, kb-init, language-learning, learn-anything, manuscript-ops, project-init, recap, review-loop) + docs/tests/README/CATALOG etc. alongside `.scratch/`
  - `git status` → On branch main, untracked `.scratch/`, `Assets/`, `docs/agents/` + modified `AGENTS.md` (local tracker note)
  - `git log --oneline -5` → `26110c9 docs: add Chinese release notes pages for v0.1.1-v0.1.5`
  - `ls /tmp/eli5-src/skills/eli5/SKILL.md` and `/tmp/release-workflow-src/SKILL.md` still present — sources not deleted
- Ensured tracker wiring:
  - `AGENTS.md:1` patched with `> Local workspace tracker: .scratch/light-skills-refactor/` note (writable ✅)
  - `docs/agents/issue-tracker.md:1` and `docs/agents/domain.md:1` verified readable & writable ✅ (generic `.scratch/<feature-slug>/` conventions, local effort is `.scratch/light-skills-refactor/`)
  - `docs/agents/triage-labels.md` also verified
- Produced inventory: `.scratch/light-skills-refactor/baseline-inventory.md` (480 lines, 28 KB)
  - Records 9 baseline skills, each with SKILL.md line count/frontmatter/headings, agents/openai.yaml, references, scripts/evals/hooks/assets/templates, tests/fixtures
  - Documents shared header asset `skills/docs/assets/skills-header.{png,svg,json}` + top-level `Assets/header.png`
  - Enumerates README/CATALOG/MAINTENANCE/REVIEW_POLICY/INSTALLATION/ADMISSION, docs/skills, docs/workflows, docs/evidence, examples, tests, cross-skill refs, and file-path index with existence checks
  - Includes verification command output (ls, git, Assets, sources)
- No migrations/ports performed — scope limited to Issue 01 as required.
