# LightDevCoder/skills v0.1.6 发布收据

[English receipt](RELEASE_RECEIPT.md)

状态：`RELEASED` — tag 已发布，post-release verification 记录在 main。

## Identity

| 字段 | 值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills`（公开） |
| 发布 | `v0.1.6` |
| 发布 commit | `e8c3589031bbc1cb76d7f928761ce3f60ebea3e1` |
| 发布 tag | `v0.1.6` |
| 发布 URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.6 |
| 范围 | 新增 `kb-init` 作为第九个已准入第一方 Skill，并把 `light-kanban-worker` 改名为 `kanban-worker`；文档/测试/证据同步到九包集合 |

## 变更

- `kb-init`（正式版知识库初始化包）替换之前未发布的草稿：扩展核心原则、决策 provenance、开放决策 surfacing、depth-before-settlement、readiness 检查、人类导航、research contract、connection setup/validation 与 backup/recovery 语义。
- `kb-init` 保持仅 user-invoked：`disable-model-invocation: true`、`allow_implicit_invocation: false`。
- `light-kanban-worker` 改名为 `kanban-worker`；包、metadata、测试、指南、目录、README 与安装面统一使用新名。
- README、目录、安装指南、维护基线、changelog 与双语指南同步为 v0.1.6 九包发布。

## Pre-release gate

| 门禁 | 状态 |
| --- | --- |
| `kb-init` contract 测试 | PASS |
| Collection 测试 | PASS |
| 完整 collection discovery/contract 套件 | PASS |
| 独立 `review-loop agent-skill` 验收 | PASS |
| 文档同步 | PASS |
| Changelog 准备 | PASS |

## Post-release verification

| 检查 | 记录 |
| --- | --- |
| 已发布 tag 与 commit | `v0.1.6` → `e8c3589031bbc1cb76d7f928761ce3f60ebea3e1` |
| `LightDevCoder/skills#v0.1.6` fresh install | PASS — [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
| Host discovery | PASS — [DISCOVERY_VERIFICATION.zh-CN.md](DISCOVERY_VERIFICATION.zh-CN.md) |
| Release CI（`collection-quality`） | PASS — run `32232850422`，commit `e8c3589` |
| GitHub Release | https://github.com/LightDevCoder/skills/releases/tag/v0.1.6 |
