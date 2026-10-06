# LightDevCoder/skills v0.2.7 发布清单

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

**准备状态：** 本地候选；必须完成的 Host 观察和独立验收尚待完成，因此生命周期尚未到达 PREPARED。v0.2.6 仍是当前稳定版。本草稿不预填未来验证结果。

本文件将冻结在候选快照。发布后事实只能在 ATTESTED 阶段于 `main` 首次创建收据；候选和标签快照不包含收据。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.7`（用户确认的目标版本，尚未发布） |
| **预期标签** | `refs/tags/v0.2.7` |
| **发布身份** | `refs/tags/v0.2.7^{commit}` |
| **发布范围** | 12 个 Light Skill 名称；包身份与界面标签；内部引用、ask-light 路由、状态和发现；迁移、归属记录、当前与发布双语文档及针对性验证。 |
| **集合包数** | 36 个已准入包；12 个改名，其他 24 个名称保留 |
| **Policy Status** | `PROVISIONAL`（Jev 策略不变） |
| **标签不可变性** | annotated tag 发布后永久不可改写 |
| **实施输入** | 名称迁移 SPEC Revision 3，本地 `.scratch/light-skill-namespace/spec-revision-3.md`；SHA-256 `f64a5f266015961b362812b24148557aca57371ba6a6dc4b8bacb680e51b2ed4` |
| **当前基线** | `origin/main`，`97adf5f319b8800b6635057434dcb4aeda2ddecd` |
| **上一稳定快照** | `v0.2.6`，`38015048f69f988eb2fc57dca66e65c252c2b4e4` |
| **兼容基线** | 职责、调用权限、分类、已发布旅行手册及 AI 行为、历史证据保留；不提供旧名可安装 alias，不自动迁移真实全局安装。 |

## 候选证据

合并后通过 534 项 pytest、158 项 unittest、编译和公开文档检查。224 个旅行及历史基线文件保持原字节。[Producer 证据](../../namespace-v0.2.7/producer-evidence.md)记录这些有界观察。A1–A10 验证、R1–R5 诊断覆盖、独立 review-loop 收敛和 project-review 最终验收仍须绑定新的冻结候选。候选 CI、A2/A9 真实 Host 选择器和实际调用、实际发布源新鲜安装尚待完成。静态发现和 Producer 自检不能代表 Host 运行时或独立验收。

## 后续发布门禁

准确候选 CI、有效标签保护与 preflight、annotated tag 身份、固定标签与默认分支新鲜安装、完整包及来源与内容核对、GitHub Release 发布和发布后证明尚待完成。先前 v0.2.6 名称迁移尝试保留为历史；用户已确认 v0.2.7 及新基线。真实用户全局迁移属于另行授权的操作。
