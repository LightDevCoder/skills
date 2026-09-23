[English README](README.md)

![Light Skills — 可组合的 Agent 工作流](Assets/header.png)

# Light Skills — 可组合的 Agent 工作流

`LightDevCoder/skills` 包含 36 个第一方 Agent Skill，既可串联用于软件项目的规划、编码与审查，也可按需单独使用。每个包位于 `skills/<category>/<name>/`，由包内的 `SKILL.md` 统领具体行为。

> **发布版本：** v0.2.5 是包含全部 36 个第一方 Skill 的当前稳定版本。阅读[中文发布说明](docs/evidence/releases/v0.2.5/RELEASE_NOTES.zh-CN.md)或[English GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.5)；不可变的[发布清单](docs/evidence/releases/v0.2.5/RELEASE_MANIFEST.zh-CN.md)与发布后的[发布收据](docs/evidence/releases/v0.2.5/RELEASE_RECEIPT.zh-CN.md)记录范围和验证事实。

## 按分类浏览

[全部分类与集合说明](skills/README.zh-CN.md)。36 个技能的源文件已按用途分类，名称和调用方式不变。

- [项目执行](skills/project/README.zh-CN.md) — 8 个技能
- [工程开发](skills/engineering/README.zh-CN.md) — 5 个技能
- [审阅验收](skills/review/README.zh-CN.md) — 4 个技能
- [澄清研究](skills/thinking/README.zh-CN.md) — 5 个技能
- [学习知识](skills/knowledge/README.zh-CN.md) — 5 个技能
- [写作编辑](skills/writing/README.zh-CN.md) — 3 个技能
- [日常工具](skills/productivity/README.zh-CN.md) — 6 个技能

[旧路径迁移说明](docs/CATEGORY_MIGRATION.zh-CN.md)

## 概述

仓库按实际开发场景划分为以下模块：

- **项目工作流（Project Workflow）：** 覆盖从项目初始化到最终发布的全流程。
- **澄清与调研（Clarification & Research）：** 在编码前理清需求、查阅一手资料。
- **执行（Execution）：** 结合 Profile 与宿主特征配置并执行边界清晰的开发任务。
- **审阅（Review）：** 包含只读专家检查与项目最终验收。
- **专项工作流（Specialized Workflows）：** 针对文稿、知识库、语言学习与看板任务的专属工具。
- **路由导航（Router）：** `ask-light` 检查工作区状态并推荐下一步。

技能编写参考 Matt Pocock Skills 的渐进式结构与 Sol Advisor 的环境检查设计，作为设计参考且不引入运行时外部依赖。

## 安装

### 当前 main / latest（包含更新后的 Agent Config）

从默认分支 `main` 安装最新集合：

```bash
npx skills add LightDevCoder/skills
```

从 `main` 安装指定单个 Skill（例如更新后的 `agent-config` Skill）：

```bash
npx skills add LightDevCoder/skills --skill agent-config
npx skills add LightDevCoder/skills --skill project-review
npx skills add LightDevCoder/skills --skill research
```

> **说明：** 不带 fragment 的仓库源（`LightDevCoder/skills`）将跟随默认分支 `main`，获取最新的已准入特性与集成。

### 稳定版本快照（v0.2.5）

若需安装可复现的稳定发布快照，请锁定 `#v0.2.5` tag：

```bash
npx skills add LightDevCoder/skills#v0.2.5
npx skills add LightDevCoder/skills#v0.2.5 --skill project-retro
```

历史版本（如 `#v0.2.4`、`#v0.2.2`、`#v0.2.1` 与 `#v0.2.0`）依然保留供复现：

```bash
npx skills add LightDevCoder/skills#v0.2.4
npx skills add LightDevCoder/skills#v0.2.2
npx skills add LightDevCoder/skills#v0.2.1
npx skills add LightDevCoder/skills#v0.2.0
```

> **说明：** `#v0.2.0` tag 保持为 v0.2.0 发布线的不可变可复现快照，不会被 `main` 上的后续工作修改。

### 直接指定目标 Agent

```bash
npx skills add LightDevCoder/skills --agent claude-code
```

### Companion MCP 运行时

`agent-config` Skill 使用可选的 Companion MCP 服务进行宿主探测与 Profile 持久化，该运行时维护于独立仓库 [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config)：

```bash
git clone https://github.com/LightDevCoder/agent-config.git
cd agent-config && npm ci && npm run build && npm install -g .
agent-config setup --check
```

### 可选语义加速（TypeSafe Jev）

`ask-light` 与 `agent-config` 支持通过 TypeSafe Jev System One 模型进行可选的语义加速，用于快速意图校准、歧义检测与抽象任务画像：

```bash
export TYPESAFE_API_KEY="your-api-key"
```

配置后，Jev 在确定性代码安全边界内完成语义裁决。未配置或离线时，两项技能平滑降级至零外部依赖的确定性规则基准，保持 Fail-Closed 硬安全保障。

详细安装选项（指定 Agent、独立复制模式、非交互式 CI 安装）、手动复制方式与验证记录见[安装指南](docs/INSTALLATION.zh-CN.md)。

## 快速上手

```text
$ask-light next        # 根据当前上下文推荐合适的 Skill
$project-init          # 初始化项目基础结构与任务跟踪
$clarify               # 通过针对性提问澄清模糊需求
$project-clarify       # 结合已有代码与文档澄清项目决策
$implement             # 执行明确的开发任务并完成验证
$project-review        # 执行最终验收：PASS / FAIL / BLOCKED
```

## 主工作流

完整项目开发推荐遵循以下阶段，也可根据任务现状随时直接切入：

