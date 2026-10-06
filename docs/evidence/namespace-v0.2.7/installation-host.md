# v0.2.7 isolated installation and Host observations

Candidate: `ce4898e782f20cb185067fab5721aec6be9b31e4`. Fixed upstream: `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d`. Local candidate evidence is separate from released-source verification R4. No repository, global Skills/config, other projects, credentials, HOME or CODEX_HOME were changed.

## A8 real installation

Skills CLI 1.7.0, CLI SHA-256 `fde68534019765fb69510a0038ca7df2810a6ffed4c26fef9beabdcf6cc6701c`. The complete candidate was extracted by `git archive` of the exact commit, then installed in four new project directories. Both source orders were tested with default and `--copy` modes. All eight actual installation commands exited 0.

Every one of eight agent destinations retained all 74 packages / 489 files with complete source hashes. Light has 36 packages / 386 files; upstream has 38 / 103. Default Codex destinations are canonical directories; all 74 default Claude target symlinks resolve to their exact canonical package. Copy mode uses independent directories for both targets. Claude runtime was not exercised. Light's complete manifest digest is `5a682a3356a501a1285735560ef2261d7bc81cf6c18c31292c54e44ef167926b` (SHA-256 of sorted compact JSON name → relative file → file SHA-256).

Evidence: `v027-installation.json`, raw `logs/v027-*.log`, and `v027-installation-check.py`. The script records exact commands, sources, file maps, symlink text and resolutions, verifies revision/source cleanliness, and refuses to overwrite prior fresh-project evidence. Actual count 386 supersedes the initial expected 385; compared with the previous 367-file snapshot, light-travelpage has 19 added files including `scripts/tests/local-wrangler.mjs`.

## A2/A9 Host gap

Prior Codex 0.160.0 attempts (explicit exec, debug prompt input, stdio app-server and daemon/code-mode variants) failed with `Operation not permitted` before initialize, discovery or model execution. Doctor established auth/config readability, desktop handshake and provider WebSocket readiness; these are not Skill-discovery success.

New read-only checks found no default app-server control socket. The actual desktop app-server process exposes anonymous sockets and uses default stdio, with no listen argument. The other Codex process uses a cloud --remote endpoint. Therefore there is no observed official local Unix/WebSocket listener to reuse for skills/list. No private pipe was probed, no daemon was started, and no failed Host attempt was repeated. The OS-error root cause remains unestablished.

A2's selector observation and A9's simultaneous discovery, Light/upstream explicit calls, and Light dependency reads remain unobserved. Metadata and successful A8 do not satisfy these Host requirements. This is an evidence report, not the project-review verdict.

## Minimal next environment action

Run in macOS Terminal outside this nested agent session:

```bash
python3 /private/tmp/light-namespace-host-20261006/v027-host/observe-external.py
```

This prepared observer runs only initialize and skills/list against the installed candidate project. It preserves HOME/CODEX_HOME, isolates state/logs in a new temporary directory, disables daemon auto-start, denies file writes outside the temporary evidence root, and creates no thread/turn. It prints only an output path and success/count/error summary. It has been syntax-checked using ast.parse without cache writes, not externally executed. It rehashes the installed source before starting Codex. skills/list interface/path fields are discovery and selector-input data; they do not replace observing the UI selector. If it initializes successfully, actual selector and ephemeral explicit-call/dependency observation still need completion; if it fails, its exact external error narrows the environment block.

Official OpenAI documentation actually opened: [App Server](https://learn.chatgpt.com/docs/app-server) and [Build skills](https://learn.chatgpt.com/docs/build-skills). The App Server contract documents default stdio, optional Unix/WebSocket listeners, initialize-before-other-RPC, skills/list, and explicit Skill input. Diagnostic details are in `v027-host/diagnosis.json`; existing raw errors remain unchanged.
