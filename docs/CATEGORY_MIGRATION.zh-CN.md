# 分类目录迁移

[English](CATEGORY_MIGRATION.md)

从当前 main 开始，36 个 Skill 的源码从平铺目录移动到分类目录。技能名称、显式调用语法、宿主安装目录和批准边界均不改变。

使用 `--skill <name>` 的安装命令不变。直接引用源码路径的脚本、符号链接和手动安装命令需要按下表更新。旧 tag 与历史证据保留原始路径；回查时使用证据记录中的 revision。分类目录不是技能包，不包含 `SKILL.md`。

| 技能 | 旧源码路径 | 新源码路径 |
| --- | --- | --- |
| `agent-config` | `skills/agent-config/` | [skills/engineering/agent-config/](../skills/engineering/agent-config/) |
| `ask-light` | `skills/ask-light/` | [skills/productivity/ask-light/](../skills/productivity/ask-light/) |
| `clarify` | `skills/clarify/` | [skills/thinking/clarify/](../skills/thinking/clarify/) |
| `code-review` | `skills/code-review/` | [skills/review/code-review/](../skills/review/code-review/) |
| `decision-map` | `skills/decision-map/` | [skills/thinking/decision-map/](../skills/thinking/decision-map/) |
| `diagnosing-bugs` | `skills/diagnosing-bugs/` | [skills/engineering/diagnosing-bugs/](../skills/engineering/diagnosing-bugs/) |
| `eli5` | `skills/eli5/` | [skills/knowledge/eli5/](../skills/knowledge/eli5/) |
| `generic-review` | `skills/generic-review/` | [skills/review/generic-review/](../skills/review/generic-review/) |
| `handoff` | `skills/handoff/` | [skills/productivity/handoff/](../skills/productivity/handoff/) |
| `humanizer` | `skills/humanizer/` | [skills/writing/humanizer/](../skills/writing/humanizer/) |
| `implement` | `skills/implement/` | [skills/project/implement/](../skills/project/implement/) |
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
| `prototype` | `skills/prototype/` | [skills/engineering/prototype/](../skills/engineering/prototype/) |
| `recap` | `skills/recap/` | [skills/productivity/recap/](../skills/productivity/recap/) |
| `release-workflow` | `skills/release-workflow/` | [skills/project/release-workflow/](../skills/project/release-workflow/) |
| `research` | `skills/research/` | [skills/thinking/research/](../skills/thinking/research/) |
| `resolving-merge-conflicts` | `skills/resolving-merge-conflicts/` | [skills/engineering/resolving-merge-conflicts/](../skills/engineering/resolving-merge-conflicts/) |
| `review-loop` | `skills/review-loop/` | [skills/review/review-loop/](../skills/review/review-loop/) |
| `socratic` | `skills/socratic/` | [skills/thinking/socratic/](../skills/thinking/socratic/) |
| `tdd` | `skills/tdd/` | [skills/engineering/tdd/](../skills/engineering/tdd/) |
| `teach` | `skills/teach/` | [skills/knowledge/teach/](../skills/knowledge/teach/) |
| `to-questionnaire` | `skills/to-questionnaire/` | [skills/thinking/to-questionnaire/](../skills/thinking/to-questionnaire/) |
| `wait-what` | `skills/wait-what/` | [skills/productivity/wait-what/](../skills/productivity/wait-what/) |
| `wizard` | `skills/wizard/` | [skills/productivity/wizard/](../skills/productivity/wizard/) |
| `writing-for-agents` | `skills/writing-for-agents/` | [skills/writing/writing-for-agents/](../skills/writing/writing-for-agents/) |

[分类导航](../skills/README.zh-CN.md)
