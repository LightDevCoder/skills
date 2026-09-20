# 第一方 Skill 目录

[English catalog](CATALOG.md)

本目录从 `skills/` 下 36 个已准入包同步生成，是可读 inventory，不是静态 workflow router，也不代表某个 Agent host 当前已安装哪些 Skill。包的 `SKILL.md` 仍是行为权威。

[按分类浏览](skills/README.zh-CN.md) · [路径迁移](docs/CATEGORY_MIGRATION.zh-CN.md)

## 集合状态

| 字段 | 值 |
| --- | --- |
| 集合 | Light Skills — Composable Agent Workflows |
| 包数量 | 36 个已准入第一方 Skill |
| 当前状态 | main 包含 36 个包；v0.2.3 为当前最新稳定版本 |
| 稳定版本 | [v0.2.3](https://github.com/LightDevCoder/skills/releases/tag/v0.2.3)（36 个包；上一稳定版为 v0.2.2） |
| 安装权威 | [docs/INSTALLATION.zh-CN.md](docs/INSTALLATION.zh-CN.md) |
| 发现检查 | [tests/test_collection_discovery.py](tests/test_collection_discovery.py) · [tests/test_composition.py](tests/test_composition.py) |
| 证据 | [v0.2.3 发布清单](docs/evidence/releases/v0.2.3/RELEASE_MANIFEST.zh-CN.md) · [v0.2.3 发布收据](docs/evidence/releases/v0.2.3/RELEASE_RECEIPT.zh-CN.md) |

`v0.1.1` 发布五个包；`v0.1.2` 增加 `recap` 与 `language-learning`（七个）；`v0.1.3` 迁移测试工具链；`v0.1.4` 增加 `kanban-worker`；`v0.1.5` 收紧看板调度与身份；`v0.1.6` 增加 `kb-init`（九个）。`v0.2.0` 正式发布涵盖项目工作流、澄清、执行、审阅与专项工具的完整 33 包架构，随后 v0.2.0 发布线扩展了 `humanizer` 准入（34 个包；见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)）。`v0.2.1` 增加 `light-travelpage` 与 `project-retro`（36 个包）。`v0.2.2` 最终收敛 TypeSafe Jev 语义加速、分类目录架构与不可变发布完整性。`v0.2.3` 拆分发布前不可变清单与发布后验证收据，追加 v0.2.2 历史事实证明，完成 project-retro 正向状态驱动重构，并形式化六阶段发布生命周期。

本表无未修改的上游复制。获批的 Matt PORT 均带 `ATTRIBUTION.md` 且无需上游运行时依赖。

## 已准入 Skill

### agent-config

- **作用：** 探测当前 Agent 宿主环境与任务要求，为任务配置合适的模型梯队、推理强度与执行拓扑，支持 10 款主流 Agent 框架及伴随 MCP。
- **调用：** Model-invoked。
- **包：** [skills/engineering/agent-config/](skills/engineering/agent-config)
- **状态：** 第一方已准入；REFACTOR（参照 Sol Advisor 设计理念，Profile 驱动跨 Harness 执行配置器，覆盖主要编码 Agent Harness [10 种原生适配器 + 1 种通用回退]）。
- **证据：** [host-evidence-schema.md](skills/engineering/agent-config/references/host-evidence-schema.md)、[plan-schema.md](skills/engineering/agent-config/references/plan-schema.md)、[task-assessment.md](skills/engineering/agent-config/references/task-assessment.md)、[profile-schema.md](skills/engineering/agent-config/references/profile-schema.md)、[companion-contract.md](skills/engineering/agent-config/references/companion-contract.md)、[harness-support.md](skills/engineering/agent-config/references/harness-support.md)、[provider-adapter-contract.md](skills/engineering/agent-config/references/provider-adapter-contract.md)；Companion 运行时维护于 [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config)。
- **安装路径：** `<skills-root>/agent-config/`。

### ask-light

- **作用：** 作为 Light 工作流顾问、导航器与路由入口：检查项目与工作流状态，推荐下一步 Skill 并给出理由，用户批准后安全转换（支持可选 TypeSafe Jev System One 语义加速）。
- **调用：** 仅 user-invoked；批准前只读。批准后支持的环境下可直接开始 model-invoked 目标，user-invoked 目标遵循 Host 转换策略并在缺少直接通道时渲染精确调用。
- **包：** [skills/productivity/ask-light/](skills/productivity/ask-light)
- **状态：** 第一方已准入；REFACTOR（在完整 Skill map 建好后最后构建）。
- **证据：** [skills/productivity/ask-light/tests/](skills/productivity/ask-light/tests) 与 [使用指南](docs/zh-CN/skills/ask-light.md)。
- **安装路径：** `<skills-root>/ask-light/`。

