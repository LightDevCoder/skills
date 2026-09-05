# Execution — 组合

[English](../../workflows/execution.md)

本文说明 **Execution** 的组合：入口、路由与 handoff。分步流程在各 `SKILL.md` 与 `references/` 中。

## 本组 Skill

- [`implement`](../../../skills/implement/SKILL.md) — user-invoked 通用有边界执行器
- [`agent-config`](../../../skills/agent-config/SKILL.md) — model-invoked Profile 驱动跨 Harness 执行配置器
- [`tdd`](../../../skills/tdd/SKILL.md) — model-invoked 测试驱动环
- [`diagnosing-bugs`](../../../skills/diagnosing-bugs/SKILL.md) — model-invoked 诊断环
- [`resolving-merge-conflicts`](../../../skills/resolving-merge-conflicts/SKILL.md) — model-invoked 合并冲突解决

均为第一方自包含包，运行时不要求 `mattpocock/skills` 或 `sol-advisor`。

## Entry → Handoff → Stop

| 场景 | 入口 | 典型路径 | Handoff / 停止 |
| --- | --- | --- | --- |
| 单个清晰 ticket/SPEC 切片 | [`implement`](../../../skills/implement/SKILL.md) — user-invoked | `implement` → 查上下文 → 当 Profile 路由/隔离性/拓扑重要时提供可选 `agent-config` → 执行 → 验证 → 交 `review-loop` 配对应 reviewer | 有界 diff + 聚焦测试 + 验证证据；止于 ticket 范围 |
| 需配置模型、effort 或执行拓扑 | [`agent-config`](../../../skills/agent-config/SKILL.md) — model-invoked | 需：有界任务或 ticket 图 + 验收权威 + 当前宿主证据 + 确认 Profile；判断 Provider 模式与任务形态，在四种执行模式（Case A、B、C、D）下精准适配模型层级与 effort | 产出 Profile 驱动的执行计划，不直接执行；执行者依计划实施 |
| 代码功能应测试先行 | [`tdd`](../../../skills/tdd/SKILL.md) — model-invoked | `red → green → refactor` 真测试循环 | 测试 + 实现切片 |
| 难 bug / 回退 | [`diagnosing-bugs`](../../../skills/diagnosing-bugs/SKILL.md) — model-invoked | 建紧 `pass/fail` 信号 → 复现 → 假设 → 埋点 → 修复 → 清理 | 带反馈环的修复 |
| 合并/变基冲突 | [`resolving-merge-conflicts`](../../../skills/resolving-merge-conflicts/SKILL.md) — model-invoked | 按 git 指引解决冲突文件 | 干净工作区待验证 |

## 双仓架构：Skill 与 Companion

执行配置系统严格将策略推理与宿主持久化/变更解耦：

- **Skill（`skills/agent-config`）：** 从本仓库（[LightDevCoder/skills](https://github.com/LightDevCoder/skills)）安装。负责任务难度评估、档位选择与执行拓扑规划，在 Agent 会话中纯策略运行。
- **Companion MCP 运行时：** 维护于独立公开仓库 [LightDevCoder/agent-config](https://github.com/LightDevCoder/agent-config)。提供 9 种原生宿主适配器（Codex、Claude Code、Antigravity / agy、DeepSeek Harness / DSH、OpenCode、ZCode、Cursor、Grok Build、Hermes）以及通用回退。
- **可选 Companion：** 未注册 Companion MCP 服务时，`agent-config` 仍能在纯会话级、纯计划（plan-only）模式下正常完整运行，不改动宿主配置。安装并注册 Companion 后，可解锁真实宿主能力探测、Profile 持久化、先预览后应用的变更控制以及健康度验证。

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
