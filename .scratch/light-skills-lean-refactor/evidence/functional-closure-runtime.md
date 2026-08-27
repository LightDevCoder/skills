# Functional closure runtime and review evidence

Date: 2026-08-26
Candidate: current working-tree diff from `HEAD`
Release status: unreleased; this record is not published-install proof

## Isolated copy and discovery

Environment: macOS, Python 3, temporary roots under `/tmp`; complete packages
were copied from the candidate into a host root outside the source checkout.

Observed evidence:

- The isolated root contained 33 complete packages with `SKILL.md`.
- The isolated `ask-light` runtime routed `Explain this like I am five` to
  `eli5` as `$eli5`, reading 33 metadata files, one body, and zero references.
- After the review repairs, the isolated runtime routed `The ticket is ready
  and unblocked` to `implement` as `$implement`, reading 33 metadata files, one
  body, and two references.
- `taskKind=debugging` with an empty goal routed to `diagnosing-bugs`; Claude
  Code presentation was `/diagnosing-bugs`.
- The isolated `project-init` runtime bootstrapped an empty repository into
  `AGENTS.md`, `docs/agents/light-project.md`, and
  `docs/agents/issue-tracker.md`; an identical second run reported all three
  paths as `preserved`.

Exact isolated-copy setup and discovery commands:

```bash
mkdir -p /tmp/light-functional-install.xx5emf/host/skills /tmp/light-functional-install.xx5emf/project
cp -R skills/. /tmp/light-functional-install.xx5emf/host/skills/
find /tmp/light-functional-install.xx5emf/host/skills -mindepth 2 -maxdepth 2 -name SKILL.md -print | wc -l
python3 /tmp/light-functional-install.xx5emf/host/skills/ask-light/scripts/ask_light.py \
  --roots-json '[{"category":"first-party","path":"/tmp/light-functional-install.xx5emf/host/skills"}]' \
  --context-json '{"goal":"The ticket is ready and unblocked","artifacts":[],"blockers":"","projectType":"software","taskKind":"","availability":{"host":"codex","readablePaths":["/tmp/light-functional-install.xx5emf/host/skills"]},"invocationControl":"explicit-only"}' \
  --host-name codex --mode next | \
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["status"], d["skill"], d["invocation"], d["reads"])'
```

Preserved output excerpt:

```text
      33
RECOMMEND implement $implement {'metadata': 33, 'bodies': 1, 'references': 2}
```

Exact fallback bootstrap command (run twice with the same JSON):

```bash
python3 /tmp/light-functional-install.xx5emf/host/skills/project-init/scripts/bootstrap.py \
  --project-root /tmp/light-functional-install.xx5emf/project-fallback \
  --config-json '{"projectType":"custom","goal":"Validate an unusual workflow","outputs":["validated plan"],"preset":"research-fallback","relevantSkills":["research","project-review"],"issueTracker":{"kind":"local-markdown","path":".scratch/<effort>/issues"},"domainContext":[],"reviewProfile":"generic","acceptanceStrategy":"source-backed review","workingArea":".scratch","collaboration":"solo","constraints":[],"instructionFile":"AGENTS.md","sources":["official-api.md","project-brief.md"],"confirmation":"user confirmed on 2026-08-26","validation":"source and path checks passed"}'
```

Preserved first/second output:

```text
first:  docs/agents/light-project.md=created; docs/agents/issue-tracker.md=created; AGENTS.md=created; conflicts=[]
second: docs/agents/light-project.md=preserved; docs/agents/issue-tracker.md=preserved; AGENTS.md=preserved; conflicts=[]
```

The generated contract contains:

```text
- Sources: official-api.md, project-brief.md
- Confirmation: user confirmed on 2026-08-26
- Validation: source and path checks passed
```

This is a pre-release isolated-copy check. It proves candidate discovery and
runtime behavior without the source checkout; it does not verify a published
installer command or release tag.

## Actual Codex invocation sequence

