# Scenario H — Fresh Identity Without Avatar

Deterministic contract fixture for the first-registration identity rule: a
new agent id with a name but no avatar must not touch the board, and the
same identity must succeed once a legal avatar is provided.

## Setup

- Board reachable at `http://127.0.0.1:8641`.
- Fresh database: `GET /api/agents` does not contain `codex-main`.

## Sequence

1. Wake with `Agent ID: codex-main`, `Agent Name: Codex`, and no avatar
   value.
2. The worker reports identity configuration missing: a new agent id needs
   `name` and `avatar` for first registration.
3. No task claimed, no task mutated — the run ends.
4. Next wake provides a legal avatar:
   `Agent Avatar: /path/to/codex-icon.png`.
5. Registration succeeds: upload the local image with
   `POST /api/avatars` (multipart/form-data, field `file`) and use the
   returned `/api/avatars/...` path, then claim succeeds.

## Verification boundary

This fixture verifies the identity contract of the worker only. It does not
exercise the Light-Kanban avatar storage or a live claim transaction; those
paths are covered by the server-side integration evidence.
