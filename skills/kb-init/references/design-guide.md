# Knowledge Base Design Guide

Turn the completed interview, Base Discovery, and readiness decisions into a coherent implementation design.

Do not restart the interview here.

## Keep the models separate

### Knowledge model

Defines:

- what belongs in the knowledge base;
- what one knowledge unit looks like;
- fields/metadata;
- relationships;
- source traceability;
- attachment handling;
- intake;
- retrieval;
- maintenance;
- validation.

### Human navigation model

Use this only when people directly browse or operate the base.

Defines:

- what the person sees first;
- the primary browse dimensions;
- how recent and older knowledge are separated or surfaced;
- how people find something they remember only partially;
- which navigation is physical hierarchy versus virtual views/filters/indexes;
- how navigation behaves as the collection grows.

The human navigation model may be different from the canonical storage model.

A flat canonical store may still have rich human navigation.

A nested canonical store may still require search, indexes, or cross-cutting views.

Do not optimize the system only for Agent/API convenience when people directly use it.

### Base operating model

Defines:

- what the selected base stores natively;
- how the Agent connects;
- available operations;
- authentication;
- automation;
- backup/export;
- current limitations;
- future reconnection.

Map the knowledge model and, when relevant, the human navigation model onto the base without unnecessarily distorting either.

## Prefer the simplest complete system

Simple does not mean shallow.

A system is complete when it supports the user's real intake, retrieval, maintenance, traceability, connection, backup, and handoff workflows.

Do not add architecture merely because it is common in knowledge-management systems.

## Structure follows retrieval and navigation

How the user needs to find, compare, filter, aggregate, browse, revisit, or ask about knowledge should materially influence the structure.

When people directly browse the base, test the design against an old-knowledge scenario such as finding something from months ago after the collection has grown substantially.

Do not accept a flat dump merely because it is easy for the Agent to write to.

Do not force nested physical hierarchy when saved views, filters, indexes, grouping, or other virtual navigation better match the user's behavior.

## Content types are first-class

If non-text content matters, define how it is stored, linked, retrieved, exported, backed up, and migrated.

## Preserve traceability at the required precision

If the user needs to trace derived knowledge back to exact source inputs, use stable identifiers or explicit relationships.

Do not rely on approximate matching such as date, title, or source label when exact provenance is required.

## Respect the consumer boundary

A downstream use may constrain the knowledge base.

For example, an external consumer may require specific fields, export formats, completeness, or identifiers.

Design those interfaces.

Do not design the downstream consumer itself unless the user explicitly expands scope.

## Make operational mechanisms explicit

Every core workflow must have an executor and mechanism.

Do not leave a capability as vague prose.

For each important workflow, decide:

- who/what executes it;
- what interface or tool it uses;
- what permissions it needs;
- how success is checked.

## Backup claims match recovery reality

Use accurate language for backup outcomes. A content snapshot, portable export, and disaster-recovery backup are different promises.

If the design claims recoverability, define how important structure, relationships, content, and attachments are reconstructed and how that path will be tested. If only an offline copy is validated, call it a snapshot rather than a full recovery backup.

## Maintenance documentation fits the base

Do not force fixed filenames.

Generate whatever authoritative operating documentation the chosen environment can preserve and future Agents can reliably discover.

The maintenance material must explain:

- what this knowledge base is;
- how it is organized;
- how new knowledge is added;
- how knowledge is found;
- how the base is accessed/reconnected;
- what the Agent may change;
- what requires the user;
- how validation works;
- how backup/export works.

## Distinguish requirement, recommendation, implementation choice, and retained user control

Do not rewrite an Agent recommendation as if the user originally required it.

If the user reserves a runtime choice for themselves, preserve that control boundary. Do not convert a previously discussed option into a default merely to make the SPEC look complete.

Pre-SPEC research artifacts are design evidence, not automatic KB deliverables. Keep them outside the implementation target when feasible and only retain them in the final KB/project when the user or approved SPEC calls for it.

## Allow decisions to reopen

If design synthesis reveals a contradiction, return to the relevant decision.

Do not hide contradictions in implementation detail.

## Graceful partial implementation

Separate deliverables into:

- complete now;
- prepared now and executable after connection/authorization;
- genuinely blocked.

Maximize the first two categories without overstating completion.
