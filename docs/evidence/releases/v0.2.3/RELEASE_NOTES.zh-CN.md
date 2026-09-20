# v0.2.3 — 发布完整性生命周期与 Project-Retro 正向重构

[English Release Notes](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [发布收据](RELEASE_RECEIPT.zh-CN.md)

Light Skills v0.2.3 正式确立了六阶段发布生命周期架构，将发布前不可变清单与发布后验证收据严格分离，提供 v0.2.2 历史事实追加证明，完成 `project-retro` 正向状态驱动指令重构，并全面增强了自动化发布完整性校验机制。

---

## v0.2.3 更新要点

### 1. 规范化发布证据生命周期
将发布证据解耦为发布前规格与发布后事实证明：
- **`RELEASE_MANIFEST.md`（发布清单）：** 直接固化于发布候选 commit 及 Tag 快照内。记录版本、范围、包数量、政策状态以及预期 Tag 身份（`refs/tags/v0.2.3^{commit}`），彻底避免 commit hash 的自引用设计困境。
- **`RELEASE_RECEIPT.md`（发布收据）：** 位于 Tag 之后的 `main` 分支。记录发布后确立的事实：Tag 对象 SHA、Peeled commit SHA、确切的 CI 运行 ID 与结果、全新安装测试数据及 GitHub Release URL。
- **六阶段发布模型：**
  ```text
  PREPARED (已准备) → CI_VERIFIED (CI 已验证) → TAGGED (已打 Tag) → INSTALL_VERIFIED (安装已验证) → PUBLISHED (已发布) → ATTESTED (已证明)
  ```

### 2. v0.2.2 发布后事实证明与历史溯源修复
记录 v0.2.2 公开发布后的完整历史事实：
- 确认 v0.2.2 Tag 快照（`90095743...`）作为永久不可变的历史快照保留。
- 记录 v0.2.2 初始 CI 在浅拉取环境（`fetch-depth: 1`）下失败的根因。
- 记录 `main` 上的后续纠正 commit（`0862a19...`）及其通过的 CI 记录（run `35502071190`）。
- 明确固化于 v0.2.2 内的 Candidate 状态收据为历史前身产物。

### 3. `project-retro` 正向指令风格重构
将面向 Agent 的指令统一调整为目标、职责、流程与状态驱动的正向表达：
- **建议动作生命周期状态机：** 显式定义复盘结论交付状态为 `AWAITING_SELECTION`；在人类用户做出显式选择后，将选定项流转为 `APPROVED_ACTION` 进而进入有界执行。
- **工程审计沟通：** 严格基于已验证的代码库事实、当前 HEAD 状态与测试结果展开，聚焦系统、流程、信息架构、防护栏与工具经济性。
- **已闭环经验隔离：** 明确 `[CLOSED]` 结论代表已有持久防护机制保护的历史经验，保留于复盘事实中但坚决排除在 Suggested Actions 之外。
- **常规无阻塞运行处理：** 明确无复发性系统摩擦的常规任务直接完成，不触发复盘。

### 4. 自动化发布完整性脚本与测试增强
- **清单一致性检查：** `scripts/verify_release_integrity.py` 针对 v0.2.3+ 自动校验 `RELEASE_MANIFEST.md` 与 `.zh-CN.md` 的存在性、包总数、政策状态与 Tag 引用。
- **收据一致性检查：** 校验发布后收据中的目标 commit 与本地/远端 Tag 的 peeled commit 一致性。
- **密封单元测试：** 扩展 `tests/test_release_integrity.py`，使用完全独立的临时 Git 仓库测试清单校验与收据目标不匹配检测。

---

## 安装方式

### 稳定版本快照锁定安装（v0.2.3）
若需安装不可变、可复现的 v0.2.3 发布快照，请锁定 `#v0.2.3` tag：

```bash
# 安装完整 36 个 Skill 集合：
npx skills add LightDevCoder/skills#v0.2.3 -y

# 安装单个 Skill：
npx skills add LightDevCoder/skills#v0.2.3 --skill project-retro -y
npx skills add LightDevCoder/skills#v0.2.3 --skill agent-config -y
npx skills add LightDevCoder/skills#v0.2.3 --skill ask-light -y
npx skills add LightDevCoder/skills#v0.2.3 --skill project-init -y
```

### 最新主干安装（main）
若需从主干分支安装最新开发状态：

```bash
npx skills add LightDevCoder/skills -y
```