### clarify

- **作用：** 针对模糊的想法、设想或流程开展多轮问答，每次给出几个针对性选项供你选择，快速理清思路（无需建立完整项目）。
- **调用：** 仅 user-invoked。
- **包：** [skills/thinking/clarify/](skills/thinking/clarify)
- **状态：** 第一方已准入；ADAPT（Matt `grill-me` → Light，经 `socratic`）。
- **证据：** [SKILL.md](skills/thinking/clarify/SKILL.md) 与 [ATTRIBUTION.md](skills/thinking/clarify/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/clarify/`。

### code-review

- **作用：** 代码审查专员：对比变更代码（`git diff`），从规范标准与业务规格两个维度检查潜在问题，仅输出问题清单而不直接修改代码。
- **调用：** Model-invoked；只读，不修复也不裁决。
- **包：** [skills/review/code-review/](skills/review/code-review)
- **状态：** 第一方已准入；ADAPT（保留 Matt `code-review` 的双轴方法）。
- **证据：** [references/WORKFLOW.md](skills/review/code-review/references/WORKFLOW.md) 与 [ATTRIBUTION.md](skills/review/code-review/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/code-review/`。

### decision-map

- **作用：** 当任务庞大且跨多轮会话时，将待决策事项梳理为一张有依赖关系的决策图谱。
- **调用：** 仅 user-invoked。
- **包：** [skills/thinking/decision-map/](skills/thinking/decision-map)
- **状态：** 第一方已准入；ADAPT（Matt `wayfinder`）。
- **证据：** [references/MAP-CONTRACT.md](skills/thinking/decision-map/references/MAP-CONTRACT.md)。
- **安装路径：** `<skills-root>/decision-map/`。

### diagnosing-bugs

- **作用：** 针对复杂 Bug 和性能回退进行系统性排查，通过建立紧凑反馈信号快速定位根因。
- **调用：** Model-invoked。
- **包：** [skills/engineering/diagnosing-bugs/](skills/engineering/diagnosing-bugs)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/diagnosing-bugs/SKILL.md)。
- **安装路径：** `<skills-root>/diagnosing-bugs/`。

### eli5

