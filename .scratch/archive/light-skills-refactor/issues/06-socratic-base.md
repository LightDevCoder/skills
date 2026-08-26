# 06 — Socratic base (core clarification capability)

**What to build:** 实现 clarification 家族的底层能力 `socratic`，让上层 clarify/project-clarify/decision-map 可组合而非重复实现。

**Blocked by:** 04 — Port Matt batch A, 05 — Port Matt batch B

**Status:** ready-for-agent

- [ ] 参考 Matt `grilling` 实现 `skills/socratic/SKILL.md`（保持精简：when/use、core behavior、supporting doc 指向、handoff 指向、停止边界）
- [ ] 支持动态追问、沿回答展开、区分事实/决策、持续收敛未解决决策（SPEC §6 socratic 职责）
- [ ] 详流放 `references/WORKFLOW.md`、`references/EXAMPLES.md` 等，不堆进 SKILL.md；不实现完整项目 workflow
- [ ] 不重新实现 `research`/`prototype`/`to-questionnaire` 能力，仅在 socratic 中声明 Unknown 路由的调用点（用户决策→socratic，外部事实→research，需实验→prototype，他人持有→to-questionnaire）
- [ ] 单元/行为测试覆盖 socratic 的对话收敛与路由，不测 prose

## Comments

Source: SPEC.md §6 / §6 Unknown Routing / §15 ADAPT / §25 Phase 4 前半。阻塞 07。
