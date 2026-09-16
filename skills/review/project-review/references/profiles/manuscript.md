# Manuscript Profile

Select this Profile when the frozen target is a manuscript, document, outline,
semantic batch, source lock, translation/derived edition, or final document
deliverable. The Profile adds manuscript-specific review dimensions and
evidence to the generic Core; it does not replace the Core's finding
identity/disposition lifecycle, repair boundary, state machine, independence
requirement, round limit, or final verdict.

## Review axes

Review every applicable axis independently and retain the axis on each finding.
On a Project route, the non-image axes are positive-or-negative audits even
when the conclusion is that the axis has no issue. The image axis is mandatory
when registered image sources, PPTX delivery, or the active batch requires it.

1. **Reader task, intent, completeness, structure, and internal logic** — the
   approved Brief's audience and reader task, scope, outline, sequencing,
   cross-references, and content boundaries are reflected in the frozen
   artifact.
2. **Source authority, provenance, factual claims, citations, numbers, and
   units** — factual claims resolve to registered authoritative sources, typed
   permitted use and exclusions are respected, citations and units are intact,
   and derivatives retain source lineage and hashes.
3. **Terminology, style, and cross-language consistency** — the approved
   glossary, terminology decisions, transliteration, style rules, and language
   relationships hold across the manuscript and every derived edition.
4. **Reader fit, accessibility, tone, and localization** — wording, reading
   level, navigation, accessibility, tone, and localization suit the approved
   audience and reading context.
5. **Safety, privacy, legal/regulatory boundaries, and metadata** — sensitive
   data, safety claims, regulated or legal content, disclaimers, metadata, and
   redaction follow the approved risk and privacy policy.
6. **Format structure, layout, pagination, tables, links, fields, and
   navigation** — the actual deliverable has the required parts, styles,
   links, fields, tables, page/slide structure, and navigation rather than
   merely valid source syntax.
7. **Images and figures** — image selection, source/rights, placement, crop,
   caption, annotation, callouts, and alt text match the Brief and artifact.
   Record a positive or negative applicability audit when the axis is not
   triggered; do not silently omit it.
8. **Lifecycle, semantic batches, human gates, and locked-source integrity** —
   the artifact is at the named lifecycle phase, active batch has accepted
   prerequisites and a frozen input snapshot, required human gates/receipts
   follow review, and translations or derivatives use the approved locked
   source.
9. **Generation reproducibility, artifact evidence, hashes, version gates,
   and recovery** — required generation captures tools, versions,
   configuration, commands, inputs, outputs, hashes, receipts, and a resumable
   evidence chain; manual binary edits have an approved disposition.
10. **Compatibility, rendering, visual QA, semantic QA, and round-trip
    preservation** — every required adapter operation is exercised with the
    declared target application/renderer, visual and semantic checks bind the
    exact artifact, and round-trip invariants are preserved when required.

## Evidence requirements

The manuscript review packet must include the following, using exactly one
primary label from the generic [Evidence Protocol](../evidence-protocol.md)
for each item:

- the approved ManuscriptBrief and frozen Acceptance Charter, including
  audience/reader task, scope and exclusions, source policy, languages,
  formats, deliverable paths, visual-QA policy, and acceptance seams;
- exact project-relative artifact paths, SHA-256 values, snapshot capture time,
  and a matching review matrix/report timestamp;
- the source map/register with stable source IDs, authority class, permitted
  use, exclusions, retrieval/provenance, derived-artifact lineage, and the
  terminology/glossary material in scope;
- the lifecycle state, semantic batch manifest, prerequisite and regression
  surface, locked-source identity, and applicable human-gate receipts;
- actual structural, generation, render, visual, semantic, and round-trip
  observations for every required format operation, with the command/tool or
  human observation and its limitations. Syntax-only validation is not render
  or visual evidence;
- per-deliverable output lineage and hashes, including the locked manuscript as
  an input for every translation/derived edition and final semantic check;
- image/figure evidence when the image axis is triggered, including source,
  rights/privacy, placement, caption/annotation, and alt-text observations;
- fresh independent Evaluator evidence with the raw Core independence value and
  the manuscript-normalized value preserved. Missing independent context is a
  blocker, not a weaker acceptance claim.

