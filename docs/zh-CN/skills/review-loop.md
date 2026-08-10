# `review-loop` 使用指南

[英文指南](../../skills/review-loop.md)

行为权威仍是 [skills/review-loop/SKILL.md](../../../skills/review-loop/SKILL.md)；本页只说明如何使用，不复制第二份契约。

## 解决什么问题

`review-loop` 把已经批准的目标与验收来源转成有边界的证据、批评、修复、评估和最终裁决循环。Core 角色冻结基线、保存 durable state、执行停止规则，并拥有 `PASS`、`FAIL`、`BLOCKED` verdict。

## 何时使用 / 不使用

当目标、范围、验收权威、证据边界和适用 Profile 已经明确时使用。可按目标选择 `agent-skill`、`software`、`manuscript`、`specification` 等 Profile。

不要用它发明产品目标、解决未决架构决策、让 reviewer 代写产物、发布 release，或为了迁就实现而放宽验收源。缺少这些前置决定时，先显式选择 `ask-light`、`project-init`、`to-spec` 等入口。

## 边界、输入和输出

它是 `model-invoked`，也支持手动入口。手动调用示例：

```text
$review-loop init using docs/acceptance.md
$review-loop review
$review-loop resume
```

输入是目标、批准的验收源、Profile、范围/排除项、证据要求，以及需要持久化时可写的 `.review-loop/`。输出包括 Charter、state、findings、round evidence、repair disposition 和最终 verdict。专家 findings 不能替代 verdict。

## 成功与 `BLOCKED`

成功要求基线已冻结、声明的验收轴都有 admissible evidence、findings 已处置、修复没有越界，并且独立 Evaluator 已向 Core 提供新鲜证据。验收源缺失/未批准、目标不可读、Profile 或证据不可用、独立性或 state gate 无法推进时，应记录最小解阻动作并返回 `BLOCKED`。

## 组合和停止点

它可以消费 `project-init`、`to-spec`、`to-tickets`、实现证据、`code-review` findings 或 manuscript format QA。`code-review` 只提供 specialist findings；最终权威仍是 `review-loop`。到 verdict 后停止，再交给 `handoff` 或 release closeout；不要隐式调用其他 user-invoked Skill。

## 安装与发现验证

对于已发布的 v0.1.2，使用 `npx skills add LightDevCoder/skills --skill review-loop --yes --copy --agent '*'` 安装，刷新 host，在不依赖 source checkout 的情况下检查已发现的 `SKILL.md` 和 `agents/openai.yaml`。运行 [Profile tests](../../../skills/review-loop/tests/)；结果记录在[安装证据](../../evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。
