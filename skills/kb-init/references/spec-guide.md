# Knowledge Base Implementation SPEC Guide

The SPEC is the boundary between discussion and implementation.

It is produced only after the user explicitly ends the interview.

It synthesizes decisions already made.

## Writing style

Write for the person who will own the knowledge base.

Use the user's terminology.

Explain technical choices by the practical problem they solve.

Separate:

- user requirements;
- accepted recommendations;
- verified environment facts;
- low-risk implementation choices;
- explicitly deferred items.

For every architecture-shaping choice in the SPEC, preserve where the decision came from.

Do not rewrite an Agent-only inference as a user decision or accepted recommendation.

If the user explicitly keeps a choice under their own control, preserve that policy in the SPEC and do not add a default value for the reserved choice.

Do not disguise blockers as settled decisions.

## Required SPEC content

The exact headings may vary, but an implementation-ready SPEC must cover the following.

### Problem and objective

What problem the knowledge base solves and what the user should be able to do afterward.

### Users and operating model

Who uses it, who maintains it, and the role of Agents.

### Knowledge scope

What belongs, important content/media types, what one knowledge unit looks like, and exclusions.

### Base decision

The selected base, why it fits, and accepted tradeoffs.

Do not include a generic product catalog.

### Base operating path

Summarize verified Base Discovery facts:

- storage model;
- programmatic access;
- authorization;
- relevant read/write/search/attachment capability;
- backup/export;
- current Agent capability;
- known limitations.

### Exact destination

State where the implementation will live or how the exact target will be selected during an approved connection step.

Do not invent a path or remote target.

### Connection plan

Include this section when the base requires a separate application/service connection.

State:

- proposed connection route;
- what the Agent can configure after approval;
- what the user must authorize or choose;
- how credentials/authorization are provided without asking the user to paste secrets into chat or shell arguments;
- whether setup is project-scoped or global;
- what remains if the current environment lacks the connector/CLI/API capability;
- how connection success will be validated.

### Knowledge structure

Describe the canonical organization:

- directories/collections/tables as appropriate;
- fields;
- relationships;
- naming;
- hierarchy;
- links/indexes;
- attachment placement;
- structured/free-form portions.

Use a tree/schema/diagram when useful.

### Human navigation and presentation

Include this section when people directly browse or operate the base.

Only include architecture-shaping navigation choices that the user explicitly decided or accepted. Do not invent the primary hierarchy/view in the SPEC.

State:

- the human entry point;
- the primary browse dimensions;
- how recent and older knowledge are surfaced;
- how a person finds something after the collection grows;
- important default views, filters, indexes, or grouping;
- what is physical hierarchy versus virtual navigation;
- any base-specific presentation choices that materially affect usability.

Do not require a human-navigation layer when the base is effectively Agent-only.

Do not turn this section into unrelated UI/product design.

### Source traceability

If required, state:

- what source material is retained;
- how source inputs receive stable identity;
- how derived knowledge links back;
- how traceability is validated.

### Knowledge intake

Describe the end-to-end intake flow.

Only include stages the user actually needs.

### Retrieval, analysis, and outward interfaces

Describe how users/Agents find, filter, compare, aggregate, export, or provide data to downstream consumers.

Define interfaces the knowledge base must expose.

Do not design downstream consumer systems unless explicitly in scope.

### Operational mechanism matrix

For each core workflow, state the actual executor and mechanism.

Recommended format:

| Workflow | Required behavior | Executor | Mechanism | Permission/Dependency | Validation |
|---|---|---|---|---|---|
| Intake | ... | ... | ... | ... | ... |
| Query | ... | ... | ... | ... | ... |
| Maintenance | ... | ... | ... | ... | ... |
| Health check | ... | ... | ... | ... | ... |
| Export | ... | ... | ... | ... | ... |
| Backup | ... | ... | ... | ... | ... |

Add/remove rows based on the actual system.

### Agent authority

What the Agent may do automatically, what requires explicit user instruction, and what requires new authorization.

### Maintenance entry point and documents

State where future Agent sessions find the authoritative maintenance rules.

List the concrete operating documents/configuration that will be generated.

Do not force fixed filenames across bases.

### Existing material and migration

If applicable:

- source locations;
- what will migrate;
- what remains untouched;
- duplicate/restructure handling;
- migration validation.

### Backup/versioning and recovery semantics

State the actual backup/version mechanism and responsibility.

Label the guarantee accurately when relevant:

- offline snapshot;
- portable export;
- recoverable backup/disaster recovery.

If recoverability is claimed, include a restore/reconstruction validation that checks the important content, fields/structure, relationships, and attachments required by the design. A file-count or size check alone validates capture, not recovery.

Do not silently add Git or another versioning system unless it was decided.

### Implementation plan

Separate:

- work the current Agent can complete immediately;
- connection/setup work after approval;
- user authorization/actions;
- work that remains blocked if capability is unavailable.

Prefer stable non-GUI routes over GUI-only routes.

### Validation

Define end-to-end checks for actual workflows, including:

- add knowledge;
- retrieve/analyze;
- human browsing/navigation when people directly use the base;
- maintain/update;
- source traceability when required;
- connection/reconnection when required;
- permissions/boundaries;
- backup/export where relevant.

### Deliverables

List only concrete outputs that will exist.

Pre-SPEC research notes are evidence, not automatic final deliverables. Include them only if the user explicitly wants them retained or the approved design gives them an ongoing role.

### Non-goals

Protect the scope.

Explicitly exclude downstream consumer design when it is not part of the knowledge-base task.

### Remaining limitations

State exactly what remains, why, what is already prepared, and what will unblock it.

## Approval gate

End with a clear stop, for example:

> 这份 SPEC 只定义实施方案，目前还没有开始创建知识库结构、配置连接或生成维护实现。  
> 如果这版没有问题，你明确告诉我开始，我再按它实施。

If pre-SPEC research artifacts already exist because the research harness had to write them locally, state that exception explicitly instead of claiming no file was created or modified.

Then stop.

A question about the SPEC is not approval.