Host: `codex-cli 0.150.0-alpha.8`, isolated `CODEX_HOME`, copied `clarify` and
`socratic` packages, `gpt-5.6-sol` with high reasoning. Thread:
`01a03c92-d97a-7122-9e4b-9d3137bc942c`.

Exact setup and invocation commands:

```bash
mkdir -p /tmp/light-functional-closure-runtime.WVVQwl/home/skills /tmp/light-functional-closure-runtime.WVVQwl/project
ln -s /Users/light/.codex/auth.json /tmp/light-functional-closure-runtime.WVVQwl/home/auth.json
cp -R skills/clarify /tmp/light-functional-closure-runtime.WVVQwl/home/skills/clarify
cp -R skills/socratic /tmp/light-functional-closure-runtime.WVVQwl/home/skills/socratic
git -C /tmp/light-functional-closure-runtime.WVVQwl/project init -q
CODEX_HOME=/tmp/light-functional-closure-runtime.WVVQwl/home codex exec \
  -C /tmp/light-functional-closure-runtime.WVVQwl/project --skip-git-repo-check \
  --ignore-user-config -m gpt-5.6-sol -c 'model_reasoning_effort="high"' --json \
  '$clarify I need to choose whether a small internal tool should start as a CLI or web app. I care most about shipping a useful first version quickly.'
CODEX_HOME=/tmp/light-functional-closure-runtime.WVVQwl/home codex exec resume \
  --ignore-user-config -m gpt-5.6-sol -c 'model_reasoning_effort="high"' --json \
  01a03c92-d97a-7122-9e4b-9d3137bc942c \
  'The first users are three engineers on macOS, all comfortable with the terminal. Version one only needs to convert a local folder and print a clear report.'
CODEX_HOME=/tmp/light-functional-closure-runtime.WVVQwl/home codex exec resume \
  --ignore-user-config -m gpt-5.6-sol -c 'model_reasoning_effort="high"' --json \
  01a03c92-d97a-7122-9e4b-9d3137bc942c \
  'Yes, that matches my intent.'
```

1. Explicit entry:
   `$clarify I need to choose whether a small internal tool should start as a
   CLI or web app. I care most about shipping a useful first version quickly.`
   Preserved assistant output:
   `Given speed is the priority, my recommendation is to start with a CLI—provided the first users are comfortable with a terminal and share a predictable environment. Who will use version one: technical users running it locally, or nontechnical users who need browser-based/shared access?`
2. Ordinary reply, with no `$clarify` token:
   `The first users are three engineers on macOS, all comfortable with the
   terminal. Version one only needs to convert a local folder and print a clear
   report.`
   Preserved assistant output:
   `The first version should be a CLI: it serves three terminal-comfortable macOS engineers, processes a local folder, and prints a clear report. A web app would add deployment, hosting, and UI work without helping the initial use case. If that matches your intent, this clarification is complete.`
3. Confirmation, again with no `$clarify` token:
   `Yes, that matches my intent.`
   Preserved assistant output:
   `Clarification complete: start with a macOS-focused CLI for local folder conversion and clear terminal reporting.`

This proves one explicit invocation, continuation across ordinary replies,
recommendation, synthesis, confirmation, and clean stop. It did not create a
SPEC, write project files, or auto-invoke another user-invoked Skill.

## Final-candidate regeneration after third review

The evidence below was regenerated after the tie-handling, UTF-8 failure,
render-value injection, and Socratic machine-contract repairs.

Isolated router commands used the refreshed package copy at
`/tmp/light-functional-install.xx5emf/host/skills`:

```bash
cp -R skills/. /tmp/light-functional-install.xx5emf/host/skills/
python3 /tmp/light-functional-install.xx5emf/host/skills/ask-light/scripts/ask_light.py \
  --roots-json '[{"category":"first-party","path":"/tmp/light-functional-install.xx5emf/host/skills"}]' \
  --context-json '{"goal":"Clarify this project requirement","artifacts":[],"blockers":"","projectType":"software","taskKind":"","availability":{"host":"codex","readablePaths":["/tmp/light-functional-install.xx5emf/host/skills"]},"invocationControl":"explicit-only"}' \
  --host-name codex --mode next
python3 /tmp/light-functional-install.xx5emf/host/skills/ask-light/scripts/ask_light.py \
  --roots-json '[{"category":"first-party","path":"/tmp/light-functional-install.xx5emf/host/skills"}]' \
  --context-json '{"goal":"Review this artifact and branch","artifacts":[],"blockers":"","projectType":"generic","taskKind":"","availability":"codex","invocationControl":"explicit-only"}' \
  --host-name codex --mode next
```

