# LightDevCoder/skills v0.2.5 发布收据

[English receipt](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 已公开发布；对应提交的 CI、注释标签、两种全量全新安装和 GitHub Release 均已核验。

## 发布身份

| 字段 | 值 |
| --- | --- |
| **代码仓库** | `LightDevCoder/skills`（公开仓库） |
| **发布版本** | `v0.2.5` |
| **发布 Tag** | `v0.2.5` |
| **Annotated Tag 对象** | `576e3bbdf2002b10390f48646184305050ed951e` |
| **Tag 目标 Commit** | `ecafc2f3da3ab25a62e7a31285658fac5a50b47f` |
| **发布 URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.5 |
| **公开发布时间戳** | `2026-09-23T17:51:28Z` |
| **发布范围** | Host/Profile 与工作流路由、共用工单编号、手稿初始化及依赖契约、审阅 Findings、旅行待办校验、完整 CI 与远端发布门禁。 |
| **集合包总数** | 36 admitted packages（36 个已准入包） |
| **政策状态** | `PROVISIONAL` |
| **Tag 不可变性** | 受保护的注释标签；更新和删除均无绕过权限 |

## 验证核对清单

| 检查门禁 | 状态 | 验证证据 |
| --- | --- | --- |
| **本地测试集** | `PASS` | 515 项 pytest、156 项 unittest、35 项 Node 测试、生成旅程校验与构建、同级 MCP 契约集成、文档检查 |
| **GitHub Actions CI (`collection-quality`)** | `PASS` | [Run 35858468222](https://github.com/LightDevCoder/skills/actions/runs/35858468222) 在候选提交 `ecafc2f3da3ab25a62e7a31285658fac5a50b47f` 上成功 |
| **Tag 对象与解析** | `PASS` | 远端注释标签对象 `576e3bbdf2002b10390f48646184305050ed951e` 准确指向候选提交 |
| **锁定版本全量全新安装** | `PASS` | 隔离目录执行 `npx --yes skills add LightDevCoder/skills#v0.2.5 --yes --copy --agent '*'`：36/36 个包、367/367 个包内文件与标签逐字节一致 |
| **最新主干全量全新安装** | `PASS` | 独立隔离目录执行 `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'`：36/36 个包、367/367 个包内文件与候选提交逐字节一致 |
| **集合发现验证** | `PASS` | Skills CLI 1.7.0 的 `npx --yes skills list --agent codex` 发现 36 个 Skill；安装命令面向 CLI 支持的全部 79 个 Agent |
| **GitHub Release 发布** | `PASS` | [v0.2.5 GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.5) 已公开，非草稿、非预发布 |

逐字节比较覆盖 36 个包内全部受 Git 跟踪的文件。包外仓库资源不由 Skills CLI 安装。通用命令跟随默认分支，只有 `main` 仍指向该候选时才具有相同内容；需要固定快照请使用标签命令。同级 `../agent-config` MCP 仅用于契约验证，不属于本次发布。
