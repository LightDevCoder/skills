# Base Discovery

Base Discovery turns "we may use this base" into an operational understanding of whether it can actually support the knowledge base.

It is platform-agnostic.

Do not maintain a catalog of named software recipes.

Base Discovery may happen during the interview because its result can change the base choice.

For a third-party software/service base, this reference must be read before that base's operating model or connection route is considered settled.

It does not perform configuration.

## Discover the storage model

Determine what the base actually stores:

- files;
- pages;
- records;
- collections;
- tables;
- objects;
- attachments;
- relationships;
- other native units.

Understand which parts are user-visible and which are implementation details.

## Discover programmatic access

Determine the currently supported non-GUI ways an Agent can interact with the base.

Possible categories may include:

- direct filesystem access;
- command-line interfaces;
- connector or MCP interfaces;
- APIs;
- SDKs;
- import/export formats;
- other documented automation surfaces.

These are categories, not assumptions.

Do not assume any category exists.

Do not ask the user to supply public links that can be researched.

If the access method is current, unfamiliar, or unverified, use `research` under `research-contract.md`.

For a third-party software or service base, do not lock a connection route from model memory alone when the official integration surface could have changed. Unless already verified from first-party sources in the current session, research the current supported programmatic access before finalizing whether the implementation should use a connector/MCP-style interface, CLI, API, SDK, import/export route, or another supported mechanism.

## Discover authentication and permissions

Determine:

- what authorization is required;
- whether user approval is needed;
- which permissions are necessary;
- whether least-privilege access is possible;
- whether setup is project-scoped or global;
- what a future Agent session needs to reconnect;
- what safe credential mechanism is supported (for example OAuth, connector-managed auth, environment/config secret store, or another non-echoing route).

Never design a connection flow that requires the user to paste secrets into chat, prompts, maintenance documentation, example files, or shell command arguments when a safer route is available.

## Discover read/write capability

Determine whether an Agent can:

- list/browse;
- search;
- read;
- create;
- update;
- move/reorganize;
- delete;
- upload or link attachments;
- create relationships;
- create fields/schemas;
- manage navigation or views;
- export/back up.

Identify missing operations that matter to the user's workflow.

## Discover attachment and non-text handling

Check how the base handles the actual content types from the interview.

If it cannot adequately store, link, retrieve, automate, export, or migrate required media, consider a hybrid design or reopen the base decision.

## Discover retrieval and analysis support

Verify that the base can support the user's real retrieval scenarios.

If analysis will happen outside the base, define how the knowledge can be extracted reliably without designing the downstream analysis system itself.

## Discover export, backup, and portability

Determine:

- whether content can be exported;
- the export shape;
- whether attachments are included;
- whether important relationships survive export;
- how backup works;
- what an exit path looks like.

When the user asks for backup, distinguish the actual guarantee offered by each route:

- offline snapshot;
- portable export/migration material;
- recoverable reconstruction/disaster recovery.

Do not equate "downloaded successfully" with "restorable". If recovery fidelity matters, determine what must be rebuilt and whether a restore/reconstruction test is possible.

## Separate product capability from current Agent capability

Record separately:

- what the base officially supports;
- what the current Agent environment can actually access now;
- what connection capability is missing;
- what user action or authorization may be needed later.

Do not equate "an interface exists" with "this Agent is already connected".

## Base fitness check

Compare the discovered operating model against the user's requirements.

If it fails a material requirement, reopen the base decision.

Do not force a poor base choice just because it was discussed earlier.

## Output of Base Discovery

Base Discovery should leave the design with:

- a verified operating model;
- a proposed connection route;
- known permissions/authorization requirements;
- known automation limits;
- a clear distinction between what can be done now and what may require later setup.

Actual connection/configuration waits until SPEC approval.
