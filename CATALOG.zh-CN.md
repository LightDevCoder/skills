# 第一方 Skill 目录

[English catalog](CATALOG.md)

本目录从 `skills/` 下 36 个已准入包同步生成，是可读 inventory，不是静态 workflow router，也不代表某个 Agent host 当前已安装哪些 Skill。包的 `SKILL.md` 仍是行为权威。

[按分类浏览](skills/README.zh-CN.md) · [路径迁移](docs/CATEGORY_MIGRATION.zh-CN.md)

## 集合状态

| 字段 | 值 |
| --- | --- |
| 集合 | Light Skills — Composable Agent Workflows |
| 包数量 | 36 个已准入第一方 Skill |
| 当前状态 | main 包含 36 个包；v0.2.5 为当前最新稳定版本 |
| 稳定版本 | [v0.2.5](https://github.com/LightDevCoder/skills/releases/tag/v0.2.5)（36 个包；上一稳定版为 v0.2.4） |
| 安装权威 | [docs/INSTALLATION.zh-CN.md](docs/INSTALLATION.zh-CN.md) |
| 发现检查 | [tests/test_collection_discovery.py](tests/test_collection_discovery.py) · [tests/test_composition.py](tests/test_composition.py) |
| 证据 | [v0.2.5 发布清单](docs/evidence/releases/v0.2.5/RELEASE_MANIFEST.zh-CN.md) · [v0.2.5 发布收据](docs/evidence/releases/v0.2.5/RELEASE_RECEIPT.zh-CN.md) |

`v0.2.5` 的公开发布与全新安装已验证；包数量仍为 36。

`v0.1.1` 发布五个包；`v0.1.2` 增加 `recap` 与 `language-learning`（七个）；`v0.1.3` 迁移测试工具链；`v0.1.4` 增加 `kanban-worker`；`v0.1.5` 收紧看板调度与身份；`v0.1.6` 增加 `kb-init`（九个）。`v0.2.0` 正式发布涵盖项目工作流、澄清、执行、审阅与专项工具的完整 33 包架构，随后 v0.2.0 发布线扩展了 `humanizer` 准入（34 个包；见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)）。`v0.2.1` 增加 `light-travelpage` 与 `project-retro`（36 个包）。`v0.2.2` 最终收敛 TypeSafe Jev 语义加速、分类目录架构与不可变发布完整性。`v0.2.3` 拆分发布前不可变清单与发布后验证收据，追加 v0.2.2 历史事实证明，完成 project-retro 正向状态驱动重构，并形式化六阶段发布生命周期。

本表无未修改的上游复制。获批的 Matt PORT 均带 `ATTRIBUTION.md` 且无需上游运行时依赖。

## 已准入 Skill

### agent-config

- **作用：** 探测当前 Agent 宿主环境与任务要求，为任务配置合适的模型梯队、推理强度与执行拓扑，支持 10 款主流 Agent 框架及伴随 MCP。
- **什么时候用：** 需要根据模型梯队、推理强度或执行拓扑配置任务，或有明确的 `agent-config setup` 初始化意图时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/engineering/agent-config/](skills/engineering/agent-config)
- **状态：** 第一方已准入；REFACTOR（参照 Sol Advisor 设计理念，Profile 驱动跨 Harness 执行配置器，覆盖主要编码 Agent Harness [10 种原生适配器 + 1 种通用回退]）。
- **证据：** [host-evidence-schema.md](skills/engineering/agent-config/references/host-evidence-schema.md)、[plan-schema.md](skills/engineering/agent-config/references/plan-schema.md)、[task-assessment.md](skills/engineering/agent-config/references/task-assessment.md)、[profile-schema.md](skills/engineering/agent-config/references/profile-schema.md)、[companion-contract.md](skills/engineering/agent-config/references/companion-contract.md)、[harness-support.md](skills/engineering/agent-config/references/harness-support.md)、[provider-adapter-contract.md](skills/engineering/agent-config/references/provider-adapter-contract.md)；Companion 运行时维护于 [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config)。
- **安装路径：** `<skills-root>/agent-config/`。

### ask-light

