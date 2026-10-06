# Real Codex Host observations after bounded runtime authorization

- Package source: ce4898e782f20cb185067fab5721aec6be9b31e4; 36 Light packages / 386 files.
- Fixed comparison source: 4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d; 38 packages / 103 files.
- Actual model and native UI Host: codex-cli 0.160.1; executable digest in host-version.json. The desktop installation advanced from the earlier 0.160.0 without this task installing or updating it.
- User authorization on 2026-10-06: “批准这两项例外并继续验证”. Only file-write-mode at ~/.codex/tmp/arg0 and file-write-data at existing ~/.codex/installation_id were added to the extra OS write policy; no configuration/Skills/auth or other global writes were permitted.

## Initialization and actual calls

The identical candidate installation initialized and returned 74 project Skills after the two exact exceptions. The installation ID content/inode and arg0 mode matched before/after. Other denied cache/alias/maintenance operations stayed denied and were nonfatal. The earlier startup failures were therefore limitations of the extra validation policy, not evidence of a namespace implementation defect. This control does not prove every individual denied operation was causal.

A first ephemeral workspace-write call reached a model turn but its read commands failed at nested sandbox_apply. The next call retained the same enforced outer OS policy and used danger-full-access only for the redundant inner model sandbox. An independent outside-root nonsecret canary write was actually denied with contents unchanged (outer-sandbox-boundary-control.json). This does not enlarge actual OS write scope. HOME/CODEX_HOME remained inherited, no daemon or persisted model session was created, and state/logs remained temporary.

The explicit $light-implement call actually read installed light-implement, light-tdd, review-loop and light-code-review entries and supporting references. It completed a bounded non_negative function task: negative input first failed then passed; zero and positive cases passed; three public-interface tests passed. The temporary work item had no Git baseline; the review handoff correctly returned REVIEW-ERROR rather than pretending independent review passed. It read the upstream implement only to distinguish source, not as its executor.

The explicit $implement call read the corresponding upstream implement/tdd/code-review contracts and changed only its temporary smoke.md from pending to observed with exact bytes verified. Light's implement entry was read only for source discrimination. Both model runs exited zero. The parent independently verified all behavior results, successful read command paths, red/green outputs, all 74 package payloads at both installed targets, and completed metadata comparisons. Actual invocation is separate from final source/project acceptance.

## Genuine native selector

The final native CLI TUI capture rendered 12/12 complete Light · labels and their unprefixed counterpart labels. It used a temporary public WebSocket transport adapter which added only ephemeral:true to thread/start; all Host Skill responses passed byte-identically, backed by matching dual-side ids/digests/sizes. No model turn was submitted through this UI. The adapter does not synthesize or repaint the selector. Native ANSI captures, key sequences, observations and digest audit are under native-selector/. The parent independently checked all twelve raw labels. Raw unrelated Host history/account/config payloads remain unpublished.

The final wrapper performed in-memory metadata comparison before and after bounded teardown; config/global Skills, auth filesystem stat and the installed package payload were unchanged. Both child processes ended, with no pending cleanup. Earlier failed Unix/resume attempts are retained in the temporary root. One earlier wrapper cleanup interruption lacks its final metadata-content comparison and remains explicitly NOT_VERIFIED; final checks do not retroactively validate that earlier comparison. Only the final completed round supports the UI outcome and complete comparison claims.

## Remaining release stages

Fresh independent final evaluation is required for the new evidence. Exact candidate CI, protected public tag, actual released-source installations, Release and post-publication receipt are not yet completed. A manual Linux runner verification entry will exercise fixed/default whole collections, representative singles and native Codex global installation without resetting HOME/CODEX_HOME or touching this user's global installations.

## Comparison-source notice

The unmodified contract excerpts in actual read-command output come from mattpocock/skills at 4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d. They are runtime evidence rather than admitted packages or runtime dependencies. [Original MIT notice](COMPARISON_SOURCE_LICENSE.txt) is preserved; no original authorship is claimed.
