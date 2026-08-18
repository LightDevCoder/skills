# Knowledge Base Implementation SPEC Guide

The SPEC is the boundary between discussion and implementation.

It is created only after the user explicitly ends the interview.

It synthesizes what has already been decided. It does not launch a new interview.

## Writing style

Write for the person who will own the knowledge base.

Use the user's own terminology where possible.

Avoid unnecessary knowledge-management jargon.

Explain technical choices by the practical problem they solve.

Separate:

- user requirements;
- accepted recommendations;
- Agent implementation choices;
- explicitly deferred items.

Do not pretend an unresolved blocker is settled.

## Required SPEC content

The exact headings may vary, but an implementation-ready SPEC must cover the following.

### Problem and objective

Describe:

- what problem the knowledge base solves;
- what the user should be able to do when it is complete.

### Users and operating model

Describe:

- who uses it;
- who maintains it;
- the role of Agents;
- collaboration expectations.

### Knowledge scope

Describe:

- what belongs in the knowledge base;
- the important content and media types;
- what one knowledge unit or record looks like;
- important exclusions.

### Base decision

Describe:

- the selected base;
- why it fits the user's workflow;
- which requirements drove the choice;
- any accepted tradeoffs.

Do not include a generic catalog of alternative products.

### Base connection and operating path

Summarize Base Discovery.

State:

- how the Agent connects;
- required authorization or setup;
- what the Agent can read/write/search/manage;
- how attachments are handled;
- what can be automated without GUI interaction;
- what the current environment cannot do;
- what manual or future steps remain;
- how another Agent session reconnects.

### Knowledge structure

Describe the actual organization.

This may include:

- directories;
- collections;
- tables;
- fields;
- relationships;
- naming;
- hierarchy;
- links;
- indexes;
- attachment placement;
- structured and free-form portions.

Use a tree, schema, or simple diagram when it improves clarity.

Explain the purpose of major structural components.

### Knowledge intake

Describe the end-to-end path for new knowledge.

Use realistic flows.

Example shape:

```text
new material
→ temporary holding step if needed
→ normalization or extraction
→ final knowledge unit
→ relationships / source links
→ validation
```

Only include stages the user actually needs.

### Retrieval, analysis, and outputs

Describe how users and Agents will:

- find information;
- filter or search;
- perform date-range or cross-record analysis;
- generate reports or exports;
- retrieve attachments or source material.

Include at least one realistic scenario derived from the interview.

### Maintenance model

Describe:

- who may create;
- who may edit;
- who may delete;
- how merges and duplicates work;
- how conflicts and outdated knowledge work;
- how structure changes;
- how navigation and relationships stay correct;
- how validation happens;
- how backups or exports happen.

### Agent authority

State clearly:

- what the Agent may do automatically;
- what requires explicit user instruction;
- what requires new authorization or connection setup.

### Maintenance documentation

List the concrete operating documents or configuration that will be generated.

Do not force fixed filenames across different bases.

The generated material must be enough for a fresh Agent session to understand and continue maintenance.

### Existing material and migration

If applicable, describe:

- source locations;
- what will be migrated;
- what remains untouched;
- how duplicates or restructuring are handled;
- how migration will be validated.

If starting empty, say so briefly.

### Implementation plan

Provide an actionable sequence.

Separate:

- work the current Agent can complete immediately;
- setup or authorization the user must perform;
- work that continues after access is available.

Prefer programmatic routes over GUI-only routes.

### Validation

Define end-to-end acceptance checks for the user's actual workflows.

At minimum include representative tests for:

- adding knowledge;
- finding or analyzing knowledge;
- maintaining knowledge;
- reconnecting to or operating the base;
- respecting permissions and boundaries.

### Deliverables

List only concrete outputs that will exist after implementation.

### Non-goals

Include important exclusions when they protect the current scope.

### Remaining limitations

If the current environment cannot complete part of the base configuration, state:

- exactly what remains;
- why;
- what has already been prepared;
- what will unblock it.

Do not bury this in notes.

## Approval gate

End the SPEC with a clear stop.

Example:

> 这份 SPEC 只定义实施方案，目前还没有创建或修改知识库。  
> 如果这版没有问题，你明确告诉我开始，我再按它实施。

Then stop.

Do not interpret a question about the SPEC as approval.