- **作用：** 作为 Light 工作流顾问、导航器与路由入口：检查项目与工作流状态，推荐下一步 Skill 并给出理由，用户批准后安全转换（支持可选 TypeSafe Jev System One 语义加速）。
- **什么时候用：** 不确定下一步该用哪个 Skill，或需要项目感知路由、集合能力导航与独立工作流推荐时。
- **调用方式：** 仅 user-invoked；批准前只读。批准后支持的环境下可直接开始 model-invoked 目标，user-invoked 目标遵循 Host 转换策略并在缺少直接通道时渲染精确调用。
- **包位置：** [skills/productivity/ask-light/](skills/productivity/ask-light)
- **状态：** 第一方已准入；REFACTOR（在完整 Skill map 建好后最后构建）。
- **证据：** [skills/productivity/ask-light/tests/](skills/productivity/ask-light/tests) 与 [使用指南](docs/zh-CN/skills/ask-light.md)。
- **安装路径：** `<skills-root>/ask-light/`。

### clarify

- **作用：** 针对模糊的想法、设想或流程开展多轮问答，每次给出几个针对性选项供你选择，快速理清思路（无需建立完整项目）。
- **什么时候用：** 想法或头脑风暴尚处模糊阶段，且不需要建立完整项目上下文时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/thinking/clarify/](skills/thinking/clarify)
- **状态：** 第一方已准入；ADAPT（Matt `grill-me` → Light，经 `socratic`）。
- **证据：** [SKILL.md](skills/thinking/clarify/SKILL.md) 与 [ATTRIBUTION.md](skills/thinking/clarify/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/clarify/`。

### code-review

- **作用：** 代码审查专员：对比变更代码（`git diff`），从规范标准与业务规格两个维度检查潜在问题，仅输出问题清单而不直接修改代码。
- **什么时候用：** 需要审查分支/PR 的代码变更（diff），或由 `review-loop` / `project-review` 请求专项软件检查时。
- **调用方式：** Model-invoked；只读，不修复也不裁决。
- **包位置：** [skills/review/code-review/](skills/review/code-review)
- **状态：** 第一方已准入；ADAPT（保留 Matt `code-review` 的双轴方法）。
- **证据：** [references/WORKFLOW.md](skills/review/code-review/references/WORKFLOW.md) 与 [ATTRIBUTION.md](skills/review/code-review/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/code-review/`。

### decision-map

- **作用：** 当任务庞大且跨多轮会话时，将待决策事项梳理为一张有依赖关系的决策图谱。
- **什么时候用：** 存在多项相互依赖的决策、工作跨越多个会话，且在进入 `project-spec` 前需要理清思路时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/thinking/decision-map/](skills/thinking/decision-map)
- **状态：** 第一方已准入；ADAPT（Matt `wayfinder`）。
- **证据：** [references/MAP-CONTRACT.md](skills/thinking/decision-map/references/MAP-CONTRACT.md)。
- **安装路径：** `<skills-root>/decision-map/`。

### diagnosing-bugs

- **作用：** 针对复杂 Bug 和性能回退进行系统性排查，通过建立紧凑反馈信号快速定位根因。
- **什么时候用：** 出现代码报错、测试失败、行为异常或性能回退，且根因尚不明显时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/engineering/diagnosing-bugs/](skills/engineering/diagnosing-bugs)
- **状态：** 第一方已准入；PORT — NO REDESIGN（保留 Matt 基线）。
- **证据：** [SKILL.md](skills/engineering/diagnosing-bugs/SKILL.md)。
- **安装路径：** `<skills-root>/diagnosing-bugs/`。

### eli5

