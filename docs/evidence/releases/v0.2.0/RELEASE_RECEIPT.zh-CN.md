# LightDevCoder/skills v0.2.0 发布收据

[English receipt](RELEASE_RECEIPT.md)

状态：`CANDIDATE` — 发布候选已就绪；tag 创建、公开发布与全新安装验证等待 Phase 2 人工批准门禁与 Phase 3 验证。

## 标识信息

| 字段 | 取值 |
| --- | --- |
| 代码仓库 | `LightDevCoder/skills` (public) |
| 发布版本 | `v0.2.0` |
| 发布提交 | `NOT TESTED`（待生成候选提交 SHA） |
| 发布 tag | `v0.2.0`（待创建） |
| 发布 URL | https://github.com/LightDevCoder/skills/releases/tag/v0.2.0 |
| 范围 | 发布完整 33 个第一方 Skill 架构（在 v0.1.6 的 9 个包基础上新增 24 个新建/重构/适配/Port 包），包含 project workflow、clarification/Socratic 引擎、review/project-review 架构、ask-light 顾问，以及 ELI5 和 release-workflow 的迁移出处与退役。 |

## 变更概述

- 将集合由 9 个包（v0.1.6）扩展为 `skills/` 下完整的 33 个第一方包。
- 引入统一项目工作流架构（`project-init`、`project-clarify`、`project-spec`、`project-tickets`、`implement`、`project-review`、`release-workflow`）。
- 构建 Socratic 澄清引擎（`socratic`），驱动 `clarify`、`project-clarify` 与 `decision-map`。
- 新增执行与审查子系统（`agent-config`、`generic-review`、`code-review`、`project-review`、`review-loop`）。
- 集成 `ask-light` 作为贯穿 33 个 Skill 的 Light 工作流顾问。
- 建立包含完整归属（`ATTRIBUTION.md`）且零上游运行时依赖的自包含批准 Port。
- 将独立仓库 `LightDevCoder/release-workflow` 与 `LightDevCoder/ELI5` 迁移入集合，记录完整溯源并规划退役。

## 候选验证检查清单

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| 本地候选测试套件 | `PASS` (Candidate baseline) | [TEST_SUMMARY.zh-CN.md](TEST_SUMMARY.zh-CN.md) |
| Phase 2 人工批准门禁 | `PENDING` | tag 创建与推送前需明确 YES |
| GitHub Actions CI (`collection-quality`) | `NOT TESTED` | 待推送 main |
| Pinned 全集合全新安装 | `NOT TESTED` | [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
| Generic Latest 全集合全新安装 | `NOT TESTED` | [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
| 33 个单个 Skill 全新安装矩阵 | `NOT TESTED` | [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md) |
| 独立仓库退役 | `NOT TESTED` | [MIGRATION_RETIREMENT.zh-CN.md](MIGRATION_RETIREMENT.zh-CN.md) |
| 发现机制验证 | `NOT TESTED` | [DISCOVERY_VERIFICATION.zh-CN.md](DISCOVERY_VERIFICATION.zh-CN.md) |
