# Specialized Workflows — 组合

[English](../../workflows/specialized-workflows.md)

本文说明 **Specialized Workflows**：各自独立，也可与主流程组合。它们不是 `project-init → … → release-workflow` 的必选成员。

## 本组 Skill

- [`manuscript-ops`](../../../skills/manuscript-ops/SKILL.md) — 文稿工程状态机
- [`kb-init`](../../../skills/kb-init/SKILL.md) — 经访谈设计、审批后实施的知识库
- [`learn-anything`](../../../skills/learn-anything/SKILL.md) — 把有证据的来源提炼为可复用方法
- [`language-learning`](../../../skills/language-learning/SKILL.md) — 六模式语言辅导
- [`kanban-worker`](../../../skills/kanban-worker/SKILL.md) — 每次唤醒一张任务的看板 worker
- [`recap`](../../../skills/recap/SKILL.md) — 一行总结（仅 `$recap`）
- [`eli5`](../../../skills/eli5/SKILL.md) — 按受众水平解释
- [`release-workflow`](../../../skills/release-workflow/SKILL.md) — 验收后发布（也是主流程收尾）

## 独立 vs 组合

八个包均已验证：

1. **独立正确性**——不依赖主流程即可满足 `SKILL.md`。
2. **组合适配**——产物可交给下一 Skill 而无须返工。

规则：产物已自然可交接（如交付物、Method Contract、看板 `complete`）时**不改 Skill**；仅真实集成缺口处允许加最小 handoff 句：

```text
When this workflow reaches <state>, the caller may continue with <skill>.
```

加一句 handoff 不是重写。

## Entry → Handoff → Stop

| Skill | 典型独立入口 | 自然 handoff（可选） | 停止点 |
| --- | --- | --- | --- |
| [`manuscript-ops`](../../../skills/manuscript-ops/SKILL.md) | 文稿范围/风险/批次/格式 | 可经用户选择调 `grill-me`/`wayfinder`；已批准 brief/Charter 可交 `project-review`（`manuscript` Profile） | 止于路由决策、Charter 冻结或已 QA 交付 |
| [`kb-init`](../../../skills/kb-init/SKILL.md) | `$kb-init` | 访谈 → 已批 SPEC → 实施；事实不足时可调 `research` | 止于设计或已初始化知识库 |
| [`learn-anything`](../../../skills/learn-anything/SKILL.md) | 含可复用方法的来源 | 内部 Method Contract → 确定性 builder → `review-loop agent-skill` → 目录/文档同步 | 止于 `method_contract` / `not_promoted` / `BLOCKED` |
| [`language-learning`](../../../skills/language-learning/SKILL.md) | 语言学习请求 | 六模式各自返回产物 | 止于课程/测验结果 |
| [`kanban-worker`](../../../skills/kanban-worker/SKILL.md) | 定时唤醒 | `complete` 或 `block` 带原因；下一次唤醒先处理 `reviewFeedback` | 一张任务后停止 |
| [`recap`](../../../skills/recap/SKILL.md) | `$recap` | 严格一行总结，不继续工作 | 停止 |
| [`eli5`](../../../skills/eli5/SKILL.md) | 解释请求 | 按受众定制的解释 | 停止 |
| [`release-workflow`](../../../skills/release-workflow/SKILL.md) | `project-review PASS` 后 | 打 tag / GitHub Release / 同步文档 | 止于发布记录 |

## 与主流程的交汇

- `project-clarify` 发现领域更适 `manuscript-ops`/`kb-init` 时可分流至专业流，而非通用 `project-spec`。
- `learn-anything` 提炼的方法经准入成为新 Skill 后，可参与后续 `implement`。
- `kanban-worker` 分解已由 `project-tickets` 产生的 ticket 并上报 `complete`/`block`。
- `release-workflow` 既是专业收尾，也是主流程尾巴。
- 不确定时用 [`ask-light`](../../../skills/ask-light/SKILL.md) 路由到合适的专业 Skill。

不做强制统一。各包保持自有形态（`references/`、`templates/`、`scripts/` 按真实需要）。
