# 11 — Review system (review-loop + generic-review + project-review)

**What to build:** 重构轻量 `review-loop` 并新建 `generic-review`/`project-review`，分离 评审引擎 / 默认评审员 / 项目终验 三层职责。

**Blocked by:** 10 — implement + code-review

**Status:** ready-for-agent

- [ ] `review-loop` REFACTOR：仅保留 `review→findings→repair→re-review` 循环，职责为 resolve reviewer / invoke reviewer / receive findings / return repair / re-run reviewer，达上限停；不再默认维护完整 acceptance system（SPEC §9 review-loop）
- [ ] `generic-review` NEW：默认 reviewer，检查 missing requirements/incorrect result/contradictions/usability/scope expansion，保持简单不建大规则库
- [ ] `project-review` NEW：项目级 final acceptance，回答目标是否达成，可组合 `generic-review/code-review/domain reviewers` 并用 `review-loop` 收敛；迁移旧 `review-loop` 中 `frozen baseline/PASS/FAIL/BLOCKED/scope-change boundary` 的成熟逻辑，不从零重写（SPEC §9 project-review / §25 Phase 7）
- [ ] `code-review` 仍作为 specialist reviewer 被 `review-loop`/`project-review` 调用，自身不跑 loop 的边界可验

## Comments

Source: SPEC.md §9 / §15 / §25 Phase 7. 阻塞 12。
