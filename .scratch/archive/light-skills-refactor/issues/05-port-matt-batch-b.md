# 05 — Port Matt batch B (diagnosing-bugs/wizard/teach/wait-what/to-questionnaire/writing-for-agents/resolving-merge-conflicts)

**What to build:** 第二批 Matt 直接 Port Skill，完成剩余 7 个 PORT 项，与 04 共同闭合 Phase 3。

**Blocked by:** 01 — Baseline clone and inventory

**Status:** ready-for-agent

- [ ] 读取 upstream 完整包：`diagnosing-bugs`、`wizard`、`teach`、`wait-what`、`to-questionnaire`、`writing-for-agents`、`resolving-merge-conflicts`
- [ ] 同 04 的最小适配原则 Port 到 `skills/<name>/`，保留 `diagnosing-bugs` 的 tight feedback loop、`wizard` 的人机栅栏脚本生成等成熟行为
- [ ] `resolving-merge-conflicts` 保持按 intent 解冲突、永不 `--abort` 的 standalone 定位
- [ ] 仅 04/05 完成后，clarification 家族才能以 Matt `grilling` 系列为真实 baseline 进行 ADAPT
- [ ] Attribution 记录 source repository/path/revision/license/Light 变更，满足 SPEC §22

## Comments

Source: SPEC.md §14 / §16 / §25 Phase 3. 与 04 并行，04+05 完成后 Phase 3 完成。
