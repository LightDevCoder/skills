# Human Navigation

Use this reference only when people will directly browse, review, or operate the chosen base.

The purpose is to design how a human moves through the knowledge base.

This is separate from the canonical knowledge structure and separate from Agent/API access.

A human-facing knowledge base should not become a flat dump merely because a flat structure is convenient for automation.

At the same time, do not create physical hierarchy when filtered views, indexes, search, or other navigation surfaces solve the problem more cleanly.

## First establish the human role

Clarify:

- Will the person open the base directly?
- Will they mostly browse, search, edit, review, or all of these?
- Is the Agent optional assistance, or is the Agent the normal gateway?
- Which devices or environments matter for direct use?

If the user will not normally interact with the base directly, do not force a human-navigation layer.

## Design the entry point

Understand what the person should see first.

Possible needs include:

- recent knowledge;
- an inbox or review queue;
- major domains or topics;
- time-based browsing;
- people/creators/entities;
- projects;
- favorites/high-value items;
- status-based work;
- a search-first home;
- other domain-specific entry points.

Do not assume a dashboard, homepage, or index is needed.

Ask what the user naturally expects to do immediately after opening the base.

Example:

> 你自己打开这个库的时候，第一眼最希望看到什么？最近新增、按主题分类、按时间找、按作者找，还是直接搜索？

## Design browse dimensions

A browse dimension is a way a person naturally groups or scans knowledge.

Relevant dimensions may include:

- time;
- topic/domain;
- author/creator/entity;
- project;
- status;
- source;
- importance/rating;
- content type;
- location;
- lifecycle;
- another domain-specific dimension.

Do not add every possible dimension.

Identify the one or two primary dimensions that match the user's real behavior, plus secondary views only when useful.

## Distinguish physical hierarchy from navigation

The user may want to browse by year/month without requiring a literal nested folder tree.

Likewise, a flat canonical store may still provide rich human navigation through:

- saved views;
- filters;
- grouped views;
- index pages;
- linked collections;
- navigation pages;
- virtual folders;
- search scopes;
- other base-native navigation features.

Choose physical hierarchy only when it solves a real storage or maintenance problem.

Choose virtual navigation when it gives the human the desired browsing experience without fragmenting the canonical data.

## Test old-knowledge retrieval

Ask at least one concrete scenario.

Examples:

> 半年以后你想找去年某个月看过的一条内容，你会先按时间翻，还是先按主题找？

> 如果这个库有 500 条甚至 5000 条，你希望怎么定位以前的东西？

> 你是更常“我记得大概什么时候看的”，还是“我记得它讲什么主题”？

The answer should influence navigation design.

## Consider human readability

When direct human use matters, also consider:

- page/card density;
- visible metadata;
- naming;
- sort order;
- default filters;
- archive visibility;
- mobile versus desktop ergonomics;
- how much detail appears before opening an item.

Do not turn this into UI design work beyond what the base itself requires.

## Navigation depth standard

Human navigation is sufficiently understood when the Agent can explain:

1. what the user sees first;
2. the primary ways the user browses;
3. how the user finds older knowledge;
4. how the navigation behaves as the collection grows;
5. which parts are physical structure versus virtual views/filters.

Only then should the human-facing structure be treated as settled.

The Agent may recommend a navigation model, but a navigation model that materially shapes how the user browses the knowledge base must be explicitly accepted by the user. Do not place an unconfirmed navigation hierarchy into the final SPEC merely because it is reasonable.
