# v0.1.1 发布收据

[English receipt](RELEASE_RECEIPT.md)

状态：`RELEASED WITH ACCEPTANCE LIMITATION`；不可变 tag、远程默认分支、GitHub
Actions 和 fresh-install 证据已核验；独立 `review-loop agent-skill` acceptance
仍为 `BLOCKED`。

## 身份

| 字段 | 值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills` |
| Release | `v0.1.1` |
| Release commit | `c50f1ef403a5f0bfe02e75d1aeff2c237556db63` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.1 |
| 日期 | `2026-07-26` |
| 范围 | 五个第一方包、双语文档、Quick Start、workflow recipes、头图、CI 和 ask-light workflow mode。 |

## 证据

- 结构与 discovery：[DISCOVERY_VERIFICATION.md](DISCOVERY_VERIFICATION.md)
- 包与集合测试：[TEST_SUMMARY.md](TEST_SUMMARY.md)
- Fresh install 与 host discovery：[INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md)
- 限制和 evidence labels：[LIMITATIONS.md](LIMITATIONS.md)
- [审查策略](../../../REVIEW_POLICY.md)
- [准入契约](../../../SKILL_ADMISSION.md)

| Fresh whole-repository install | `VERIFIED` | 见 [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md)。 |
| Fresh per-Skill install | `VERIFIED` | 见 [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md)。 |
| Independent `review-loop agent-skill` acceptance | `BLOCKED` | 等待 fresh independent evaluator 记录；同一上下文不是独立证据。 |
| GitHub Actions | `VERIFIED` | 合并后的 release commit 上的 workflow 已通过。 |

这是一份 release 记录，不是独立 acceptance 记录；在 independent evaluator 行为
为 `BLOCKED` 期间，不能把结构证据写成模型介导的 runtime proof。
