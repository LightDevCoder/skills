# A8/A9 — isolated installation and Codex Host observation

Date: 2026-10-06 (Asia/Taipei). This record reports observations only; `project-review` owns the candidate verdict. Local candidate installation is distinct from released-source installation (R4).

## Scope and tools

- Temporary validation root: `/private/tmp/light-namespace-host-20261006`.
- Candidate input: complete 36-package snapshot under `candidate-snapshot/skills`, copied from the authorized repository working tree. Source was being finalized by the Producer; final package reconciliation is still pending.
- Fixed upstream checkout: `/private/tmp/light-namespace-upstream-20261006`, Git HEAD `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d`.
- Actual Skills CLI: `1.7.0`, executed from existing `/private/tmp/npm-cache/_npx/ac0ed6aa23b37c1e/node_modules/skills/dist/cli.mjs` after inspecting help and package version. CLI SHA-256: `fde68534019765fb69510a0038ca7df2810a6ffed4c26fef9beabdcf6cc6701c`.
- Actual Codex CLI: `0.160.0`, `/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex`.
- `HOME` and `CODEX_HOME` were not reset. No real user global Skills or Host configuration was modified. No commits, push, publication, or setup was attempted by the smoke projects.
- Installer telemetry disabled with `DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`.

## A8 installation observations

Both installation orders were run in fresh project directories, first with Codex alone, then with an additional project-local `claude-code` target to observe actual symlink identity. Every command exited `0` (16 commands total). Each installation retained Light's 36 packages / 367 intended files and fixed upstream's 38 packages / 103 intended files. Every complete package matched the respective snapshot byte-for-byte after excluding generated `__pycache__`, `.pyc` and Finder metadata. The initial raw comparison recorded the installer correctly excluding nine generated ask-light Python cache files; no intended source file was excluded.

| Order | CLI mode | Codex `.agents/skills` | Additional `.claude/skills` target | Complete content |
| --- | --- | --- | --- | --- |
| Light → upstream | default | 74 canonical directories | 74 symlinks to canonical directories | 74/74 exact |
| upstream → Light | default | 74 canonical directories | 74 symlinks to canonical directories | 74/74 exact |
| Light → upstream | `--copy` | 74 independent directories | 74 independent directories | 74/74 exact |
| upstream → Light | `--copy` | 74 independent directories | 74 independent directories | 74/74 exact |

CLI 1.7.0 defines Codex's project destination as the canonical `.agents/skills` root itself. Thus its default mode outputs `copy → Codex`; it does not create a self-symlink. The additional Claude directory tests actual default symlink behavior without claiming Claude runtime support.

Commands used per source, from each fresh project directory:

```bash
node /private/tmp/npm-cache/_npx/ac0ed6aa23b37c1e/node_modules/skills/dist/cli.mjs add <source> --skill '*' --agent codex --yes
node /private/tmp/npm-cache/_npx/ac0ed6aa23b37c1e/node_modules/skills/dist/cli.mjs add <source> --skill '*' --agent codex --yes --copy
node /private/tmp/npm-cache/_npx/ac0ed6aa23b37c1e/node_modules/skills/dist/cli.mjs add <source> --skill '*' --agent codex claude-code --yes
node /private/tmp/npm-cache/_npx/ac0ed6aa23b37c1e/node_modules/skills/dist/cli.mjs add <source> --skill '*' --agent codex claude-code --yes --copy
```

`<source>` was the complete candidate snapshot or the fixed upstream local checkout. Per-command arguments, exit codes and raw installer logs are in `install-commands.json` and `logs/*-linktarget-*.log`. Per-package source, file count, hashes, symlink state and resolved paths are in `expected-packages.json` and `install-content-checks.json` under the temporary root.

Initial normalized Light package manifest digest (canonical JSON, sorted names/paths, compact separators): `38f9e43531cf14d9c0169507ac3846cf53fc9c8d61056afabef2a57d2ec8c09b`. Final candidate reconciliation remains pending; the initial file delta was preserved in `candidate-delta.json`.

## A9 real Host attempts — not tested / blocked at initialization

Two explicit safe-task prompts were prepared in installed disposable Git projects:

