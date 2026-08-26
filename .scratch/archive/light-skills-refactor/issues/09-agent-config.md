# 09 — agent-config (host-agnostic runtime inspection)

**What to build:** 新建 `agent-config`，在复杂执行前检查真实 Agent Host 能力并做执行路由，而非凭空设计模型的垂直切片。

**Blocked by:** 01 — Baseline clone and inventory

**Status:** ready-for-agent

- [ ] 参考 `https://github.com/DannyMac180/sol-advisor` 的 runtime inspection / model awareness / role assignment 思想，不复制 `Sol/Terra/Luna` 固定拓扑（SPEC §8 agent-config / §15 NEW）
- [ ] 能识别：available models/agents、subagents、parallelism、reasoning levels、multi-session、worktrees、concurrency；无法确认的不猜测
- [ ] 使用抽象角色 `Controller/Explorer/Implementer/Reviewer/Merger` 再映射到真实环境，fallback：multi-model+multi-agent→充分编排，single-model+multi-agent→同模不同 context/role，single-model+single-agent→顺序执行
- [ ] `SKILL.md` 精简，详表放 `references/`；简单任务不强制调用 agent-config，不过度编排
- [ ] Light 主 workflow 不要求安装 Sol Advisor，`agent-config` 自包含（SPEC §22）

## Comments

Source: SPEC.md §8 / §15 / §25 Phase 6. 可与 04-08 并行，阻塞 10。
