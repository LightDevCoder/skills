# `language-learning` 使用指南

[English guide](../../skills/language-learning.md)

行为权威是 [skills/language-learning/SKILL.md](../../../skills/language-learning/SKILL.md)；本页只说明使用方式，不创建第二份契约。

## 作用

`language-learning` 是仅 user-invoked 的任意目标语言辅导。它通过六种学习模式运行：每日课程、即时卡片、对话练习、语法解码、进度测验与沉浸翻译。它会复用会话中的目标语言、学习者水平、母语和近期已学词汇，而不是每次都重新询问；纠错也按需选择，而不是每次都套一遍教学模板。

## 调用

必须显式选择：

```text
$language-learning
```

也可以直接指定模式，例如：

```text
$language-learning Spanish, flashcards for: perro, gato, casa
```

它不能自动运行；会沿用会话中已有的水平，水平未知时默认 beginner，并让学习者持续输出语言。

## 预期结果

- **成功：** 请求的模式完成契约——30 分钟课程、给定条目逐一成卡、展开对话、解码语法、10 题测验，或带理解提问的沉浸式改编翻译。
- **边界：** 混合或模糊请求只路由到一个主模式，并顺带给出第二个选项，而不是发明新能力。
- **失败：** 每次调用都重新询问语言、水平与模式，或逐条列出学习者的全部错误，都违反教学契约。

`language-learning` 不会调用另一个 user-invoked Skill。持久化续接记录需要用户另行选择 `handoff`；最终验收仍由 `project-review` 拥有。`BLOCKED` 或不完整的准入状态不会改变包契约。

## 验证与发布状态

运行 [package tests](../../../skills/language-learning/tests/)，并检查 `agents/openai.yaml` 中的 `allow_implicit_invocation: false`。纯提示型快速通道 `PASS` 准入证据见[准入记录](../../evidence/admissions/language-learning/README.zh-CN.md)。

`language-learning` 已在 v0.1.2 中发布。使用 `npx skills add LightDevCoder/skills --skill language-learning` 安装，刷新 host，并在脱离 source checkout 的情况下确认 discovery；见[安装策略](../../INSTALLATION.zh-CN.md)。

## 行为来源

本 skill 为原创第一方设计。本包未复制任何上游 Skill 代码或 prompt 文本。
