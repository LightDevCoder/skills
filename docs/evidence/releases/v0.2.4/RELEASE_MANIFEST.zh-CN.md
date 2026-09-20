# LightDevCoder/skills v0.2.4 发布清单

[English Manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

本发布清单代表发布版本 `v0.2.4` 的不可变发布前规格说明。本清单直接提交至候选发布 commit，并永久固化于 Annotated Release Tag 快照内部。发布后事实证明将在公开发布后于 main 分支的 RELEASE_RECEIPT.zh-CN.md 中完成收据记录。

---

## 1. 发布规格

| 属性 | 记录值 |
| :--- | :--- |
| **发布版本** | `v0.2.4` |
| **预期 Tag** | `refs/tags/v0.2.4` |
| **发布身份** | `refs/tags/v0.2.4^{commit}`（创建 Tag 时确定） |
| **发布范围** | 涵盖 7 大分类共 36 个已准入的第一方 Skill；发布完整性校验机制加固（清单、说明与收据的 Git 对象严格绑定）；发布后收据快照严格隔离与防漂移；Fail-Closed 单向 Tag Preflight；Annotated Tag 强制校验；公开文档质量门禁与双语一致性保障。 |
| **集合包总数** | 36 个已准入包 |
| **政策状态** | `PROVISIONAL` |
| **工作区基线** | 干净工作区，受跟踪范围内零未提交修改 |
| **Tag 不可变性** | 发布后永久不可变 |

---

## 2. 发布生命周期模型

本发布强制执行六阶段生命周期架构：

```text
PREPARED
    ↓
CI_VERIFIED
    ↓
TAGGED
    ↓
INSTALL_VERIFIED
    ↓
PUBLISHED
    ↓
ATTESTED
```

- **发布清单职责：** 在发布前固化发布身份与交付范围，封存于 Release Tag 提交中。
- **发布收据职责：** 在公开发布后于 `main` 分支证明远端 CI 结论、全新安装计数与 GitHub Release 正式发布事实。

---

## 3. 打标签前本地验证证据

| 检查门禁 | 状态 | 验证证据 |
| :--- | :--- | :--- |
| **本地测试套件** | `PASS` | 509 passed；全量 unittest 与集成用例绿灯通过 |
| **字节码编译** | `PASS` | `python -m compileall -q skills tests scripts` 无错误 |
| **发布完整性预检** | `PASS` | `scripts/verify_release_integrity.py` 绿灯通过 |
| **Git 格式规范** | `PASS` | `git diff --check` 无空白字符违规 |
| **包契约与发现** | `PASS` | 全量 36 个 Skill 均符合规范契约与发现标准 |

---

## 4. 兼容性基线

- **Python 运行环境：** Python >= 3.9（已在 3.9, 3.11 环境下验证）
- **Node.js 运行环境：** Node.js >= 18（已在 20 环境下验证）
- **官方 Skills CLI：** 兼容 `vercel-labs/skills` v1.7.0 CLI 规范
- **Harness 集成模式：** 宿主端平铺安装（`<skills-root>/<name>/`），支持全局与项目双作用域