```text
project-init
      ↓
project-clarify
      ↓
project-spec
      ↓
project-tickets
      ↓
implement
      ↓
project-review
      ↓
release-workflow
      ↓
project-retro（Agent 评估摩擦信号）
```

- `project-init`：初始化项目基础结构与任务跟踪配置。
- `project-clarify → project-spec → project-tickets`：澄清模糊需求、编写技术规格并拆分为可执行任务清单。
- `implement`：逐个执行任务并运行自动化测试。
- `project-review`：对照验收基准验证交付质量；由 `review-loop` 驱动多轮修复。
- `release-workflow`：执行发布验证、打 tag 并完成发布。
- `project-retro`：在流程终点由 Agent 自主评估执行摩擦（导航、自动化检查、规范、工具开销）并输出改进建议。

常用单项任务路径：

```text
clarify                          # 独立需求澄清与共识确认
implement                        # 直接执行明确的任务
diagnosing-bugs → implement      # 定位疑难问题并完成修复
release-workflow                 # 仅执行发布流程
$ask-light                       # 任务不确定时获取路由建议
```

完整组合说明见 [docs/zh-CN/workflows/](docs/zh-CN/workflows)。

## 任务路由建议

```text
$ask-light next
$ask-light workflow
```

`ask-light` 是 Light 工作流顾问、导航器与路由入口。它检查真实项目与工作流状态，由模型判断最合适的下一 Skill，解释原因，并在用户批准后按 Skill 调用策略与 Host 能力完成安全转换（支持的环境下可直接开始 model-invoked 目标；缺少直接 Host 转换通道时安全降级为渲染精确调用）。

详见 [ask-light](skills/productivity/ask-light/SKILL.md) 与 [docs/zh-CN/workflows/](docs/zh-CN/workflows)。

## 能力概览

| 分组 | Skill | 详细文档 |
| --- | --- | --- |
| **项目流程** | `project-init`、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`project-review`、`release-workflow` | [CATALOG.zh-CN.md](CATALOG.zh-CN.md) |
| **澄清与调研** | `socratic`（引擎）、`clarify`、`project-clarify`、`decision-map`、`research`、`prototype`、`to-questionnaire` | [clarification-system](docs/zh-CN/workflows/clarification-system.md) |
| **任务执行** | `implement`、`agent-config`（原生支持主要编码 Harness：10 种原生适配器与通用回退）、`tdd`、`diagnosing-bugs`、`resolving-merge-conflicts` | [execution](docs/zh-CN/workflows/execution.md) |
| **质量审阅** | `review-loop`（引擎）、`generic-review`、`code-review`、`project-review`（验收） | [review-system](docs/zh-CN/workflows/review-system.md) |
| **专项工具** | `manuscript-ops`、`kb-init`、`learn-anything`、`language-learning`、`kanban-worker`、`eli5`、`recap` | [specialized-workflows](docs/zh-CN/workflows/specialized-workflows.md) |
| **协作效率** | `handoff`、`humanizer`、`wizard`、`wait-what`、`writing-for-agents`、`light-travelpage` | [CATALOG.zh-CN.md](CATALOG.zh-CN.md) |

每个 Skill 的完整功能、使用时机与调用方式见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)。

## 溯源与归属

| 来源分类 | 管理策略 | 仓库内处理方式 |
| --- | --- | --- |
| 第一方原生 | 集合所有者原创 | 维护于 `skills/<category>/<name>/`。 |
| 经批准 Port（Matt Pocock） | 保留上游行为并附 `ATTRIBUTION.md` | 自包含于 `skills/<category>/<name>/`，无外部运行时依赖。 |
| 第三方未修改 | 外部原作者维护 | 建议直接从上游安装，本仓库不冗余存放。 |
| 第三方定制修改 | 私有仓库 `LightDevCoder/skills-3rdParty` 托管 | 记录完整补丁、许可证与同步状态。 |
| 历史独立迁移 | 整合并入主集合 | 在发布记录中记载迁移历史与退役状态。 |

经批准的 Matt Port（共 11 个）：`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`。各包均含 `ATTRIBUTION.md`，无需在运行时安装上游包。

改编来源（2 个包）：`humanizer` 是基于 blader/humanizer（2.11.2）实质性转换的第一方能力，外加参考 op7418/Humanizer-zh 的薄中文适配层；两份 MIT 许可均在其 [ATTRIBUTION.md](skills/writing/humanizer/ATTRIBUTION.md) 中保留。

`light-travelpage` 基于 do-tongxue/Travel-Plan-Page 实质性转换，增加受保护的 D1 协作、校验、恢复和生成更新工具；MIT 来源记录见 [ATTRIBUTION.md](skills/productivity/light-travelpage/ATTRIBUTION.md)。

## 治理与参考文档

- [维护契约](AGENTS.md)
- [Skill 准入规范](docs/SKILL_ADMISSION.zh-CN.md)
- [维护与文档同步](docs/MAINTENANCE.zh-CN.md)
- [安装指南](docs/INSTALLATION.zh-CN.md)
- [审阅策略](docs/REVIEW_POLICY.zh-CN.md) · [Reviewer 契约](docs/REVIEWER_CONTRACT.zh-CN.md)
- [目录](CATALOG.zh-CN.md) · [变更记录](CHANGELOG.zh-CN.md)
- [工作流指南](docs/zh-CN/workflows)
- [发布收据](docs/evidence/releases/v0.2.5/RELEASE_RECEIPT.zh-CN.md)
- [集合发现测试](tests/test_collection_discovery.py) · [组合测试](tests/test_composition.py)
