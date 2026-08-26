# 10 — implement + code-review (execution core)

**What to build:** 实现通用 bounded executor `implement` 与只读双轴评审 `code-review`，打通 执行→TDD→review→commit 的主流程。

**Blocked by:** 07 — Clarify family, 08 — Planning, 09 — agent-config

**Status:** ready-for-agent

- [ ] `implement` 参考 Matt `implement` 再适配为 general-purpose：支持 code/document/configuration/research artifact/Skill；流程 `inspect context → agent-config when useful → execute → verify → review-loop when appropriate`；Coding 时 `implement→tdd→code changes→tests→review-loop→code-review`，Non-coding 时 `implement→artifact→review-loop→generic-review`；不复制 `agent-config/tdd/review-loop` 全文（SPEC §8 implement）
- [ ] `code-review` 参考 Matt `code-review` 适配为 read-only reviewer：并行 Standards + Spec 双轴评审，产出 findings，不自行修码/不跑 repair loop/不定最终 PASS（SPEC §9 code-review）
- [ ] 二者 `SKILL.md` 精简，详 workflow/examples 放 supporting files，不要求统一 package shape
- [ ] 验证 implement 能消费 `project-tickets` 产出的单票文件，并在独立 context 窗口内完成单票

## Comments

Source: SPEC.md §8 / §9 / §15 ADAPT / §25 Phase 6 后半 + Phase 7 前半。阻塞 11。
