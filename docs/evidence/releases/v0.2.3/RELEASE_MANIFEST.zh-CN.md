# LightDevCoder/skills v0.2.3 发布清单 (Release Manifest)

[English Version](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md) · [发布收据](RELEASE_RECEIPT.zh-CN.md)

本发布清单是 `v0.2.3` 版本的发布前不可变规格记录。它直接提交于 release 候选 commit 中，并永久固化于 annotated tag 快照内部。

---

## 1. 发布规格

| 属性 | 记录值 |
| :--- | :--- |
| **发布版本** | `v0.2.3` |
| **预期 Tag** | `refs/tags/v0.2.3` |
| **发布身份** | `refs/tags/v0.2.3^{commit}`（由 Tag 创建时动态解析） |
| **发布范围** | 包含七大分类目录下的 36 个已准入第一方 Skill；发布证据生命周期重构（拆分发布前不可变清单 Manifest 与发布后收据 Receipt）；v0.2.2 历史事实追加证明；`project-retro` 正向指令重构与建议动作状态机（`AWAITING_SELECTION` $\to$ `APPROVED_ACTION`）；自动化清单完整性校验。 |
| **集合包总数** | 36 admitted packages (36 个已准入包) |
| **政策状态** | `PROVISIONAL` |
| **工作区基线** | Clean（工作区整洁，受版本控制文件无未提交修改） |
| **Tag 不可变性** | 永久不可变发布快照 |

---

## 2. 发布生命周期模型

本次发布严格遵循六阶段生命周期架构：

```text
PREPARED (已准备)
    ↓
CI_VERIFIED (CI 验证完成)
    ↓
TAGGED (已打 Tag)
    ↓
INSTALL_VERIFIED (全新安装验证完成)
    ↓
PUBLISHED (已公开发布)
    ↓
ATTESTED (发布事实已证明)
```

- **Manifest 职责：** 记录发布前确定的事实、身份与范围，固化于 Tag 内。
- **Receipt 职责：** 记录发布后确定的远端 CI 结论、全新安装事实以及 GitHub Release 发布事实，存于 `main`。

---

## 3. 打 Tag 前本地验证证据

| 检查门禁 | 状态 | 验证证据 |
| :--- | :--- | :--- |
| **本地测试集** | `PASS` | 413 passed（全量本地测试套件通过）；unittest 契约检查通过 |
| **字节码编译** | `PASS` | `python -m compileall -q skills tests` 无编译错误 |
| **发布完整性检查** | `PASS` | `scripts/verify_release_integrity.py` 校验全部通过 |
| **Git 格式规范** | `PASS` | `git diff --check` 无空白字符违规 |
| **Skill 包契约** | `PASS` | 全量 36 个包符合包契约与发现规范 |

---

## 4. 兼容性基线

- **Python 运行环境：** Python >= 3.9（CI 与本地测试覆盖 3.9, 3.11）
- **Node.js 运行环境：** Node.js >= 18（CI 验证覆盖 20）
- **官方 Skills CLI：** 兼容 `vercel-labs/skills` v1.7.0 CLI 规范
- **Agent Harness 集成：** 扁平安装目录（`<skills-root>/<name>/`），支持全局与项目级多范围发现
