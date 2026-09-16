# Knowledge Base Interview Contract

The purpose of this interview is to design a knowledge base from the user's real workflow.

It is not a generic questionnaire.

The eight areas below are minimum coverage areas. They are not fixed user-facing headings and do not have to be asked in order.

## Conversation rules

Use ordinary language.

Assume the user understands their own work but may not know knowledge-management, database, API, or information-architecture terminology.

When a specialist term is necessary, explain what it does in this system.

A user may answer a question with another question. In that case:

1. answer the user's question;
2. explain tradeoffs;
3. keep the underlying decision open;
4. return to the decision afterward.

Do not interpret curiosity as approval.

If the user explicitly keeps a choice under their own runtime control (for example, "这个我每次自己决定"), treat that control boundary as settled. Do not turn an earlier suggestion into a hidden default for the reserved choice.

Do not optimize for few turns.

There is no fixed minimum or maximum number of interview rounds.

## Decision depth

Coverage and depth are different.

- **Coverage** means the topic has been surfaced.
- **Depth** means the decision is understood well enough to design from without guesswork.

For an important decision, do not mark it settled after one shallow answer.

Before settling a high-impact decision, understand enough of these three layers:

1. **Real workflow** — what the user will actually do.
2. **Priority or tradeoff** — what matters most and what compromise is acceptable.
3. **Concrete scenario** — how this choice should behave in a realistic future case.

Example:

> “I want this organized by topic” is useful, but may not be deep enough.

A follow-up might be:

> “When you come back six months later, will you usually remember the topic first, the approximate date, the source, or something else?”

Do not mechanically ask three questions for every detail. Apply this depth standard mainly to decisions that materially affect architecture, retrieval, maintenance, navigation, automation, or migration.

## Open-decision surfacing

The Agent's internal reasoning may reveal design questions the user has not answered yet.

If such a question could materially change:

- knowledge structure;
- human navigation;
- base selection;
- storage layout;
- automation mechanism;
- permissions;
- migration;
- backup/versioning;
- connection method;
- long-term operating workflow;

the Agent must not silently answer it for the user.

Either:

1. ask the user directly; or
2. present a concrete recommendation with the tradeoff and ask whether the user accepts it.

Do not downgrade an architecture-shaping question into an "implementation detail" merely because one answer seems sensible.

Low-risk implementation details may still be chosen by the Agent when they do not materially alter the user's knowledge-base behavior or future options.

## 1. Purpose, users, and outcomes

Understand:

- what domain or activity the knowledge base serves;
- why the user wants it;
- who will use it;
- who will maintain it;
- whether people directly browse/operate the base or mainly interact through an Agent;
- what useful outcomes should come from it.

Ask concretely.

Examples:

> 这个库以后最常拿来做什么？自己翻资料、直接问 Agent、给团队查、做分析，还是会拿里面的数据继续做别的事情？

> 主要是谁用？你自己、你和 Agent、一个小团队，还是很多人一起维护？

> 你自己会经常直接打开这个知识库浏览和找东西，还是基本都让 Agent 帮你查和维护？

This distinction matters. A base that people directly browse needs a deliberate human-navigation model. A base used mainly through an Agent may not.

Downstream use is relevant only insofar as it changes what the knowledge base must store or expose.

## 2. Content and record types

Understand what the knowledge base actually contains.

Do not reduce this to "documents or data".

Explore relevant material types such as:

- narrative text;
- structured records;
- documents;
- spreadsheets;
- webpages or links;
- code or configuration;
- images or screenshots;
- diagrams;
- vector or animated media;
- audio;
- video;
- online media links;
- attachments;
- generated artifacts;
- other domain-specific material.

Also understand what one meaningful knowledge unit looks like.

Examples:

> 你以后最常往里放的一条东西大概长什么样？是一篇完整笔记、一条固定字段的记录、一份文档，还是经常会带图片和其他附件？

> 图片、视频、链接这些只是附件，还是它们本身也需要被检索和长期管理？

## 3. Base and storage environment

Only discuss the base after enough is known about usage and content, unless the user already chose one.

Understand practical constraints such as:

- local or remote;
- personal or collaborative;
- offline requirements;
- mobile access;
- attachment volume;
- expected scale;
- version history;
- permission control;
- automation requirements;
- portability;
- cost or platform constraints;
- whether the user already has a preferred environment.

Do not make the user choose technology they do not understand.

If the user is unsure, explain a small number of relevant approaches in plain language and recommend one.

The base stays unresolved until the user accepts a direction.

When a serious candidate emerges, Base Discovery may run before this decision is fully settled.

## 4. Knowledge structure and human navigation

Understand both the canonical knowledge structure and, when relevant, how people directly navigate it.

### Canonical knowledge structure

This may include:

- folders or collections;
- record granularity;
- naming rules;
- hierarchy depth;
- fields;
- tags;
- links and relationships;
- attachment placement;
- structured and free-form portions;
- cross-topic relationships.

Do not ask the user to invent a folder tree unless they want to.

The Agent may propose a structure, but a proposal is not a settled decision.

Explain what problem each major structural part solves.

### Human navigation

If people will directly browse or operate the base, read `human-navigation.md`.

Do not assume the canonical storage structure is automatically a good browsing structure.

Clarify how the person should:

- enter the knowledge base;
- browse recent and older knowledge;
- move by the dimensions they naturally remember;
- distinguish active/recent material from archived/older material;
- find knowledge when the collection becomes much larger.

