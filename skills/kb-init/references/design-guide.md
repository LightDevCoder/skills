# Knowledge Base Design Guide

This guide turns the completed interview plus Base Discovery into a coherent implementation design.

Do not restart the interview here.

## Separate the two models

Keep these separate until they are intentionally combined.

### Knowledge model

Defines:

- what belongs in the knowledge base;
- what one knowledge unit looks like;
- what metadata or fields are needed;
- how related knowledge is represented;
- how attachments are represented;
- how new knowledge enters;
- how users and Agents find it;
- how it is updated and validated.

### Base operating model

Defines:

- what the selected base stores natively;
- how the Agent connects;
- what operations are available;
- what authentication is required;
- what can be automated now;
- what remains manual;
- how backup/export works;
- how a future Agent reconnects.

A good design maps the knowledge model onto the base without unnecessarily distorting either.

## Design rules

### Prefer the simplest complete system

Simple does not mean shallow.

A system is complete when it supports the user's real intake, retrieval, maintenance, and handoff workflows.

Do not add folders, fields, indexes, databases, workflows, or automation merely because they are common in knowledge systems.

### Structure follows retrieval

How the user needs to find, compare, filter, aggregate, or ask about knowledge should materially influence the structure.

A structure that is pleasant to browse but poor for the user's actual analysis tasks is not sufficient.

### Content types are first-class

Do not design as if all knowledge were text.

If images, audio, video, spreadsheets, generated artifacts, links, or binary attachments matter, define how they are stored, linked, searched, moved, backed up, and migrated.

### Make maintenance explicit

The design must define:

- creation;
- updates;
- deletion;
- merges;
- duplicate handling;
- conflicts;
- outdated knowledge;
- category changes;
- relationship maintenance;
- validation;
- backup;
- Agent permissions.

### Maintenance documentation fits the base

Do not force a fixed set of filenames.

Generate whatever operating documentation the chosen environment can actually preserve and future Agents can actually find.

The documentation must answer:

- what this knowledge base is;
- how it is organized;
- how new knowledge is added;
- how knowledge is found;
- how the base is accessed;
- how the Agent reconnects;
- what the Agent may change;
- what requires the user;
- how validation works;
- how backup/export works.

### Distinguish requirement, recommendation, and inference

The design may include recommendations, but label them internally and in the SPEC when useful.

Do not rewrite an Agent recommendation as if the user originally requested it.

### Allow revisiting decisions

If design synthesis reveals a contradiction, return to the relevant interview decision.

Do not hide contradictions in implementation detail.

## Graceful partial implementation

A knowledge base can still be meaningfully initialized when the current Agent lacks a platform-specific capability.

Separate deliverables into:

- complete now;
- prepared now, executable after connection/authorization;
- genuinely blocked.

Maximize the first two categories.

Do not describe a design as complete if the user's core workflow remains impossible.
