# 02 — Migrate eli5

**What to build:** 将 `LightDevCoder/ELI5` 完整迁入 `skills/eli5`，作为第一方 Skill 可被发现、可安装、引用不断的垂直切片。

**Blocked by:** 01 — Baseline clone and inventory

**Status:** ready-for-agent

- [ ] 完整拷贝 ELI5 成熟 package 到 `skills/eli5/`（保留原有 SKILL.md、references/templates/scripts/tests 等，不重新设计、不压缩 SKILL.md）
- [ ] 验证 discovery/installation：CATALOG 可列出 eli5、调用路径与真实 package 一致
- [ ] 验证 cross-reference 无断链（README/CATALOG/workflow docs 如有指向需更新）
- [ ] 不修改来源仓库 `LightDevCoder/ELI5`
- [ ] `git diff` 显示仅新增 `skills/eli5/`，无对 NO REWRITE 列表中其他 Skill 的无意改动

## Comments

Source: SPEC.md §4.1 Migrated / §16 Matrix `eli5 MIGRATE — NO REWRITE` / §25 Phase 2. 可与 03 并行。
