# LightDevCoder/skills v0.2.6 发布清单

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

**准备状态：BLOCKED 草稿。** 名称迁移候选尚未发布；本地实现已提交，但没有可发布候选或 PREPARED 完整性检查结果。v0.2.5 是本 checkout 的已验证基线。远端 v0.2.6 已被占用，D7 禁止覆盖或自行改号。见[发布阻断记录](../publication-blocker.md)。

本文件为不可变候选快照准备。发布后事实只能在 ATTESTED 阶段于 `main` 首次创建收据；候选和标签快照不包含收据。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.6` |
| **请求标签（已占用）** | `refs/tags/v0.2.6` |
| **请求身份（非本候选）** | `refs/tags/v0.2.6^{commit}` |
| **发布范围** | 12 个 Light Skill 名称及现行引用、路由、界面、发现、归属记录；双语迁移与发布文档；已有旅行 PDF 预览和可读地图导航修复；稳定版检查的目标读取与 v0.2.5 标签之后的文档和发布证明后续。 |
| **集合包数** | 36 个已准入包；12 个改名，其他 24 个名称保留 |
| **Policy Status** | `PROVISIONAL`（Jev 策略不变） |
| **标签不可变性** | annotated tag 发布后永久不可改写 |
| **实施输入** | 本地名称迁移 SPEC Revision 2；基线 `7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6` |
| **本地已验证发布基线** | `v0.2.5`，`ecafc2f3da3ab25a62e7a31285658fac5a50b47f` |

## 本地候选证据

已审阅的本地实现为 `79d15fd410f1295f84d9761d66c601895ff9ee31`，通过 521 项 pytest、158 项 unittest、编译与公开文档检查。两个独立审阅方向已收敛。四种本地安装组合保留包身份、完整内容和正确链接；Light 清单 digest 为 `fe58ea6e7af0e7ffa4b52fc484c9b78cdbffc6e8c22cf1a28b0596779c191041`。

[Producer 证据](../producer-evidence.md)、[安装与实际 Host 尝试](../installation-host.md)和[独立审阅收敛](../review-summary.md)分别保留边界。A2 Host 选择器、A9 实际发现与调用未观察，[最终候选验收](../acceptance.md)经全新独立 Evaluator 检查后为 BLOCKED。R3 被既有发布版本阻断；本候选尚未完成 R4/R5。

## 后续阶段门禁

准确候选远端 CI、标签保护与 preflight、annotated tag 身份、远端固定版本与默认分支新鲜安装、包内容与来源核对、GitHub Release 发布及发布后证明尚待完成。各阶段只记录实际观察的证据和限制。真实用户全局迁移属于另行授权的操作，不在本次仓库实施范围内。
