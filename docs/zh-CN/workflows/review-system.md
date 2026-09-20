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
| Reviewer | [`generic-review`](../../../skills/review/generic-review/SKILL.md) | model-invoked 只读 | 输出包含严重级别、具体位置与原因的结构化问题清单；仅做检查，不修复、不做最终裁决 |
| Reviewer | [`code-review`](../../../skills/review/code-review/SKILL.md) | model-invoked 只读 | 针对变更代码（`git diff`），从规范标准与业务规格两个维度检查潜在问题 |
| Engine | [`review-loop`](../../../skills/review/review-loop/SKILL.md) | model-invoked（支持手动） | 确定适用的审查角色并调用，收集问题清单后指导修复，随后重新复查；全部通过或达轮次上限时停止 |
| Acceptance | [`project-review`](../../../skills/review/project-review/SKILL.md) | model-invoked（支持手动） | 确认验收范围与准则，组合多个审查角色并驱动修复循环，最终给出明确的 `PASS`、`FAIL` 或 `BLOCKED` 验收结论 |

见 [运行时 reviewer 契约](../../../skills/review/review-loop/references/reviewer-contract.md)（人类摘要：[Reviewer 契约](../../REVIEWER_CONTRACT.zh-CN.md)）的归一化输入包（`Target`·`Requirements`·`Relevant context`·`Previous findings`）与结果（`Findings: []`）。

## Entry → Handoff → Stop

| 场景 | 入口 | 路径 | 停止点 |
| --- | --- | --- | --- |
| 通用文档或配置（非代码制品） | `generic-review` 经 `review-loop` | `review-loop` → `generic-review` → 发现问题 → 指导修复 → 复检 | 问题全部清空或达到重试上限；引擎自身不发布最终裁决 |
| 代码变更（git diff） | `code-review` 经 `review-loop` | `review-loop` → `code-review`（规范与规格双轴并行检查） → 问题清单 | 仅产出问题清单，由外层决定处理 |
| 项目需最终验收 | [`project-review`](../../../skills/review/project-review/SKILL.md) | `project-review init`（确认验收基准） → `review`（组合各 reviewer 并由 `review-loop` 驱动） → 评估结果 → `PASS`/`FAIL`/`BLOCKED` | 输出不可变验收结论与证据后停止 |

## 与 `implement` 的关系

```text
implement → review-loop + (generic-review | code-review)
implement（项目级）→ project-review → review-loop + reviewers
```

`implement` 推荐并移交 review 路径后停止；reviewer 执行检查，引擎收敛，验收方裁决。

## 历史

原嵌于 `review-loop` 的 `frozen baseline` / `final verdict` / `PASS`/`FAIL`/`BLOCKED` / `scope-change boundary` 能力已迁至 `project-review`（SPEC §25 Phase 7），`review-loop` 为轻量引擎。
