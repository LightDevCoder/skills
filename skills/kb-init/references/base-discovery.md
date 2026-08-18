# Base Discovery

Base Discovery happens only after the interview has produced a selected or strongly preferred base.

The purpose is to turn "we want to use X" into an operational understanding of how an Agent can actually build and maintain the knowledge base on X.

Do not maintain a catalog of platform recipes in this skill.

Research the selected base as needed.

## What to discover

Build an internal operating profile covering the following.

### Storage model

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

### Programmatic access

Determine the supported non-GUI ways an Agent can interact with it.

Possible categories may include:

- direct filesystem access;
- command-line interfaces;
- application programming interfaces;
- SDKs;
- MCP or connector-style interfaces;
- import/export formats;
- other documented automation surfaces.

Do not assume any category exists.

Do not prefer one merely because this skill has seen it before.

### Authentication and permissions

Determine:

- what credentials or authorization are required;
- whether the user must create an application, token, workspace permission, or similar grant;
- which permissions are necessary;
- whether least-privilege access is possible;
- what a future Agent session needs in order to reconnect.

Never ask the user to paste secrets into maintenance documentation.

### Read/write capability

Determine whether an Agent can:

- list or browse;
- search;
- read;
- create;
- update;
- move or reorganize;
- delete;
- upload or link attachments;
- create relationships;
- create fields or schemas;
- manage views or navigation;
- export or back up.

Identify important missing operations.

### Attachments and non-text content

Determine how the chosen base handles the content types found during the interview.

Pay special attention to:

- large files;
- images;
- audio/video;
- linked external media;
- binary attachments;
- generated artifacts.

If the base cannot adequately store or automate these, consider a hybrid design or reopen the base decision.

### Retrieval and analysis

Verify that the base can support the user's real retrieval scenarios.

If analysis will happen outside the base, define how data is extracted reliably.

If the base's native search is weak, do not pretend it satisfies the user's query needs.

### Export, backup, and portability

Determine:

- whether content can be exported;
- what export format is available;
- whether attachments are included;
- whether the structure survives export;
- how backups can be made;
- what an exit path looks like.

### Current Agent environment

Separate the base's theoretical capabilities from the current Agent environment.

Record:

- what the base supports;
- what the current environment can actually access now;
- which connectors, CLIs, credentials, or network permissions are present;
- what is missing.

Do not equate "the product supports an API" with "this Agent is currently connected to it".

## Research rule

Use `research` when any material part of the operating profile is unfamiliar, current, or unverified.

Research should prioritize first-party documentation and official interfaces.

A useful research brief is narrow and operational:

> Research the currently supported programmatic ways an Agent can read, create, update, search, attach files to, export from, and authenticate with <selected base>. Prefer official documentation. Report which operations require user setup or authorization and which can be automated without GUI interaction.

Do not research every feature of the product.

Research only what affects the knowledge-base implementation.

## No computer-use dependency

The preferred route is a stable non-GUI route.

Computer use may supplement the implementation, but do not make it the sole planned route unless:

1. no programmatic or import/export route can satisfy the requirement; and
2. the user explicitly accepts that dependency.

If the current Agent lacks the required connector or programmatic access:

- complete all base-independent work;
- prepare the knowledge structure;
- prepare schemas or field definitions;
- prepare importable content;
- prepare scripts or configuration where useful;
- prepare exact setup and authorization instructions;
- document the remaining manual step;
- make future continuation straightforward.

The goal is graceful partial completion, not an all-or-nothing outcome.

## Base fitness check

After Base Discovery, compare the operating profile against the user's requirements.

Ask:

- Does it store the required content types?
- Does it support the required retrieval and analysis?
- Can the Agent maintain it at the desired autonomy level?
- Are the required permissions acceptable?
- Is the manual remainder acceptable?
- Is backup/export acceptable?
- Does it meet the user's collaboration, privacy, cost, and scale constraints?

If not, reopen the base decision.

Do not force a poor base choice merely because the interview selected it earlier.

## Output to the SPEC

The final SPEC should summarize Base Discovery as practical operating decisions, not as a research dump.

It should make clear:

- why the base is suitable;
- how the Agent connects;
- what the Agent can automate;
- what the user must do;
- what limitations remain;
- how another Agent session reconnects and continues maintenance.