- **作用：** 按指定受众水平解释任意主题、代码或错误。
- **什么时候用：** 用户要求“像对 5 岁孩子一样解释”、“向领导汇报”或需要非技术视角的通俗讲解时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/knowledge/eli5/](skills/knowledge/eli5)
- **状态：** 第一方已准入；MIGRATE — NO REWRITE（源自上游 `DreambigOu/ELI5` @ `a766623`，经临时迁移 fork `LightDevCoder/ELI5`）。
- **证据：** [SKILL.md](skills/knowledge/eli5/SKILL.md)、[ATTRIBUTION.md](skills/knowledge/eli5/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/eli5/`。

### generic-review

- **作用：** 通用文档与制品审阅：检查非代码产物（文档、配置、计划）中的遗漏、事实矛盾、格式错误或体验缺陷。
- **什么时候用：** 缺乏更专用的审查器，需要对通用文档、配置或产物进行一致性与质量审查时。
- **调用方式：** Model-invoked；只读，不裁决。
- **包位置：** [skills/review/generic-review/](skills/review/generic-review)
- **状态：** 第一方已准入；NEW。
- **证据：** [SKILL.md](skills/review/generic-review/SKILL.md)。
- **安装路径：** `<skills-root>/generic-review/`。

### handoff

- **作用：** 将当前会话压缩为下一 agent 的交接文档。
- **什么时候用：** 需要在会话结束时或在不同 Agent / 会话之间交接当前上下文时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/productivity/handoff/](skills/productivity/handoff)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/productivity/handoff/SKILL.md)。
- **安装路径：** `<skills-root>/handoff/`。

### humanizer

- **作用：** 将带有 AI 痕迹的中英文文本改写为自然行文，且不改变原意。
- **什么时候用：** 编辑或审查包含夸大宣称、销售腔调、模糊信源、套话与机械表达的中英文文本时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/writing/humanizer/](skills/writing/humanizer)
- **状态：** 第一方已准入，full-path `PASS`；v0.2.0 线发布；ADAPT 自 blader/humanizer（2.11.2）+ 薄中文适配，MIT 归属保留。
- **证据：** [SKILL.md](skills/writing/humanizer/SKILL.md)、[准入记录](docs/evidence/admissions/humanizer/README.zh-CN.md)。
- **安装路径：** `<skills-root>/humanizer/`。

### implement

- **作用：** 执行单个已确认的任务（代码、文档或配置），完成本地验证并提交审查。
- **什么时候用：** 具体的任务工单（Ticket）或明确的规格切片已就绪且无歧义，准备进入编码或实施时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/project/implement/](skills/project/implement)
- **状态：** 第一方已准入；ADAPT（Matt `implement` → 通用执行器）。
- **证据：** [references/WORKFLOW.md](skills/project/implement/references/WORKFLOW.md)。
- **安装路径：** `<skills-root>/implement/`。

### kanban-worker

- **作用：** 在定时运行中认领并执行一张看板任务，优先处理已有修改意见或进行中的工作。
- **什么时候用：** 调度执行 Light-Kanban 看板任务时。
- **调用方式：** Model-invoked；支持手动入口。
- **包位置：** [skills/project/kanban-worker/](skills/project/kanban-worker)
- **状态：** 第一方已准入（通过 full path review-loop agent-skill PASS）；在 v0.1.6 中自 light-kanban-worker 更名。
- **证据：** [SKILL.md](skills/project/kanban-worker/SKILL.md)。
- **安装路径：** `<skills-root>/kanban-worker/`。

### kb-init

- **作用：** 通过专属访谈设计并初始化可维护知识库，获批后才实施。
- **什么时候用：** 需要新建或重构项目知识库、参考资料库或研究归档时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/knowledge/kb-init/](skills/knowledge/kb-init)
- **状态：** 第一方已准入（通过 full path review-loop agent-skill PASS）；随 v0.1.6 发布。
- **证据：** [SKILL.md](skills/knowledge/kb-init/SKILL.md)。
- **安装路径：** `<skills-root>/kb-init/`。

### language-learning

- **作用：** 通过六种模式辅导任意语言——课程、卡片、对话、语法、测验与沉浸。
- **什么时候用：** 学习或练习外语（如精读、语法分析、表达润色、听说测试）时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/knowledge/language-learning/](skills/knowledge/language-learning)
- **状态：** 第一方已准入（通过 prompt-only fast-track PASS）；随 v0.1.2 发布。
- **证据：** [skills/knowledge/language-learning/tests/](skills/knowledge/language-learning/tests)。
- **安装路径：** `<skills-root>/language-learning/`。

### learn-anything

- **作用：** 将证据充分的对话/笔记/workflow 提炼为可复用 Agent Skill 方法。
- **什么时候用：** 原始资料或对话中包含可复用、有证据支持的技能或实践方法，需要提炼沉淀时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/knowledge/learn-anything/](skills/knowledge/learn-anything)
- **状态：** 第一方已准入；PRESERVE — NO REWRITE。
- **证据：** [package contract](skills/knowledge/learn-anything/SKILL.md)。
- **安装路径：** `<skills-root>/learn-anything/`。

### light-travelpage

- **作用：** 从资料生成或更新中英双语手机旅行网页，提供航班/住宿卡片、地区地图导航，共享同行人、账单、币种设置、待办与门票状态。
- **什么时候用：** 需要根据已有行程资料生成或维护手机旅行网页（含账单、待办、地图），而非普通旅行咨询或票务购买时。
- **调用方式：** Model-invoked 或 user-invoked。
- **包位置：** [skills/productivity/light-travelpage/](skills/productivity/light-travelpage)
- **状态：** 实质性转换的第一方能力，已收录于当前稳定版本集合；默认 GitHub + Cloudflare Pages、Functions 与 D1，每个部署一个同权限小组。
- **证据：** [准入](docs/evidence/admissions/light-travelpage/README.md) · [本次更新](docs/evidence/maintenance/2026-09-15-light-travelpage.md) · [来源](skills/productivity/light-travelpage/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/light-travelpage/`。

### manuscript-ops

- **作用：** 从小笔记到多语言多格式交付的文稿工程治理。
- **什么时候用：** 需要对文稿范围、风险评估、批次处理、审查与多格式导出交付进行统一治理时。
- **调用方式：** Model-invoked；支持手动入口。
- **包位置：** [skills/writing/manuscript-ops/](skills/writing/manuscript-ops)
- **状态：** 第一方已准入；PRESERVE — NO REWRITE。
- **证据：** [package contract](skills/writing/manuscript-ops/SKILL.md)。
- **安装路径：** `<skills-root>/manuscript-ops/`。

### project-clarify

- **作用：** 读取已有代码和文档资料，只追问尚未确定的关键决策，并将确认结果交给技术规格编写。
- **什么时候用：** 已有项目需求存在不确定性，需要基于项目上下文开展定向澄清时（避免重复询问已有事实）。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/project/project-clarify/](skills/project/project-clarify)
- **状态：** 第一方已准入；ADAPT（Matt `grill-with-docs`）。
- **证据：** [references/project-clarification-contract.md](skills/project/project-clarify/references/project-clarification-contract.md)。
- **安装路径：** `<skills-root>/project-clarify/`。

