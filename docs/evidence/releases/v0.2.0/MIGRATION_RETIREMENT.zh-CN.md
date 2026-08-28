# 迁移与仓库退役记录 — v0.2.0

[English record](MIGRATION_RETIREMENT.md)

本文档记录作为 v0.2.0 33-Skill 架构发布的一部分整合并入 `LightDevCoder/skills` 的独立仓库的溯源、迁移历史与退役计划。

## 1. LightDevCoder/release-workflow

### 上游与独立历史

- **原代码仓库：** `LightDevCoder/release-workflow` (public)
- **独立仓库最终 HEAD：** `fc454f63b44b88779a7b607c5bea0c95f0bcfa01`
- **迁移目标路径：** `LightDevCoder/skills` 仓库下的 `skills/release-workflow/`
- **退役原因：** 将发布治理与发布执行工作流直接整合进统一的第一方 Skill 集合中，确保发布门禁、验证流程与技能目录的原子级同步维护。

### 迁移细节

- **迁移并保留的文件：**
  - `SKILL.md`（发布工作流契约与四阶段治理流程）
  - `references/VERIFICATION.md`（全新安装验证步骤与命令矩阵）
  - `agents/openai.yaml`（接口与策略元数据）
- **迁移后维护变更：**
  - 将遗留的 PowerShell 测试引用替换为可移植的 Python 测试套件（`pytest`、`unittest`、`compileall`、`git diff --check`）。
  - 将 Phase 2 的人工发布门禁扩展为同时推送候选 `main` 分支与 tag，确保通用 latest 安装（`npx skills add LightDevCoder/skills`）能正确解析候选提交。
  - 增加原子推送偏好（`git push --atomic origin main v0.2.0`）及安全顺序推送回退。
  - 对齐 GitHub Actions `collection-quality` 的 CI 语义（在 push `main`、PR 与 workflow_dispatch 时触发）。
- **退役 / 删除状态：**
  - **计划删除日期：** 2026-08-28（v0.2.0 发布并完成验证后）
  - **验证状态：** `NOT TESTED`（等待 Phase 2 与 Phase 3 完成后执行 `gh repo delete LightDevCoder/release-workflow --yes`）

---

## 2. LightDevCoder/ELI5

### 上游与独立历史

- **原始上游仓库：** `DreambigOu/ELI5` (public)
- **源码对应版本：** `a766623b062331fdde53467001379b4ddf3acc2f`
- **临时迁移 fork：** `LightDevCoder/ELI5`
- **开源协议：** MIT License
- **迁移目标路径：** `LightDevCoder/skills` 仓库下的 `skills/eli5/`
- **退役原因：** `LightDevCoder/ELI5` 仅作为集合整合过程中的临时迁移 fork。维护功能现已作为 `skills/eli5/` 纳入统一集合治理。

### 迁移细节

- **迁移并保留的文件：**
  - `SKILL.md`（ELI5 提示词与角色矩阵）
  - `ATTRIBUTION.md`（上游溯源、MIT 许可声明与源码 commit 链接）
- **行为变更：** `none / MIGRATE — NO REWRITE`
- **退役 / 删除状态：**
  - `DreambigOu/ELI5`（原始上游）：**不得删除 / 保持不变**（外部作者的原生上游仓库）。
  - `LightDevCoder/ELI5`（临时迁移 fork）：计划在 v0.2.0 发布验证成功后执行 `gh repo delete LightDevCoder/ELI5 --yes` 进行退役删除。
  - **验证状态：** `NOT TESTED`（等待 Phase 2 与 Phase 3 完成）