Preserved reduced outputs:

```text
RECOMMEND project-clarify $project-clarify {'metadata': 33, 'bodies': 1, 'references': 3}
NEED-INPUT ['Material Light route tie: code-review, generic-review. Provide the intended outcome or project stage.']
```

The final isolated bootstrap used the same `research-fallback` JSON recorded
above with project root `/tmp/light-functional-install.xx5emf/project-final`.
The first run reported all three paths `created`; the identical second run
reported all three `preserved`.

The final actual Codex sequence used a newly installed pair and a new thread:

```bash
mkdir -p /tmp/light-functional-closure-final.kvdbOm/home/skills/.system /tmp/light-functional-closure-final.kvdbOm/project
ln -s /Users/light/.codex/auth.json /tmp/light-functional-closure-final.kvdbOm/home/auth.json
cp -R skills/clarify /tmp/light-functional-closure-final.kvdbOm/home/skills/clarify
cp -R skills/socratic /tmp/light-functional-closure-final.kvdbOm/home/skills/.system/socratic
git -C /tmp/light-functional-closure-final.kvdbOm/project init -q
CODEX_HOME=/tmp/light-functional-closure-final.kvdbOm/home codex exec \
  -C /tmp/light-functional-closure-final.kvdbOm/project --skip-git-repo-check \
  --ignore-user-config -m gpt-5.6-sol -c 'model_reasoning_effort="high"' --json \
  '$clarify I need to choose whether the first version should send reports by email or save them locally. The priority is a quick internal pilot.'
CODEX_HOME=/tmp/light-functional-closure-final.kvdbOm/home codex exec resume \
  --ignore-user-config -m gpt-5.6-sol -c 'model_reasoning_effort="high"' --json \
  01a03da2-2cda-7b50-9c2c-5d73fda9d27c \
  'All five pilot users can open files from a shared local folder. Automatic inbox delivery is not required for the pilot.'
CODEX_HOME=/tmp/light-functional-closure-final.kvdbOm/home codex exec resume \
  --ignore-user-config -m gpt-5.6-sol -c 'model_reasoning_effort="high"' --json \
  01a03da2-2cda-7b50-9c2c-5d73fda9d27c \
  'Yes, that is the decision.'
```

Preserved assistant outputs from thread
`01a03da2-2cda-7b50-9c2c-5d73fda9d27c`:

```text
For a quick internal pilot, I recommend saving reports locally. It avoids email credentials, delivery failures, and recipient management while you validate the report itself. Can pilot users reliably open or download the saved reports, or must reports arrive automatically in their inbox?

Shared understanding: the first version will save reports to the shared local folder for the five pilot users. Email delivery is deferred until after the pilot. Does that match your decision?

Confirmed. Clarification complete: v1 saves reports to the shared local folder; email delivery is deferred.
```

## Automated validation

- `python3 -m pytest -q` -> 162 passed.
- `python3 -m unittest discover -s tests` -> 26 tests OK;
  `COLLECTION_PYTHON_ASSERTIONS=245`, `LEARN_ANYTHING_HOOK_ASSERTIONS=7`.
- Every current `skills/*/tests` unittest suite -> OK.
- `python3 -m compileall -q skills tests` -> OK.
- `git diff --check` -> OK.
- Frozen baseline comparison -> `FROZEN_INTEGRITY=PASS`.
- Current Integration-only worktree diff ->
  `INTEGRATION_ONLY_WORKTREE_DIFF=PASS`.

## Review rounds