### project-init

- **作用：** 为新项目或已有项目建立基础结构与任务跟踪配置，让后续澄清、拆任务和执行可以直接接上。
- **什么时候用：** 新项目需要建立经过确认的最小起点时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/project/project-init/](skills/project/project-init)
- **状态：** 第一方已准入；REFACTOR（仓库 bootstrap；完整澄清仍归 `project-clarify`）。
- **证据：** [skills/project/project-init/tests/](skills/project/project-init/tests)。
- **安装路径：** `<skills-root>/project-init/`。

### project-review

- **作用：** 项目最终验收：基于已确认的验收基准，组合各项审查结果，给出最终的验收判定（`PASS` / `FAIL` / `BLOCKED`）。
- **什么时候用：** 完整项目完成开发，在进入 `release-workflow` 发布前需要进行最终验收与裁决时。
- **调用方式：** Model-invoked；支持手动入口。
- **包位置：** [skills/review/project-review/](skills/review/project-review)
- **状态：** 第一方已准入；NEW（从旧 `review-loop` 迁移 final-acceptance 逻辑）。
- **证据：** [SKILL.md](skills/review/project-review/SKILL.md)。
- **安装路径：** `<skills-root>/project-review/`。

### project-retro

- **作用：** 在项目或长会话结束后进行复盘，分析环境阻力、自动化检查、导航效率与命令开销，提出具体改进建议。
- **什么时候用：** 工作流收尾阶段（Agent 自检执行中是否存在摩擦），或由用户发起会话复盘时。
- **调用方式：** Model-invoked（工作流终点由 Agent 自主评估是否需要调用）；支持手动入口。
- **包位置：** [skills/project/project-retro/](skills/project/project-retro)
- **状态：** 第一方已准入；PORT 与 Light 工作流适配（Matt Pocock `retro`）。
- **证据：** 契约与行为测试见 [skills/project/project-retro/tests/](skills/project/project-retro/tests)；[SKILL.md](skills/project/project-retro/SKILL.md)，[ATTRIBUTION.md](skills/project/project-retro/ATTRIBUTION.md)。
- **安装路径：** `<skills-root>/project-retro/`。

