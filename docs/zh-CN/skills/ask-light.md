# `ask-light` 使用指南

[英文指南](../../skills/ask-light.md)

工作流顾问、router 与输出契约见 [skills/ask-light/SKILL.md](../../../skills/ask-light/SKILL.md) 和 [discovery contract](../../../skills/ask-light/references/discovery-contract.md)。

## 解决什么问题

`ask-light` 是 Light 工作流顾问、导航器与路由：确定性检查项目与 host 证据，理解用户意图与候选 Skill 契约，基于上下文进行工作流推理并给出下一步 Light Skill 建议，等待用户批准并在转换前验证所选动作与仓库硬约束。

架构：
```text
Code 确定可靠事实。
Model 理解当前场景。
Model 选择工作流动作。
Code 验证该项选择。
```

## 模式和边界

它是 `user-invoked only`，主要入口为：

```text
$ask-light next
$ask-light workflow
$ask-light <category>
```

`next` 返回一个基于证据的建议，最多一个动作不同的并列候选。`workflow` 返回锚定在当前状态的 recipe，包含步骤可用性、handoff 契约与停止点。`navigate` 回答“显示项目 Skills”或精确对比等收藏浏览问题。

批准前 `ask-light` 是只读的：不执行、不安装、不编辑、不委派，也不创建永久 state machine。用户以普通 `yes`/`可以`/`go ahead` 批准后，对 model-invoked 推荐可在当前对话中开始；对 user-invoked 推荐，仅在存在验证过的 host 证据支持 approved transition 时直接进入，否则渲染精确调用（Codex 为 `$skill`，Claude Code 为 `/<skill>`）并请用户启动。它不假装执行，不会在被接受 Skill 之外自动串联，也绝不在无 host 证据时假设具备该能力。

## 输入和输出

`ask_light.py` 提供确定性的证据收集（`--mode next`）、recipe 发布（`--mode workflow`）、分类查找（`--mode navigate`）与选后验证（`--mode validate`）。语义路由判断归属 Model。选中的 Skill 不可用或违反硬约束时保留逻辑推荐并返回 `BLOCKED`。

可执行 helper 依赖 Python 3.9 或更高版本，并支持根发现（`LIGHT_SKILL_ROOTS`、源码 checkout 的 `skills/` 根或文档化 host roots）。缺少 Python 时，PowerShell launcher 返回结构化 `BLOCKED`；此时按 discovery contract 协议手工完成。

示意输出（不是本次 host 已经执行的证明）：

```text
Mode: next
Status: RECOMMEND
Skill: project-tickets
Scope: current-workflow
Next: awaiting-approval
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

## 误用、组合和停止点

不要把它当成 discovery/specification 引擎、installer、scheduler 或静默自动串联器。它只路由真实第一方 Skills，包括 `project-init`、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`code-review`、`project-review`、`learn-anything` 或 `manuscript-ops`。执行仅在用户同意后按 host 支持方式开始。规范项目流程为 `project-clarify → project-spec → project-tickets → implement → project-review`。`project-review` 拥有最终验收。建议后等待批准，或遇到 `NEED-INPUT`/`BLOCKED` 后停止。

## 安装与发现验证

验证时，将完整 `ask-light` 包复制到隔离的 host Skill 根，刷新后在不依赖 source checkout 的情况下检查 `SKILL.md`、`light-skill-map.json`、Python helper 与 PowerShell 兼容 launcher。在相应 release 通过发布安装门禁前，不把任何安装命令标记为已验证。运行 [contract test](../../../skills/ask-light/tests/test_ask_light_contract.py) 与 [behavior test](../../../skills/ask-light/tests/test_ask_light_behavior.py)，覆盖证据检查、选择验证、审查事务安全性、freshness 检查、根发现、来源、host 可用性与批准转换边界。