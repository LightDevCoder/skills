# Connection Setup and Validation

Use this only after the SPEC is explicitly approved and the selected base requires a separate connection.

Direct local file/database access may not need this phase.

## Principles

- Configuration follows the approved SPEC.
- Prefer stable programmatic access over GUI-only automation.
- Do not keep platform-specific recipes in this skill.
- Do not ask the user for public links the Agent can research itself.
- Ask for only the minimum private/account-specific information or authorization the Agent cannot obtain.
- Never ask the user to paste secrets into chat, prompts, maintenance documents, example files, or shell command arguments.
- Never place secrets in maintenance documents.
- Never echo secrets back to the user or copy them into example files.
- Never interpolate secrets directly into shell command arguments when the command can read them from an environment file, credential store, stdin, or another safer runtime mechanism.
- Do not print secrets in logs, diagnostics, screenshots, or validation output.
- If a secret is discovered in an example file, log, command history, or other exposed location, remove the exposed copy when safe and tell the user that credential rotation may be necessary.
- Prefer project-scoped setup when available.
- Global Agent/harness configuration requires explicit approval.

## Step 1 — Reconfirm the planned connection

Use the connection route already justified by Base Discovery.

If the route is no longer current or available, stop and re-research instead of silently choosing another architecture.

## Step 2 — Inspect current environment capability

Determine what is actually available now:

- required connector/MCP capability;
- required CLI/tool;
- network access;
- runtime/SDK support;
- credentials/authorization state;
- target workspace/container identity.

Separate "not installed" from "not authorized" and from "unsupported".

## Step 3 — Complete Agent-manageable setup

Within the approved scope, the Agent should actively perform setup it can safely do.

This may include:

- writing project configuration;
- installing project-scoped dependencies when approved;
- configuring a connection;
- preparing an API/SDK client;
- generating import/config files;
- creating required local support files.

Do not change global configuration unless the SPEC explicitly approved it.

## Step 4 — Ask the user only when necessary

Examples of legitimate user actions:

- choose an account/workspace;
- approve OAuth or another authorization screen;
- approve an installation;
- create/approve an application when only the user can do so;
- provide a private/internal endpoint;
- grant permissions.

Do not ask the user to paste a secret into chat. Prefer OAuth/connector-managed authorization when supported. Otherwise tell the user where to place the secret locally (for example an approved environment/config secret location or credential store) so the Agent can use it without displaying or copying its value.

If the current harness has no safe way to consume the credential except through chat, stop that connection path and explain the limitation rather than requesting the secret. Validation should report only whether the credential is configured and usable, not its value.

## Step 5 — Validate the connection

A connection is not valid just because setup files exist.

Validate the actual operations the knowledge base requires.

At minimum, when applicable:

1. identify the intended target;
2. read from it;
3. perform a safe write/create;
4. read back the result;
5. update if the system requires updates;
6. search if retrieval depends on search;
7. handle an attachment if attachments are required.

Prefer a real initialization object that belongs to the approved design over disposable test clutter.

If a temporary test object is needed, clean it up only when deletion is safe and approved.

## Step 6 — Handle failure gracefully

If setup or validation fails:

- preserve completed base-independent work;
- report the exact failed step;
- distinguish permission, connectivity, missing tool, and unsupported operation;
- prepare the remaining config/scripts/instructions when useful;
- state the exact user action or capability needed to continue;
- do not claim the knowledge base is connected.

## Step 7 — Record reconnection guidance

The maintenance material must explain how a future Agent session reconnects without embedding secrets.

Record:

- connection mechanism;
- required non-secret identifiers;
- required permission scope;
- where project configuration lives;
- how to verify the connection.