The first fresh Sol / High read-only review returned `fix-first`: preserve
user-authored initialization-section content, add explicit task-kind aliases,
reject unclosed frontmatter, and supply fresh discovery/invocation evidence.
All four findings were repaired and covered by tests or runtime evidence.

A separate `codex review --uncommitted` specialist review found six additional
issues: incomplete next-intent coverage, incorrect invocation types, unsafe
tracker locators, unmatched managed markers, preset/runtime tracker mismatch,
and an incorrect v0.1.2 installation statement. All six were repaired. The
extended routing matrix, package-derived invocation assertion, path and marker
negative tests, preset contract, and unreleased installation wording now cover
those findings.

Two subsequent fresh Sol / High evaluations returned `fix-first`. The first
closed reversed marker ordering, fallback field persistence, and exact evidence
capture. The second closed semantic-route tie precedence, rendered-value
injection, invalid UTF-8 handling, and new prose-coupled Socratic tests. The
latest candidate adds deterministic precedence plus `NEED-INPUT` on unresolved
ties, validates every rendered scalar/list value before writes, converts read
and decode failures to structured `BLOCKED`, and tests Socratic/clarify behavior
through machine-readable contracts and executable lifecycle state. Runtime and
full-suite evidence above was regenerated after those product corrections;
the later policy-only machine fields were followed by the same full suite.

Fresh final evaluation is required after these repairs; neither specialist
review is a final project verdict.

## Final-boundary regeneration after fifth review

The last three fix-first findings were regenerated from a fresh isolated copy
at `/tmp/light-functional-final-8FcsNl` after the implementation repair:

- `Final review this artifact` returned `RECOMMEND project-review` with
  `$project-review`.
- Generic `Review this artifact` with `taskKind: final-review` also returned
  `RECOMMEND project-review` with `$project-review`.
- Workflow mode with two readable first-party `project-init` packages returned
  `BLOCKED` and
  `Duplicate first-party workflow steps require host precedence evidence: project-init`.
- When `docs/agents/issue-tracker.md` already existed as a directory,
  `project-init` exited 1 with `bootstrap target exists but is not a regular
  file`; the only paths present afterward were the pre-existing directory and
  its parents. Neither `docs/agents/light-project.md` nor `AGENTS.md` was
  created.

Focused post-repair validation:

```text
python3 -m unittest discover -s skills/ask-light/tests     -> 19 tests OK
python3 -m unittest discover -s skills/project-init/tests  -> 18 tests OK
python3 -m pytest -q skills/ask-light/tests skills/project-init/tests tests/test_functional_closure.py
                                                            -> 41 passed
python3 -m compileall -q skills/ask-light skills/project-init -> OK
git diff --check                                           -> OK
```

These results close late-target atomicity, duplicate workflow provenance, and
final-authority precedence. A clean specialist review and a fresh final
Evaluator verdict still follow; this section does not claim final acceptance.

## Specialist review repair round

Fresh `codex review --uncommitted` ran with `gpt-5.6-sol` / High in thread
`01a03dae-7d62-7593-90fc-b99b4a2bd692`. The cumulative binary diff hash before
and after was identical:

```text
d96b0121303b2b7e2aebc903d75ad2d0bb0ca0b63cfa6898b65ca1c2f2d0e6f8
```

It returned seven actionable findings: host-aware instruction selection,
precedence without a primary semantic match, natural working-tree review
phrasing, contradictory noncanonical tracker locators, instruction symlink
aliasing, overlapping discovery roots, and empty first-party root paths. The
repair now:

- requires `instructionFile: AGENTS.md | CLAUDE.md` from current host evidence;
- supports only `.scratch/<effort>/issues` until another tracker adapter exists;
- rejects resolved write-target aliases before preparing content;
- applies precedence only after a primary pattern or task-kind match;
- routes ordinary code-change review phrasing and `taskKind: review` to
  `code-review`;
- deduplicates packages by resolved physical path; and
- rejects missing/empty first-party root paths instead of treating the working
  directory as provenance.

