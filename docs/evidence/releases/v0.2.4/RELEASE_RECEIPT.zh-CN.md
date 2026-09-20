# LightDevCoder/skills v0.2.4 发布收据 (Release Receipt)

[English Version](RELEASE_RECEIPT.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

状态：`VERIFIED` — 已正式公开发布，远端 CI 校验通过，全新安装测试已在全量 36 个已准入包上确认，并在 `main` 完成事实证明。

## 发布身份

| 属性 | 记录值 |
| :--- | :--- |
| **代码仓库** | `LightDevCoder/skills`（公开仓库） |
| **发布版本** | `v0.2.4` |
| **发布 Tag** | `v0.2.4` |
| **Annotated Tag 对象** | `7dbfa42244975064ffa1084c59495da9203f7049` |
| **Tag 目标 Commit** | `230b67e4694703df30880b4bfa09e933932eaf83` |
| **发布 URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.4 |
| **公开发布时间戳** | `2026-09-20T18:24:01Z` |
| **发布范围** | 涵盖 7 大分类共 36 个已准入的第一方 Skill；发布完整性校验机制加固（清单、说明与收据的 Git 对象严格绑定）；发布后收据快照严格隔离与防漂移；Fail-Closed 单向 Tag Preflight；Annotated Tag 强制校验；公开文档质量门禁与双语一致性保障。 |
| **集合包总数** | 36 admitted packages (36 个已准入包) |
| **政策状态** | `PROVISIONAL` |
| **Tag 不可变性** | 发布后永久不可变 |

## 更新概要

- **Git 对象发布证据绑定：** 将发布清单与发布说明的校验直接绑定至不可变的 Git tree 对象快照（`candidate_commit` 与 `refs/tags/v0.2.4^{commit}`），彻底防止工作区未提交或未跟踪文件穿透门禁。
- **发布后收据快照严格隔离：** 发布收据中的准入包总数校验强制绑定至发布时不可变候选快照（`release_revision`），防止后续 `main` 分支包增减漂移污染已发布版本的事实证明。
- **Fail-Closed 单向 Tag Preflight 门禁：** Tag 预检默认校验 `origin` 远端状态，网络或鉴权失败时严格阻塞（`BLOCKED`）；本地或远端已存在 Tag 时严格阻断，确保单向、安全发布。
- **严格 Annotated Tag 校验：** 强制要求发布 Tag 必须为 Annotated Tag 对象（`git cat-file -t` 返回 `tag`），全生命周期拒绝 lightweight tag。
- **独立 TAGGED 阶段复审支持：** 明确 `check_receipt_absence_in_candidate` 在传入 `revision` 时仅检查 Git 快照，允许在完成 post-publication attestation 后重新执行 `stage=tagged` 复核通过，杜绝工作区收据干扰。
- **零 Traceback 结构化失败机制：** 审计校验分支与规范显示路径，确保所有异常或错误均以标准 `VerificationResult` 结构化返回，杜绝 Python 未定义变量 traceback。
- **公开文档质量门禁：** 全面统一 `README.md`、`CATALOG.md`、`INSTALLATION.md` 中英文术语及调用/状态对称性，去除 AI 写作痕迹。

## 验证核对清单

| 检查门禁 | 状态 | 验证证据 |
| :--- | :--- | :--- |
| **本地测试集** | `PASS` | 509 passed；compileall 通过；git diff --check 通过 |
| **发布清单完整性** | `PASS` | 双语清单均包含 36 个包并符合策略状态 |
| **GitHub Actions CI (`collection-quality`)** | `PASS` | Run ID `35528714674` 运行于目标 commit `230b67e4694703df30880b4bfa09e933932eaf83`（耗时 30s，全绿通过） |
| **Tag 对象与解析** | `PASS` | Annotated tag `7dbfa422...` 准确 peel 至已验证 commit `230b67e...` |
| **锁定版本全量全新安装** | `PASS` | `npx --yes skills add LightDevCoder/skills#v0.2.4 --yes --copy --agent '*'` — 36/36 全部成功安装 |
| **最新主干全量全新安装** | `PASS` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` — 36/36 全部成功安装 |
| **集合发现验证** | `PASS` | 全量 36 个包 frontmatter 与包契约通过 `npx skills list` 发现 |
| **GitHub Release 发布** | `PASS` | 已发布至 https://github.com/LightDevCoder/skills/releases/tag/v0.2.4 |
