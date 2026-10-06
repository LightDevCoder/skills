# Category directory migration

[简体中文](CATEGORY_MIGRATION.zh-CN.md)

v0.2.2 moved all 36 source packages from a flat directory into categories without changing names or invocation modes at that time. The table preserves old flat paths and links to the current v0.2.7 candidate; 12 packages also have a separate [name migration](MIGRATION-v0.2.7.md). The published v0.2.6 release retains the earlier names.

A category is not a Skill package and contains no `SKILL.md`. Old tags and historical evidence retain their original paths; inspect their recorded revision. When updating source references, symlinks, or manual copies to the candidate, also update `--skill` values and explicit invocations through the name migration guide.

| Skill | Old source path | New source path |
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

[Category index](../skills/README.md)
