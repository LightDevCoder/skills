---
name: manuscript-ops
description: Route and govern manuscript engineering from small notes and structured reports to large manuals, books, multilingual editions, and reproducible multi-format deliverables. Use when an agent must assess document scope and risk, create or resume a writing project, manage sources and semantic batches, coordinate explicit clarify, decision-map, project-init, or project-review handoffs, freeze or lock drafts, or generate and QA TXT, Markdown, DOCX, PDF, HTML, EPUB, PPTX, and related formats.
---

# Manuscript Ops

For one-session clarification, `clarify` is the external user-facing entry
point and `socratic` is its underlying model-invoked capability. Treat them as
one discovery handoff, not two separate user-facing steps.

Treat the manuscript as a governed state machine, not a single editable file.
Keep source authority, user decisions, reproducible generation, review evidence,
and human gates visible throughout the work.

## 1. Preflight without writing

1. Resolve the exact project root. Pause if a user-named path is absent.
2. Read applicable `AGENTS.md` files and existing project state.
3. Inspect paths, formats, version control, source classes, likely deliverables,
   and available agent/tool capabilities. Preserve existing files and paths.
   The bundled Python tools require Python 3.11 or newer.
4. Run the read-only assessor when useful:

   ```text
   python scripts/assess_project.py --root <project-root> --answers <routing-input.json>
   ```

5. Produce a `RoutingSnapshot` with all six dimensions, hard triggers,
   repository evidence, unknowns, route, and reasons. Treat an unknown dimension
   as one point, escalate unknown boundary cases, and select Project while any
   hard-trigger fact remains unresolved.

Read [routing.md](references/routing.md) for scoring, hard triggers, and examples.
Preflight is complete only when every dimension is scored or explicitly unknown
and the selected route is justified by evidence.

## 2. Take exactly one route

- **Quick** — score `0-3`, no hard trigger. Perform the bounded task directly.
  Do not initialize project state. Run only the format and content checks that
  can materially fail.
- **Structured** — score `4-7`, no hard trigger. Establish a lightweight Brief,
  source map, outline, output plan, and review axes. Invoke `clarify` first only
  when a key user-intent decision remains unresolved.
- **Project** — score `8-12` or any hard trigger. Follow the explicit handoff
  sequence below. Never compress it into an internal substitute.

## 3. Execute a Project route through explicit handoffs

1. Choose one discovery handoff:
   - single-session decisions: logically activate `clarify` to resolve the
     open manuscript decisions recorded in `<path>`;
   - multi-session fog: logically activate `decision-map` to chart the effort in a
     local Markdown task graph without implementing it.
   Render these calls using the current host's syntax.
2. Stop. Continue only after the user explicitly activates `manuscript-ops`
   with `resume`.
3. Verify that the resulting `ManuscriptBrief` is approved and contains no
   unresolved scope, acceptance, or authority decisions.
4. Read [project-init-boundary.md](references/project-init-boundary.md). Check
   that project initialization has produced the exact root mapping, applicable
   project rules, a Project Profile, and resumable manuscript state. If any
   result is missing, report `BLOCKED` at the exact root, state the required
   initialization outcome, recommend explicit `project-init` activation, and
   stop. Do not automatically invoke another user-invoked Skill.
5. Ask for the fixed initialization gate. After explicit approval, initialize
   or inherit local version control, create the Project Profile and project
   structure, and freeze a dated baseline.
6. Tell the user to activate `project-review` with
   `init using <approved-brief-path>`. Stop and resume only after an approved
   review charter exists.
7. Build the approved outline, batches, locked source, derived editions, and
   finals. Supply the manuscript review profile and artifact evidence to
   `project-review` at the outline, candidate, and final milestones and at any
   project-specific risk gate.

Read [handoffs.md](references/handoffs.md) before emitting a dependency call.
If a dependency is missing, report `BLOCKED`, give its installation method, and
wait. Do not emulate it. A handoff is complete only when the next exact
invocation and resume condition are stated.

## 4. Initialize or map the project

For a new Project route, create the standard logical structure described in
[project-layout.md](references/project-layout.md). For an existing project,
leave every existing path in place and map logical roles to actual paths in the
`ProjectProfile`.

Copy and fill only the templates needed for the selected route:

- [Manuscript Brief](assets/templates/manuscript-brief.md)
- [Lifecycle State](assets/templates/state.json)
- [Project Profile](assets/templates/project-profile.json)
- [Batch Manifest](assets/templates/batch-manifest.json)
- [Manuscript Review Profile](assets/templates/review-matrix.json)
- [Gate Receipt](assets/templates/gate-receipt.json)
- [Source Register](assets/templates/source-register.tsv)
- [Platform Capability Snapshot](assets/templates/platform-capabilities.json)
- [Format QA Record](assets/templates/format-qa-record.json)

