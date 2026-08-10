# `language-learning` 准入证据

[English record](README.md)

## 范围与状态

- 包：`skills/language-learning/`
- 调用类型：仅 user-invoked
- Profile：`review-loop` `agent-skill`
- 准入状态：低风险纯提示型快速通道 `PASS`
- 稳定版本边界：v0.1.1 包含五个包，不含 `language-learning`

## 证据摘要

| 领域 | 结果 | 证据边界 |
| --- | --- | --- |
| 来源 | PASS | 原创第一方设计；无复制的第三方代码、脚本或资源。 |
| 结构 | PASS | 33 条契约断言；七个包合计 931 条 collection-discovery 断言；frontmatter 有效、链接可解析。 |
| 调用 | PASS | Claude `disable-model-invocation: true` 与 Codex `allow_implicit_invocation: false`；仅 user-invoked；非触发场景返回 `NOT_INVOKED`。 |
| Fresh-copy 安装 | PASS | 隔离副本只含 `language-learning`、无 source checkout、文件集一致、零 SHA-256 差异、安装副本契约测试 33 断言 PASS；host 安装逐字节一致并在 host skills root 被发现。 |
| 行为 | PASS | Fresh Agent 产出路由后的卡片组与默认 beginner 的每日课程，且不重问语言/水平/模式。 |
| 文档同步 | PASS | collection discovery、目录、双语指南、维护基线、changelog 一致：`main` 七个包，稳定 v0.1.1 五个包。 |
| 独立评审 | PASS | Fresh 最终快速通道 Evaluator 确认资格、复现证据、逐条验证全部九项验收标准并返回 `PASS`。Evaluator 提出一条 Low 级证据准确性观察，已在 Producer 记录中解决。 |

完整记录见 [review-loop/](review-loop/)。

本地源与 host 安装证据是准入证据，不是已发布安装命令的证明。pinned `language-learning` 安装命令必须等下一个已发布 tag 与 fresh released-repository 验证。

## 行为来源

原创第一方设计。本包未复制任何上游 Skill 代码或 prompt 文本。
