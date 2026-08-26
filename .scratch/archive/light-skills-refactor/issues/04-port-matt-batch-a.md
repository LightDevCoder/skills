# 04 — Port Matt batch A (research/prototype/tdd/handoff)

**What to build:** 首批 Matt 直接 Port Skill 达到 Light 自包含可用，每包读完整 upstream 后仅做最小适配的垂直切片。

**Blocked by:** 01 — Baseline clone and inventory

**Status:** ready-for-agent

- [ ] 逐个读取 upstream `mattpocock/skills` 对应 package 全量：`research`、`prototype`、`tdd`、`handoff`（含 SKILL.md + references/templates/scripts）
- [ ] Port 到 `skills/research/` 等 4 个目录，保留成熟行为，仅做：新增 ATTRIBUTION、移除不兼容的 upstream 运行时耦合、替换 Light 命名/handoff 指向
- [ ] 禁止“读后自己重写一份”；如仅需改调用名则只改一处（SPEC §15 Matt Direct Port 规则）
- [ ] 每个 Skill 的 `SKILL.md` 不膨胀为架构文档，详流放 supporting files，composition 优先于复制
- [ ] Light 主 workflow 不要求 `install Matt skills first`（SPEC §22），`go test`/`npm test` 等现有测试仍绿（如有）

## Comments

Source: SPEC.md §14 / §16 `PORT — NO REDESIGN` / §25 Phase 3. 与 05 并行。
