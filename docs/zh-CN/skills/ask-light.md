# `ask-light` 使用指南

[英文指南](../../skills/ask-light.md)

行为与 router 输出契约见 [skills/ask-light/SKILL.md](../../../skills/ask-light/SKILL.md) 和 [discovery contract](../../../skills/ask-light/references/discovery-contract.md)。

## 解决什么问题

`ask-light` 先通过 Light 自有的 33-Skill 语义地图判断逻辑匹配，再单独验证该 Skill 在当前 host 是否可用。可选 UI metadata 缺失不会隐藏已知包，generic host root 也不会被当作第一方来源。

## 模式和边界

它是 `user-invoked only`，入口为：

```text
$ask-light next
$ask-light workflow
```

`next` 返回一个建议，最多一个真实且动作不同的并列候选。`workflow` 返回 entry condition、步骤、source、invocation type、expected input/output、handoff artifact、stop condition、optional 和 missing dependency。两种模式都不执行、不安装、不编辑、不委派，也不创建永久 state machine；不会重新引入退休的 `project-workflow`。

## 输入和输出

提供 goal、artifacts、blockers、project type、task kind、真实 host availability/readable roots 和 invocation control。逻辑路由来自 `light-skill-map.json`；包读取只证明 host availability 与本地 pointer 完整性。缺上下文返回 `NEED-INPUT`；选中的 Skill 不可用时保留逻辑推荐并返回 `BLOCKED`。

可执行 router 依赖 Python 3.9 或更高版本。缺少 Python 时，PowerShell launcher 返回结构化 `BLOCKED`；此时按 discovery contract 的双层协议手工完成路由。

示意输出（不是本次 host 已经执行的证明）：

```text
Mode: workflow
Status: RECOMMEND
Workflow: software-feature
Execution: recommendation only; nothing was invoked, installed, or orchestrated
```

## 误用、组合和停止点

不要把它当成 discovery/specification 引擎、installer、scheduler 或自动串联器。它只路由真实第一方 Skills，可以指向 `project-init`、`learn-anything`、`manuscript-ops`、`project-spec`、`implement`、`code-review` 或 `project-review`，但下一步必须由用户显式选择。需要验收的 recipe 最终 verdict 归 `project-review`；建议、`NEED-INPUT` 或 `BLOCKED` 记录后就停止。

## 安装与发现验证

该 router 属于尚未发布的 33-package 分支。预发布验收时，将完整 `ask-light` 包复制到隔离的 host Skill 根，刷新后在不依赖 source checkout 的情况下检查 `SKILL.md`、`light-skill-map.json`、Python router 与 PowerShell 兼容 launcher；在相应 release 通过发布安装门禁前，不把任何安装命令标记为已验证。运行 [contract test](../../../skills/ask-light/tests/test_ask_light_contract.py) 与 [behavior test](../../../skills/ask-light/tests/test_ask_light_behavior.py)，覆盖代表性 top result、Frozen metadata、来源、host 可用性、调用展示与 pointer failure。