Fresh isolated replay at `/tmp/light-functional-repair-9kvcFH` confirmed:

```text
Deploy this repository                     -> NEED-INPUT
Review the current code changes             -> RECOMMEND code-review
overlapping collection + recap package root -> RECOMMEND recap; one candidate
empty first-party root path                 -> BLOCKED with non-empty-path gap
empty Claude-host repository                -> CLAUDE.md + two managed contracts
noncanonical tracker path                   -> exit 1; zero files written
AGENTS.md symlink alias to project contract -> exit 1; no new file written
```

The replay also exposed a valid `recap` directory link (`tests/`) being treated
as a broken file link. Pointer validation now accepts existing in-package
directories while continuing to reject missing, escaping, or unreadable file
references. Post-repair focused results are 24 ask-light tests, 21 project-init
tests, and 49 combined pytest cases, all passing. A new clean specialist review
is still required.

## Package-contract and transaction repair rounds

Fresh `codex review --uncommitted` in thread
`01a03ebb-b47a-7112-a0aa-5ec8ab7b73e2` returned four findings. The repair:

- stores only semantic patterns and concrete recipe handoffs in the Light map;
  package description and invocation type now come from `SKILL.md`;
- emits task-kind aliases as context-specific recommendation evidence;
- replaces generic workflow placeholders with concrete input, output, artifact,
  and stopping boundaries; and
- reports a pre-existing empty bootstrap target as `updated`, not `created`.

The next fresh specialist review, thread
`01a03ec7-574a-7fc2-80d9-166805448d4c`, reproduced four more boundary failures.
The final repair now stages every changed bootstrap file and rolls the full set
back after a late replacement failure, rejects unwritable targets before any
write, validates every unique workflow step package and its local pointers,
declares and gates the Python 3.9 runtime, and repairs the exact replay JSON with
`instructionFile: AGENTS.md`.

The corrected replay succeeded at
`/tmp/light-functional-evidence-replay.rT0taa`, reporting all three bootstrap
paths as `created`. Focused suites now report 25 ask-light and 24 project-init
tests. Current cumulative validation is:

```text
python3 -m pytest -q                                  -> 162 passed
python3 -m unittest discover -s tests                 -> 26 tests OK
COLLECTION_PYTHON_ASSERTIONS                          -> 245
LEARN_ANYTHING_HOOK_ASSERTIONS                        -> 7
every skills/*/tests unittest suite                   -> OK
python3 -m compileall -q skills tests                 -> OK
git diff --check                                      -> OK
Frozen baseline                                       -> PASS
Integration-only worktree diff                        -> PASS
```

A new clean specialist review is still required after these repairs; this
section records convergence work and does not claim final acceptance.

## Sixth specialist repair and user-approved recap amendment — 2026-08-27

Fresh read-only specialist thread
`01a03ed2-9dc3-7f70-921b-63ac29d33308` found five functional gaps. The
repairs now:

- use callable regular-expression replacements so Windows paths remain
  literal in managed project and instruction sections;
- preserve omitted `acceptanceStrategy`, `collaboration`, and `constraints`
  values on partial reruns;
- accept `explicit-only`, `model-callable`, and `either` invocation controls
  and check package-derived invocation compatibility;
- register bootstrap staging files before fallible writes so cleanup removes
  temp files and newly created directories; and
- direct no-Python manual routing to root records and `SKILL.md` frontmatter,
  rather than metadata removed from the semantic map.

Regression suites added Windows-path reruns, optional-decision preservation,
staging-write failure cleanup, and invocation-control compatibility. Focused
results were 25 `project-init` tests, 22 `ask-light` tests, and 4 functional
closure tests before the subsequent `recap` amendment.

The user then explicitly amended the Frozen scope for `recap`. Anthropic
first-party research is preserved in
`analysis/16-recap-claude-code-research.md`. The resulting package keeps:

- the user-approved description, `show one concise line about the current
  session without replacing or compacting conversation history.`;
- `disable-model-invocation: true` and host metadata
  `allow_implicit_invocation: false` for manual-only invocation; and
