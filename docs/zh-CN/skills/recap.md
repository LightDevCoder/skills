# `recap` 使用指南

[English guide](../../skills/recap.md)

行为权威是 [skills/recap/SKILL.md](../../../skills/recap/SKILL.md)；本页只说明使用方式，不创建第二份契约。

## 作用

`recap` 是仅 user-invoked、只读的状态速览。它用严格一行纯文本总结当前目标、最新关键结果和当前状态。该实现独立复刻 Anthropic 已公开说明的按需 recap 边界：显示一行摘要，但不替换历史。

## 调用

必须显式选择：

```text
$recap
```

它不能自动运行；只使用当前已有 session context，不运行工具、不修改文件、不压缩历史，并在输出一行后停止。

## 预期结果

- **成功：** 一句简洁文本包含最新关键结果与当前状态。
- **边界：** session 几乎没有上下文时，用一行说明没有可总结的先前活动，不虚构进度。
- **失败：** 多行、带标签、项目符号、调用工具或改变状态的输出都违反契约，不能作为有效 recap。

`recap` 不会调用另一个 user-invoked Skill。持久化续接记录需要用户另行选择 `handoff`；最终验收仍由 `review-loop` 拥有。缺少 session context 只产生一行边界结果，不能被静默改写成 `review-loop` 的 `BLOCKED` verdict。

## 验证与发布状态

运行 [package tests](../../../skills/recap/tests/)，并检查 `agents/openai.yaml` 中的 `allow_implicit_invocation: false`。Fresh-copy 与独立审查证据见[准入记录](../../evidence/admissions/recap/README.zh-CN.md)。

`recap` 已在 v0.1.2 中发布。使用 `npx skills add LightDevCoder/skills --skill recap --yes --copy --agent '*'` 安装，刷新 host，并在脱离 source checkout 的情况下确认 discovery；见[安装策略](../../INSTALLATION.zh-CN.md)。

## 行为参考

- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code session recap](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code prompt caching 与 `/recap`](https://code.claude.com/docs/en/prompt-caching)

这些链接只定义可观察的产品边界；本包未复制 Anthropic 源码或 prompt 文本。
