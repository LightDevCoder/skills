# 08 — Planning (project-spec / project-tickets)

**What to build:** 实现 Planning 双阶段，将已澄清线程转为正式 SPEC 再转为可执行票证图的端到端切片。

**Blocked by:** 07 — Clarify family

**Status:** ready-for-agent

- [ ] `project-spec` 参考 Matt `to-spec`：将 `project-clarify`/`decision-map` 的已澄清信息整理为正式 project SPEC，不重开访谈；仍有阻塞决策则返回 `project-clarify`（SPEC §7 project-spec）
- [ ] `project-tickets` 参考 Matt `to-tickets`：将 SPEC 转为 tracer-bullet 垂直切片，声明 dependencies/ready work/parallelizable，详 workflow 放 supporting docs 而非堆进 SKILL.md（SPEC §7 project-tickets）
- [ ] 二者 `SKILL.md` 保持执行入口感，`project-spec → project-tickets` 串联可验（本票本身即 dog-food 案例）
- [ ] `project-tickets` 产出的 `.scratch/<feature>/issues/` 单票单文件、Blocked by 边与本 tracker 的 `docs/agents/issue-tracker.md:21` Wayfinding 操作兼容

## Comments

Source: SPEC.md §7 / §15 / §25 Phase 5. 阻塞 10 与 12 的部分依赖。
