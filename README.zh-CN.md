[English README](README.md)

![LightDevCoder/skills — 可组合的 Agent 工作流](Assets/header.png)

# Light Skills — 可组合的 Agent 工作流

`LightDevCoder/skills` 是**第一方、通用、可组合的 Agent 工作流系统**—— 33 个小而明确、独立发现的 Skill，可串成完整项目流，也可单独使用。每个包的 `SKILL.md` 是行为权威；本 README 只说明仓库。

> **简介：** Light Skills — Drive your creativity. 小而清晰，可组合，可检查。

> **发布：** [v0.1.6](https://github.com/LightDevCoder/skills/releases/tag/v0.1.6) 是最后发布的稳定版本（9 个包）。当前分支包含 **33 个第一方 Skill**（未发布重构，见 [CHANGELOG.zh-CN.md](CHANGELOG.zh-CN.md)）。安装方式仍为 `npx skills add LightDevCoder/skills`。

## Light Skills 是什么

不是巨型编排器，而是能力系统。仓库按职责提供：

- **Project Workflow** — 从初始化到发布
- **Clarification & Research** — 先把事问清楚
- **Execution** — 在 host 能力范围内做有边界的执行
- **Review** — 从只读 findings 到项目验收
- **Specialized Workflows** — 文稿、知识库、学习、看板
- **Router** — `ask-light` 推荐下一步，批准后开始执行

架构决定*有哪些能力以及如何组合*；Skill 写作参照 [Matt Pocock Skills](https://github.com/mattpocock/skills)，host 感知路由参照 [Sol Advisor](https://github.com/DannyMac180/sol-advisor)——均为设计参考，不构成运行时依赖。

## 安装

```text
npx skills add LightDevCoder/skills --yes --copy --agent '*'
```

安装同一版本下的一个 Skill：

```text
npx skills add LightDevCoder/skills --skill project-review --yes --copy --agent '*'
npx skills add LightDevCoder/skills --skill research --yes --copy --agent '*'
```

对最后发布的 tag：

```text
npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'
```

刷新 host 后脱离 source checkout 验证 discovery。见[安装说明](docs/INSTALLATION.zh-CN.md)了解 revision 语义、manual fallback 和 fresh-install 证据。

## 快速开始

```text
$ask-light next        # 不知道下一步 — 得到一个推荐后停止
$project-init          # 从 preset 建立稳定 Light 项目契约
$clarify               # 一次调用 → 连续澄清，无 SPEC
$project-clarify       # 真实项目 → 先检查仓库，再提问
$implement             # 一个清晰 ticket → 一个已验证产物
$project-review        # 最终验收：PASS / FAIL / BLOCKED
```

## 主流程

推荐的主流程（不是强制流水线，中途任务可直接切入对应阶段）：

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
```

- `project-init` — 幂等 Light bootstrap，建立稳定项目/tracker 契约，不做完整澄清。
- `project-clarify → project-spec → project-tickets` — 澄清决策、冻结 SPEC、切成 tracer-bullet tickets。
- `implement` — 通用有边界执行器（代码、文档、配置、Skill）。
- `project-review` — 项目级最终验收；`review-loop` 是其收敛引擎。
- 任务已进入中间状态时可直接从对应 Skill 开始。

小任务路径：

```text
clarify                          # 独立连续澄清 → 共同理解确认
implement                        # 一个 ready ticket → 验证 → 需要时 review-loop
diagnosing-bugs → implement      # 难 bug → 紧反馈环 → 修复 → review
release-workflow                 # 仅发布
$ask-light                       # 不确定入口 → 一个推荐
```

完整组合见 [docs/zh-CN/workflows/](docs/zh-CN/workflows/)。每个 `SKILL.md` 仍是权威。

## 不知道下一步时

```text
$ask-light next
$ask-light workflow
```

`ask-light` 是**Light 工作流路由器**—— user-invoked、只读。它先从 Light 自有的 33-Skill 地图判断逻辑匹配，再独立验证 host availability，只返回*一个*推荐（或一个有边界 recipe），含来源、理由和 host 适配的调用方式，然后停止。绝不安装、执行或自动串联另一个 user-invoked Skill。

见 [ask-light](skills/ask-light/SKILL.md) 与 [docs/zh-CN/workflows/](docs/zh-CN/workflows/)。

## 代表性能力

| 分组 | Skill | 入口 |
| --- | --- | --- |
| **Project** | `project-init`、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`project-review`、`release-workflow` | [CATALOG.zh-CN.md](CATALOG.zh-CN.md) |
| **Clarification & Research** | `socratic`（引擎）、`clarify`、`project-clarify`、`decision-map`、`research`、`prototype`、`to-questionnaire` | [clarification-system](docs/zh-CN/workflows/clarification-system.md) |
| **Execution** | `implement`、`agent-config`、`tdd`、`diagnosing-bugs`、`resolving-merge-conflicts` | [execution](docs/zh-CN/workflows/execution.md) |
| **Review** | `review-loop`（引擎）、`generic-review`、`code-review`、`project-review`（验收） | [review-system](docs/zh-CN/workflows/review-system.md) |
| **Specialized** | `manuscript-ops`、`kb-init`、`learn-anything`、`language-learning`、`kanban-worker`、`eli5`、`recap` | [specialized-workflows](docs/zh-CN/workflows/specialized-workflows.md) |
| **Productivity** | `handoff`、`wizard`、`wait-what`、`writing-for-agents` | [CATALOG.zh-CN.md](CATALOG.zh-CN.md) |

全部 33 个包的完整清单——作用、when to use、调用方式与路径——见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)。不在此复制完整 Skill 文档。

## 第一方目录（摘要）

`skills/` 下 33 个已准入第一方 Skill。包契约是行为权威。

完整表格见 [CATALOG.zh-CN.md](CATALOG.zh-CN.md)。

## 所有权与上游边界

| 来源状态 | 权威 | 本仓库处理方式 |
| --- | --- | --- |
| First-party | 本仓库及其包契约 | 放在 `skills/` 下。 |
| 已批准 Port（Matt） | 原始上游 + `ATTRIBUTION.md` + Light 集成 | 自包含于此；运行时不需要安装 Matt Skills。 |
| Direct upstream（其他） | 原始上游仓库 | 直接安装，不复制未修改 Skill。 |
| Modified third-party | 私有 `LightDevCoder/skills-3rdParty` | 保留 provenance、patch、license、sync lock、证据。 |
| Deprecated / archived | 已发布迁移记录 | 保留历史，指向当前权威。 |

本仓库已批准的 Matt PORT（SPEC §14）：`research`、`prototype`、`tdd`、`handoff`、`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`。每个均有 `ATTRIBUTION.md`，无上游运行时依赖。Light 主流程不需要在运行时安装 `mattpocock/skills` 或 `sol-advisor`。

## 治理与证据

- [维护契约](AGENTS.md)
- [Skill 准入](docs/SKILL_ADMISSION.zh-CN.md)
- [维护与同步](docs/MAINTENANCE.zh-CN.md)
- [安装与 fresh-install 验证](docs/INSTALLATION.zh-CN.md)
- [审查策略](docs/REVIEW_POLICY.zh-CN.md) · [Reviewer 契约](docs/REVIEWER_CONTRACT.zh-CN.md)
- [目录](CATALOG.zh-CN.md) · [变更记录](CHANGELOG.zh-CN.md)
- [工作流](docs/zh-CN/workflows/) — project、clarification、execution、review、specialized
- [发布收据](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.zh-CN.md)
- [Collection discovery](tests/test_collection_discovery.py) · [Composition checks](tests/test_composition.py)

## 头图

头图：[Assets/header.png](Assets/header.png)（本 README 首行）。可编辑的遗留头图仍保留在 `skills/docs/assets/skills-header.svg` / `.png`，清单为 `skills/docs/assets/skills-header.json`，供包测试使用。
