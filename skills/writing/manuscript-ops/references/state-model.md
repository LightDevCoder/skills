# Public state model

All machine state is UTF-8 JSON unless a template specifies Markdown or TSV.
Use `schema_version: "1"` and preserve unknown fields when updating a file.
Timestamps use RFC 3339 UTC. Date versions use `YYYY.MM.DD` with optional
same-day suffix `-02`, `-03`, and so on.

## RoutingSnapshot

Required fields:

- `schema_version`, `captured_at`, `root`;
- `dimensions`: six named objects with `score`, `effective_score`, `unknown`,
  and `evidence`;
- `hard_triggers`: named booleans;
- `repository_evidence`, `unknowns`;
- `total`, `route`, `reasons`;
- `next_action` and optional `next_invocation`.

Snapshots are observations, not timeless facts. Record the maximum accepted age
in project state and re-assess after material source, scope, output, or tool
changes.

## ManuscriptBrief

The approved Brief records:

- goal and user-visible outcome;
- audience and reading context;
- scope and explicit non-scope;
- source-authority policy;
- approved outline or outline acceptance rule;
- deliverables, languages, and formats;
- review and human gates;
- acceptance conditions, risks, assumptions, and open questions;
- approval state, approver statement, and approval date.

An unresolved scope, authority, safety, or acceptance decision prevents Project
initialization.

Each deliverable row has a unique project-relative stable path. Format QA is
indexed by that path, not only by adapter ID, so two language editions or two
files in the same format require two separate artifact-bound QA records.
Deliverable language and format sets match the ProjectProfile exactly. A stable
file suffix must belong to its named adapter; custom adapters cannot claim or
masquerade behind a canonical extension. `Reproducible` is `required` or
`not_required`; `Visual QA` is `full`, `sampled`, or `not_applicable`.

## ProjectProfile

The Profile is executable configuration, not narrative. Each value is wrapped:

```json
{
  "value": "docs/manuscript-brief.md",
  "origin": "规则推导",
  "evidence": "standard logical layout",
  "confirmed_at": "2026-07-18T00:00:00Z"
}
```

`origin` must be exactly `资料发现`, `用户决定`, or `规则推导`. Except for
`schema_version` and structural object keys, every configurable leaf is wrapped
this way: date version, route, paths, formats, languages, dependencies,
capability snapshot, version-control settings, freshness, and unknowns.
Existing projects retain their paths.

## LifecycleState

`.manuscript-ops/state.json` names the current phase, date version, active batch,
required gate receipts, the active dated receipt for each gate, source register,
ReviewMatrix, latest ReviewReport, capability snapshot, and format-QA records.
It is the stage-aware index used by `validate_state.py`; an empty gates
directory never establishes readiness. Historical successor receipts remain in
`gates/`; `active_receipts` selects the receipt targeted by each mutable
`current-*` alias.

Supported phases are `brief-approved`, `initialized`, `framework-approved`,
`working`, `candidate`, `source-locked`, `deriving`, `final-approved`,
`published`, and `archived`. Later phases require all applicable earlier fixed
gates. `archived` preserves the active `publish-approved` receipt; archiving
cannot erase publication authority or its evidence chain.

## BatchManifest

Each batch declares:

- stable `id`, label, semantic scope, and included units;
- prerequisite batch IDs and source dependencies;
- risk level and applicable review axes;
- target review volume and cumulative/regression scope;
- input snapshot, hash-capable output objects, status, and user gate;
- hash-bound specialist ReviewReport and user confirmation when accepted.

Every source dependency is an object with `source_id`, `use`, and `purpose`.
`use` is `factual`, `context`, `style`, or `incoming`; factual use requires an
authoritative Source Register row, and incoming use requires an incoming-draft
row. An unregistered ID blocks the batch.

`input_snapshot` may be `null` only while a batch is `planned`. An
`active`, `review`, `accepted`, or `blocked` batch binds a project-relative
path, SHA-256, and capture timestamp. Only one batch may be `active` or
`review` at a time, and its ID must equal LifecycleState `active_batch`.
Successor work requires a new frozen snapshot rather than silently refreshing
the input of a live batch.

Every `active`, `review`, or `accepted` batch has only accepted prerequisites.
Outputs are project-relative `{path, sha256}` objects; review/accepted states
require real hash-valid files. An accepted batch requires a matching milestone
ReviewReport with `PASS`, all declared axes, and every output in its frozen
snapshot. If `user_gate` is `required`, confirmation follows that review.

Do not use page count as the only partitioning rule.

## Manuscript review profile and project-review result

The local `ReviewMatrix` file is a manuscript review Profile, not a second
review engine. It names the frozen artifact snapshot and every manuscript review
axis. Each axis records applicability, the reason, and the artifact-bound
evidence required for that domain audit. Inapplicable axes remain present with a
reason. On the Project route, the eight non-image axes are mandatory; the image
axis is added when the source or deliverable contract requires it.

