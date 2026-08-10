# v0.1.2 发布收据

[English receipt](RELEASE_RECEIPT.md)

状态：`VERIFIED` — 七包集合、`v0.1.2` tag、GitHub release、fresh-install 验证
与 publish 提交均已完成。

## 身份

| 字段 | 值 |
| --- | --- |
| Repository | `LightDevCoder/skills` |
| Release | `v0.1.2` |
| Release commit | `8de5ec1a453b0e93f71dcda160e17ea7b42c3997` |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.2 |
| 日期 | `2026-08-10` |
| 范围 | 七个第一方包（v0.1.1 的五个加上 `recap` 与 `language-learning`）、双语文档、Quick Start、workflow recipes、header、CI 与通用 `latest` 安装命令。 |

## 验收证据

- 结构与 discovery：[DISCOVERY_VERIFICATION.zh-CN.md](DISCOVERY_VERIFICATION.zh-CN.md)
- 包与集合测试：[TEST_SUMMARY.zh-CN.md](TEST_SUMMARY.zh-CN.md)
- Fresh install 与 host discovery：[INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)
- 限制与 evidence 标签：[LIMITATIONS.zh-CN.md](LIMITATIONS.zh-CN.md)
- 审查策略：[../../../REVIEW_POLICY.zh-CN.md](../../../REVIEW_POLICY.zh-CN.md)
- 准入契约：[../../../SKILL_ADMISSION.zh-CN.md](../../../SKILL_ADMISSION.zh-CN.md)

## Release gate

| Gate | 状态 | 证据 |
| --- | --- | --- |
| 所有权与范围 | `VERIFIED` | 七个第一方包列表与公开所有权边界。 |
| Metadata/invocation 一致性 | `VERIFIED` | 集合测试 + 包 frontmatter 与 `agents/openai.yaml`。 |
| 包行为 | 所列本地 contract/behavior 检查为 `VERIFIED` | 见 [TEST_SUMMARY.zh-CN.md](TEST_SUMMARY.zh-CN.md)；fresh installation 与独立验收是单独的 gate。 |
| Fresh 整仓安装 | `VERIFIED` | CLI `1.5.22`；`latest` 与 `#v0.1.2` 两种形式均 `PASS`。见 [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)。 |
| Fresh 单包安装 | `VERIFIED` | CLI `1.5.22`；`latest` 与 `#v0.1.2` 两种形式均 `PASS`。见 [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)。 |
| 独立 `review-loop agent-skill` 验收 | 两个新准入包 `VERIFIED`；原有五个 `BLOCKED` | `recap` 与 `language-learning` 各自带有 fresh independent fast-track Evaluator `PASS`；原有五个仍缺 fresh independent evaluator record。 |
| GitHub Actions | release commit 上 `PASS` | Run `31362999381`（`collection-quality`）。见 `.github/workflows/quality.yml`。 |

对原有五个包，在它们的独立 evaluator 行为 `BLOCKED` 解除前，不要把本收据
当作独立验收记录。不要把结构证据当作 runtime proof。
