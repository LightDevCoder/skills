# LightDevCoder/skills v0.2.6 发布收据

[English receipt](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 已公开发布；对应提交的 CI、注释标签、两种全量全新安装和 GitHub Release 均已核验。

## 发布身份

| 字段 | 值 |
| --- | --- |
| **代码仓库** | `LightDevCoder/skills`（公开仓库） |
| **发布版本** | `v0.2.6` |
| **发布 Tag** | `v0.2.6` |
| **Annotated Tag 对象** | `33dfd1acbce07f2908c1662c5c527fcc6fc6f0d1` |
| **Tag 目标 Commit** | `38015048f69f988eb2fc57dca66e65c252c2b4e4` |
| **发布 URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.6 |
| **公开发布时间戳** | `2026-10-05T11:01:46Z` |
| **发布范围** | 旅行手册 UI、可见每日路线与整组地点选择、空日期初始化、登录及次级界面统一、可选服务端 AI、鼠标日期条拖动，以及凭据、草稿和重试保护。 |
| **集合包总数** | 36 admitted packages（36 个已准入包） |
| **政策状态** | `PROVISIONAL` |
| **Tag 不可变性** | 受保护的注释标签；更新和删除均无绕过权限 |

## 验证核对清单

| 检查门禁 | 状态 | 验证证据 |
| --- | --- | --- |
| **独立源码验收** | `PASS` | 独立 Standards/Spec 与另一全新全包 Evaluator；Core 在 `d0a4b0700cc645aa9ca45bff0106a2c7badb52de` 记录 PASS，Profile 为 `agent-skill`，用户授权第 4/4 轮，独立性 `FULL`，无例外或未关闭阻断项。候选后续只改文档，冻结实现逐字节一致。 |
| **本地测试集** | `PASS` | 528 项 pytest、156 项 unittest、80 项模板、4 项生成器测试，AI 关闭/开启/空日期构建、编译和文档检查 |
| **GitHub Actions CI (`collection-quality`)** | `PASS` | [Run 37299427425](https://github.com/LightDevCoder/skills/actions/runs/37299427425) 在候选提交 `38015048f69f988eb2fc57dca66e65c252c2b4e4` 上成功 |
| **Tag 对象与解析** | `PASS` | 远端注释标签对象 `33dfd1acbce07f2908c1662c5c527fcc6fc6f0d1` 准确指向候选提交 |
| **锁定版本全量全新安装** | `PASS` | 隔离目录执行 `npx --yes skills add LightDevCoder/skills#v0.2.6 --yes --copy --agent '*'`：36/36 个包、385/385 个包内文件与标签逐字节一致 |
| **最新主干全量全新安装** | `PASS` | 独立隔离目录执行 `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'`：36/36 个包、385/385 个包内文件与候选提交逐字节一致 |
| **单技能安装** | `PASS` | 在另两个全新项目目录从 `#v0.2.6` 分别选择 `--skill light-travelpage` 和 `--skill project-retro`，各自 75/75 和 8/8 文件与标签逐字节一致；使用 `--yes --copy --agent '*'` 执行。 |
| **集合发现验证** | `PASS` | Skills CLI 1.7.0 的 `npx --yes skills list --agent codex` 发现 36 个 Skill；安装命令面向 CLI 支持的全部 79 个 Agent |
| **GitHub Release 发布** | `PASS` | [v0.2.6 GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.6) 已公开，非草稿、非预发布 |

逐字节比较覆盖 36 个包内全部受 Git 跟踪的文件。包外仓库资源不由 Skills CLI 安装。通用命令跟随默认分支，只有 `main` 仍指向该候选时才具有相同内容；需要固定快照请使用标签命令。同级 `../agent-config` MCP 仅用于契约验证，不属于本次发布。

英文 GitHub Release 链接到不可变标签中的独立中文说明，中文页可返回英文 Release 和说明。浏览器证据属于桌面及 390px 模拟宽度，AI 使用本地合成服务；不代表已验证远端模型、实体手机、原生地图应用或宿主热加载。
