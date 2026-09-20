# LightDevCoder/skills v0.2.3 发布收据 (Release Receipt)

[English Version](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 已正式公开发布，远端 CI 校验通过，全新安装测试已在全量 36 个已准入包上确认，并在 `main` 完成事实证明。

## 发布身份

| 属性 | 记录值 |
| :--- | :--- |
| **代码仓库** | `LightDevCoder/skills`（公开仓库） |
| **发布版本** | `v0.2.3` |
| **发布 Tag** | `v0.2.3` |
| **Annotated Tag 对象** | `547fa4bd6c38f45fe3f8028e7c0741c48f41ad31` |
| **Tag 目标 Commit** | `398e30627c18d9bffe877bb69695d38dcd5e7633` |
| **发布 URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.3 |
| **公开发布时间戳** | `2026-09-20T12:10:10Z` |
| **发布范围** | 包含七大分类目录下的 36 个已准入第一方 Skill；发布证据生命周期重构（拆分发布前不可变清单 Manifest 与发布后收据 Receipt）；v0.2.2 历史事实追加证明；`project-retro` 正向指令重构与建议动作状态机（`AWAITING_SELECTION` $\to$ `APPROVED_ACTION`）；自动化清单完整性校验。 |
| **集合包总数** | 36 admitted packages (36 个已准入包) |
| **政策状态** | `PROVISIONAL` |
| **Tag 不可变性** | 发布后永久不可变 |

## 更新概要

- **发布证据生命周期解耦：** 拆分发布前不可变清单（`RELEASE_MANIFEST.md`，固化于 Tag 内）与发布后验证事实收据（`RELEASE_RECEIPT.md`，存于 main 分支）。
- **v0.2.2 历史事实追加证明：** 详细记录 v0.2.2 发布事实、初始 CI 浅拉取失败根因以及后续纠正提交。
- **`project-retro` 正向指令重构：** 围绕目标、职责、状态转换（`AWAITING_SELECTION` $\to$ `APPROVED_ACTION`）与工程审计沟通进行指令重构。
- **自动化发布完整性校验：** 增加清单一致性与目标 commit 关联校验，并由密封单元测试覆盖。

## 验证核对清单

| 检查门禁 | 状态 | 验证证据 |
| :--- | :--- | :--- |
| **本地测试集** | `PASS` | 418 passed；compileall 通过；git diff --check 通过 |
| **发布清单完整性** | `PASS` | 双语清单均包含 36 个包并符合策略状态 |
| **GitHub Actions CI (`collection-quality`)** | `PASS` | Run ID `35509619162` 运行于目标 commit `398e30627c18d9bffe877bb69695d38dcd5e7633`（耗时 28s，全绿通过） |
| **Tag 对象与解析** | `PASS` | Annotated tag `547fa4bd...` 准确 peel 至已验证 commit `398e306...` |
| **锁定版本全量全新安装** | `PASS` | `npx --yes skills add LightDevCoder/skills#v0.2.3 --yes --copy --agent '*'` — 36/36 全部成功安装 |
| **最新主干全量全新安装** | `PASS` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` — 36/36 全部成功安装 |
| **集合发现验证** | `PASS` | 全量 36 个包 frontmatter 与包契约通过 `npx skills list` 发现 |
| **GitHub Release 发布** | `PASS` | 已发布至 https://github.com/LightDevCoder/skills/releases/tag/v0.2.3 |