- `$light-implement`: fix a bounded Python `non_negative` bug using installed `light-tdd`, then hand to `review-loop` using `light-code-review`. Global writes, setup, commits and publication were forbidden.
- `$implement`: use the fixed upstream installed entry for a one-line document state change; global writes, setup, commits and publication were forbidden.

Observed attempts:

1. Actual `codex exec --ephemeral --sandbox workspace-write --skip-git-repo-check -C <installed-project> --json -` exited `1` before a model turn. stderr recorded an attempted readonly global logs database maintenance (write was denied), then `failed to initialize in-process app-server client: Operation not permitted (os error 1)`.
2. Retried the Light explicit prompt through normal escalation with an additional macOS sandbox that denied all file writes except this temporary validation root. Used `--ephemeral --ignore-user-config --disable shell_snapshot`, `history.persistence="none"`, `sqlite_home=<temporary>/sqlite`, `log_dir=<temporary>/codex-logs`, and a temporary `TMPDIR`. Exit `1`; the same in-process initialization error occurred. Temporary SQLite databases were created at the specified location, confirming that state storage was isolated.
3. Ran the upstream explicit prompt with the same isolated runtime configuration. Exit `1`; the same initialization error occurred.
4. Generated the CLI's app-server schema and attempted documented stdio `initialize` followed by `skills/list` with `cwds=[<installed-project>]`, `forceReload=true`. The server exited `1` before replying to initialize; stderr `Operation not permitted`. No discovery result was obtained.
5. The additional write-restricting macOS sandbox successfully executed `/usr/bin/true` (exit `0`), so that policy itself could initialize. A read-only macOS deny-log query supplied no more specific Codex denial path.
6. Retried with inherited desktop task IPC and task-identity variables removed from only the child-process environment, while retaining all sandbox/permission variables, `HOME` and `CODEX_HOME`. The same initialization error remained (exit `1`); `host-light-standalone-command.json` and `logs/host-light-standalone-isolated.stderr` preserve this diagnostic.

The runtime did not reach model execution or Skill contract reads. Therefore this record does **not** establish actual Host discovery, explicit source selection, `light-implement` execution, or Light dependency reads. A9 remains `not tested`; the required runtime evidence is blocked. Static metadata and successful installer output do not repair that gap.

Exact CLI arguments and environment-isolation checks: `host-light-command.json`, `host-upstream-command.json`, `appserver-command.json`. Safe prompts: `host-light-prompt.txt`, `host-upstream-prompt.txt`. Raw attempts: `logs/host-light.stderr`, `logs/host-light-isolated.stderr`, `logs/host-upstream-isolated.stderr`, `logs/appserver.stderr`; JSONL files are empty because startup failed before event delivery. No approval-review rejection occurred; commands were approved but runtime initialization failed.

## Documentation and limitations