These are Profile inputs to the Core. Candidate findings enter the generic
finding schema with stable IDs, immutable observations, and a Core disposition;
the Profile does not create a second finding registry or review state.

## Specialist reviewers

Use read-only manuscript-domain specialists for source/provenance, editorial
and terminology, safety/privacy, and format/render/visual QA axes as applicable.
The manuscript specialist reports observations and candidate findings; it never
edits the artifact and never issues the Program's final `PASS`, `FAIL`, or
`BLOCKED`. The Core validates every specialist candidate and owns the verdict.

## Severity guidance

Use impact against the frozen manuscript baseline, not estimated repair effort:

- **Critical** — unsafe or unlawful content, privacy breach, fabricated or
  unauthorised factual authority, corrupt output, or a failure that makes the
  accepted reader task unusable;
- **High** — a required audience/structure/source/language/deliverable seam is
  absent or materially wrong, a locked-source or lifecycle gate is bypassed, or
  required render/visual evidence is missing for an accepted final output;
- **Medium** — a material in-scope factual, terminology, accessibility,
  layout, metadata, reproducibility, or compatibility gap that must be resolved
  before `PASS` unless the user records eligible risk acceptance;
- **Low** — a limited-impact editorial, navigation, diagnostic, or test-quality
  observation that does not block `PASS` unless the Charter says otherwise.

Severity is impact against the frozen target. It does not authorize a new
language, format, source, audience, architecture, or product decision.

## Acceptance conditions

The Core may ask its fresh Evaluator to consider `PASS` only when:

- the exact artifact snapshot, approved Brief/Charter revision, and manuscript
  Profile are frozen and agree;
- every applicable axis has correctly labeled evidence, including negative
  applicability audits, and all required manuscript-domain specialist reports
  are present;
- source authority/provenance, terminology, reader fit, safety/privacy,
  lifecycle/batch/gate, and deliverable-language/format seams are evidenced;
- every required format has real structural, render, visual, semantic, and
  round-trip evidence as declared by its adapter and Brief policy, with no
  syntax-only substitute;
- all confirmed blocking findings have fresh per-ID repair evidence under the
  same stable identity, and any Medium/Low accepted risk has the user's exact
  post-review statement, actor, and timestamp;
- derived editions and final deliverables bind the approved locked source and
  their artifact-bound hashes; and
- the fresh Evaluator records criterion-by-criterion judgment in a genuinely
  independent context. The generic Core records the final verdict.

## Artifact-specific failure cases

Preserve the specialist observation and apply the Core's generic `FAIL` or
`BLOCKED` stopping rule when:

- the approved Brief/Charter, artifact snapshot, source authority/register,
  provenance, terminology, lifecycle state, or required gate receipt is
  missing, stale, contradictory, or cannot identify the reviewed scope;
- a factual claim uses reference-only or incoming material as authority, a
  source use is excluded/unregistered, or a derivative loses parent lineage;
- required language/format deliverables, locked-source inputs, batch
  prerequisites, or human gates do not match the frozen Brief;
- a required renderer, visual/semantic/round-trip check, image audit, or
  artifact-bound hash is absent, syntax-only checks are presented as layout
  acceptance, or the environment cannot perform a blocking QA operation;
- a translation is generated from an unlocked source, terminology drifts
  across editions, or a privacy/safety/legal/metadata boundary is breached;
- generation is required to be reproducible but tool/version/configuration,
  locked inputs, output lineage, or manual-edit disposition is missing;
- the reviewer drops an axis because of concurrency, treats a specialist
  summary as the Program verdict, or attempts to edit the manuscript; or
- a proposed repair expands the frozen audience, scope, sources, language,
  format, lifecycle gate, or architecture, or requires new authority or
  tickets. Do not weaken this Profile to make such a target pass.

The generic Core, not this Profile or a manuscript specialist, owns finding
identity, dispositions, repair rounds, state transitions, independence stops,
scope handling, and final `PASS`, `FAIL`, or `BLOCKED`.

## Selection record

Record `Profile: manuscript` in the Acceptance Charter and identify the
manuscript target, lifecycle milestone, and reason this Profile applies. A
later request to change the audience, authority policy, language, format, or
milestone is a baseline change requiring the Core's approved change process.
