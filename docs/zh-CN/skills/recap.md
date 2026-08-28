# `recap` 使用指南

[English guide](../../skills/recap.md)

行为权威是 [skills/recap/SKILL.md](../../../skills/recap/SKILL.md)；本页只说明使用方式，不创建第二份契约。

## 作用

用一句不超过 400 字符的简洁文本展示当前 session，不替换或压缩对话历史。

## 调用

必须显式选择：

```text
$recap
```

包 frontmatter 与 host metadata 将该入口保持为 user-invoked。

## 验证与发布状态

当前修订由 [tests/test_functional_closure.py](../../../tests/test_functional_closure.py) 验证。未改动的 [package tests](../../../skills/recap/tests/) 是旧版长契约的历史记录，不属于当前主动套件。Fresh-copy 与独立审查证据见[准入记录](../../evidence/admissions/recap/README.zh-CN.md)。

旧版 `recap` 已在 v0.1.2 中发布；本次仅手动触发的修订仍属于当前未发布候选。当前稳定发布版可使用 `npx skills add LightDevCoder/skills#v0.1.6 --skill recap` 安装，刷新 host，并在脱离 source checkout 的情况下确认 discovery；见[安装策略](../../INSTALLATION.zh-CN.md)。

## 行为参考

- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code session recap](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code prompt caching 与 `/recap`](https://code.claude.com/docs/en/prompt-caching)

这些链接只定义可观察的产品边界；本包未复制 Anthropic 源码或 prompt 文本。
