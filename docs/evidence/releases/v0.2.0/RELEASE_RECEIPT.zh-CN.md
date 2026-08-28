# LightDevCoder/skills v0.2.0 发布收据

[English receipt](RELEASE_RECEIPT.md)

状态：`RELEASED` — tag 已发布（`v0.2.0`），GitHub Release 已创建，CI 在候选提交上通过（`PASS`），且全部 33 个包在全新隔离环境中的安装验证全部通过（`PASS`）。

## 标识信息

| 字段 | 取值 |
| --- | --- |
| 代码仓库 | `LightDevCoder/skills` (public) |
| 发布版本 | `v0.2.0` |
| 发布提交 | `9c2572bc0361e1e2c34cb4b6c02fdaa4ed349d47` |
| 发布 tag | `v0.2.0` |
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

## 发布验证检查清单

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| 本地候选测试套件 | `PASS` | 309 pytest、27 unittest（245 条断言）、compileall 零错误、git diff --check 零错误 |
| Phase 2 人工批准门禁 | `PASS` | 明确人工批准确认 |
| GitHub Actions CI (`collection-quality`) | `PASS` | Run ID `33137041472` (22s) |
| Pinned 全集合全新安装 | `PASS` | 安装 33 个包，与源码逐字节一致 |
| Generic Latest 全集合全新安装 | `PASS` | 安装 33 个包，退出码 0 |
| 33 个单独 Skill 全新安装矩阵 | `PASS` | 66/66 安装（33 latest + 33 pinned）退出码 0，各恰好 1 个包 |
| 发现机制验证 | `PASS` | `npx --yes skills list` 在无源码检出环境下正常发现已安装包 |
| 独立仓库退役 | `RETIRED` | 溯源与退役记录详见 [MIGRATION_RETIREMENT.zh-CN.md](MIGRATION_RETIREMENT.zh-CN.md) |