Possible navigation can be physical or virtual. A person may browse by time, topic, author, project, status, or another domain-specific dimension without requiring a literal nested hierarchy.

At least one realistic human-browsing scenario should be understood before this area is settled.

If people will not directly use the base, do not over-engineer a human-facing navigation layer.

## 5. How new knowledge enters and how sources are traced

Understand the real intake workflow.

Clarify when relevant:

- where new material comes from;
- whether there is a temporary holding step;
- whether original material is retained;
- whether derived knowledge must link back to original material;
- whether duplicate detection matters;
- whether review is needed;
- whether records have statuses;
- whether a person or Agent performs each step.

If original material is retained, ask whether the user needs precise traceability.

Example:

> 以后如果发现 Agent 整理错了，你需要能精确追到“这条知识是从哪一份原始输入来的”，还是只要知道大概来源就够？

If precise traceability is required, the design should use stable identifiers or explicit relationships. Do not rely only on weak labels such as date or source name.

Do not expose internal terms such as Raw layer, Source layer, provenance, or ingestion pipeline unless useful, and explain them if used.

## 6. Retrieval, analysis, and outputs

Understand how the knowledge will be used after it grows.

Explore real needs such as:

- full-text search;
- filtering by fields;
- following links;
- date-range queries;
- cross-record comparison;
- aggregation;
- Agent Q&A;
- semantic retrieval;
- export;
- statistics;
- generating downstream inputs.

Ask for realistic future examples.

Example:

> 假设这个库已经用了半年，你最可能对 Agent 说什么？是找某条知识、比较一段时间的数据，还是把库里的内容导出去给别的系统继续处理？

### Consumer boundary

Use downstream needs to define what the knowledge base must expose.

Do not design the downstream consumer itself.

If the user says they will later create a report, analysis package, dashboard, app, model input, or other consumer, determine only:

- what data/content must be available;
- what structure or export format the consumer needs;
- what traceability or completeness the knowledge base must guarantee.

Do not continue into the downstream product's own internal structure, prompts, charts, UI, report sections, or analysis workflow unless the user explicitly expands the scope.

A useful test is:

> Will this decision change the knowledge base itself or only the thing that consumes it?

If only the consumer changes, stop at the interface requirement.

## 7. Maintenance and Agent autonomy

Understand how the knowledge base stays usable.

Discuss:

- who creates knowledge;
- who updates it;
- how duplicates are handled;
- how conflicts are handled;
- how outdated knowledge is treated;
- whether navigation/relationships must be maintained;
- whether categories may change;
- whether validation or health checks are needed;
- what the Agent may do automatically;
- what requires explicit user instruction.

Ask in practical terms.

Example:

> 平时新增和小修改可以让 Agent 自己做吗？像删除、合并、改整个分类结构这种影响比较大的动作，你希望它先问你，还是也可以自己处理？

Do not invent confirmation gates the user does not need.

## 8. Boundaries, history, migration, and growth

Understand constraints that could invalidate the design later.

Discuss when relevant:

- existing material to migrate;
- material that must remain untouched;
- sensitive or private content;
- Agent access boundaries;
- backup expectations and, when it matters, whether "backup" means an offline snapshot, portable export, or recoverable reconstruction;
- version history;
- audit/change logs;
- expected growth;
- long-term versus project-lifetime use;
- export/exit strategy;
- future integration with other systems.

Examples:

> 现在已经有一批资料了吗，还是从空库开始？

> 这里面会不会有不希望 Agent 读取的私人或公司敏感内容？

> 你觉得这个库以后大概会增长到什么规模？这个会影响我们要不要一开始就给结构留余地。

## Research detours

Use research for facts, not user preferences.

Typical triggers include:

- the user asks for current capability facts before deciding;
- a candidate base's official integration method is unclear;
- attachment/search/permission/export limits matter;
- the Agent is unfamiliar with the candidate base;
- the user explicitly asks to research a direction.

Whenever research is used, follow `research-contract.md`.

After research, return to the paused decision.

## Decision dependency

Treat the interview like a design tree.

Do not ask a decision whose prerequisite is still unresolved unless exploring both together is genuinely useful.

A later answer may reopen earlier decisions.

Examples:

- attachment behavior can reopen the base;
- retrieval needs can reopen structure or storage;
- Base Discovery can reopen the base choice;
- migration can reopen the target structure.

## Settlement standard

Before marking a high-impact area settled, check:

- Is the real workflow understood?
- Is the important user priority or accepted tradeoff understood?
- Is there at least one concrete scenario showing how the choice should behave?
- If people directly use the base, is the human-facing experience clear enough for the relevant structure/navigation decision?
- Is the decision source valid?

A valid high-impact decision source is one of:

- explicit user decision;
- user-accepted recommendation;
- verified environment fact;
- explicit user deferral;
- genuinely not-applicable.

The following is **not** valid:

- "the Agent has a reasonable default";
- "this is probably what the user wants";
- "the current directory suggests this destination";
- "the Agent already designed something plausible in reasoning".

If not, the area is still `discussing`, even if it has already been mentioned.

## Do not close early

Do not say the interview is complete merely because all eight headings have been touched once.

Before using any closure-signaling language — including "last question", "final few questions", "wrapping up", "after this it is complete", or equivalent wording — run `readiness-check.md`.

Even after readiness passes, the user still owns the end of the interview.