### project-spec

- **作用：** 把已澄清的需求与决策整理成正式的开发规格（SPEC），避免在编写阶段重新提问。
- **什么时候用：** 需求与决策已澄清，需要为工单拆解产出结构化技术规格（SPEC）时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/project/project-spec/](skills/project/project-spec)
- **状态：** 第一方已准入；ADAPT（Matt `to-spec`）。
- **证据：** [references/](skills/project/project-spec/references)。
- **安装路径：** `<skills-root>/project-spec/`。

### project-tickets

- **作用：** 把已确认的技术规格拆解为有先后依赖关系的任务清单，方便逐步独立执行。
- **什么时候用：** 技术规格（SPEC）已获批准，需要将其拆解为具备清晰依赖的最小可执行工单时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/project/project-tickets/](skills/project/project-tickets)
- **状态：** 第一方已准入；ADAPT（Matt `to-tickets`）。
- **证据：** [references/](skills/project/project-tickets/references)。
- **安装路径：** `<skills-root>/project-tickets/`。

### prototype

- **作用：** 为设计问题构建一次性原型。
- **什么时候用：** 在正式编码前，需要快速构建探索性原型以验证状态模型或 UI 逻辑交互感受时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/engineering/prototype/](skills/engineering/prototype)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/prototype/SKILL.md)。
- **安装路径：** `<skills-root>/prototype/`。

### recap

- **作用：** 用一句简洁文本展示当前 session，不替换或压缩对话历史。
- **什么时候用：** 用户显式要求 `$recap`，需要一句话概括当前会话进展且不压缩上下文时。
- **调用方式：** 仅 user-invoked；唯一入口为 `$recap`。
- **包位置：** [skills/productivity/recap/](skills/productivity/recap)
- **状态：** 第一方已准入；仅手动触发的稳定形式随 v0.2.0 发布；当前 main 分支跟踪集合更新。
- **证据：** 当前修订由 [tests/test_functional_closure.py](tests/test_functional_closure.py) 验证；冻结历史测试保留在 [skills/productivity/recap/tests/](skills/productivity/recap/tests)。
- **安装路径：** `<skills-root>/recap/`。

### release-workflow

- **作用：** 发布已完成项目——同步文档、执行质量门、打 tag、发布。
- **什么时候用：** 项目已通过 `project-review` 验收，准备执行版本发布、Tag 创建与收据证明时。
- **调用方式：** Model-invoked；支持手动入口。
- **包位置：** [skills/project/release-workflow/](skills/project/release-workflow)
- **状态：** 第一方已准入；MIGRATE — NO REWRITE（来自 `LightDevCoder/release-workflow`）。
- **证据：** [SKILL.md](skills/project/release-workflow/SKILL.md)。
- **安装路径：** `<skills-root>/release-workflow/`。

### research

- **作用：** 针对外部问题做高可信来源调研并沉淀结论。
- **什么时候用：** 本地预设或已知事实不足以支持决策，需要检索外部权威证据与资料时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/thinking/research/](skills/thinking/research)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/thinking/research/SKILL.md)。
- **安装路径：** `<skills-root>/research/`。

### resolving-merge-conflicts

- **作用：** 解决进行中的 `git` merge/rebase 冲突。
- **什么时候用：** Git merge 或 rebase 遇到代码冲突停滞时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/engineering/resolving-merge-conflicts/](skills/engineering/resolving-merge-conflicts)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/resolving-merge-conflicts/SKILL.md)。
- **安装路径：** `<skills-root>/resolving-merge-conflicts/`。

