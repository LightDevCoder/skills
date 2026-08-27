# Reviewer Contract（审查者契约）— 人类阅读摘要

运行时审查者契约归 `review-loop` 所有，权威位置在
[skills/review-loop/references/reviewer-contract.md](../skills/review-loop/references/reviewer-contract.md)。

本页仅供人类阅读并作为指针，**不是**第二份独立维护的运行时契约。

## 契约涵盖内容

reviewer 是只读能力：接收有界输入包，返回规范化 finding 报告。

- **输入包：** Target、Requirements、Relevant context、Previous findings。
- **规范化结果：** findings 包含 `id`、`state`、`severity`、`location`、
  `problem`、`reason`，以及可选 `suggestion`；干净报告为 `Findings: []`。
- **边界：** reviewer 只检查，不写 target、evidence 或 review state；也从不签发
  最终 `PASS`、`FAIL` 或 `BLOCKED`。

包括身份/跨轮状态与 severity 指引在内的完整运行时细节，统一维护在上方
`review-loop` 包引用中。任何 review 行为变更都应改那里，而不是改这份摘要。