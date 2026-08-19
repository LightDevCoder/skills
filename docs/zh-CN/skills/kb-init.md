# `kb-init` 使用指南

[English guide](../../skills/kb-init.md)

行为权威是 [skills/kb-init/SKILL.md](../../../skills/kb-init/SKILL.md)；本页只说明使用方式，不创建第二份契约。

## 作用

`kb-init` 是仅 user-invoked 的 Skill，用于设计并初始化可维护的知识库。它先进行知识库专属访谈，再调研所选 base 的实际可操作方法，产出实施方案 SPEC，并且必须在用户明确批准后才能开始创建任何内容。

它不是通用 grilling 技能，也不绑定任何特定 wiki、笔记应用、数据库或文件格式。

## 调用

必须显式选择：

```text
$kb-init
```

它不能因为泛泛提到知识库、笔记、wiki 或研究档案而自动触发。一旦被显式调用且几乎没有上下文，它会自动开始访谈。

## 预期结果

- **成功：** 访谈覆盖所需设计领域，用户明确结束访谈，生成知识库专属 SPEC；只有明确批准后才开始实施、验证与 handoff。
- **边界：** 用户提问或质疑时先回答问题，再继续访谈；相关决策保持开放，不能把问题当作接受。
- **失败：** 在用户明确批准前产出 SPEC 或实施任何内容都违反契约，不能作为有效的 `kb-init` 结果。

`kb-init` 可在需要当前外部事实时调用 model-invoked `research` 能力；绝不调用另一个 user-invoked Skill。

## 验证与发布状态

运行 [package contract test](../../../skills/kb-init/tests/) 并检查 `agents/openai.yaml` 中的 `allow_implicit_invocation: false`。完整准入路径使用 `review-loop agent-skill`；最终 verdict 为 `PASS`，没有未解决的 `BLOCKED` 条件。证据见[准入记录](../../evidence/admissions/kb-init/README.zh-CN.md)。

`kb-init` v1.0.0 已随 v0.1.6 发布。使用 `npx skills add LightDevCoder/skills --skill kb-init --yes --copy --agent '*'` 安装，刷新 host，并在脱离 source checkout 的情况下确认 discovery；见[安装策略](../../INSTALLATION.zh-CN.md)。
