# 03 — Migrate release-workflow

**What to build:** 将 `LightDevCoder/release-workflow` 完整迁入 `skills/release-workflow`，与 02 构成 Phase 2 的可并行垂直切片。

**Blocked by:** 01 — Baseline clone and inventory

**Status:** ready-for-agent

- [ ] 完整拷贝 release-workflow 成熟 package 到 `skills/release-workflow/`（保留主体，不重写）
- [ ] 验证 discovery/installation 与 02 同标准
- [ ] 引用与 workflow 串联检查：`release-workflow` 能作为主流程终点被 `project-review` 后调用，无需重构为 `project-init→…` 子步骤
- [ ] 不修改来源仓库 `LightDevCoder/release-workflow`
- [ ] `git diff` 仅新增 `skills/release-workflow/`

## Comments

Source: SPEC.md §4.1 / §16 / §25 Phase 2. 与 02 并行，二者完成后 Phase 2 完成。