### review-loop

- **作用：** 审查与修复循环引擎：将产物提交给对应的审查技能，收集发现的问题并指导修复，直到通过或达到轮次上限。
- **什么时候用：** 任何具有指定审阅者且具备有限轮次修复窗口的产物审阅与修复循环。
- **调用方式：** Model-invoked；支持手动入口。
- **包位置：** [skills/review/review-loop/](skills/review/review-loop)
- **状态：** 第一方已准入；REFACTOR + SPLIT（终审验收移至 project-review）。
- **证据：** [SKILL.md](skills/review/review-loop/SKILL.md)。
- **安装路径：** `<skills-root>/review-loop/`。

### socratic

- **作用：** 启发式问答引擎：提出相互独立的选择题并给出倾向建议，逐步梳理决策并形成共识，供上层澄清技能调用。
- **什么时候用：** 作为 `clarify`、`project-clarify`、`decision-map` 的底层提问引擎（非独立项目入口）。
- **调用方式：** Model-invoked（由 clarify 等技能调用）。
- **包位置：** [skills/thinking/socratic/](skills/thinking/socratic)
- **状态：** 第一方已准入；ADAPT（Matt grilling）。
- **证据：** [SKILL.md](skills/thinking/socratic/SKILL.md)。
- **安装路径：** `<skills-root>/socratic/`。

### tdd

- **作用：** 测试驱动开发（红-绿-重构）：先编写失败的测试用例，再补充实现使其通过，最后优化重构。
- **什么时候用：** 采用测试驱动开发模式编写代码新功能，或在修复 Bug 时增加回归测试时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/engineering/tdd/](skills/engineering/tdd)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/engineering/tdd/SKILL.md)。
- **安装路径：** `<skills-root>/tdd/`。

### teach

- **作用：** 在当前 workspace 内教授新 Skill 或概念。
- **什么时候用：** 用户希望针对特定主题开展由浅入深的引导式教学时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/knowledge/teach/](skills/knowledge/teach)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/knowledge/teach/SKILL.md)。
- **安装路径：** `<skills-root>/teach/`。

### to-questionnaire

- **作用：** 将未决问题转为面向持信息人的问卷。
- **什么时候用：** 所需关键信息掌握在他人手中，需要将澄清问题转为适合外部填写的问卷时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/thinking/to-questionnaire/](skills/thinking/to-questionnaire)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/thinking/to-questionnaire/SKILL.md)。
- **安装路径：** `<skills-root>/to-questionnaire/`。

### wait-what

- **作用：** 重讲上一条未被理解的消息。
- **什么时候用：** 用户表示困惑（如“等等，你说什么？”），需要从全新视角重新解释前文时。
- **调用方式：** 仅 user-invoked。
- **包位置：** [skills/productivity/wait-what/](skills/productivity/wait-what)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/productivity/wait-what/SKILL.md)。
- **安装路径：** `<skills-root>/wait-what/`。

### wizard

- **作用：** 为只能人做的步骤生成交互式 bash 向导（置备、密钥、第三方控制台、割接）。
- **什么时候用：** 任务涉及必须由人工操作的步骤（如配置云控制台、管理凭据、切流），需要交互式向导时。
- **调用方式：** Model-invoked 或 user-invoked。
- **包位置：** [skills/productivity/wizard/](skills/productivity/wizard)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/productivity/wizard/SKILL.md)。
- **安装路径：** `<skills-root>/wizard/`。

### writing-for-agents

- **作用：** 为 agent 编写或改进面向模型的文档（Skills、AGENTS.md、CLAUDE.md）。
- **什么时候用：** 编写或优化 Agent 指令（AGENTS.md、CLAUDE.md）或 Skill 包时。
- **调用方式：** Model-invoked。
- **包位置：** [skills/writing/writing-for-agents/](skills/writing/writing-for-agents)
- **状态：** 第一方已准入；PORT — NO REDESIGN。
- **证据：** [SKILL.md](skills/writing/writing-for-agents/SKILL.md)。
- **安装路径：** `<skills-root>/writing-for-agents/`。
