# Project Workflow — 组合

[English](../../workflows/project-workflow.md)

本文说明 **Project Workflow** 的组合方式：入口、handoff 产物与停止点，不复制任一 Skill 的内部流程。行为以 `SKILL.md` 为准。

## 推荐流程

```text
project-init
      ↓  （项目基础结构与任务跟踪配置）
project-clarify
      ↓  （已澄清需求：确认的决策与待定问题）
project-spec
      ↓  （冻结的 SPEC + 验收来源）
project-tickets
      ↓  （按依赖排序的任务清单）
implement
      ↓  （清晰的代码变更 + 针对性测试 + 验证结果）
project-review
      ↓  （最终 PASS / FAIL / BLOCKED）
release-workflow
      ↓  （可选：Agent 自主评估摩擦信号 → project-retro 复盘）
project-retro
```

这是*推荐*流程，非强制流水线。中途任务可直接切入对应阶段；任一 Skill 不会自动调用下一个 user-invoked Skill。

## Entry → Handoff → Stop

| 步骤 | 入口条件 | Skill 与调用 | 输出 / Handoff | 停止点 |
| --- | --- | --- | --- | --- |
| 1 | 新项目需要稳定且已确认的起点 | [`project-init`](../../../skills/project/project-init/SKILL.md) — user-invoked | `docs/agents/light-project.md` + 任务跟踪配置 + 指令入口 | 停止，由用户选下一步 |
| 2 | 真实项目存在未决决策，仓库事实不应重问 | [`project-clarify`](../../../skills/project/project-clarify/SKILL.md) — user-invoked → `socratic` 引擎 | 供 `project-spec` 的清晰需求总结与决策清单 | 止于澄清 summary，不建 SPEC |
| 3 | 决策已澄清，需要正式 SPEC | [`project-spec`](../../../skills/project/project-spec/SKILL.md) — user-invoked | 冻结 SPEC + 验收来源 | 止于待审批；阻塞则返回 `project-clarify` |
| 4 | SPEC 已批准 | [`project-tickets`](../../../skills/project/project-tickets/SKILL.md) — user-invoked | 按依赖排序的任务清单 | 停止，不自动起 `implement` |
| 5 | 单个 ticket 已就绪且无歧义 | [`implement`](../../../skills/project/implement/SKILL.md) — user-invoked，必要时可选 `agent-config` / 内部调 `tdd` | 清晰的代码变更 + 测试 + 本地验证 | 止于 ticket 范围；合适时交 review |
| 6 | 产物需最终验收 | [`project-review`](../../../skills/review/project-review/SKILL.md) — model-invoked（支持手动）经 `review-loop` | 冻结 Charter + reviewer findings + 最终 `PASS`/`FAIL`/`BLOCKED` | 止于 verdict |
| 7 | 项目已通过验收 | [`release-workflow`](../../../skills/project/release-workflow/SKILL.md) — model-invoked | 同步文档/目录/测试、打 tag、发布 | 止于 release 记录 |
| 8 | 工作流结束；Agent 自主评估是否发生摩擦 | [`project-retro`](../../../skills/project/project-retro/SKILL.md) — model-invoked（自主评估） | 按严重性排序的结构化复盘发现 | 止于输出发现；修改须经用户确认 |

### 工作流终点 Agent 自主评估

在工作流最后一步（`project-review` 或 `release-workflow` 完成后），Agent 独立判断是否需要调用 `project-retro`。检查执行中是否存在摩擦信号：
- **导航困难：** 文件难以发现、未索引依赖导致耗时。
- **自动化检查缺位：** 发生本可通过自动化检查（lint、类型检查、pre-commit 钩子、CI）确切捕获的语法/类型/测试错误。
- **规范缺口：** 审查遗漏，或将机械检查规则错置于自然语言规范文档。
- **引导膨胀：** `AGENTS.md` / `CLAUDE.md` 过于庞大、包含空操作（no-ops）或失效指令。
- **工具开销：** 出现高开销或重复读取等 token 浪费现象。
- **信息缺失：** 关键日志、错误堆栈或文档难以获取。

若检测到上述摩擦，Agent 调用 `project-retro` 提出具体改进建议；若流程顺畅无摩擦，则干净跳过，不增加额外干扰。

**可选 / 并行：** 大型模糊任务可用 `decision-map` 替代/增强 `project-clarify`，见 [clarification-system](clarification-system.md)。`implement` 可按需调用 `tdd`、`diagnosing-bugs`、`resolving-merge-conflicts`，见 [execution](execution.md)。Review 经 `generic-review`/`code-review`/领域 reviewer 走 `review-loop`，见 [review-system](review-system.md)。

## 未知或专业入口

- 无项目上下文的模糊想法 → [`clarify`](../../../skills/thinking/clarify/SKILL.md)（standalone，经 `socratic` 后停止）。
- 不知入口 → [`ask-light`](../../../skills/productivity/ask-light/SKILL.md) `next` — 一个推荐，等待批准，随后按调用策略完成转换。
- 文稿 / 知识库 / 看板 / 学习 → [specialized-workflows](specialized-workflows.md)。

组合是显式的：顾问给出建议，用户批准，随后按目标 Skill 的调用策略与当前 Host 能力进行转换。`SKILL.md` 始终是契约。