Use the public interface definitions in
[state-model.md](references/state-model.md). Record the origin of every Profile
value as exactly `资料发现`, `用户决定`, or `规则推导`. Initialization is complete
only when logical roles resolve to real paths, unknowns remain explicit, and a
baseline receipt binds the approved state to hashes.

## 5. Move through the manuscript lifecycle

Use this semantic order:

```text
authoritative sources -> reference-only material -> optional incoming draft
-> outline -> working draft -> frozen review draft -> candidate
-> locked source -> translation/derived edition -> final -> archive
```

Keep the main thread as the only body writer. Partition batches by meaning,
dependency, risk, and reviewable volume rather than raw page count. Review normal
batches incrementally; run cumulative regression at outline, candidate, and
final milestones. Read [lifecycle.md](references/lifecycle.md) for gates,
snapshots, locking, and batch rules.

Do not advance a batch until its prerequisites are accepted. Review and accepted
outputs are hash-bound files; acceptance requires a matching specialist PASS,
all declared axes, and any required user confirmation after review.

## 6. Define the manuscript review boundary

Select every applicable manuscript axis, including content/structure,
format/layout, image placement, image annotations, privacy, reader fit, factual
sources, safety, terminology, reproducibility, and round-trip preservation.
Record why each axis is applicable or not and the exact artifact-bound evidence
required for an audit. On a Project route, treat every non-image core axis as a
mandatory positive-or-negative audit; require the image axis when sources, PPTX,
or the active batch trigger it.

Read [review.md](references/review.md) when constructing the manuscript review
profile. Pass the frozen profile, artifact snapshot, source authority, batch
context, and format-QA evidence to `project-review`. `project-review` owns generic
finding identity and disposition, repair rounds, reviewer independence, review
state, and the final verdict. `manuscript-ops` records and verifies the
manuscript-specific evidence boundary and consumes the returned verdict; it does
not reimplement those generic mechanics.

## 7. Apply a format adapter

Read [formats.md](references/formats.md) and the machine registry at
[format-registry.json](assets/format-registry.json) for every input and output
format in scope. Probe local capabilities with:

```text
python scripts/probe_capabilities.py
```

When host-native tools are involved, fill a structured platform snapshot and
pass `--platform-capabilities <path>`. Use
[platform-capability-map.json](assets/platform-capability-map.json) only as a
logical mapping; it never proves that a tool is currently exposed.

For each format, record reading, editing, generation, rendering, visual QA,
round-trip, dependencies, and degradation behavior. A syntactically valid file
is not visual evidence. If real rendering or visual inspection is unavailable,
report `DEGRADED` or `BLOCKED`; never claim layout acceptance. Create one
artifact-bound QA record per approved Brief deliverable, with structured
coverage, typed hashed evidence, and a distinct hashed round-trip output when
required.
Brief format/language sets must exactly match the Profile, file suffixes must
match adapters, and sampled checks must bind that deliverable's approved
sampling policy. READY evidence also records reproducible/manual generation,
tool and command, configuration, locked inputs, output lineage, and semantic
comparison to the active locked manuscript.

## 8. Freeze gates with Jujutsu

Prefer an existing version system. For a new Project route, use non-colocated,
local Jujutsu after capability detection. The tested baseline is `jj 0.43.0`;
other versions require command probing. Do not add a remote, fetch, push,
upgrade, or downgrade automatically.

Create dated immutable gate bookmarks such as
`source-locked-YYYY.MM.DD` and mutable `current-*` aliases. On same-day conflict,
append `-02`, `-03`, and so on. Bind each gate to a `GateReceipt` containing the
date version, change/commit IDs, file hashes, review result, and user
confirmation. Read [version-control.md](references/version-control.md) before
initialization or gate creation.

A publish receipt additionally names the exact target and hash-binds the active
final receipt by path and bytes. Baseline receipts bind an immutable Profile
snapshot; framework receipts bind the mapped outline; source-lock receipts bind
the registered sources and locked manuscript. Never reuse publication authority
for a different repository, release, deployment, installation, or distribution
target.

## 9. Validate before pausing or closing

Run the read-only state validator:

```text
python scripts/validate_state.py --root <project-root> --check-jj
```

Re-run stale or missing evidence. Report status using `implemented`, `verified`,
`independently accepted`, `blocked`, `not tested`, and `out of scope`. Keep
those states distinct.

Read [failure-recovery.md](references/failure-recovery.md) whenever a dependency,
snapshot, review, version, render, or resume check fails. A Project route is
ready for human final approval only when the final gate receipt, format QA
evidence for every Brief deliverable, and independent verdict agree.