- one execution sentence requiring explicit `$recap`, one line of at most 400
  characters, current-session-so-far scope, no history clearing/replacement/
  compaction/rewriting, and stop.

Fresh project-local Codex observations loaded the candidate from
`/tmp/light-recap-project.f2o19U/.agents/skills/recap`:

```text
explicit $recap thread 01a04094-327d-7461-b3a5-711482eb95af
-> Parser implementation is complete; all automated tests passed; independent review remains pending.

ordinary two-bullet request thread 01a04094-9a8e-7c10-adc2-f3a9c7e0b0a8
-> - The parser implementation is complete.
   - An independent review is still pending.
```

The first result is one line and 98 characters. The ordinary request retained
its requested two-line shape, providing fresh non-trigger evidence. An earlier
attempt with an isolated empty `CODEX_HOME` was `BLOCKED` by missing
authentication (HTTP 401) and is not treated as behavior evidence; the
project-local run used the authenticated host while loading the candidate from
the isolated temporary project.

Current cumulative validation after the user amendment:

```text
python3 -m pytest -q                                  -> 174 passed
python3 -m unittest discover -s tests                 -> 27 tests OK
COLLECTION_PYTHON_ASSERTIONS                          -> 245
LEARN_ANYTHING_HOOK_ASSERTIONS                        -> 7
every active skills/*/tests unittest suite            -> OK
frozen historical skills/recap/tests                  -> not active after amendment
python3 -m compileall -q skills tests                 -> OK
git diff --check                                      -> OK
Frozen baseline except user-amended recap             -> PASS
recap exact user amendment and 400-character tests    -> PASS
Integration-only worktree diff                        -> PASS
```

Only `skills/recap/SKILL.md` was released from the Frozen boundary. The two
package-local `skills/recap/tests` files remain byte-for-byte unchanged and
assert prose from the superseded long-form contract, so they are retained as
historical records rather than executed as current acceptance tests. The active
repository-level functional suite checks the exact minimal body, explicit-only
metadata, one-line output, 400-character limit, and amended Frozen hashes.

The fresh collaboration reviewer could not start because that reviewer account
hit its usage limit. Two local `codex review` attempts were stopped when the
user refined `recap`; neither stale attempt is a clean verdict. A new review of
the exact current diff is still required.

## Seventh and eighth specialist repair rounds — 2026-08-27

Fresh Sol / High specialist review
`01a0419a-161f-7da1-b030-a21ace16c605` found three issues: the active GitHub
workflow still invoked the frozen historical recap contract test, the new
router omitted the existing `setup` and `discovery` workflow aliases, and the
catalog accidentally assigned recap's unreleased status to `language-learning`.
The repair removes both historical recap tests from CI, updates the CI file list
to the current review-loop suites, runs the Python ask-light behavior suite on
every CI host, restores both aliases with regression coverage, and corrects the
bilingual catalog and recap test guidance.

The next fresh Sol / High specialist review
`01a041a0-8562-7fc3-8f04-5a13c40cc9b3` found four remaining boundaries. The
repair now:

- recursively validates in-package Markdown references with cycle tracking;
- ignores fenced Markdown examples when locating the live Project
  Initialization section;
- pins the documented stable recap install command to `#v0.1.6`; and
- refreshes manuscript dependency package trees and blob identities to local
  product commit `b671a90ac10b5777a50ca897a03242cc51949478`.

Focused post-repair results are 31 ask-light tests, 29 project-init tests, and
67 combined pytest cases. The current GitHub workflow command set replays
successfully, and the complete active suite reports 174 pytest cases plus 27
repository-level unittest cases.

The manuscript dependency check against the local catalog now has zero errors
and reports `DEGRADED` only because resource-byte comparison requires
`--online`. The pinned product commit is intentionally local and unpushed for
human review, so an online GitHub check cannot succeed yet. This is a release
and remote-availability limitation, not published-install or handoff `READY`
evidence; no release claim is made.

A fresh clean specialist review and the final independent project Evaluator
still follow this repair record.
