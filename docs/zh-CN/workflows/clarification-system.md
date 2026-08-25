# Clarification System — 组合

[English](../../workflows/clarification-system.md)

本文说明 **Clarification & Research** 的组合：入口、handoff 与停止。追问逻辑在各 `SKILL.md` 与 `references/` 中。

## 家族

```text
                 socratic  （model-invoked 引擎）
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
   clarify   project-clarify  decision-map
                │                  │
                └───── unknown ────┘
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
        research  prototype  to-questionnaire
```

- [`socratic`](../../../skills/socratic/SKILL.md) — 核心引擎：动态、decision-owned 的追问，无固定问卷，区分事实与用户决策；本身不是项目流程，被其他 Skill 调用。
- [`clarify`](../../../skills/clarify/SKILL.md) — **user-invoked 单入口**，面向无项目上下文的模糊想法。`clarify → socratic`。返回 `Current understanding / Resolved / Still unresolved / Gaps` + 当前问题后停止，不产 SPEC。

## 面向项目的澄清

| Skill | 入口 | 如何用 `socratic` | Handoff | 停止点 |
| --- | --- | --- | --- | --- |
| [`project-clarify`](../../../skills/project-clarify/SKILL.md) — user-invoked | 现有项目仍有未决决策 | **先检查：** `README`、`AGENTS.md`、`CLAUDE.md`、既有文档/SPEC/源码；*再* 对仅需用户决策的缺口调 `socratic` | 供 `project-spec` 的有界 handoff（仍模糊则回 `decision-map`） | 止于澄清 summary，不建 SPEC/tickets |
| [`decision-map`](../../../skills/decision-map/SKILL.md) — user-invoked | 大型、模糊、跨会话、依赖多 | 在 `.scratch/<effort>/map.md` 及子 tickets 上维护决策地图，可按 unknown 路由调 `socratic` 与 `research`/`prototype`/`to-questionnaire` | 决策收敛后交 `project-spec` | 止于地图更新；工作留痕于 tracker |

## Unknown 路由

```text
Unknown
  ├─ 须由用户决定          → socratic
  ├─ 外部事实              → research（PORT，读一手来源）
  ├─ 需实验                → prototype（一次性探针）
  └─ 信息在他人处          → to-questionnaire（PORT，生成问卷）
```

调能力，不抄指令；`research`/`prototype` 为只读查证，`to-questionnaire` 返回问卷由用户转交。

## Handoff 规则

- `clarify` 止于 summary；出现正式项目时由*用户*显式调 `project-clarify`/`decision-map`，不自动串联。
- `project-clarify` 交 `project-spec`；`project-spec` 若仍有阻塞决策则返回 `project-clarify`。
- `decision-map` 清雾后交 `project-spec`。

见 [project-workflow](project-workflow.md) 了解澄清如何进入规划；入口不清时用 [`ask-light`](../../../skills/ask-light/SKILL.md)。
