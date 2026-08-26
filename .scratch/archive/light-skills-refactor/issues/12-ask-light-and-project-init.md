# 12 — ask-light + project-init refactor

**What to build:** 最后重构路由与初始化，使全量 Skill map 真实存在后再画地图。

**Blocked by:** 07 — Clarify family, 08 — Planning, 11 — Review system

**Status:** ready-for-agent

- [ ] `ask-light` REFACTOR：作为 Light Workflow Router 最后实施，理解 `current intent/project context/artifacts/available Skills/stage/host capabilities`，路由表覆盖 SPEC §13 典型路由（vague→clarify，existing+unclear→project-clarify，large foggy→decision-map，missing fact→research，need experiment→prototype，SPEC exists→project-tickets，ticket ready→implement，hard bug→diagnosing-bugs，complete→project-review，publish→release-workflow，wait-what 分支），不重实现被路由能力（SPEC §13 / §25 Phase 10，先修路再画地图）
- [ ] `project-init` REFACTOR：在 `project-clarify` 已存在后剥离完整 clarification 职责，仅保留 minimum initialization（SPEC §25 Phase 8）
- [ ] 验证 preserve 列表：除本票与 06-11 外，19 个 NO REWRITE Skill 本票无 substantive 行为改动（SPEC §14 / §26）

## Comments

Source: SPEC.md §13 / §15 / §25 Phase 8+10. 完成后解锁 13 的文档同步。
