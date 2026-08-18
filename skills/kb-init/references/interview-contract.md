# Knowledge Base Interview Contract

This document defines the knowledge-base-specific interview.

The goal is not to ask a fixed questionnaire. The goal is to make sure every major design area is genuinely discussed instead of silently inferred.

The interview should feel like collaborative design, not form filling.

## Conversation behavior

Use ordinary language.

Assume the user understands their own work but may not know knowledge-management, database, API, or information-architecture terminology.

When a specialist term is necessary, immediately explain what it does in this knowledge base.

Example:

> 我这里说的“字段”，就是每条记录里固定会出现的几个信息位，比如日期、设备型号、状态。它的作用是以后能稳定筛选和统计。

Do not introduce terminology merely to sound precise.

### Ask, explain, then decide

A user may answer a question with another question.

Example:

> Agent: 我现在更倾向某种结构化存储方式。
>
> User: 为什么？和普通 Markdown 到底差在哪？

The correct behavior is:

1. explain the difference;
2. answer the user's concern;
3. keep the storage decision open;
4. ask whether the user now has a preference or wants further research.

Do not interpret curiosity as approval.

### Do not optimize for few turns

Do not compress several major design areas into one giant message just to reduce turns.

Prefer one major decision area, or one tightly related cluster, per turn.

A normal interview should take as many rounds as the design needs.

There is no fixed minimum or maximum number of rounds.

Completion is controlled by coverage and the user's explicit decision to end the interview, not by speed.

## Required design areas

The following eight areas form the minimum knowledge-base design coverage.

They are internal coverage areas, not headings that must be shown to the user.

The order is adaptive.

A later answer may reopen an earlier area.

---

## 1. Purpose, users, and outcomes

Understand:

- what domain or activity the knowledge base serves;
- why the user wants it;
- who will use it;
- who will maintain it;
- what useful outcomes should come from it.

Possible outcomes include learning, lookup, operational reuse, analysis, reporting, collaboration, archival, troubleshooting, or decision support.

Ask concretely.

Examples:

> 这个库以后最常拿来做什么？自己翻资料、直接问 Agent、给团队查、做分析，还是还会拿它生成报告之类的东西？

> 主要是谁用？你自己、你和 Agent、一个小团队，还是很多人一起维护？

If purpose and users are already clear from context, confirm only what still affects the design.

---

## 2. Content and record types

Understand what the knowledge base actually contains.

Do not reduce this to "documents or data".

Explore the real material types when relevant:

- narrative text;
- structured records;
- documents;
- spreadsheets;
- webpages or links;
- code or configuration;
- images or screenshots;
- diagrams;
- vector graphics;
- animated media;
- audio;
- video;
- online media links;
- attachments;
- generated reports;
- other domain-specific artifacts.

Also understand what one meaningful knowledge unit looks like.

Examples:

> 你以后最常往里放的“一条东西”大概长什么样？是一篇完整笔记、一条带固定字段的记录、一份 PDF，还是经常会带图片和其他附件？

> 图片、视频、链接这些只是附件，还是它们本身也是需要被检索和长期管理的知识？

This area strongly affects the base, structure, storage model, attachment handling, and retrieval method.

---

## 3. Base and storage environment

Only discuss the base after enough is known about usage and content, unless the user already chose one.

Understand the practical constraints:

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

The base remains `unresolved` until the user accepts a direction.

Once a base is selected, it will later go through Base Discovery. Do not embed platform-specific integration recipes here.

---

## 4. Knowledge structure and organization

Understand how the knowledge should be organized once it exists.

This may include:

- folders or collections;
- record granularity;
- naming rules;
- hierarchy depth;
- fields;
- tags;
- links and relationships;
- index or navigation pages;
- attachment placement;
- structured versus free-form sections;
- how cross-topic knowledge is represented.

Do not ask the user to invent a folder tree unless they want to.

The Agent may propose a structure, but a proposal is not a settled decision.

Example:

> 这类知识本身有没有比较自然的几大块？如果现在说不准，我可以先按你的实际使用方式提出一个结构，再一起改。

When proposing a structure, explain what problem each major part solves.

Do not create complexity only to look organized.

---

## 5. How new knowledge enters

Understand the real intake workflow.

Possible questions:

> 平时拿到一份新资料以后，你希望直接整理进库，还是先随手丢进去，等 Agent 之后统一处理？

