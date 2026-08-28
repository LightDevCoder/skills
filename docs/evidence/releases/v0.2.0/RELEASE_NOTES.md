# v0.2.0 — Light Workflow 33-Skill Architecture

[中文发布说明 (Chinese Release Notes)](#中文发布说明) · [Release Receipt](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.0/RELEASE_RECEIPT.md)

## What's new

Light Skills v0.2.0 introduces the complete 33 first-party Skill architecture (expanded from 9 packages in v0.1.6 to 33 packages), covering end-to-end project development workflows, the Socratic clarification engine, execution and review subsystems, and the comprehensive collection advisor `ask-light`.

## Core Architecture Evolution

1. **Project Workflow Lifecycle:**
   - Standardized lifecycle: `project-init` → `project-clarify` → `project-spec` → `project-tickets` → `implement` → `project-review` → `release-workflow`.
   - Clear input/output contracts and artifact handoff boundaries at each stage, supporting both end-to-end delivery and single-stage invocation.

2. **Socratic Clarification & Decision Engine:**
   - Core engine `socratic` powers independent multi-round questions and option frontier exploration.
   - Powers lightweight clarification `clarify`, engineering-aware `project-clarify`, and multi-session `decision-map`.

3. **Execution & Specialist Review Subsystems:**
   - `agent-config` inspects host environment evidence to plan safe execution paths.
   - `review-loop` provides lightweight review-repair convergence; `generic-review` and `code-review` act as read-only specialist reviewers; `project-review` governs frozen baselines and final verdicts (`PASS`/`FAIL`/`BLOCKED`).

4. **Self-Contained Approved Ports & Provenance:**
   - 11 approved self-contained Matt Ports with `ATTRIBUTION.md` and zero upstream runtime dependencies.
   - Incorporated `eli5` (from `DreambigOu/ELI5`) and `release-workflow` (from `LightDevCoder/release-workflow`) into unified collection governance with complete migration and retirement records.

5. **Collection Advisor:**
   - `ask-light` serves as the read-only router and workflow advisor across all 33 Skills, suggesting next actions based on workspace context.

## Installation & Verification

- **Interactive Install (Recommended):**
  ```bash
  npx skills add LightDevCoder/skills
  ```
- **Pinned Stable Release:**
  ```bash
  npx skills add LightDevCoder/skills#v0.2.0
  ```
- **Single Skill Example:**
  ```bash
  npx skills add LightDevCoder/skills --skill project-review
  ```

**Verification:** Local automated test suites (309 pytest, 27 unittest, compileall, git diff check) and GitHub Actions CI (Run ID `33137041472`) all PASS. Fresh isolated environment tests verified generic latest and pinned `#v0.2.0` across whole-collection and all 33 individual package install matrices (66/66 PASS).

---

## 中文发布说明

[English Release Notes](#v020--light-workflow-33-skill-architecture) · [中文发布收据](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/releases/v0.2.0/RELEASE_RECEIPT.zh-CN.md)

### 本次更新

Light Skills 正式发布 v0.2.0，引入完整的 33 个第一方 Skill 架构（由 v0.1.6 的 9 个包扩展至 33 个），覆盖端到端项目开发流程、Socratic 澄清引擎、执行与审查架构，以及全集合工作流顾问 `ask-light`。

### 核心架构演进

1. **项目工作流闭环（Project Workflow）：**
   - 形成 `project-init` → `project-clarify` → `project-spec` → `project-tickets` → `implement` → `project-review` → `release-workflow` 的标准化链路。
   - 各阶段均具备明确的输入输出契约与工件交接边界，支持从头执行或中途切入。

2. **Socratic 澄清与决策引擎：**
   - 核心引擎 `socratic` 提供多轮独立问题探索与选项前沿推进。
   - 统一驱动轻量连续澄清 `clarify`、工程感知澄清 `project-clarify` 与跨会话决策规划 `decision-map`。

3. **执行与专业审查体系：**
   - `agent-config` 依据宿主环境特征规划安全执行方案。
   - `review-loop` 负责轻量级审阅修复循环；`generic-review` 与 `code-review` 作为只读专家审阅器；`project-review` 统领冻结基线与最终验收裁决（`PASS`/`FAIL`/`BLOCKED`）。

4. **自包含批准 Port 与溯源归属：**
   - 包含 11 个经批准的自包含 Matt Port，各附 `ATTRIBUTION.md`，无任何上游运行时依赖。
   - `eli5`（源自 `DreambigOu/ELI5`）与 `release-workflow`（源自 `LightDevCoder/release-workflow`）正式纳入统一集合治理，记录完整历史与迁移退役计划。

5. **全集工作流顾问：**
   - `ask-light` 作为贯穿 33 个 Skill 的只读导航与推荐顾问，支持依据工作区上下文推荐下一步行动。

### 安装与验证

- **交互式安装（推荐）：**
  ```bash
  npx skills add LightDevCoder/skills
  ```
- **指定稳定版本：**
  ```bash
  npx skills add LightDevCoder/skills#v0.2.0
  ```
- **单 Skill 安装示例：**
  ```bash
  npx skills add LightDevCoder/skills --skill project-review
  ```

验证结果：本地全套自动化测试（Pytest 309 tests、Unittest 27 tests、Compileall、Git diff check）与 GitHub Actions CI（Run ID `33137041472`）全部通过。在全新隔离环境中实测 generic latest 与 pinned `#v0.2.0` 全集合及全部 33 个单个包安装矩阵，66/66 全部验证通过。