- **作用：** 按指定受众水平解释任意主题、代码或错误。
- **调用：** Model-invoked。
- **包：** [skills/knowledge/eli5/](skills/knowledge/eli5)
- **状态：** 第一方已准入；MIGRATE — NO REWRITE（源自上游 `DreambigOu/ELI5` @ `a766623`，经临时迁移 fork `LightDevCoder/ELI5`）。
- **证据：** [SKILL.md](skills/knowledge/eli5/SKILL.md)、[ATTRIBUTION.md](skills/knowledge/eli5/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/eli5/`。

### generic-review

- **作用：** 通用文档与制品审阅：检查非代码产物（文档、配置、计划）中的遗漏、事实矛盾、格式错误或体验缺陷。
- **调用：** Model-invoked；只读，不裁决。
- **包：** [skills/review/generic-review/](skills/review/generic-review)
- **状态：** 第一方已准入；NEW。
- **证据：** [SKILL.md](skills/review/generic-review/SKILL.md)。
- **安装路径：** `<skills-root>/generic-review/`。

### handoff

- **作用：** 将当前会话压缩为下一 agent 的交接文档。
- **调用：** 仅 user-invoked。
- **包：** [skills/productivity/handoff/](skills/productivity/handoff)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/productivity/handoff/SKILL.md)。
- **安装路径：** `<skills-root>/handoff/`。

### humanizer

- **作用：** 将带有 AI 痕迹的中英文文本改写为自然行文，且不改变原意。
- **调用：** Model-invoked。
- **包：** [skills/writing/humanizer/](skills/writing/humanizer)
- **状态：** 第一方已准入，full-path `PASS`；v0.2.0 线发布；ADAPT 自 blader/humanizer（2.11.2）+ 薄中文适配，MIT 归属保留。
- **证据：** [SKILL.md](skills/writing/humanizer/SKILL.md)、[准入记录](docs/evidence/admissions/humanizer/README.zh-CN.md)。
- **安装路径：** `<skills-root>/humanizer/`。

### implement

- **作用：** 执行单个已确认的任务（代码、文档或配置），完成本地验证并提交审查。
- **调用：** 仅 user-invoked。
- **包：** [skills/project/implement/](skills/project/implement)
- **状态：** 第一方已准入；ADAPT（Matt `implement` → 通用执行器）。
- **证据：** [references/WORKFLOW.md](skills/project/implement/references/WORKFLOW.md)。
- **安装路径：** `<skills-root>/implement/`。

### kanban-worker

- **作用：** 在定时运行中认领并执行一张看板任务，优先处理已有修改意见或进行中的工作。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/project/kanban-worker/](skills/project/kanban-worker)
- **状态：** 第一方已准入；经完整路径（`review-loop agent-skill` PASS）；v0.1.6 由 `light-kanban-worker` 改名。
- **证据：** [skills/project/kanban-worker/tests/](skills/project/kanban-worker/tests) 与 [使用指南](docs/zh-CN/skills/kanban-worker.md)。
- **安装路径：** `<skills-root>/kanban-worker/`。

### kb-init

- **作用：** 通过专属访谈设计并初始化可维护知识库，获批后才实施。
- **调用：** 仅 user-invoked。
- **包：** [skills/knowledge/kb-init/](skills/knowledge/kb-init)
- **状态：** 第一方已准入；完整路径 `PASS`，随 v0.1.6 发布。
- **证据：** [skills/knowledge/kb-init/tests/](skills/knowledge/kb-init/tests)。
- **安装路径：** `<skills-root>/kb-init/`。

### language-learning

- **作用：** 通过六种模式辅导任意语言——课程、卡片、对话、语法、测验与沉浸。
- **调用：** 仅 user-invoked。
- **包：** [skills/knowledge/language-learning/](skills/knowledge/language-learning)
- **状态：** 第一方已准入；纯提示型快速通道 `PASS`，v0.1.2 发布。
- **证据：** [skills/knowledge/language-learning/tests/](skills/knowledge/language-learning/tests)。
- **安装路径：** `<skills-root>/language-learning/`。

### learn-anything

- **作用：** 将证据充分的对话/笔记/workflow 提炼为可复用 Agent Skill 方法。
- **调用：** 仅 user-invoked。
- **包：** [skills/knowledge/learn-anything/](skills/knowledge/learn-anything)
- **状态：** 第一方已准入；PRESERVE — NO REWRITE。
- **证据：** [package contract](skills/knowledge/learn-anything/SKILL.md)。
- **安装路径：** `<skills-root>/learn-anything/`。

### light-travelpage

- **作用：** 从资料生成或更新中英双语手机旅行网页，提供航班/住宿卡片、地区地图导航，共享同行人、账单、币种设置、待办与门票状态。
- **时机：** 创建或维护旅行网页；普通旅行咨询和预订购买不触发。
- **调用：** Model-invoked。
- **包：** [skills/productivity/light-travelpage/](skills/productivity/light-travelpage)
- **安装路径：** `<skills-root>/light-travelpage/`。
- **状态：** 实质性转换的第一方能力，已准入 main、尚未发布版本标签；默认 GitHub + Cloudflare Pages、Functions、D1，每个部署一个同权限小组。
- **证据：** [准入](docs/evidence/admissions/light-travelpage/README.md) · [本次更新](docs/evidence/maintenance/2026-09-15-light-travelpage.md) · [来源](skills/productivity/light-travelpage/ATTRIBUTION.md)。

### manuscript-ops

- **作用：** 从小笔记到多语言多格式交付的文稿工程治理。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/writing/manuscript-ops/](skills/writing/manuscript-ops)
- **状态：** 第一方已准入；PRESERVE — NO REWRITE。
- **证据：** [package contract](skills/writing/manuscript-ops/SKILL.md)。
- **安装路径：** `<skills-root>/manuscript-ops/`。

### project-clarify

- **作用：** 读取已有代码和文档资料，只追问尚未确定的关键决策，并将确认结果交给技术规格编写。
- **调用：** 仅 user-invoked。
- **包：** [skills/project/project-clarify/](skills/project/project-clarify)
- **状态：** 第一方已准入；ADAPT（Matt `grill-with-docs`）。
- **证据：** [references/project-clarification-contract.md](skills/project/project-clarify/references/project-clarification-contract.md)。
- **安装路径：** `<skills-root>/project-clarify/`。

### project-init

- **作用：** 为新项目或已有项目建立基础结构与任务跟踪配置，让后续澄清、拆任务和执行可以直接接上。
- **调用：** 仅 user-invoked。
- **包：** [skills/project/project-init/](skills/project/project-init)
- **状态：** 第一方已准入；REFACTOR（仓库 bootstrap；完整澄清仍归 `project-clarify`）。
- **证据：** [skills/project/project-init/tests/](skills/project/project-init/tests)。
- **安装路径：** `<skills-root>/project-init/`。

### project-review

- **作用：** 项目最终验收：基于已确认的验收基准，组合各项审查结果，给出最终的验收判定（`PASS` / `FAIL` / `BLOCKED`）。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/review/project-review/](skills/review/project-review)
- **状态：** 第一方已准入；NEW（从旧 `review-loop` 迁移 final-acceptance 逻辑）。
- **证据：** [SKILL.md](skills/review/project-review/SKILL.md)。
- **安装路径：** `<skills-root>/project-review/`。

### project-retro

- **作用：** 在项目或长会话结束后进行复盘，分析环境阻力、自动化检查、导航效率与命令开销，提出具体改进建议。
- **调用：** Model-invoked（工作流终点由 Agent 自主评估是否需要调用）；支持手动入口。
- **包：** [skills/project/project-retro/](skills/project/project-retro)
- **状态：** 第一方已准入；PORT 与 Light 工作流适配（Matt Pocock `retro`）。
- **证据：** 契约与行为测试见 [skills/project/project-retro/tests/](skills/project/project-retro/tests)；[SKILL.md](skills/project/project-retro/SKILL.md)，[ATTRIBUTION.md](skills/project/project-retro/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/project-retro/`。

### project-spec

- **作用：** 把已澄清的需求与决策整理成正式的开发规格（SPEC），避免在编写阶段重新提问。
- **调用：** 仅 user-invoked。
- **包：** [skills/project/project-spec/](skills/project/project-spec)
- **状态：** 第一方已准入；ADAPT（Matt `to-spec`）。
- **证据：** [references/](skills/project/project-spec/references)。
- **安装路径：** `<skills-root>/project-spec/`。

### project-tickets

- **作用：** 把已确认的技术规格拆解为有先后依赖关系的任务清单，方便逐步独立执行。
- **调用：** 仅 user-invoked。
- **包：** [skills/project/project-tickets/](skills/project/project-tickets)
- **状态：** 第一方已准入；ADAPT（Matt `to-tickets`）。
- **证据：** [references/](skills/project/project-tickets/references)。
- **安装路径：** `<skills-root>/project-tickets/`。

### prototype

- **作用：** 为设计问题构建一次性原型。
- **调用：** Model-invoked。
- **包：** [skills/engineering/prototype/](skills/engineering/prototype)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/prototype/SKILL.md)。
- **安装路径：** `<skills-root>/prototype/`。