Official Codex Skills documentation was actually fetched to `openai-skills-doc.html`; it describes repository `.agents/skills` discovery and notes that duplicate names are not merged. Official config reference was fetched to `openai-config-doc.html`; it describes `history.persistence` and supports the temporary `sqlite_home` / `log_dir` settings also observed in the local binary. Sources: [Codex Skills](https://developers.openai.com/codex/skills/), [Codex config reference](https://developers.openai.com/codex/config-reference/).

Initial npm resolution under the ordinary sandbox failed with DNS `ENOTFOUND`. An approved registry connectivity check succeeded. Instead of relying on unpinned `npx` resolution, actual installation used the existing fixed CLI 1.7.0 distribution above. This is a local CLI validation, not a verified public release installation command.

This evidence does not cover R4, real global migration, Claude runtime, other Hosts, or global automatic-invocation exclusivity.

## Final frozen-candidate A8 reconciliation

The Producer froze the final implementation at commit `da7a8e9d33db5bea7bab85ef94f1fc4711e1b45b`. A new complete snapshot was extracted from `git archive` of that exact commit to `/private/tmp/light-namespace-host-20261006/candidate-final`; it therefore contains committed package files rather than mutable working-tree files or generated caches. Git HEAD was rechecked after installation and remained the same. The upstream checkout HEAD remained `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d`, with a clean working tree.

Four additional fresh projects were installed with actual CLI 1.7.0. Eight actual installation commands exited `0`, using the same source/agent flags as the earlier link-target matrix; default mode omitted `--copy`, and copy mode included it. All projects retained Light 36 packages / 367 files and fixed upstream 38 packages / 103 files. At each agent destination every one of the 74 packages / 470 files matched the appropriate complete source package byte-for-byte. All 12 new Light names and their upstream unprefixed counterparts remained distinct because the checks covered the complete package-name set and every file's source hash.

| Final project | Codex identity and contents | Additional target identity and contents |
| --- | --- | --- |
| `final-light-first-default` | 74 canonical directories; 74/74 exact | 74 symlinks to correct canonical package; 74/74 exact |
| `final-upstream-first-default` | 74 canonical directories; 74/74 exact | 74 symlinks to correct canonical package; 74/74 exact |
| `final-light-first-copy` | 74 independent directories; 74/74 exact | 74 independent directories; 74/74 exact |
| `final-upstream-first-copy` | 74 independent directories; 74/74 exact | 74 independent directories; 74/74 exact |

Final Light package manifest SHA-256: `95cfe696c090067aa5ada472cf05d3f7da5f4227a5a54dc7a3d00f3fa8f1603e`. Digest construction is SHA-256 of UTF-8 JSON mapping canonical package name to the map of relative file path → file SHA-256, with sorted keys and compact `(',', ':')` separators. The final candidate has 36 packages / 367 package files. This resolves the earlier pending candidate reconciliation without altering the initial snapshot observations.

All final commands, exit codes, per-package hashes, source paths, symlink identities and resolved targets are preserved in `/private/tmp/light-namespace-host-20261006/final-installation.json`; raw CLI logs are `logs/final-*.log`. The initial-to-final package delta is preserved in `final-versus-initial.json`. Initial snapshots and logs remain available, so the earlier mutable-candidate facts were not overwritten.

A8's final local installation and source/identity checks are satisfied for the exact frozen implementation commit. A9 remains `not tested / BLOCKED` with the previously recorded initialization failures. No further Host retries or permission widening were performed. R4 remains a separate released-source verification gate.

## Post-review frozen-candidate A8 reconciliation

Independent review identified remaining current capability tokens; the Producer supplied a new frozen implementation commit `79d15fd410f1295f84d9761d66c601895ff9ee31`. This section records a new installation run and preserves all preceding `da7a8e9` results as historical facts.

The complete new source snapshot was extracted directly from `git archive` of that exact commit to `/private/tmp/light-namespace-host-20261006/candidate-review2`. The Light payload remains 36 packages / 367 files. Its package manifest SHA-256, calculated with the same canonical JSON method above, is `fe58ea6e7af0e7ffa4b52fc484c9b78cdbffc6e8c22cf1a28b0596779c191041`. HEAD was rechecked after installation and remained the same. Fixed upstream HEAD remains `4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d`; its working tree is clean.

Actual Skills CLI 1.7.0 was rerun in four fresh `review2-<order>-<mode>` projects. Eight installation commands exited `0`. Both installation orders retained all Light and fixed upstream packages. Every agent destination contained 74/74 packages and 470/470 intended files exactly matching their complete source packages.

| New candidate matrix | Codex `.agents/skills` | Additional `.claude/skills` target |
| --- | --- | --- |
| Light → upstream, default | 74 canonical directories; 74/74 exact | 74 correct symlinks; 74/74 exact |
| upstream → Light, default | 74 canonical directories; 74/74 exact | 74 correct symlinks; 74/74 exact |
| Light → upstream, copy | 74 independent directories; 74/74 exact | 74 independent directories; 74/74 exact |
| upstream → Light, copy | 74 independent directories; 74/74 exact | 74 independent directories; 74/74 exact |

New exact commands, exit codes, complete package file hashes, source identity and link targets are in `/private/tmp/light-namespace-host-20261006/review2-installation.json`, with raw `logs/review2-*.log`. The prior `final-installation.json`, snapshot and logs remain unchanged. A8's local installation checks are satisfied for the newer frozen commit. A9 remains `not tested / BLOCKED`; no further Host attempt or permission widening occurred.
