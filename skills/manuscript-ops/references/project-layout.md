# Project layout and path mapping

## New Project route

Create the smallest standard structure that supports the approved Brief:

```text
<root>/
|-- AGENTS.md
|-- docs/
|   |-- manuscript-brief.md
|   |-- outline.md
|   |-- source-map.md
|   `-- glossary.md
|-- sources/
|   |-- authoritative/
|   `-- reference-only/
|-- manuscript/
|-- assets/
|-- deliverables/
|-- archive/
`-- .manuscript-ops/
    |-- state.json
    |-- routing-snapshot.json
    |-- project-profile.json
    |-- batch-manifest.json
    |-- format-registry.json
    |-- platform-capabilities.json
    |-- capability-snapshot.json
    |-- format-qa/
    |-- sources/
    |   `-- source-register.tsv
    |-- reviews/
    |-- snapshots/
    `-- gates/
```

Create only approved folders. Keep temporary renderings and caches in a declared
ignored QA location, never beside user deliverables.

## Existing project

Preserve every existing path. Do not move, rename, or normalize files merely to
match the standard tree. Map logical roles in `project-profile.json`, for
example:

```json
{
  "paths": {
    "brief": {
      "value": "planning/approved-scope.md",
      "origin": "资料发现",
      "evidence": "existing approved planning record"
    },
    "deliverables": {
      "value": "output/final",
      "origin": "用户决定",
      "evidence": "user-designated delivery directory"
    }
  }
}
```

## Separation rules

- `docs/` holds human-readable intent, outline, source map, and terminology.
- `.manuscript-ops/` holds machine state, snapshots, batch definitions, adapter
  results, review evidence, and gate receipts.
- `sources/authoritative/` may support factual claims.
- `sources/reference-only/` may inform structure or presentation but cannot
  support factual claims unless reclassified with evidence.
- `manuscript/` holds readable source drafts.
- `deliverables/` holds user-facing outputs only.
- `archive/` holds superseded immutable milestones according to retention rules.

## Source intake

Record every source before use: stable ID, authority class, adapter ID, path or
URL, owner/publisher, retrieval time, SHA-256 of the local file or retained
capture, privacy class,
permitted use, exclusions, typed `metadata_json`, and
`derived_artifacts_json`. Typed metadata must satisfy the selected source
adapter in `format-registry.json`. Preserve original inputs unless the user
explicitly authorizes movement or deletion.

Batch dependencies reference the stable ID with a typed use and purpose.
`factual` use resolves only to `authoritative`; `incoming` resolves only to
`incoming-draft`. Missing IDs, blank exclusions, or authority mismatches block
the batch.
`permitted_use` is a comma-separated subset of `factual`, `context`, `style`,
and `incoming`. `exclusions` is `none` or a disjoint subset using those same
tokens. A batch use must be permitted and must not be excluded.

Web, email, image/scan, audio, video, and transcript sources require provenance.
OCR and transcription are derivatives and never silently replace their source.