### recap

- **作用：** 用一句简洁文本展示当前 session，不替换或压缩对话历史。
- **调用：** 仅 user-invoked；唯一入口为 `$recap`。
- **包：** [skills/productivity/recap/](skills/productivity/recap)
- **状态：** 第一方已准入；仅手动触发的稳定形式随 v0.2.0 发布；当前 main 分支跟踪集合更新。
- **证据：** 当前修订由 [tests/test_functional_closure.py](tests/test_functional_closure.py) 验证；冻结历史测试保留在 [skills/productivity/recap/tests/](skills/productivity/recap/tests)。
- **安装路径：** `<skills-root>/recap/`。

### release-workflow

- **作用：** 发布已完成项目——同步文档、执行质量门、打 tag、发布。
- **调用：** Model-invoked。
- **包：** [skills/project/release-workflow/](skills/project/release-workflow)
- **状态：** 第一方已准入；MIGRATE — NO REWRITE（来自 `LightDevCoder/release-workflow`）。
- **证据：** [SKILL.md](skills/project/release-workflow/SKILL.md)。
- **安装路径：** `<skills-root>/release-workflow/`。

### research

- **作用：** 针对外部问题做高可信来源调研并沉淀结论。
- **调用：** Model-invoked。
- **包：** [skills/thinking/research/](skills/thinking/research)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/thinking/research/SKILL.md)。
- **安装路径：** `<skills-root>/research/`。

