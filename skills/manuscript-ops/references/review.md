# Manuscript review boundary

`manuscript-ops` supplies the manuscript Profile to `project-review`; it does not
own a second review engine. The frozen Profile records the manuscript-specific
axes, applicability reasons, required evidence, source authority, deliverable
paths, batch context, and milestone snapshot.

## Manuscript axes

Keep these axes available in every Project Profile. Mark an axis inapplicable
only with a recorded reason; a negative conclusion such as “no images” is still
evidence for the applicable axis decision.

- `intent-structure`: goal, completeness, structure, internal logic, and reader task;
- `factual-sources`: source authority, citations, numbers, units, and provenance;
- `terminology-localization`: terminology, glossary, translation, and cross-language consistency;
- `reader-accessibility`: audience fit, accessibility, tone, and localization;
- `safety-privacy-legal`: safety, privacy, legal or regulatory boundaries, and metadata;
- `format-layout`: format structure, layout, pagination, tables, fields, links, and navigation;
- `images`: image selection, placement, crop, captions, annotations, and alt text;
- `reproducibility-recovery`: generation inputs, hashes, gates, receipts, and resume/recovery evidence;
- `compatibility-round-trip`: target compatibility and round-trip preservation.

On the Project route, the eight non-image axes are mandatory positive-or-negative
audits. Add `images` when the Source Register contains image sources, PPTX is a
selected deliverable, or the active batch requires it. A batch may add a
manuscript-specific axis only when its reason and evidence requirement are
recorded in the Profile.

## Evidence contract

Capture the exact artifact snapshot before handing it to `project-review`. Each
applicable axis must name the evidence needed to inspect it. Evidence is typed
and project-relative; files, rendered pages, source-register rows, capability
snapshots, format-QA records, and receipts are hash-bound. A valid file without
render or visual evidence does not establish layout acceptance.

The project-review result must retain a `manuscript_evidence` projection with one
entry per applicable manuscript axis. Each entry points to the hashed evidence
artifacts used for that axis. `manuscript-ops` checks that the projection covers
the frozen Profile and that candidate outputs, locked sources, and final format
QA are included where the lifecycle gate requires them.

## Delegated generic review mechanics

`project-review` owns the generic finding schema and stable identities, finding
disposition and resolution, repair rounds and stopping rules, reviewer and
Evaluator independence, durable review state, and the final `PASS`, `FAIL`, or
`BLOCKED` verdict. `manuscript-ops` must not copy or reimplement those rules.

At each manuscript milestone, pass the Profile, frozen artifact snapshot, source
authority, active batch, and format evidence to `project-review`. Consume its
hash-bound ReviewReport and preserve its raw verdict and independence metadata in
the manuscript lifecycle and GateReceipt. The manuscript validator may check the
integration envelope, milestone, artifact hashes, and manuscript evidence
coverage, but must leave generic findings and verdict reasoning to `project-review`.

If the project-review dependency or an independent review context is unavailable,
preserve the current manuscript evidence and return `BLOCKED` with the exact
resume point. Do not simulate a reviewer, repair loop, or final verdict inside
`manuscript-ops`.
