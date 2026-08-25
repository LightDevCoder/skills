# Execution — 组合

[English](../../workflows/execution.md)

本文说明 **Execution** 的组合：入口、路由与 handoff。分步流程在各 `SKILL.md` 与 `references/` 中。

## 本组 Skill

- [`implement`](../../../skills/implement/SKILL.md) — user-invoked 通用有边界执行器
- [`agent-config`](../../../skills/agent-config/SKILL.md) — model-invoked host 能力映射
- [`tdd`](../../../skills/tdd/SKILL.md) — model-invoked 测试驱动环
- [`diagnosing-bugs`](../../../skills/diagnosing-bugs/SKILL.md) — model-invoked 诊断环
- [`resolving-merge-conflicts`](../../../skills/resolving-merge-conflicts/SKILL.md) — model-invoked 合并冲突解决

均为第一方自包含包，运行时不要求 `mattpocock/skills` 或 `sol-advisor`。

## Entry → Handoff → Stop

| 场景 | 入口 | 典型路径 | Handoff / 停止 |
| --- | --- | --- | --- |
| 单个清晰 ticket/SPEC 切片 | [`implement`](../../../skills/implement/SKILL.md) — user-invoked | `implement` → 查上下文 → 必要时 `agent-config`（当路由/独立性重要） → 执行 → 验证 → 交 `review-loop` 配对应 reviewer | 有界 diff + 聚焦测试 + 验证证据；止于 ticket 范围 |
| 需决定执行拓扑 | [`agent-config`](../../../skills/agent-config/SKILL.md) — model-invoked | 需：有界任务 + 验收权威 + 带 ownership 的 change units + 当前 host 证据；返回 `multi-model/multi-agent` / `single-model/multi-agent` / `single-model/single-agent` / `BOUNDARY` | 产出执行计划，不直接执行 |
| 代码功能应测试先行 | [`tdd`](../../../skills/tdd/SKILL.md) — model-invoked | `red → green → refactor` 真测试循环 | 测试 + 实现切片 |
| 难 bug / 回退 | [`diagnosing-bugs`](../../../skills/diagnosing-bugs/SKILL.md) — model-invoked | 建紧 `pass/fail` 信号 → 复现 → 假设 → 埋点 → 修复 → 清理 | 带反馈环的修复 |
| 合并/变基冲突 | [`resolving-merge-conflicts`](../../../skills/resolving-merge-conflicts/SKILL.md) — model-invoked | 按 git 指引解决冲突文件 | 干净工作区待验证 |

## 与 Review 的组合

`implement` 不复制 reviewer 指令。代码：

```text
implement → tdd（合适时） → 代码 + 测试 → review-loop → code-review
```

非代码：

```text
implement → 产物 → review-loop → generic-review / 领域 reviewer
```

reviewer 只读；`review-loop` 为收敛引擎；需项目级验收时由 `project-review` 签发最终 `PASS`/`FAIL`/`BLOCKED`（见 [review-system](review-system.md)）。

## 何时不用本组

- 想法模糊 → 先 [clarification-system](clarification-system.md)。
- SPEC 已准入 → 先 [`project-tickets`](../../../skills/project-tickets/SKILL.md)。
- 项目已完成 → [`project-review`](../../../skills/project-review/SKILL.md) / [review-system](review-system.md)。
- 不知入口 → [`ask-light`](../../../skills/ask-light/SKILL.md)。
