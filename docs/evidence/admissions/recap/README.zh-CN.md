# `recap` 准入证据

[English record](README.md)

## 范围与状态

- Package：`skills/recap/`
- 调用类型：仅 user-invoked
- Profile：`review-loop` `agent-skill`
- 稳定版本边界：v0.1.1 包含五个包，不包含 `recap`
- 准入状态：低风险纯提示型快速通道 `PASS`；旧完整路径历史保留在 [review-loop/](review-loop/)

## 证据摘要

| 领域 | 结果 | 证据边界 |
| --- | --- | --- |
| Source | PASS | Anthropic 官方 commands、interactive-mode、prompt-caching 文档定义可观察的按需一行/不压缩边界；实现为独立编写。 |
| Structure | PASS | 12 条 contract 断言；Claude 与 Codex metadata 均为 explicit-only；无 runtime dependency。 |
| Output contract | PASS | 8 条准确标注的 deterministic assertions 覆盖正向、多行、通用 leading-label 与零断言边界。 |
| Fresh-copy install | PASS | 最终隔离的本地 source 单包复制只发现 `recap`，destination 无 source checkout，完整 file set 一致且 SHA-256 mismatch 为 0，安装后的 12 + 8 条断言通过。 |
| Behavior | PASS | Fresh agents 分别给出有效的成功与空 session 一行输出。 |
| Invocation | PASS | 另一个 fresh agent 在没有 `$recap` 时返回 `NOT_INVOKED`。 |
| Collection quality | PASS | 最终 closeout：Header 11、Quick Start 8、collection discovery 853、ask-light behavior 54、recap 20、全部 review-loop Profile suites、Python collection 74、hooks 7 和 4 个 Python tests 均在本地通过。 |
| Independent review | PASS | 全新的最终快速通道 Evaluator 确认 eligibility、完整 evidence、exact-copy installation、准确 output-contract label，且没有问题需要升级完整路径；较早的完整路径 `BLOCKED` 仅作为历史保留。 |

本地 source fresh-copy 只是准入证据，不是已发布安装命令的证明。Pinned `recap` 命令必须等待下一 tag 发布并针对 released repository 完成 fresh 验证。

## 行为来源

- [Claude Code commands](https://code.claude.com/docs/en/commands)
- [Claude Code interactive mode](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code prompt caching](https://code.claude.com/docs/en/prompt-caching)

未复制 Anthropic 源码或 proprietary prompt 文本。
