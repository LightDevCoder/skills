# Producer Evidence — language-learning fast-track

This is Producer evidence, not final acceptance. Evidence labels follow the
review-loop [Evidence Protocol](../../../../../skills/review-loop/references/evidence-protocol.md).

## Scope
- Charter revision: 1
- Profile: agent-skill
- Target: `skills/language-learning/` at commit `215c65ccbfd323c3f43265c45ddcbae5962b7818`
- In-scope work: package structure, installation/discovery, invocation, and behavior evidence for the prompt-only fast track
- Out-of-scope check: no new modes, no runtime executables, no external dependencies added

## Evidence

### E-001 — Structural: package tree, metadata, links, contract tests, collection discovery
- Evidence label: structural
- Run or observation: from the repository root `pwsh -NoProfile -File skills/language-learning/tests/language-learning-contract-tests.ps1` and `pwsh -NoProfile -File tests/collection-discovery-tests.ps1`
- Expected: 33 non-zero contract assertions PASS; collection discovery assertions PASS across all seven packages; every relative Markdown link in the repo resolves
- Observed: `LANGUAGE_LEARNING_CONTRACT=33 PASS`; `COLLECTION_DISCOVERY=931 PASS` (includes recap 12 + 8, language-learning 33, and the main collection script 878); `RECAP_CONTRACT=PASS`, `RECAP_OUTPUT_CONTRACT=PASS`. Note: an earlier draft of this record listed 929; the independent Evaluator found the drift (2 assertions), the suite was re-run at the frozen commit, and 931 is the accurate current count.
- Outcome: PASS
- Validates: AC-1, AC-2, AC-6, AC-7
- Environment: Windows 11 Pro 10.0.26300, PowerShell 7.6.4, Git Bash, repo at commit 215c65c
- Artifact: output above; package tree = 9 files (SKILL.md, agents/openai.yaml, 6 references, 1 contract test)

### E-002 — Installation: isolated fresh-copy and host install
- Evidence label: installation
- Run or observation: copied `skills/language-learning` to an isolated temp destination (`/tmp/tmp.F9kuJSxbAF/installed-language-learning`) and to the host-recognized root `C:\Users\Service01\.claude\skills\language-learning`; compared file sets and SHA-256 per file; ran the installed contract test from each copy
- Expected: destination contains only the `language-learning` package; file set matches the source exactly; zero SHA-256 mismatches; no `.git`/source-checkout residue; installed contract test passes
- Observed: isolated copy file set = 9 files, identical; zero SHA-256 mismatches; 0 source-checkout hits; installed copy contract test `LANGUAGE_LEARNING_CONTRACT=33 PASS`. Host install is byte-identical to the repository (verified via `cmp`, same SHA-256) and its contract test passes 33 assertions; it is discovered in the host skills root alongside `review-loop`.
- Outcome: PASS
- Validates: AC-5
- Environment: same as E-001; destination hosts: `/tmp/...` (isolated) and `C:\Users\Service01\.claude\skills\` (host)
- Artifact: `ls` of both destinations; per-file SHA-256 comparison output

### E-003 — Behavioral: explicit-use success routes to a declared mode without re-asking
- Evidence label: behavioral
- Run or observation: a fresh independent subagent read the installed skill and handled the explicit invocation `$language-learning Spanish, level intermediate. Make flashcards for: perro, gato, casa`
- Expected: routes to Flashcards; does not re-ask for target language, level, or mode (the Start contract); produces one card per given item with target/definition/usage/memory tip and no dropped items
- Observed: routed to Flashcards; `NO` re-asking for language/level/mode (native language English inferred as obvious, per contract); three cards produced — `perro`, `gato`, `casa` — each with all four fields and a usage gloss; pronunciation note added only for `perro` (trilled rr), skipped where spelling is clear; agent reported no contract deviations
- Outcome: PASS
- Validates: AC-3, AC-4
- Environment: fresh read-only subagent; no files modified
- Artifact: agent report (agentId a33337c93e3769632)

### E-004 — Behavioral: unknown level defaults to beginner
- Evidence label: behavioral
- Run or observation: a second fresh subagent read the installed skill and handled `$language-learning Create a daily lesson on the preterite tense.` with no level stated
- Expected: routes to Daily Lesson; defaults the level to beginner per the Start contract; does not ask for the level or the mode; produces a complete lesson (objective, explanation, examples, exercises, quiz) with the 10/10/5/5 split as a guideline
- Observed: routed to Daily Lesson; level defaulted to beginner; `No` asking for level or mode; complete preterite lesson produced with objective, warm-up/core/practice/quiz arc, a 3-question quiz with answers gated per-attempt, a takeaway close, and a tomorrow-review item; the agent assumed Spanish from conversation context per the skill's own example and permitted inference
- Outcome: PASS
- Validates: AC-3, AC-4
- Environment: fresh read-only subagent; no files modified
- Artifact: agent report (agentId a0781f7237672017d)

### E-005 — Invocation: non-trigger does not invoke the Skill
- Evidence label: invocation
- Run or observation: a third fresh subagent received only `Can you proofread this paragraph for grammar mistakes?` with no explicit `$language-learning` invocation
- Expected: the Skill is NOT invoked (its `disable-model-invocation: true` metadata and user-invoked-only boundary); the request is handled directly as plain proofreading
- Observed: `NO / NOT_INVOKED`; the subagent confirmed `disable-model-invocation: true` on SKILL.md and handled the request as ordinary proofreading without adopting the skill's tutor structure
- Outcome: PASS
- Validates: AC-8
- Environment: fresh read-only subagent; no files modified
- Artifact: agent report (agentId a9810f3829ae2ecf3)

### E-006 — Invocation: no automatic invocation of another user-invoked Skill
- Evidence label: invocation
- Run or observation: inspection of SKILL.md and all six references for any instruction to call, run, or chain another user-invoked Skill
- Expected: the package only recommends other capabilities (e.g. `handoff`, `review-loop`) as explicit user choices and never executes them; the Choose-a-mode table routes only to the package's own references
- Observed: `SKILL.md` route table links only to `references/` files inside the package; no other Skill is invoked or loaded; no script or tool call exists anywhere in the package
- Outcome: PASS
- Validates: AC-8
- Environment: structural inspection of the package at 215c65c
- Artifact: package tree and route table

## Post-Evaluator correction
The independent Evaluator (agentId a1b3b6795fb7a4ab8) returned `PASS` and
identified one Low-severity evidence-accuracy observation: E-001 recorded the
collection-discovery assertion count as 929 instead of the actual 931. That
observation is resolved above by re-running the suite at the frozen commit and
recording the accurate count. No other finding was raised; no escalation is
required.

## Summary
Six evidence items, each with a single primary label, all `PASS`. No blocking
finding is asserted here; that judgment is the independent Evaluator's and the
Core's, not the Producer's.