`project-review` consumes that Profile and owns generic reviewer identity, finding
identity and disposition, repair rounds, independence, durable review state, and
the final verdict. Its JSON ReviewReport is an external result. The manuscript
integration envelope must identify `provider: project-review` and `profile:
manuscript`, hash-bind the same artifact snapshot, and retain one typed,
hash-bound `manuscript_evidence` entry for each applicable manuscript axis.
`manuscript-ops` validates only this boundary and the lifecycle-specific
artifact bindings; it does not validate or reproduce generic finding or verdict
rules.

LifecycleState and GateReceipt reference the external JSON result. A missing,
stale, or non-PASS result blocks the manuscript gate and is resumed only after
the project-review result is imported or refreshed.

On the Project route, the non-image core axis catalog is always applicable as a
positive or negative audit. The image axis is additionally mandatory when the
Source Register, selected PPTX delivery, or active batch requires it. Candidate
state requires a candidate-milestone report whose snapshot contains every
active candidate-batch output.

## GateReceipt

A receipt binds one of `brief-approved`, `baseline`, `framework-approved`,
`source-locked`, `final-approved`, or `publish-approved` and records:

- gate name and date version;
- immutable bookmark and mutable current alias;
- Jujutsu change ID and commit ID of the frozen parent content revision;
- every gated file path and SHA-256;
- capability snapshot and format QA evidence paths plus hashes;
- review report hash, verdict, and independence;
- exact user confirmation, confirmation date, and actor;
- for publish approval, a structured target and hash-bound active final receipt;
- receipt creation time and receipt hash when externally recorded.

The gated file set is closed over its evidence: every file in the referenced
ReviewReport artifact snapshot must also appear in the receipt; final and
publish receipts must additionally include every format-QA artifact. A
baseline receipt hash-binds an immutable full ProjectProfile snapshot under
`.manuscript-ops/snapshots/`. A framework receipt and review hash-bind the
Profile-mapped outline. A source-lock receipt and its ReviewReport bind both the
active Source Register and a locked manuscript inside the Profile manuscript
mapping. Final semantic QA and generation inputs bind that same locked
manuscript.
A Brief receipt repeats the approved Brief's actor, exact statement, and
timestamp byte-for-byte. Confirmation must occur after all referenced review,
capability, and QA evidence completed, and the receipt must be created no
earlier than the confirmation.

Publication authority identifies the active final receipt by exact
project-relative path and SHA-256, not only by its bookmark string. Its
confirmation occurs no earlier than the referenced final receipt's confirmation
and creation. The dated bookmark points to a child receipt-seal revision: its
GateReceipt bytes must exactly match the current file, its parent IDs must match
the receipt's Jujutsu IDs, and every receipt-listed file is read from that
parent and compared with the recorded SHA-256.

Never edit a receipt in place after its bookmark is created. Create a successor
receipt and version when evidence changes.

## FormatAdapter

Each adapter records:

- `id`, format, tier, extensions, and media type;
- read, edit, generate, render, visual QA, and round-trip capabilities;
- required and optional dependencies;
- validation contract;
- degradation status, blocking QA gaps, and provider-alternative dependencies.

The packaged registry is the minimum canonical contract. A project copy may add
adapters and observed provider evidence, but it cannot remove a canonical
adapter or weaken its format, tier, extensions, media types, operations,
dependencies, validation clauses, blocking-QA rule, or degradation statement.
No two adapters may claim the same normalized file extension.

Capability values are `supported`, `conditional`, `unsupported`, or
`not_applicable`. Status values are `READY`, `DEGRADED`, or `BLOCKED`.
Process probes cannot see every host primitive. Host-native evidence uses
`platform-capabilities.json` with provider, version, access evidence, and
operation coverage. State validation reproduces every claimed
`source: process_probe` entry against the fixed live process-probe contract;
arbitrary capability names or operation lists cannot establish readiness.

Each format-QA index entry binds a JSON record from
`assets/templates/format-qa-record.json`. That record hashes the artifact,
identifies the provider/version, and gives structural, render, visual, semantic,
and round-trip evidence. Every PASS/FAIL check lists its coverage counts, exact
item IDs, and typed hash-bound evidence artifacts. A sampled PASS hash-binds the
approved Brief and the matching deliverable's `sampled` policy. Semantic PASS
hash-binds a distinct locked-source reference; a round-trip PASS hash-binds a
distinct output and compared invariants. Every READY record also captures
generation mode, tool/version, ordered command or actions, configuration,
hash-bound inputs, exact output, and any manual reproducibility disposition.
Host-native capabilities must exactly match a hash-bound platform snapshot
interpreted through the canonical capability map. Final
LifecycleState records and active final/publish receipts must match exactly,
cover every Brief deliverable path, and be entirely `READY`.
