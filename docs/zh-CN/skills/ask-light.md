# `ask-light` 使用指南

[英文指南](../../skills/ask-light.md)

行为与 scanner 输出契约见 [skills/ask-light/SKILL.md](../../../skills/ask-light/SKILL.md) 和 [discovery contract](../../../skills/ask-light/references/discovery-contract.md)。

## 解决什么问题

`ask-light` 检查当前 host 可见的 Skill metadata 和 availability，返回一个最合适的下一 Skill，或一个有边界的 workflow recipe。它保留重复 source identity，只读取 shortlist 的 body，报告 metadata 缺口，并尊重 invocation policy。

## 模式和边界

它是 `user-invoked only`，入口为：

```text
$ask-light next
$ask-light workflow
```

`next` 返回一个建议，最多一个真实且动作不同的并列候选。`workflow` 返回 entry condition、步骤、source、invocation type、expected input/output、handoff artifact、stop condition、optional 和 missing dependency。两种模式都不执行、不安装、不编辑、不委派，也不创建永久 state machine；不会重新引入退休的 `project-workflow`。

## 输入和输出

提供 goal、artifacts、blockers、project type、task kind、真实 host availability/readable roots 和 invocation control。先读 metadata，再有限读取 body/reference。缺上下文返回 `NEED-INPUT`；必需 Skill 不可见或 metadata 不可读返回带准确缺口的 `BLOCKED`。私有 `skills-3rdParty` 根不存在时，不能声称其可用。

示意输出（不是本次 host 已经执行的证明）：

```text
Mode: workflow
Status: RECOMMEND
Workflow: software-feature
Execution: recommendation only; nothing was invoked, installed, or orchestrated
```

## 误用、组合和停止点

不要把它当成 discovery/specification 引擎、installer、scheduler 或自动串联器。它可以指向 `project-init`、`learn-anything`、`manuscript-ops`、`to-spec`、`implement`、`code-review` 或 `review-loop`，但下一步必须由用户显式选择。最终 verdict 归 `review-loop`；建议、`NEED-INPUT` 或 `BLOCKED` 记录后就停止。

## 安装与发现验证

对于已发布的 v0.1.2，使用 `npx skills add LightDevCoder/skills --skill ask-light --yes --copy --agent '*'` 安装，刷新 host，在不依赖 source checkout 的情况下检查 `SKILL.md`、`agents/openai.yaml` 和 PowerShell scanner。运行 [contract test](../../../skills/ask-light/tests/test_ask_light_contract.py) 与 [behavior test](../../../skills/ask-light/tests/test_ask_light_behavior.py)，覆盖 learn-anything、私有依赖缺失和歧义 fixtures。
