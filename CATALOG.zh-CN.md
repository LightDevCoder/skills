# 第一方 Skill 目录

[English catalog](CATALOG.md)

本目录从 `skills/` 下 34 个已准入包同步生成，是可读 inventory，不是静态 workflow router，也不代表某个 Agent host 当前已安装哪些 Skill。包的 `SKILL.md` 仍是行为权威。

## 集合状态

| 字段 | 值 |
| --- | --- |
| 集合 | Light Skills — Composable Agent Workflows |
| 包数量 | 34 个已准入第一方 Skill |
| 当前状态 | 已发布 [v0.2.0](https://github.com/LightDevCoder/skills/releases/tag/v0.2.0)（包含 34 个第一方包） |
| 稳定版本 | [v0.2.0](https://github.com/LightDevCoder/skills/releases/tag/v0.2.0)（34 个包；上一稳定版为 9 个包的 v0.1.6） |
| 安装权威 | [docs/INSTALLATION.zh-CN.md](docs/INSTALLATION.zh-CN.md) |
| 发现检查 | [tests/test_collection_discovery.py](tests/test_collection_discovery.py) · [tests/test_composition.py](tests/test_composition.py) |
| 证据 | [v0.2.0 发布证据](docs/evidence/releases/v0.2.0/RELEASE_RECEIPT.zh-CN.md) |

`v0.1.1` 发布五个包；`v0.1.2` 增加 `recap` 与 `language-learning`（七个）；`v0.1.3` 迁移测试工具链；`v0.1.4` 增加 `kanban-worker`；`v0.1.5` 收紧看板调度与身份；`v0.1.6` 增加 `kb-init`（九个）。`v0.2.0` 正式发布涵盖项目工作流、澄清、执行、审阅与专项工具的完整 33 包架构，随后 v0.2.0 发布线扩展了 `humanizer` 准入（34 个包；见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)）。

本表无未修改的上游复制。获批的 Matt PORT 均带 `ATTRIBUTION.md` 且无需上游运行时依赖。

## 已准入 Skill

### agent-config

- **作用：** Profile 驱动的跨 Harness 执行配置器：检查当前宿主真实执行能力，匹配用户确认的模型档位 Profile 与任务形态，精准配置执行拓扑、模型等级与 effort，支持可选 companion MCP（原生支持 10 种 P0 主流 Harness 与通用回退机制）并提供单模型对等一等模式。
- **调用：** Model-invoked。
- **包：** [skills/agent-config/](skills/agent-config/)
- **状态：** 第一方已准入；REFACTOR（参照 Sol Advisor 设计理念，Profile 驱动跨 Harness 执行配置器，覆盖 10 种 P0 主流原生 Harness 与通用回退）。
- **证据：** [host-evidence-schema.md](skills/agent-config/references/host-evidence-schema.md)、[plan-schema.md](skills/agent-config/references/plan-schema.md)、[task-assessment.md](skills/agent-config/references/task-assessment.md)、[profile-schema.md](skills/agent-config/references/profile-schema.md)、[companion-contract.md](skills/agent-config/references/companion-contract.md)、[harness-support.md](skills/agent-config/references/harness-support.md)、[provider-adapter-contract.md](skills/agent-config/references/provider-adapter-contract.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/agent-config/`。

### ask-light

- **作用：** 作为 Light 工作流顾问、导航器与路由入口：检查项目与工作流状态，推荐下一步 Skill 并给出理由，用户批准后安全转换。
- **调用：** 仅 user-invoked；批准前只读。批准后支持的环境下可直接开始 model-invoked 目标，user-invoked 目标遵循 Host 转换策略并在缺少直接通道时渲染精确调用。
- **包：** [skills/ask-light/](skills/ask-light/)
- **状态：** 第一方已准入；REFACTOR（在完整 Skill map 建好后最后构建）。
- **证据：** [skills/ask-light/tests/](skills/ask-light/tests/) 与 [使用指南](docs/zh-CN/skills/ask-light.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/ask-light/`。

### clarify

- **作用：** 一次调用启动面向模糊想法/需求/流程的连续澄清，不产生正式 SPEC。以一轮多问题形式询问当前 frontier，并接受批量回复。
- **调用：** 仅 user-invoked。
- **包：** [skills/clarify/](skills/clarify/)
- **状态：** 第一方已准入；ADAPT（Matt `grill-me` → Light，经 `socratic`）。
- **证据：** [SKILL.md](skills/clarify/SKILL.md) 与 [ATTRIBUTION.md](skills/clarify/ATTRIBUTION.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/clarify/`。

### code-review

- **作用：** 针对有界 `git diff` 的只读 specialist 审查（Standards + Spec 双轴）。
- **调用：** Model-invoked；只读，不修复也不裁决。
- **包：** [skills/code-review/](skills/code-review/)
- **状态：** 第一方已准入；ADAPT（保留 Matt `code-review` 的双轴方法）。
- **证据：** [references/WORKFLOW.md](skills/code-review/references/WORKFLOW.md) 与 [ATTRIBUTION.md](skills/code-review/ATTRIBUTION.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/code-review/`。

### decision-map

- **作用：** 将大型、模糊、跨会话的工作规划为可持久化的决策地图 tickets。
- **调用：** 仅 user-invoked。
- **包：** [skills/decision-map/](skills/decision-map/)
- **状态：** 第一方已准入；ADAPT（Matt `wayfinder`）。
- **证据：** [references/MAP-CONTRACT.md](skills/decision-map/references/MAP-CONTRACT.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/decision-map/`。

### diagnosing-bugs

- **作用：** 针对难 bug 与性能回退的诊断环，需紧反馈信号。
- **调用：** Model-invoked。
- **包：** [skills/diagnosing-bugs/](skills/diagnosing-bugs/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/diagnosing-bugs/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/diagnosing-bugs/`。

### eli5

- **作用：** 按指定受众水平解释任意主题、代码或错误。
- **调用：** Model-invoked。
- **包：** [skills/eli5/](skills/eli5/)
- **状态：** 第一方已准入；MIGRATE — NO REWRITE（源自上游 `DreambigOu/ELI5` @ `a766623`，经临时迁移 fork `LightDevCoder/ELI5`）。
- **证据：** [SKILL.md](skills/eli5/SKILL.md)、[ATTRIBUTION.md](skills/eli5/ATTRIBUTION.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/eli5/`。

### generic-review

- **作用：** 针对普通制品的只读默认 reviewer，找遗漏、错误、矛盾与可用性问题。
- **调用：** Model-invoked；只读，不裁决。
- **包：** [skills/generic-review/](skills/generic-review/)
- **状态：** 第一方已准入；NEW。
- **证据：** [SKILL.md](skills/generic-review/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/generic-review/`。

### handoff

- **作用：** 将当前会话压缩为下一 agent 的交接文档。
- **调用：** 仅 user-invoked。
- **包：** [skills/handoff/](skills/handoff/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/handoff/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/handoff/`。

### humanizer

- **作用：** 将带有 AI 痕迹的中英文文本改写为自然行文，且不改变原意。
- **调用：** Model-invoked。
- **包：** [skills/humanizer/](skills/humanizer/)
- **状态：** 第一方已准入，full-path `PASS`；v0.2.0 线发布；ADAPT 自 blader/humanizer（2.11.2）+ 薄中文适配，MIT 归属保留。
- **证据：** [SKILL.md](skills/humanizer/SKILL.md)、[准入记录](docs/evidence/admissions/humanizer/README.zh-CN.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/humanizer/`。

### implement

- **作用：** 执行一个已决策、有边界的工作项（代码、文档、配置、Skill）。
- **调用：** 仅 user-invoked。
- **包：** [skills/implement/](skills/implement/)
- **状态：** 第一方已准入；ADAPT（Matt `implement` → 通用执行器）。
- **证据：** [references/WORKFLOW.md](skills/implement/references/WORKFLOW.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/implement/`。

### kanban-worker

- **作用：** 每次定时运行领取并执行一张 Light-Kanban 任务；先继续持有任务与 `reviewFeedback`。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/kanban-worker/](skills/kanban-worker/)
- **状态：** 第一方已准入；经完整路径（`review-loop agent-skill` PASS）；v0.1.6 由 `light-kanban-worker` 改名。
- **证据：** [skills/kanban-worker/tests/](skills/kanban-worker/tests/) 与 [使用指南](docs/zh-CN/skills/kanban-worker.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/kanban-worker/`。

### kb-init

- **作用：** 通过专属访谈设计并初始化可维护知识库，获批后才实施。
- **调用：** 仅 user-invoked。
- **包：** [skills/kb-init/](skills/kb-init/)
- **状态：** 第一方已准入；完整路径 `PASS`，随 v0.1.6 发布。
- **证据：** [skills/kb-init/tests/](skills/kb-init/tests/)。
- **安装路径：** host 认可的 Skills root 下的 `skills/kb-init/`。

### language-learning

- **作用：** 通过六种模式辅导任意语言——课程、卡片、对话、语法、测验与沉浸。
- **调用：** 仅 user-invoked。
- **包：** [skills/language-learning/](skills/language-learning/)
- **状态：** 第一方已准入；纯提示型快速通道 `PASS`，v0.1.2 发布。
- **证据：** [skills/language-learning/tests/](skills/language-learning/tests/)。
- **安装路径：** host 认可的 Skills root 下的 `skills/language-learning/`。

### learn-anything

- **作用：** 将证据充分的对话/笔记/workflow 提炼为可复用 Agent Skill 方法。
- **调用：** 仅 user-invoked。
- **包：** [skills/learn-anything/](skills/learn-anything/)
- **状态：** 第一方已准入；PRESERVE — NO REWRITE。
- **证据：** [package contract](skills/learn-anything/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/learn-anything/`。

### manuscript-ops

- **作用：** 从小笔记到多语言多格式交付的文稿工程治理。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/manuscript-ops/](skills/manuscript-ops/)
- **状态：** 第一方已准入；PRESERVE — NO REWRITE。
- **证据：** [package contract](skills/manuscript-ops/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/manuscript-ops/`。

### project-clarify

- **作用：** 基于已检查的项目事实澄清真实未决决策，输出给 `project-spec` 的有界 handoff。采用与 `clarify` 相同的 frontier-round 交互，并注入项目证据。
- **调用：** 仅 user-invoked。
- **包：** [skills/project-clarify/](skills/project-clarify/)
- **状态：** 第一方已准入；ADAPT（Matt `grill-with-docs`）。
- **证据：** [references/project-clarification-contract.md](skills/project-clarify/references/project-clarification-contract.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-clarify/`。

### project-init

- **作用：** 幂等建立下游 Project Skills 消费的稳定 Light 项目与 tracker 契约。
- **调用：** 仅 user-invoked。
- **包：** [skills/project-init/](skills/project-init/)
- **状态：** 第一方已准入；REFACTOR（仓库 bootstrap；完整澄清仍归 `project-clarify`）。
- **证据：** [skills/project-init/tests/](skills/project-init/tests/)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-init/`。

### project-review

- **作用：** 项目级最终验收——冻结 baseline、组合 reviewer、签发 `PASS`/`FAIL`/`BLOCKED`。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/project-review/](skills/project-review/)
- **状态：** 第一方已准入；NEW（从旧 `review-loop` 迁移 final-acceptance 逻辑）。
- **证据：** [SKILL.md](skills/project-review/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-review/`。

### project-spec

- **作用：** 将已澄清的输出整理为正式 SPEC，不再重做访谈。
- **调用：** 仅 user-invoked。
- **包：** [skills/project-spec/](skills/project-spec/)
- **状态：** 第一方已准入；ADAPT（Matt `to-spec`）。
- **证据：** [references/](skills/project-spec/references/)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-spec/`。

### project-tickets

- **作用：** 将已批准 SPEC 转为按依赖排序的 tracer-bullet ticket 图。
- **调用：** 仅 user-invoked。
- **包：** [skills/project-tickets/](skills/project-tickets/)
- **状态：** 第一方已准入；ADAPT（Matt `to-tickets`）。
- **证据：** [references/](skills/project-tickets/references/)。
- **安装路径：** host 认可的 Skills root 下的 `skills/project-tickets/`。

### prototype

- **作用：** 为设计问题构建一次性原型。
- **调用：** Model-invoked。
- **包：** [skills/prototype/](skills/prototype/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/prototype/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/prototype/`。

### recap

- **作用：** 用一句简洁文本展示当前 session，不替换或压缩对话历史。
- **调用：** 仅 user-invoked；唯一入口为 `$recap`。
- **包：** [skills/recap/](skills/recap/)
- **状态：** 第一方已准入；v0.1.2 发布的是旧版；仅手动触发的修订仍待当前候选验收，尚未发布。
- **证据：** 当前修订由 [tests/test_functional_closure.py](tests/test_functional_closure.py) 验证；冻结历史测试保留在 [skills/recap/tests/](skills/recap/tests/)。
- **安装路径：** host 认可的 Skills root 下的 `skills/recap/`。

### release-workflow

- **作用：** 发布已完成项目——同步文档、执行质量门、打 tag、发布。
- **调用：** Model-invoked。
- **包：** [skills/release-workflow/](skills/release-workflow/)
- **状态：** 第一方已准入；MIGRATE — NO REWRITE（来自 `LightDevCoder/release-workflow`）。
- **证据：** [SKILL.md](skills/release-workflow/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/release-workflow/`。

### research

- **作用：** 针对外部问题做高可信来源调研并沉淀结论。
- **调用：** Model-invoked。
- **包：** [skills/research/](skills/research/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/research/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/research/`。

### resolving-merge-conflicts

- **作用：** 解决进行中的 `git` merge/rebase 冲突。
- **调用：** Model-invoked。
- **包：** [skills/resolving-merge-conflicts/](skills/resolving-merge-conflicts/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/resolving-merge-conflicts/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/resolving-merge-conflicts/`。

### review-loop

- **作用：** 轻量 review/repair 引擎——解析 reviewer、调用、收 findings、回 Producer、重跑。
- **调用：** Model-invoked；支持手动入口。
- **包：** [skills/review-loop/](skills/review-loop/)
- **状态：** 第一方已准入；REFACTOR + SPLIT（final acceptance 已移至 `project-review`）。
- **证据：** [SKILL.md](skills/review-loop/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/review-loop/`。

### socratic

- **作用：** 核心澄清引擎——内部 decision frontier 以一轮多问题呈现，含选项、建议、批量回复与共同理解确认。
- **调用：** Model-invoked（供其他 Skill 调用的引擎）。
- **包：** [skills/socratic/](skills/socratic/)
- **状态：** 第一方已准入；ADAPT（Matt `grilling`）。
- **证据：** [SKILL.md](skills/socratic/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/socratic/`。

### tdd

- **作用：** 测试驱动开发—— red → green → refactor 真测试循环。
- **调用：** Model-invoked。
- **包：** [skills/tdd/](skills/tdd/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/tdd/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/tdd/`。

### teach

- **作用：** 在当前 workspace 内教授新 Skill 或概念。
- **调用：** 仅 user-invoked。
- **包：** [skills/teach/](skills/teach/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/teach/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/teach/`。

### to-questionnaire

- **作用：** 将未决问题转为面向持信息人的问卷。
- **调用：** 仅 user-invoked。
- **包：** [skills/to-questionnaire/](skills/to-questionnaire/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/to-questionnaire/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/to-questionnaire/`。

### wait-what

- **作用：** 重讲上一条未被理解的消息。
- **调用：** 仅 user-invoked。
- **包：** [skills/wait-what/](skills/wait-what/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/wait-what/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/wait-what/`。

### wizard

- **作用：** 为只能人做的步骤生成交互式 bash 向导（置备、密钥、第三方控制台、割接）。
- **调用：** Model-invoked。
- **包：** [skills/wizard/](skills/wizard/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/wizard/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/wizard/`。

### writing-for-agents

- **作用：** 为 agent 编写或改进面向模型的文档（Skills、AGENTS.md、CLAUDE.md）。
- **调用：** Model-invoked。
- **包：** [skills/writing-for-agents/](skills/writing-for-agents/)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/writing-for-agents/SKILL.md)。
- **安装路径：** host 认可的 Skills root 下的 `skills/writing-for-agents/`。

## 来源边界

| 状态 | 所属位置 | 目录处理 |
| --- | --- | --- |
| First-party | 本仓库 | 准入后列在上方。 |
| 已批准 Port（Matt） | 本仓库且带 `ATTRIBUTION.md` | 列在上方；自包含，无 Matt 运行时依赖。 |
| Direct upstream | 原始上游仓库 | 作为依赖说明，不在此复制。 |
| Modified third-party | `skills-3rdParty` | 在私有仓库的 source catalog 中列出。 |
| Deprecated / archived | 已发布迁移记录 | 列出并注明替代与迁移路径。 |

参见 [维护说明](docs/MAINTENANCE.zh-CN.md) 与 [准入说明](docs/SKILL_ADMISSION.zh-CN.md)。
