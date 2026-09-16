# Format adapters

Use `assets/format-registry.json` as the machine registry. Copy the selected
adapter entries into project state and add observed tools and versions. Process
probes may be supplemented only by an evidence-backed
`assets/templates/platform-capabilities.json`; use
`assets/platform-capability-map.json` to translate host primitives into logical
capabilities.

The packaged registry is a canonical minimum. A project registry may extend it,
but it cannot delete a canonical adapter or weaken any canonical capability,
dependency, validation, blocking-QA, or degradation field. If local policy
needs a stricter contract, add constraints or mark the observed adapter
`BLOCKED`; do not rewrite the baseline to make missing capability appear
acceptable.

Adapter extensions are globally unique. Brief format IDs match ProjectProfile
format IDs exactly, and each file deliverable suffix belongs to its selected
adapter. An extensionless cloud adapter cannot be used to relabel a canonical
`.docx`, `.pdf`, or other registered file.

## Tier 1

Tier 1 formats require an explicit end-to-end contract:

- TXT and Markdown;
- DOCX and PDF;
- HTML and EPUB;
- PPTX.

For each, record reading, editing, generation, structural validation, real
rendering, visual QA, round-trip expectations, dependencies, metadata/privacy
checks, and degradation behavior.

Tier 1 does not mean every environment supports every operation. It means the
agent must either fulfill the complete contract or name the missing capability
and stop at `DEGRADED` or `BLOCKED`.

## Tier 2

Enable ODT, RTF, LaTeX, ODP, XLSX, ODS, CSV, Google Workspace, Microsoft 365,
and Apple iWork only when the platform exposes the needed operations. Record
which platform performed the operation and whether fidelity was checked.

Cloud-native documents require a stable document identity, revision or export
snapshot, permission boundary, and deterministic export where possible.

## Source-layer formats

Web pages, emails, images/scans, audio, video, and transcripts are sources, not
automatically manuscripts. Register provenance, retrieval time, privacy class,
hashes for local files, and conversion lineage.

- OCR output must link to the image/scan and record engine/language.
- Transcripts must use `parent_source_id` to link a different registered
  audio/video row and record engine/language/timestamps.
- Email exports must preserve thread identity while excluding unnecessary
  personal data.
- Web capture must record URL, retrieval time, and archived content or hash when
  policy permits.

Every `derived_artifacts_json` entry is an object with `kind`, stable `path`,
`sha256`, `parent_source_ids`, and `created_at`. OCR/transcript-like derivatives
also record `engine_or_author` and `language`. A row cannot satisfy lineage by
pointing to itself.

## QA contract

1. **Structural QA** — parseability, required parts, links, metadata, styles,
   dimensions, fields, and internal relationships.
2. **Render QA** — use a real application or renderer representative of the
   target format.
3. **Visual QA** — inspect every page/slide or a declared risk-based sample only
   when the Brief permits sampling.
4. **Semantic QA** — compare headings, steps, tables, figures, numbers, and
   cross-references with the locked source.
5. **Round-trip QA** — save through the target application and compare semantic
   and layout invariants when round-trip is required.

Every check records `coverage.mode`, unit, total item count, inspected count,
and exact inspected item IDs. A `full` PASS inspects every item. A `sampled`
PASS names and hashes the approved Brief, the exact deliverable path, and its
machine `policy: sampled`; a free-text assertion is insufficient. `partial`
is permitted only for FAIL evidence. Every PASS/FAIL check references typed,
hashed evidence artifacts: validator log, rendered output, inspection record,
or comparison report as applicable. Semantic PASS records compared invariants;
and a distinct locked-source reference. Round-trip PASS additionally hashes a
distinct saved output.

Every READY record also contains `generation`: reproducible or manual mode,
tool/version/evidence, an ordered command or action array, hash-bound
configuration or an explicit reason none exists, hash-bound inputs, and the
exact output. A Brief deliverable marked `required` cannot use manual mode.
Manual mode records a non-reproducibility disposition. Final generation inputs
and semantic comparison both bind the active locked manuscript.

QA is keyed by the approved deliverable path, not by format alone. Each Brief
deliverable requires its own QA record even when several deliverables share the
same adapter.

Syntax-only validation never establishes layout acceptance.

## Degradation rule

- `READY`: required operation and QA evidence are available.
- `DEGRADED`: a non-critical fidelity or automation capability is missing and
  the user-approved acceptance policy permits a reduced claim. This never
  authorizes a final gate whose adapter marks the missing QA group as blocking.
- `BLOCKED`: an output cannot be safely generated, rendered, visually checked,
  or compared as required.

State exactly what was not tested. Do not substitute a different renderer
without recording the change in the adapter snapshot.

Host-native operations use a `platform-capabilities.json` file inside the
project evidence boundary. The capability probe records its SHA-256 and the
canonical capability-map SHA-256; state validation reparses the file and
requires the observed platform entries to match it exactly.
Claims labeled `process_probe` are independently reproduced at validation time
against the fixed capability-name and operation map; copied or invented probe
objects are rejected.
The platform snapshot's own capture time must satisfy the Profile freshness
window; wrapping old platform evidence in a new outer snapshot does not renew it.
Derived aliases are also closed: only `microsoft_word` or `libreoffice` may
establish `rtf_capable_editor`, and only `microsoft_excel` or `libreoffice` may
establish `spreadsheet_application`. The validator rejects every other alias
name/parent pair.