### resolving-merge-conflicts

- **作用：** 解决进行中的 `git` merge/rebase 冲突。
- **调用：** Model-invoked。
- **包：** [skills/engineering/resolving-merge-conflicts/](skills/engineering/resolving-merge-conflicts)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/resolving-merge-conflicts/SKILL.md)。
- **安装路径：** `<skills-root>/resolving-merge-conflicts/`。

### review-loop

- **作用：** 审查与修复循环引擎：将产物提交给对应的审查技能，收集发现的问题并指导修复，直到通过或达到轮次上限。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/review/review-loop/](skills/review/review-loop)
- **状态：** 第一方已准入；REFACTOR + SPLIT（final acceptance 已移至 `project-review`）。
- **证据：** [SKILL.md](skills/review/review-loop/SKILL.md)。
- **安装路径：** `<skills-root>/review-loop/`。

### socratic

- **作用：** 启发式问答引擎：提出相互独立的选择题并给出倾向建议，逐步梳理决策并形成共识，供上层澄清技能调用。
- **调用：** Model-invoked（供其他 Skill 调用的引擎）。
- **包：** [skills/thinking/socratic/](skills/thinking/socratic)
- **状态：** 第一方已准入；ADAPT（Matt `grilling`）。
- **证据：** [SKILL.md](skills/thinking/socratic/SKILL.md)。
- **安装路径：** `<skills-root>/socratic/`。

### tdd

- **作用：** 测试驱动开发（红-绿-重构）：先编写失败的测试用例，再补充实现使其通过，最后优化重构。
- **调用：** Model-invoked。
- **包：** [skills/engineering/tdd/](skills/engineering/tdd)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/tdd/SKILL.md)。
- **安装路径：** `<skills-root>/tdd/`。

### teach

- **作用：** 在当前 workspace 内教授新 Skill 或概念。
- **调用：** 仅 user-invoked。
- **包：** [skills/knowledge/teach/](skills/knowledge/teach)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/knowledge/teach/SKILL.md)。
- **安装路径：** `<skills-root>/teach/`。

### to-questionnaire

- **作用：** 将未决问题转为面向持信息人的问卷。
- **调用：** 仅 user-invoked。
- **包：** [skills/thinking/to-questionnaire/](skills/thinking/to-questionnaire)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/thinking/to-questionnaire/SKILL.md)。
- **安装路径：** `<skills-root>/to-questionnaire/`。

### wait-what

- **作用：** 重讲上一条未被理解的消息。
- **调用：** 仅 user-invoked。
- **包：** [skills/productivity/wait-what/](skills/productivity/wait-what)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/productivity/wait-what/SKILL.md)。
- **安装路径：** `<skills-root>/wait-what/`。

### wizard

- **作用：** 为只能人做的步骤生成交互式 bash 向导（置备、密钥、第三方控制台、割接）。
- **调用：** Model-invoked。
- **包：** [skills/productivity/wizard/](skills/productivity/wizard)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/productivity/wizard/SKILL.md)。
- **安装路径：** `<skills-root>/wizard/`。

### writing-for-agents

- **作用：** 为 agent 编写或改进面向模型的文档（Skills、AGENTS.md、CLAUDE.md）。
- **调用：** Model-invoked。
- **包：** [skills/writing/writing-for-agents/](skills/writing/writing-for-agents)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/writing/writing-for-agents/SKILL.md)。
- **安装路径：** `<skills-root>/writing-for-agents/`。

## 来源边界

| 状态 | 所属位置 | 目录处理 |
| --- | --- | --- |
| First-party | 本仓库 | 准入后列在上方。 |
| 已批准 Port（Matt） | 本仓库且带 `ATTRIBUTION.md` | 列在上方；自包含，无 Matt 运行时依赖。 |
| Direct upstream | 原始上游仓库 | 作为依赖说明，不在此复制。 |
| Modified third-party | `skills-3rdParty` | 在私有仓库的 source catalog 中列出。 |
| Deprecated / archived | 已发布迁移记录 | 列出并注明替代与迁移路径。 |

参见 [维护说明](docs/MAINTENANCE.zh-CN.md) 与 [准入说明](docs/SKILL_ADMISSION.zh-CN.md)。
