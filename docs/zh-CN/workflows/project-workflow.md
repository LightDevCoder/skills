# Project Workflow — 组合

[English](../../workflows/project-workflow.md)

本文说明 **Project Workflow** 的组合方式：入口、handoff 产物与停止点，不复制任一 Skill 的内部流程。行为以 `SKILL.md` 为准。

## 推荐流程

```text
project-init
      ↓  （稳定的 Light 项目与 tracker 契约）
project-clarify
      ↓  （有界澄清 handoff：理解 / 已决 / 未决 / 缺口）
project-spec
      ↓  （冻结的 SPEC + 验收来源）
project-tickets
      ↓  （tracer-bullet 依赖 ticket 图）
implement
      ↓  （有界 diff + 聚焦测试 + 验证）
project-review
      ↓  （最终 PASS / FAIL / BLOCKED）
release-workflow
```

这是*推荐*流程，非强制流水线。中途任务可直接切入对应阶段；任一 Skill 不会自动调用下一个 user-invoked Skill。

## Entry → Handoff → Stop

| 步骤 | 入口条件 | Skill 与调用 | 输出 / Handoff | 停止点 |
| --- | --- | --- | --- | --- |
| 1 | 新项目需要稳定且已确认的起点 | [`project-init`](../../../skills/project-init/SKILL.md) — user-invoked | `docs/agents/light-project.md` + tracker 契约 + instruction pointer | 停止，由用户选下一步 |
| 2 | 真实项目存在未决决策，仓库事实不应重问 | [`project-clarify`](../../../skills/project-clarify/SKILL.md) — user-invoked → `socratic` 引擎 | 供 `project-spec` 的有界 handoff | 止于澄清 summary，不建 SPEC |
| 3 | 决策已澄清，需要正式 SPEC | [`project-spec`](../../../skills/project-spec/SKILL.md) — user-invoked | 冻结 SPEC + 验收来源 | 止于待审批；阻塞则返回 `project-clarify` |
| 4 | SPEC 已批准 | [`project-tickets`](../../../skills/project-tickets/SKILL.md) — user-invoked | 按依赖排序的 tracer-bullet ticket 图 | 停止，不自动起 `implement` |
| 5 | 单个 ticket 已就绪且无歧义 | [`implement`](../../../skills/implement/SKILL.md) — user-invoked，必要时可选 `agent-config` / 内部调 `tdd` | 有界 diff + 测试 + 本地验证 | 止于 ticket 范围；合适时交 review |
| 6 | 产物需最终验收 | [`project-review`](../../../skills/project-review/SKILL.md) — model-invoked（支持手动）经 `review-loop` | 冻结 Charter + reviewer findings + 最终 `PASS`/`FAIL`/`BLOCKED` | 止于 verdict |
| 7 | 项目已通过验收 | [`release-workflow`](../../../skills/release-workflow/SKILL.md) — model-invoked | 同步文档/目录/测试、打 tag、发布 | 止于 release 记录 |

**可选 / 并行：** 大型模糊任务可用 `decision-map` 替代/增强 `project-clarify`，见 [clarification-system](clarification-system.md)。`implement` 可按需调用 `tdd`、`diagnosing-bugs`、`resolving-merge-conflicts`，见 [execution](execution.md)。Review 经 `generic-review`/`code-review`/领域 reviewer 走 `review-loop`，见 [review-system](review-system.md)。

## 未知或专业入口

- 无项目上下文的模糊想法 → [`clarify`](../../../skills/clarify/SKILL.md)（standalone，经 `socratic` 后停止）。
- 不知入口 → [`ask-light`](../../../skills/ask-light/SKILL.md) `next` — 一个推荐，等待批准，随后按调用策略完成转换。
- 文稿 / 知识库 / 看板 / 学习 → [specialized-workflows](specialized-workflows.md)。

组合是显式的：顾问给出建议，用户批准，随后按目标 Skill 的调用策略与当前 Host 能力进行转换。`SKILL.md` 始终是契约。
