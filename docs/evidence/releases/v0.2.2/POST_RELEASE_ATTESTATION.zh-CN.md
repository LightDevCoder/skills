# v0.2.2 发布后事实证明与溯源记录 (Post-Release Attestation)

[English Version](POST_RELEASE_ATTESTATION.md) · [发布收据](RELEASE_RECEIPT.zh-CN.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

本说明记录 `v0.2.2` 发布的公开历史事实、CI 运行结论以及随后的发布后修复事实。

---

## 1. 历史发布事实

| 属性 | 记录值 |
| :--- | :--- |
| **发布 Tag** | `v0.2.2` |
| **Annotated Tag 对象** | `e3a6775838a16f27a7e07abbc5187585ce871151` |
| **Tag 目标 Commit** | `90095743cde38c3513e141838c988adcdaf8a4eb` |
| **GitHub Release 发布时间** | `2026-09-20T09:17:42Z` |
| **GitHub Release URL** | https://github.com/LightDevCoder/skills/releases/tag/v0.2.2 |
| **Tag 不可变性状态** | 永久不可变的历史发布快照 |

---

## 2. Tag 关联 CI 状态及失败根因

| 流水线 | Run ID | 结论 | 备注 |
| :--- | :--- | :--- | :--- |
| GitHub Actions `collection-quality` | `35501872550` | `FAILURE` | 运行于目标 commit `90095743...` |

### 失败根因分析
在目标 commit `90095743cde38c3513e141838c988adcdaf8a4eb` 触发的 CI 执行中，由于 GitHub Actions 的 `actions/checkout` 默认配置为浅拉取（`fetch-depth: 1`，`fetch-tags: false`），而当时的发布完整性单元测试直接依赖真实仓库的 Git 历史与 Tag，导致测试在浅检出工作区中因找不到完整历史而失败。

---

## 3. 发布后修复与验证状态

v0.2.2 公开发布后，立即在 `main` 分支进行了纠正性修复：

| 属性 | 记录值 |
| :--- | :--- |
| **纠正 Commit** | `0862a19617aa9f9161575fe9c8b882fd1c3eb134` |
| **纠正措施 1** | 配置 CI actions/checkout 完整拉取历史（`fetch-depth: 0`）。 |
| **纠正措施 2** | 将 `tests/test_release_integrity.py` 重构为使用密封的临时 Git 仓库进行单元测试，完全移除对外部 Tag 的运行时依赖。 |
| **纠正 CI Run ID** | `35502071190` |
| **纠正 CI 结论** | `SUCCESS`（运行 29s，全部测试通过） |

---

## 4. 固化收据状态说明

在 `v0.2.2` Tag 快照中，内置的 `docs/evidence/releases/v0.2.2/RELEASE_RECEIPT.zh-CN.md` 记录：

```text
Status: CANDIDATE
Human approval: PENDING
CI: PENDING
Fresh install: PENDING
```

这反映了历史上的收据架构问题：候选收据在发布前已被提交入 Tag，而非拆分为发布前不可变清单（Manifest）与发布后验证收据（Receipt）。

---

## 5. 架构边界结论

- **`v0.2.2` Tag 快照 (`90095743...`):** 保持为不可变的已发布历史快照。Tag 绝不重新指向、绝不强制移动、绝不重写代码。
- **发布后开发线 (`0862a196+`):** 承载 CI 修复、本历史事实证明文件，以及在 `v0.2.3` 中正式确立的全新发布生命周期架构。
