# `learn-anything` 使用指南

[English guide](../../skills/learn-anything.md)

唯一行为权威是 [skills/learn-anything/SKILL.md](../../../skills/learn-anything/SKILL.md)。

## 解决什么问题

`learn-anything` 判断资料中是否存在可复用的方法，并提取由 source 支持的内部 Method Contract。它保留 trigger、decision、命令、约束、failure mode、资源、输出和 verification，不把被动摘要伪装成 Skill。

## 何时使用 / 不使用

当 conversation、transcript、issue、folder workflow、README 或重复用户修正包含可复用操作方法时使用。一次性任务、叙述、稀疏笔记和通用 authoring 建议不应直接生成 Skill。证据不完整时必须返回 learning summary 或 `BLOCKED`，不能补写缺失字段。

它是 `user-invoked only`：

```text
$learn-anything
```

输入是 source、provenance、必须保留的命令/路径/错误，以及项目或 Skill 规则。完整结果是内部 Method Contract；通过 gate 后才进入 deterministic Package Build Layer，例如：

```text
python learn-anything/hooks/package_builder.py --contract-file <method-contract-result.json> --output-root <skill-collection-root>
```

builder 会报告 `created`、`updated`、`no-op`、`duplicate` 或 `blocked`。只安装完整生成包，并验证第二次安装幂等。

## 成功与 `BLOCKED`

成功要求所有方法字段都有证据，且没有 unresolved marker。source gap、矛盾 invocation、未解析资源或 ownership duplicate 时返回精确的 `BLOCKED`；被动或一次性资料则标记 `not_promoted`。不要用通用 Purpose、Workflow 或 Quality Checks 填空。

## 组合和停止点

`writing-great-skills` 只能在 Method Contract 后提供可选 authoring knowledge，不是 `learn-anything` 的隐式 runtime dependency。deterministic package build 后交给 `review-loop` 的 `agent-skill` Profile，再走 admission。到 Method Contract、builder 结果或精确 `BLOCKED` 缺口时停止；不要隐式调用其他 user-invoked Skill。

## 安装与发现验证

对于已发布的 v0.1.1，使用 `npx skills add LightDevCoder/skills#v0.1.1 --skill learn-anything` 安装，刷新 host，在脱离 source checkout 的情况下检查 `SKILL.md`、`agents/openai.yaml` 和 `hooks/`。显式 metadata 必须包含 `allow_implicit_invocation: false`。
