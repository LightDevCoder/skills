# Review System — 组合

[English](../../workflows/review-system.md)

本文说明 **Review** 的组合：reviewer vs 引擎 vs 验收拥有者。不要把最终验收塞回引擎。

## 职责分离

```text
                  review-loop  （轻量引擎）
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 generic-review  code-review   领域 reviewer
        └─────────────┼─────────────┘
                      ▼
                project-review  （验收拥有者）
                      │
               PASS / FAIL / BLOCKED
```

| 角色 | Skill | 调用 | 保证 |
| --- | --- | --- | --- |
| Reviewer | [`generic-review`](../../../skills/generic-review/SKILL.md) | model-invoked 只读 | 归一化 `id`/`severity`/`location`/`problem`/`reason` findings；不修复不裁决 |
| Reviewer | [`code-review`](../../../skills/code-review/SKILL.md) | model-invoked 只读 | 有界 `git diff` 的 Standards + Spec findings |
| Engine | [`review-loop`](../../../skills/review-loop/SKILL.md) | model-invoked（支持手动） | 解析 reviewer → 调用 → 收 findings → 交 Producer → 重跑；干净或达上限即停 |
| Acceptance | [`project-review`](../../../skills/project-review/SKILL.md) | model-invoked（支持手动） | 冻结 Charter/baseline、组合 reviewer、经 `review-loop` 驱动并签发最终 `PASS`/`FAIL`/`BLOCKED` |

见 [Reviewer 契约](../../../docs/REVIEWER_CONTRACT.zh-CN.md) 的归一化输入包（`Target`·`Requirements`·`Relevant context`·`Previous findings`）与结果（`Findings: []`）。

## Entry → Handoff → Stop

| 场景 | 入口 | 路径 | 停止点 |
| --- | --- | --- | --- |
| 普通制品（无 specialist） | `generic-review` 经 `review-loop` | `review-loop` → `generic-review` → findings → Producer 修复 → 复检 | `Findings: []` 或有界 `persists`；引擎不发最终 verdict |
| 有界代码 diff | `code-review` 经 `review-loop` | `review-loop` → `code-review`（并行 Standards + Spec） → findings | 仅 findings，verdict 在他处 |
| 项目需最终验收 | [`project-review`](../../../skills/project-review/SKILL.md) | `project-review init`（冻结 Charter/Profile） → `review`（组合 reviewer 经 `review-loop`） → `resume` → fresh Evaluator → `PASS`/`FAIL`/`BLOCKED` | 持久 verdict + 证据后停止 |

## 与 `implement` 的关系

```text
implement → review-loop + (generic-review | code-review)
implement（项目级）→ project-review → review-loop + reviewers
```

`implement` 推荐并移交 review 路径后停止；reviewer 执行检查，引擎收敛，验收方裁决。

## 历史

原嵌于 `review-loop` 的 `frozen baseline` / `final verdict` / `PASS`/`FAIL`/`BLOCKED` / `scope-change boundary` 能力已迁至 `project-review`（SPEC §25 Phase 7），`review-loop` 为轻量引擎。
