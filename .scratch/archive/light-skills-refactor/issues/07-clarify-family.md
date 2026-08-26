# 07 — Clarify family (clarify / project-clarify / decision-map)

**What to build:** 在 socratic 之上完成三层 clarification 入口，覆盖轻量、项目感知、大型持久三种场景的完整垂直切片。

**Blocked by:** 06 — Socratic base

**Status:** ready-for-agent

- [ ] `clarify` 参考 Matt `grill-me`：standalone 轻量入口，`clarify → socratic`，不要求产出正式 SPEC，用于 idea/requirement/brainstorm（SPEC §6 clarify）
- [ ] `project-clarify` 参考 Matt `grill-with-docs`：项目感知入口，提问前先读 `README/AGENTS.md/CONTEXT.md/docs/adr/source/specs/task state`，项目可回答的事实不重问；`project-clarify → socratic`，必要时调用 `research`/`prototype`，大型任务可升级 `decision-map`
- [ ] `decision-map` 参考 Matt `wayfinder`：用于绿地/巨型多 Session 的决策地图，维护 `.scratch/<effort>/map.md` + decisions，通过 `research/prototype/socratic/to-questionnaire` 逐票 resolve，直到 fog 清除后 handoff 到 `project-spec`
- [ ] 三者均保持 `SKILL.md` 精简，详例放 supporting files；composition before duplication，不复制 socratic 指令
- [ ] 验证 handoff：`project-clarify` 能产出可直接进入 `project-spec` 的线程材料；`decision-map` 能通过 wayfinder 的 map/child/blocking/frontier 操作

## Comments

Source: SPEC.md §6 / §15 / §25 Phase 4. 完成后解锁 08 与 10。
