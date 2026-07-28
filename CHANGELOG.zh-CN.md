# 变更记录

[English changelog](CHANGELOG.md)

所有变更都必须记录在实际版本/tag 对应的条目中，不能因为文档已起草就提前宣称 release。

## 0.1.1 — 2026-07-26

### 新增

- 五个第一方 Skill 的双语用户指南、已验证的 workflow recipes 和可运行大小的 Quick Start 示例。
- `docs/evidence/releases/v0.1.1/` release 证据目录，以及覆盖结构、metadata、链接、双语配对、包测试、退休引用和头图的 CI 检查。
- 显式 `$ask-light next` 与 `$ask-light workflow` 模式，包含 bounded recipe、availability gap、handoff 字段和不执行测试。
- 可编辑 SVG 与 1600 × 480 PNG 头图：平面叠层的 `LightDevCoder` / `/skills` wordmark 和 serif slogan。

### 修复

- 为 user-invoked 的 `learn-anything`、`ask-light`、`project-init` 补齐 `policy.allow_implicit_invocation: false` 及对应 frontmatter。
- 修正安装语义：无 fragment 的仓库来源遵循 CLI 默认 revision，发布后 `#v0.1.1` 才是固定 target tag。

### Release 证据

- Release tag：`v0.1.1`，commit `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.20`，均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.1
- 整仓与单 Skill fresh-install 目标记录：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.1/TEST_SUMMARY.zh-CN.md)。
- 五个包组成的集合仍可安装，`collection-quality` 检查已通过。`review-loop
  agent-skill` acceptance gate 的独立 evaluator 证据仍为 `BLOCKED`；这不影响
  一般安装或使用。准确证据边界见[发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.0 — 2026-07-23

- 建立第一方治理基础并准入五个第一方 Skill。
- 已发布于 https://github.com/LightDevCoder/skills。
- 稳定 tag：v0.1.0。
- v0.1.0 的整集合与单 Skill 安装命令曾针对 fresh destination 和已发布包内容完成验证；这份历史证据与 v0.1.1 release 证据一并保留。
- 历史命令：`npx skills add LightDevCoder/skills` 和
  `npx skills add LightDevCoder/skills --skill review-loop`。
- 历史安装明细：[v0.1.0 摘要](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v0.1.0-摘要)。
