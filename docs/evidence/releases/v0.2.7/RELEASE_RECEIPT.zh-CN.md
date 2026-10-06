# LightDevCoder/skills v0.2.7 发布收据

[English receipt](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 准确候选 CI、受保护 annotated tag、真实发布源新鲜安装和正式 GitHub Release 均已验证。本收据在公开发布后首次于 main 创建，标签中没有收据。

| 字段 | 值 |
| --- | --- |
| **仓库** | `LightDevCoder/skills` |
| **发布版本** | `v0.2.7` |
| **发布 Tag** | `v0.2.7` |
| **Annotated Tag 对象** | `faf5e6c93e13a9e1e805e4d46d72b3a63e2f3817` |
| **Tag 目标 Commit** | `ef2d840b102df881bc8d6ae251af7db1ad3a21a7` |
| **发布 URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.7 |
| **公开发布时间戳** | `2026-10-06T16:09:01Z` |
| **集合包数量** | 36 个已准入包，386 个包内文件 |
| **策略状态** | `PROVISIONAL` |
| **范围** | 12 项名称迁移及内部引用、路由、界面来源、双语迁移/归属/文档和检查；没有新增旅行功能 |
| **验证器提交 / 默认分支安装来源** | `a7fd7d69bd9073db46c19bae9f388f9b3ec43352` |

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| **独立源码验收** | `PASS` | [恢复后验收](../../namespace-v0.2.7/acceptance-resumed.md)，A1-A10，完整独立性；真实原生CLI选择器、来源调用和依赖读取 |
| **本地测试** | `PASS` | 候选543pytest/167unittest；修正验证器544pytest/168unittest、10项focused；编译/文档，保留80项旅行模板与4项生成器测试 |
| **GitHub Actions CI** | `PASS` | [37491785260](https://github.com/LightDevCoder/skills/actions/runs/37491785260) 绑定准确候选；修正后的main验证器 [37492572835](https://github.com/LightDevCoder/skills/actions/runs/37492572835) 成功 |
| **标签对象及解析** | `PASS` | 远端对象及peel匹配准确候选，规则23728847禁止修改/删除且无绕过 |
| **锁定版本全量全新安装** | `PASS` | [37492680408](https://github.com/LightDevCoder/skills/actions/runs/37492680408)：Codex、Claude Code项目目标各36包/386文件匹配准确标签 |
| **最新主干全量全新安装** | `PASS` | 同一新鲜OS用户内的另一项目，Codex、Claude Code各36/386匹配准确main `a7fd7d69bd9073db46c19bae9f388f9b3ec43352`；安装期间main稳定 |
| **原生Codex全局安装** | `PASS` | 真实 `--global --agent codex` 写入 `/home/runner/.agents/skills`，36/386匹配标签；未重设HOME/CODEX_HOME |
| **新名称单包安装** | `PASS` | 分别在新鲜Codex项目安装light-implement7文件、light-tdd5文件、light-research3文件，全部匹配标签 |
| **GitHub Release 发布** | `PASS` | [v0.2.7](https://github.com/LightDevCoder/skills/releases/tag/v0.2.7) 已公开，非draft/prerelease，实际时间戳如上 |

[完整安装清单与命令](installation/result.json)、[主Agent独立内容核对](installation/parent-check.json)绑定6个场景、8个目标和12条成功命令。CLI1.7.0实际文件SHA256为`fde68534019765fb69510a0038ca7df2810a6ffed4c26fef9beabdcf6cc6701c`，Light完整来源清单digest为`5a682a3356a501a1285735560ef2261d7bc81cf6c18c31292c54e44ef167926b`。[独立发布证据复核](release-evidence-evaluation.md)从Git重建清单并逐项匹配全部目标。

首次安装运行 [37492137382](https://github.com/LightDevCoder/skills/actions/runs/37492137382) 在安装成功后，因标签内验证器检查 ~/.codex/skills 而失败。main的单路径修复改用实际 ~/.agents/skills，另经CI与测试，实际新鲜重跑通过。[原始失败日志](installation/command-logs.zip)保留。不可变标签继续保留原验证器、Notes和Manifest；标签与包内容未移动或修改。main的发布说明同步实际发布结果。收据及真实安装产物均在发布后添加。

安装范围限已声明的Codex/Claude Code目标，不代表所有Agent逐字节一致或Claude运行时。Codex运行证据来自CLI0.160.1及已披露的临时公共传输适配器，不声称desktopGUI验证。未迁移真实用户全局Skills/config/auth、其他项目或自动化。默认命令跟随其观察到的main；固定标签保留不可变快照。
