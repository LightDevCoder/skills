# `ask-light` 使用指南

[英文指南](../../skills/ask-light.md)

工作流顾问、router 与输出契约见 [skills/ask-light/SKILL.md](../../../skills/ask-light/SKILL.md) 和 [discovery contract](../../../skills/ask-light/references/discovery-contract.md)。

## 解决什么问题

`ask-light` 先检查当前项目/工作流状态，再通过 Light 自有的 33-Skill 语义地图判断逻辑匹配，并单独验证该 Skill 在当前 host 是否可用。它给出带工作流理由的下一步建议，等待用户批准后再开始被接受的 Skill。可选 UI metadata 缺失不会隐藏已知包，generic host root 也不会被当作第一方来源。

## 模式和边界

它是 `user-invoked only`，入口为：

```text
$ask-light next
$ask-light workflow
$ask-light <category>
```

`next` 返回一个基于证据的建议，最多一个真实且动作不同的并列候选。`workflow` 返回 entry condition、步骤、source、invocation type、expected input/output、handoff artifact、stop condition、optional 和 missing dependency。`navigate` 回答“显示项目 Skills”“哪些是学习类”等收藏浏览问题。

批准前 `ask-light` 是只读的：不执行、不安装、不编辑、不委派，也不创建永久 state machine。用户以普通 `yes`/`可以`/`go ahead` 批准后，在当前对话中开始被推荐的 Skill（Codex），或使用 host 支持的转换机制。它不会重新引入退休的 `project-workflow`，也不会在被接受 Skill 之外自动串联。

## 输入和输出

项目阶段路由需要 goal、artifacts、blockers、project type、task kind、真实 host availability/readable roots 和 invocation control。逻辑路由来自 `light-skill-map.json`；包读取只证明 host availability 与本地 pointer 完整性。缺上下文返回 `NEED-INPUT`；选中的 Skill 不可用时保留逻辑推荐并返回 `BLOCKED`。

可执行 router 依赖 Python 3.9 或更高版本，并支持不传 `--roots-json` 的根发现（`LIGHT_SKILL_ROOTS`、源码 checkout 的 `skills/` 根或文档化 host roots）。缺少 Python 时，PowerShell launcher 返回结构化 `BLOCKED`；此时按 discovery contract 的双层协议手工完成路由。

示意输出（不是本次 host 已经执行的证明）：

```text
Mode: next
Status: RECOMMEND
Skill: project-tickets
Next: awaiting-approval
Execution: recommendation phase was read-only; execution begins only after explicit user approval
```

## 误用、组合和停止点

不要把它当成 discovery/specification 引擎、installer、scheduler 或静默自动串联器。它只路由真实第一方 Skills，可以指向 `project-init`、`learn-anything`、`manuscript-ops`、`project-spec`、`implement`、`code-review` 或 `project-review`，但只有用户同意后才开始执行。需要验收的 recipe 最终 verdict 归 `project-review`；建议后等待批准，或遇到 `NEED-INPUT`/`BLOCKED` 后停止。

## 安装与发现验证

该 router 属于尚未发布的 33-package 分支。预发布验收时，将完整 `ask-light` 包复制到隔离的 host Skill 根，刷新后在不依赖 source checkout 的情况下检查 `SKILL.md`、`light-skill-map.json`、Python router 与 PowerShell 兼容 launcher；在相应 release 通过发布安装门禁前，不把任何安装命令标记为已验证。运行 [contract test](../../../skills/ask-light/tests/test_ask_light_contract.py) 与 [behavior test](../../../skills/ask-light/tests/test_ask_light_behavior.py)，覆盖项目状态建议、批准到执行、根发现、来源、host 可用性、调用展示与 pointer failure。