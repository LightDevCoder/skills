# v0.2.0 — Light Workflow 33-Skill Architecture 发布说明

[English release receipt](RELEASE_RECEIPT.md)

## 本次更新

Light Skills 发布 v0.2.0，正式引入完整的 33 第一方 Skill 架构体系（从 v0.1.6 的 9 个包扩展至 33 个），涵盖端到端项目工作流、Socratic 澄清引擎、执行与审查架构，以及跨集合工作流顾问 `ask-light`。

## 核心架构演进

1. **项目工作流闭环（Project Workflow）：**
   - `project-init` → `project-clarify` → `project-spec` → `project-tickets` → `implement` → `project-review` → `release-workflow`。
   - 形成清晰的制品交接与边界约束，从项目初始化一直贯穿至发布与审查。

2. **Socratic 澄清与决策引擎：**
   - 核心引擎 `socratic` 提供多轮独立问题探索、选项生成与决策前沿推进。
   - 驱动独立轻量澄清 `clarify`、项目感知澄清 `project-clarify` 与长跨度决策图规划 `decision-map`。

3. **执行与专业审查体系：**
   - `agent-config` 依据宿主环境特征规划安全执行路径。
   - `review-loop` 负责轻量级审阅修复循环；`generic-review` 与 `code-review` 作为只读专家审阅器；`project-review` 统领冻结基线与最终 `PASS`/`FAIL`/`BLOCKED` 裁决。

4. **自包含批准 Port 与溯源归属：**
   - 包含 11 个经批准的自包含 Matt Port，各附 `ATTRIBUTION.md`，无任何上游运行时依赖。
   - `eli5`（源自 `DreambigOu/ELI5`）与 `release-workflow`（源自 `LightDevCoder/release-workflow`）正式纳入统一集合治理，记录完整历史与迁移退役计划。

5. **全集工作流顾问：**
   - `ask-light` 作为贯穿 33 个 Skill 的导航与推荐顾问，支持依据工作区上下文推荐下一步行动。

## 验证与门禁状态

发布候选阶段本地全套自动化测试（Pytest 309 tests、Unittest 27 tests、Compileall、Git diff check 及各子包测试）全部通过。公开发布后将执行 GitHub Actions CI 检查与针对已发布 tag 和 generic latest 的全新隔离环境安装验证。
