# `manuscript-ops` 使用指南

[英文指南](../../skills/manuscript-ops.md)

完整行为契约见 [skills/manuscript-ops/SKILL.md](../../../skills/manuscript-ops/SKILL.md)。

## 解决什么问题

`manuscript-ops` 管理从笔记、结构化报告到多语言、多格式交付物的文稿工程。它持续保存 source authority、用户决定、可复现生成、review evidence、format QA、锁版和 resume boundary。

## 何时使用 / 不使用

当 manuscript、manual、book、多语言版本或格式风险较高的文稿需要 source、batch、review 或 production 治理时使用。它不是通用 task router、静默 project initializer、自动 workflow manager，也不替代 `project-review` 的最终 verdict 机制。

它是 `model-invoked`，host 允许时也可手动进入：

```text
$manuscript-ops
$manuscript-ops resume
```

## 前置条件、输入和输出

先解析准确的 project root，读取适用规则和状态，检查 formats/sources/capabilities；内置工具要求 Python 3.11+。输入包括六维 routing、source register、Manuscript Brief、Project Profile、format set、验收轴和已有 state。输出包括 routing snapshot、显式 handoff、可恢复 state、source/batch/format 记录、review evidence 和 production QA。

## Handoff、成功和 `BLOCKED`

Project route 先按需要选择一个 discovery handoff：单会话决策用 `clarify`，多会话不确定性用 `decision-map`，随后停止。`clarify` 是用户入口，底层的 model-invoked 能力是 `socratic`；二者是同一澄清能力，不是两个用户步骤。只有用户显式 resume 才能继续。初始化前需用户显式选择 `project-init`，review 前需批准的 `project-review` Charter。root、dependency、brief、capability、证据或真实渲染/round-trip proof 缺失时返回 `BLOCKED`，不能把语法有效当成视觉验收。

## 组合和最终权威

标准治理路径为 `manuscript-ops` → `clarify`/`decision-map` → `project-init` → `project-review init` → production → `project-review` manuscript review（经 `review-loop` 收敛）。每个 user-invoked handoff 和 resume 都由用户控制。`project-review` 拥有 generic findings、独立性、state 和最终 `PASS`/`FAIL`/`BLOCKED`；`manuscript-ops` 只提供文稿证据边界并消费 verdict。到 handoff 或最终 verdict 即停止。

## 安装与发现验证

对于已发布的 v0.1.2，使用 `npx skills add LightDevCoder/skills --skill manuscript-ops --yes --copy --agent '*'` 安装，刷新 host，在不依赖 source checkout 的情况下验证 `assets/`、`references/`、`scripts/` 等完整资源。先运行 capability/dependency/state 检查，再把 format 结果标为 verified。
