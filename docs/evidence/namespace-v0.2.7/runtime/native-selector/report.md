# Native Codex selector evidence — observation only

The actual Codex CLI Host `0.160.1`, bundled with the desktop installation, rendered all 12 migrated `Light · …` display labels in its native `$` completion selector. Every stem also had a genuinely rendered corresponding label without the Light prefix. This report supplies A2 Host-selector evidence; it does not issue the final A2 verdict or project acceptance.

## Scope and provenance

Candidate source commit: `ce4898e782f20cb185067fab5721aec6be9b31e4`. Project: `/private/tmp/light-namespace-host-20261006/v027-light-first-default`. All 74 installed payloads were matched to `v027-installation.json` before and after the final capture. Global installed Skills and configuration were not changed. Existing global Skills may contribute additional legacy rows in the selector; the isolated Light and upstream package paths are independently present in the unmodified Host response.

The observation used genuine native `codex --remote <loopback endpoint> --no-alt-screen` output through a **temporary public WebSocket transport adapter**. This was not a direct TUI connection. The adapter added only `ephemeral:true` to the native TUI `thread/start` request. It passed all Host responses and Skill data unchanged. It did not reconstruct or synthesize a selector. The final session `01a10fd5-2f32-7762-be64-c8c800dde952` was ephemeral. No model turn was submitted.

The outer macOS write policy retained exactly two approved global runtime operation/path pairs: `file-write-mode` at `/Users/light/.codex/tmp/arg0`, and `file-write-data` at `/Users/light/.codex/installation_id`. Other global writes were denied. Temporary state/logs were under the already-approved temporary root. HOME and CODEX_HOME stayed inherited. No daemon, persisted chat, global Skill install, configuration write, credential copy, repository edit, commit, push, tag, or release was performed. Authentication content was not read by the harness; only its filesystem stat metadata was compared. Installation metadata buffers and config/global Skill content digests remained in process memory.

## Native observations

Each query was preceded by Esc to close the prior popup, then Ctrl+U to clear the input. The query was typed without Enter. The native selector reopened and rendered the labels. Raw ANSI files are the native process bytes; derived JSON excerpts only remove ANSI escapes for text inspection.

| Query | Native Light label | Native unprefixed label | Raw native capture |
| --- | --- | --- | --- |
| `$code-review` | Light · Code Review | Code Review | `002-dollar-code-review.ansi` |
| `$diagnosing-bugs` | Light · Diagnosing Bugs | Diagnosing Bugs | `004-dollar-diagnosing-bugs.ansi` |
| `$handoff` | Light · Handoff | Handoff | `006-dollar-handoff.ansi` |
| `$implement` | Light · Implement | Implement | `008-dollar-implement.ansi` |
| `$prototype` | Light · Prototype | Prototype | `010-dollar-prototype.ansi` |
| `$research` | Light · Research | Research | `012-dollar-research.ansi` |
| `$tdd` | Light · TDD | TDD | `014-dollar-tdd.ansi` |
| `$teach` | Light · Teach | Teach | `016-dollar-teach.ansi` |
| `$to-questionnaire` | Light · To Questionnaire | To Questionnaire | `018-dollar-to-questionnaire.ansi` |
| `$wait-what` | Light · Wait What | Wait What | `020-dollar-wait-what.ansi` |
| `$wizard` | Light · Wizard | Wizard | `022-dollar-wizard.ansi` |
| `$writing-for-agents` | Light · Writing for Agents | Writing for Agents | `024-dollar-writing-for-agents.ansi` |

## Audit and bounded teardown

`audit-summary.json` confirms 12/12 native Light labels, 12/12 native unprefixed counterpart labels, two `skills/list` responses with identical message ids/SHA-256/byte lengths on both transport sides, exactly one ephemeral `thread/start`, zero upstream `turn/start`, and no reconnect text during the final capture. `transport-audit.jsonl` records each side, id, method, exact message digest, size and shape; full initialize/thread-start/skills-list messages are included. Config/account/history payload contents are not exported. Two native `app/read` queries were rejected by the strict read RPC allowlist; they did not prevent the observed skill selector. They were not converted into permission changes.

`record.json` contains metadata comparisons before bounded teardown and after teardown. Installation content and inode, arg0 mode, global configuration/Skill content, auth stat metadata, and installed payload were unchanged. Runtime metadata restoration was not needed. PTY master was closed before child waits. TUI exited via SIGHUP (`-1`), app-server exited `0`, wrapper exited `0`, `cleanup_pending` is empty, and process inventory confirmed final child PIDs `23438` and `23459` were absent. The temporary adapter listener ended with its Python process. Native-WebSocket close warnings during this intentional teardown are recorded separately from selector behavior.

## Earlier unsuccessful attempts retained

- `native-selector-20261006-135142`: explicit Unix listener exited before socket creation. Metadata/payload checks completed unchanged. The exact EPERM cause was not established; no exception was added.
- `native-selector-20261006-135247`: direct public WebSocket ephemeral start succeeded, but native `resume` failed because Host required a disk rollout: `no rollout found for thread id`. Checks completed unchanged.
- `native-selector-20261006-140148`: native labels appeared, but the transport library default 1 MiB frame limit rejected a genuine 13 MiB Host history response, leading to reconnects. The first wrapper also waited without a bound after KILL while retaining the PTY. It was interrupted to release the PTY; all three processes ended. **Its last metadata content comparison was not completed and remains NOT_VERIFIED** in `cleanup-limitation.json`. The later final checks do not retroactively prove this earlier comparison. This was a temporary wrapper/transport defect, not a Skill source change.

The final capture fixed only the temporary harness: no message size cap, no extra transport keepalive, necessary genuine read-only hooks/app discovery, PTY closure before wait, early in-memory metadata checks, and bounded child/WebSocket waits. No repository or global runtime permission was expanded.

## Reproduction

Temporary harness: `/private/tmp/light-namespace-host-20261006/v027-host/native-selector-prep/probe.py`; keyboard driver: adjacent `control.py`. Requires existing authenticated current Host, installed immutable project payload, and Python `websockets 15.0.1`. The harness uses the approved exact operation/path exceptions and verifies installed source payload before starting. It writes each execution into a new temporary evidence directory. Do not use a modified payload or infer a future Host result from this capture.

Start the harness in an execution environment permitted to run `sandbox-exec`; its command and policy are recorded in `record.json`. Wait for `status.json.phase == "ready"`. Use `control.py ESC 0.4`, then `control.py '$<stem>' 0.8` for each of the 12 table rows. Finally use `control.py STOP 0.4`. Do not send Enter or a model prompt. Verify `record.json` after bounded cleanup.

Official documentation read: [Codex App Server](https://learn.chatgpt.com/docs/app-server) and [Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli). The version-specific schema confirmed `ThreadStartParams.ephemeral` and the `read-only` sandbox enum. Actual Host responses established successful ephemeral creation and actual native display.
