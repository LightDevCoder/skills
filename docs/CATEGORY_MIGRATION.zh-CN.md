# 分类目录迁移

[English](CATEGORY_MIGRATION.md)

v0.2.2 将 36 个源码包从平铺目录迁移到分类目录，当时名称与调用方式不变。下表保留旧平铺路径，目标链接指向当前 v0.2.7 候选；其中 12 个包另有名称迁移，详见[名称迁移说明](MIGRATION-v0.2.7.zh-CN.md)。已发布的 v0.2.6 保留迁名前名称。

分类目录不是 Skill 包，不包含 `SKILL.md`。旧 tag 与历史证据保留其原始路径；回查时使用记录中的 revision。按当前候选更新源码引用、软链接和手动复制路径时，也要按迁移说明更新 `--skill` 参数与显式调用。

| 技能 | 旧源码路径 | 新源码路径 |
| --- | --- | --- |
| `agent-config` | `skills/agent-config/` | [skills/engineering/agent-config/](../skills/engineering/agent-config/) |
| `ask-light` | `skills/ask-light/` | [skills/productivity/ask-light/](../skills/productivity/ask-light/) |
| `clarify` | `skills/clarify/` | [skills/thinking/clarify/](../skills/thinking/clarify/) |
| `light-code-review` | `skills/code-review/` | [skills/review/light-code-review/](../skills/review/light-code-review/) |
| `decision-map` | `skills/decision-map/` | [skills/thinking/decision-map/](../skills/thinking/decision-map/) |
| `light-diagnosing-bugs` | `skills/diagnosing-bugs/` | [skills/engineering/light-diagnosing-bugs/](../skills/engineering/light-diagnosing-bugs/) |
| `eli5` | `skills/eli5/` | [skills/knowledge/eli5/](../skills/knowledge/eli5/) |
| `generic-review` | `skills/generic-review/` | [skills/review/generic-review/](../skills/review/generic-review/) |
| `light-handoff` | `skills/handoff/` | [skills/productivity/light-handoff/](../skills/productivity/light-handoff/) |
| `humanizer` | `skills/humanizer/` | [skills/writing/humanizer/](../skills/writing/humanizer/) |
| `light-implement` | `skills/implement/` | [skills/project/light-implement/](../skills/project/light-implement/) |
| `kanban-worker` | `skills/kanban-worker/` | [skills/project/kanban-worker/](../skills/project/kanban-worker/) |
| `kb-init` | `skills/kb-init/` | [skills/knowledge/kb-init/](../skills/knowledge/kb-init/) |
| `language-learning` | `skills/language-learning/` | [skills/knowledge/language-learning/](../skills/knowledge/language-learning/) |
| `learn-anything` | `skills/learn-anything/` | [skills/knowledge/learn-anything/](../skills/knowledge/learn-anything/) |
| `light-travelpage` | `skills/light-travelpage/` | [skills/productivity/light-travelpage/](../skills/productivity/light-travelpage/) |
| `manuscript-ops` | `skills/manuscript-ops/` | [skills/writing/manuscript-ops/](../skills/writing/manuscript-ops/) |
| `project-clarify` | `skills/project-clarify/` | [skills/project/project-clarify/](../skills/project/project-clarify/) |
| `project-init` | `skills/project-init/` | [skills/project/project-init/](../skills/project/project-init/) |
| `project-retro` | `skills/project-retro/` | [skills/project/project-retro/](../skills/project/project-retro/) |
| `project-review` | `skills/project-review/` | [skills/review/project-review/](../skills/review/project-review/) |
| `project-spec` | `skills/project-spec/` | [skills/project/project-spec/](../skills/project/project-spec/) |
| `project-tickets` | `skills/project-tickets/` | [skills/project/project-tickets/](../skills/project/project-tickets/) |
| `light-prototype` | `skills/prototype/` | [skills/engineering/light-prototype/](../skills/engineering/light-prototype/) |
| `recap` | `skills/recap/` | [skills/productivity/recap/](../skills/productivity/recap/) |
| `release-workflow` | `skills/release-workflow/` | [skills/project/release-workflow/](../skills/project/release-workflow/) |
| `light-research` | `skills/research/` | [skills/thinking/light-research/](../skills/thinking/light-research/) |
| `resolving-merge-conflicts` | `skills/resolving-merge-conflicts/` | [skills/engineering/resolving-merge-conflicts/](../skills/engineering/resolving-merge-conflicts/) |
| `review-loop` | `skills/review-loop/` | [skills/review/review-loop/](../skills/review/review-loop/) |
| `socratic` | `skills/socratic/` | [skills/thinking/socratic/](../skills/thinking/socratic/) |
| `light-tdd` | `skills/tdd/` | [skills/engineering/light-tdd/](../skills/engineering/light-tdd/) |
| `light-teach` | `skills/teach/` | [skills/knowledge/light-teach/](../skills/knowledge/light-teach/) |
| `light-to-questionnaire` | `skills/to-questionnaire/` | [skills/thinking/light-to-questionnaire/](../skills/thinking/light-to-questionnaire/) |
| `light-wait-what` | `skills/wait-what/` | [skills/productivity/light-wait-what/](../skills/productivity/light-wait-what/) |
| `light-wizard` | `skills/wizard/` | [skills/productivity/light-wizard/](../skills/productivity/light-wizard/) |
| `light-writing-for-agents` | `skills/writing-for-agents/` | [skills/writing/light-writing-for-agents/](../skills/writing/light-writing-for-agents/) |

[分类导航](../skills/README.zh-CN.md)
