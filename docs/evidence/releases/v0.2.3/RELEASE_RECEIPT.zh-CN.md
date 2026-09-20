# LightDevCoder/skills v0.2.3 发布收据 (Release Receipt)

[English Version](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`CANDIDATE` — 已完成发布准备；Tag 创建、CI 远端验证及全新安装验证待第二阶段发布门禁确认。

## 发布身份

| 属性 | 记录值 |
| :--- | :--- |
| **代码仓库** | `LightDevCoder/skills`（公开仓库） |
| **发布版本** | `v0.2.3` |
| **发布 Tag** | `v0.2.3` |
| **发布身份** | 候选 commit（将被 tag 为 `v0.2.3`） |
| **发布 URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.3 |
| **发布范围** | 包含七大分类目录下的 36 个已准入第一方 Skill；发布证据生命周期重构（拆分发布前不可变清单 Manifest 与发布后收据 Receipt）；v0.2.2 历史事实追加证明；`project-retro` 正向指令重构与建议动作状态机（`AWAITING_SELECTION` $\to$ `APPROVED_ACTION`）；自动化清单完整性校验。 |
| **集合包总数** | 36 admitted packages (36 个已准入包) |
| **工作区状态** | `CLEAN` |
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
| **本地测试集** | `PASS` | 413 passed；compileall 通过；git diff --check 通过 |
| **发布清单完整性** | `PASS` | 双语清单均包含 36 个包并符合策略状态 |
| **用户发布确认门禁** | `PENDING` | 仅本地 commit；等待第二阶段显式确认 |
| **GitHub Actions CI (`collection-quality`)** | `PENDING` | 待候选 commit 推送至 main |
| **锁定版本全量全新安装** | `PENDING` | `npx skills add LightDevCoder/skills#v0.2.3 -y` |
| **最新主干全量全新安装** | `PENDING` | `npx skills add LightDevCoder/skills -y` |
| **集合发现验证** | `PASS` | 全量 36 个包 frontmatter 与包契约均被正确发现 |
