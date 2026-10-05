# LightDevCoder/skills v0.2.6 发布清单

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

**准备状态：BLOCKED 草稿。** 名称迁移候选尚未发布；尚未记录干净候选提交或 PREPARED 完整性检查结果。v0.2.5 是本 checkout 的已验证基线。远端 v0.2.6 已被占用，D7 禁止覆盖或自行改号。见[发布阻断记录](../publication-blocker.md)。

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

本地检查、A1–A10 候选证据、R1–R5 失败诊断、独立 review-loop 收敛与 project-review 最终验收尚待完成。本草稿不会把 Producer 自检当作独立验收，也不会把结构检查当作 Host 运行时证据。候选证据须在冻结候选提交前补充。

## 后续阶段门禁

准确候选远端 CI、标签保护与 preflight、annotated tag 身份、远端固定版本与默认分支新鲜安装、包内容与来源核对、GitHub Release 发布及发布后证明尚待完成。各阶段只记录实际观察的证据和限制。真实用户全局迁移属于另行授权的操作，不在本次仓库实施范围内。
