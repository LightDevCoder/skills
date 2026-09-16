# Implementation Readiness Check

Run this before telling the user that the interview is fully covered or ready for a SPEC.

This is not another long questionnaire.

It is a silent or concise gap check for implementation-critical facts that are easy to miss even after the conceptual design feels complete.

## Required readiness questions

### Open decision surfacing

Review the Agent's own reasoning and decision map.

Has the Agent noticed any architecture-shaping question that has not actually been surfaced to the user?

If yes, readiness fails.

A plausible Agent answer does not close an open decision.

### Decision provenance

For every high-impact settled decision, can it be attributed to one of:

- explicit user decision;
- user-accepted recommendation;
- verified environment fact;
- explicit deferral;
- not-applicable?

If the only basis is Agent inference or a default chosen for convenience, readiness fails.

If the user explicitly reserved a choice for themselves or excluded it from Agent control, is that boundary preserved without a hidden default being added? If not, readiness fails.

### Decision depth

Have important decisions been understood beyond surface coverage?

For each architecture-shaping decision, is there enough understanding of:

- the real workflow;
- the user's priority or accepted tradeoff;
- a realistic future-use scenario?

If not, the interview is not ready merely because the topic has been discussed.

### Human navigation when people directly use the base

If people will directly browse or operate the base:

- has `human-navigation.md` actually been read in this session?
- is it clear:

- what they see first;
- the primary browse dimensions;
- how they find older knowledge;
- how the experience behaves at expected scale;
- which parts are physical structure versus views/filters/indexes or other virtual navigation?

If direct human use is not part of the operating model, this check is not applicable.

### Required reference loading

If a third-party software/service base is a serious or selected candidate, has `base-discovery.md` actually been read in this session?

If external/current facts were needed, has `research-contract.md` actually been read before research?

Missing a conditionally required reference is a readiness failure.

### Exact destination

Is it clear where the knowledge base will actually live?

Examples of acceptable specificity:

- a concrete local/project path;
- a selected remote workspace/container;
- a clearly identified database/location;
- a destination that will be chosen during an explicitly approved connection step.

Do not invent a location.

### Base fit and operating model

Has Base Discovery been completed enough to know whether the selected base can support the required workflows?

If the base is direct local storage, this may be simple.

If it requires a separate software/service connection, the intended connection route and user authorization requirements must be known before the SPEC is implementation-ready.

### Maintenance entry point

Is it clear where a future Agent session will find the authoritative maintenance rules?

The exact filename or mechanism depends on the base.

Do not assume a fixed AGENTS.md or other filename.

### Operational mechanisms

For each core workflow, is it clear what will actually execute it?

Core workflows commonly include:

- intake;
- query/retrieval;
- maintenance/update;
- validation/health checks;
- export;
- backup;
- migration when applicable.

The mechanism may be:

- Agent following written rules;
- base-native behavior;
- CLI/API/connector operation;
- script/tool;
- user action.

Do not leave "the system supports X" without deciding how X actually happens.

### Existing material and migration

If existing material exists, is its source/location and migration treatment clear enough to implement safely?

### Backup/version responsibility

Is it clear how backup/versioning will work and who is responsible?

If backup is required, is the assurance level stated accurately? Distinguish when relevant between:

- **offline snapshot** — a local copy that preserves content for inspection;
- **portable export** — an export intended to move/rebuild knowledge elsewhere, possibly with fidelity loss;
- **recoverable backup** — a backup expected to reconstruct the important structure, relationships, and attachments after loss.

Do not call a snapshot "disaster recovery" unless a restore/reconstruction path is defined and validated.

Do not silently initialize version-control systems merely because the files are local.

### Pre-approval side effects

Has the interview/research phase avoided creating knowledge-base implementation artifacts before approval?

Research evidence may exist, but it should be isolated from the intended KB target when feasible and must not be silently promoted into final deliverables. If project-local research evidence was unavoidable, later approval-gate wording must acknowledge it accurately.

### Connection/setup scope

If setup requires installing a CLI, connector, MCP server, SDK, or changing Agent/harness configuration:

- is that change included in the intended SPEC?
- is the scope project-level or global?
- would global changes require explicit user approval?
- is credential handling safe, without requiring the user to paste secrets into chat or command arguments?

### Boundaries and permissions

Are write/delete/move/restructure permissions clear enough for implementation?

## Result

If any missing item would materially change the implementation, do not use closure language.

Ask only the smallest useful question needed to fill the gap.

If every material item is ready, report that the necessary content and implementation prerequisites are covered, but still wait for the user to explicitly end the interview.
