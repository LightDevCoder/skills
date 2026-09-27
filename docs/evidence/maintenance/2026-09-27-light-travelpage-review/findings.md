# Finding registry

## F-001 — Template map disclaimer persisted in geographic mode
- Axis: Spec
- Severity: Medium
- First observed: Round 1, candidate a16e9c210ba19448913e5724d20f1beed7872b83
- Disposition: confirmed; repaired in 4e35eda3d9a522842ab33d2f6a53437c582070f2; independent code-review recheck fixed.
- Evidence: `build-map.mjs` replaces the blank template's schematic disclaimer in geographic mode; the geographic fixture contains that exact disclaimer and checks the generated output. The generated SVG description also has a geographic default.

## F-002 — Mobile zoom assumed a left-side itinerary inset
- Axis: Spec
- Severity: Medium
- First observed: Round 2, candidate 9a104360fbd27c193fbfda6025890217f0c77e91
- Disposition: confirmed; repaired in 4e35eda3d9a522842ab33d2f6a53437c582070f2; independent code-review recheck fixed.
- Evidence: `mapZoomScrollLeft` locates the inset from the configured projection frame; a right-side inset fixture verifies initial visibility.

Standards axis: `Findings: []` in all three code-review runs. No active findings after Round 3.

## F-003 — Chinese collection records missed the updated behavior
- Axis: Agent-Skill package structure / collection metadata
- Severity: Medium
- First observed: Fresh independent Evaluator after Round 3, candidate 4e35eda3d9a522842ab33d2f6a53437c582070f2
- Disposition: confirmed; repaired at `45c04b65edfcb6ad17c0f1dd00d536c5fcbea93e`; focused independent generic review marked fixed.
- Evidence: `CATALOG.zh-CN.md` lacked the desktop and geographic behavior and stated an outdated invocation type; `CHANGELOG.zh-CN.md` lacked this unreleased change. Charter AC-5 and `docs/MAINTENANCE.md` update synchronization matrix.

## F-004 — Maintenance note linked review files before archival
- Axis: Agent-Skill documentation integrity
- Severity: Medium
- First observed: Focused read-only document review after F-003 repair, candidate 45c04b65edfcb6ad17c0f1dd00d536c5fcbea93e
- Disposition: confirmed; repaired at `0616b6a8bbaa03dd58a9bc1e0500ca4955c880ec`; focused independent generic recheck marked fixed. Terminal review links will be added after the records exist.
- Evidence: The maintenance note linked files in a review archive that did not yet exist. Charter AC-5 and the repository maintenance link requirements apply.
