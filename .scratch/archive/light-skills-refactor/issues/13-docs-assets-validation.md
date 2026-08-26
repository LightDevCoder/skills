# 13 — Docs · Assets · Validation

**What to build:** 同步仓库维护文档、接入新头图、跑通全量校验的收口垂直切片，确保交付物自解释且测试守护行为而非 prose。

**Blocked by:** 02 — Migrate eli5, 03 — Migrate release-workflow, 04 — Port Matt batch A, 05 — Port Matt batch B, 11 — Review system, 12 — ask-light + project-init

**Status:** ready-for-agent

- [ ] 仓库文档同步（SPEC §20/§25 Phase 11）：`README.md/README.zh-CN.md`（what is/install/quick start/main workflow/ask-light 入口）、`CATALOG.md/zh-CN.md`（33 Skill 与真实 package 一致，不复制 Skill 全文）、`docs/workflows/{project-workflow,clarification-system,execution,review-system,specialized-workflows}.md`（只讲 Skill 组合与 handoff，不复刻 Skill 内流）、`AGENTS.md`（明确 Matt 为 Skill 写作参照、Sol Advisor 为 agent-config 参照、不重写成熟 Skill 等 9 条规则，不膨胀为 SPEC）、`docs/MAINTENANCE.md`、`docs/SKILL_ADMISSION.md`（允许本 SPEC 批准的 Port + attribution）、`docs/REVIEW_POLICY.md`（reviewer vs review-loop vs project-review）、`CHANGELOG.md/zh-CN.md`（记 unreleased，不发版）
- [ ] 不互相复制：Repository documentation explains the repository, Skill documentation explains the Skill
- [ ] Hero 接入（SPEC §23/§25 Phase 12）：检查 `Assets/` 实际新头图文件名，更新 `README*.md`，清理不再被引用的旧 header
- [ ] Validation（SPEC §24/§25 Phase 13）：保留有效旧测试，更新锁旧架构的测试；Repository Tests（33 Skill 存在/frontmatter 有效/引用可达/CATALOG 一致/link 可达/无 stale 旧名/无 Matt/Sol 运行时依赖/hero 存在/EN-zh 同步）、Composition Tests（clarify→socratic 等 7 条）、Behavior Tests（护行为与 handoff，不护标题措辞）
- [ ] 专项验证：`manuscript-ops/kb-init/learn-anything/language-learning/kanban-worker/recap` 的 standalone + composition 验证，仅 integration 缺口才加最小 handoff（SPEC §19 Phase 9）
- [ ] Final No-Redesign Check（SPEC §26）：对 19 个 NO REWRITE/PORT 列表逐个 `git diff` 检查，成熟 Light Skill 的改动需指出真实 integration 需求，Matt PORT 的 rewrite 需指出真实 Light 不兼容，否则撤销

## Comments

Source: SPEC.md §19-§26 / §25 Phase 11-13 + §26. 本票为 frontier 终点，所有阻塞关闭后即可交付。
