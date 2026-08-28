# `review-loop` 使用指南

[英文指南](../../skills/review-loop.md)

行为权威仍是 [skills/review-loop/SKILL.md](../../../skills/review-loop/SKILL.md)；本页只说明如何使用，不复制第二份契约。

## 解决什么问题

`review-loop` 是轻量 Review Engine：驱动 `review → findings → repair → re-review` 单一循环。它解析 reviewer、调用、收归一化 findings、把确认且 in-scope 的 findings 交回 Producer，并在干净或达到有界上限时停止。

它不拥有项目最终 `PASS`/`FAIL`/`BLOCKED`；那是 `project-review` 的职责。

## 何时使用 / 不使用

当有界评审需要修复收敛时使用：实现 handoff、包评审、或已有 bounded packet 和具体修复路径的例行评审。

不要用它冻结验收基线、签发项目 verdict，或替代 `project-review`。

## 边界、输入和输出

它是 `model-invoked`，也支持手动入口。

输入 packet 有四个字段：Target、Requirements、Relevant context、Previous findings。输出为归一化 findings（干净时 `Findings: []`），或缺少必要输入时的 `REVIEW-ERROR`。达到上限时把未决 findings 交给调用方。

## 成功与 `BLOCKED`

成功意味着循环到达 `Findings: []`，或在配置上限处把未决 findings 交给调用方。`BLOCKED`/`PASS`/`FAIL` 不是引擎 verdict；`project-review` 经此引擎组合 reviewer 后签发。

## 组合和停止点

默认组合 `generic-review`；软件 diff 用 `code-review`；有已接受 specialist 时用领域 reviewer。`project-review` 是最终验收拥有者。干净或达上限后停止并交给调用方；不要隐式调用其他 user-invoked Skill。

## 安装与发现验证

使用 `npx skills add LightDevCoder/skills --skill review-loop` 安装，刷新 host，在不依赖 source checkout 的情况下检查已发现的 `SKILL.md` 和 `agents/openai.yaml`。运行 [tests](../../../skills/review-loop/tests/)；结果记录在[安装证据](../../evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.zh-CN.md)。