> 如果是你自己的一条经验，是直接保存最终结论，还是还要保留当时的原始记录？

Clarify when relevant:

- where new material comes from;
- whether there is a temporary holding area;
- whether original material is retained;
- whether derived knowledge must link back to sources;
- whether duplicate detection matters;
- whether review is needed;
- whether records have statuses;
- whether an Agent or person performs each step.

Do not expose internal terms such as ingestion pipeline, Raw layer, Source layer, or provenance unless useful, and explain them if used.

---

## 6. Retrieval, analysis, and outputs

Understand how the knowledge will be used after it grows.

This is a separate design problem from storage.

Explore real tasks such as:

- browsing;
- full-text search;
- filtering by fields;
- following links;
- date-range queries;
- cross-record comparison;
- aggregation;
- Agent Q&A;
- semantic retrieval;
- report generation;
- export;
- statistics;
- dashboards;
- other domain-specific analysis.

Ask for concrete future examples.

Example:

> 假设这个库已经用了半年，你最可能对 Agent 说什么？“帮我找某个案例”，还是“比较最近三个月的数据”，或者“把这些内容整理成报告”？

At least one realistic retrieval or analysis scenario should be understood before finalizing the base.

If the desired retrieval behavior conflicts with the current base choice, reopen the base decision.

---

## 7. Maintenance and Agent autonomy

Understand how the knowledge base stays usable.

Discuss:

- who creates new knowledge;
- who updates existing knowledge;
- how duplicates are handled;
- how conflicts are handled;
- how outdated knowledge is treated;
- whether relationships or navigation are maintained;
- whether categories may change;
- whether validation or health checks are needed;
- what the Agent may do automatically;
- what requires explicit user instruction.

Ask in practical terms.

Example:

> 平时新增和小修改可以让 Agent 自己做吗？像删除、合并、改整个分类结构这种影响比较大的动作，你希望它先问你，还是也可以自己处理？

Do not invent confirmation gates the user does not need.

Do not grant broad write/delete authority by assumption.

---

## 8. Boundaries, history, migration, and growth

Understand the constraints that could invalidate the design later.

Discuss when relevant:

- existing material to migrate;
- material that must remain untouched;
- sensitive or private content;
- Agent access boundaries;
- backup expectations;
- version history;
- audit or change logs;
- expected growth;
- long-term versus project-lifetime use;
- export or exit strategy;
- future integration with other systems.

Examples:

> 现在已经有一批资料了吗，还是从空库开始？

> 这里面会不会有不希望 Agent 读取的私人或公司敏感内容？

> 你觉得这个库以后大概是几百条、几千条，还是可能长期一直长？这个会影响我们要不要一开始就为规模留余地。

Do not over-engineer for hypothetical future scale, but do not ignore growth the user explicitly expects.

## Research detours

Research is used for facts, not user preferences.

Typical triggers include:

- the user asks why one approach is better than another and the answer depends on current capabilities;
- a platform's integration method is unclear;
- current API/CLI/MCP/SDK support matters;
- attachment, search, size, permission, export, or collaboration limits affect the decision;
- the Agent is unfamiliar with the proposed base;
- the user explicitly asks to research a direction before deciding.

When research starts, mark the current decision `researching`.

Say what is being investigated.

Example:

> 这个会直接影响“基座”这一步，我先查清楚它现在有哪些正式的读写方式、附件能力和导出方式。这个问题先保持未决定，查完我们再回来选。

After research, do not jump forward.

Return to the same decision.

## Decision dependency

Treat the interview like a design tree.

Do not ask a decision whose prerequisite is still unresolved unless exploring both together is genuinely useful.

Examples:

- attachment layout may depend on content types;
- query design may force a different storage base;
- Agent maintenance rules may depend on how the base exposes write operations;
- migration may depend on the target structure.

When a new answer changes a prerequisite, reopen downstream decisions.

## Interview completion

The Agent does not decide when the interview ends.

Even if all eight areas are `settled`, remain in interview mode until the user explicitly ends it.

If all areas are covered, say:

> 我这边需要弄清楚的部分已经都覆盖到了。你还可以继续问、改任何一块，也可以让我再 research 一个方向。等你觉得够了，再告诉我“出 SPEC”。

Do not generate the SPEC in the same message unless the user already explicitly asked for it.

If the user explicitly ends the interview while a blocking decision is unresolved, explain the blocker instead of silently filling it.
