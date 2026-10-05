# Namespace migration Producer evidence

Date: 2026-10-06 (Asia/Taipei). Acceptance source: local SPEC Revision 2 at `.scratch/light-skill-namespace/spec.md`. Fixed implementation baseline: `7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6`. This record does not issue independent acceptance.

| Criterion | Current evidence | Boundary / remaining gap |
| --- | --- | --- |
| A1 | `identity-policy-audit.json`; collection discovery tests: 36 canonical packages, 12 renames, 24 retained names | structural |
| A2 | input UI/policy snapshot vs current audit: 12 Light display labels, canonical default prompts, unchanged disable/implicit policies | structural; actual Host selector remains unobserved |
| A3 | existing ask-light behavior/semantic/approval tests migrated; ready-ticket returns light-implement, approval remains separate; light-code-review and socratic factRoutes updated | behavioral fixtures, not Host runtime |
| A4 | new namespace tests: all 12 old same-name packages rejected as Light availability; mixed roots resolve exact new Light paths; old callable names rejected | public validator behavioral fixtures; actual content installation in A8 |
| A5 | research project type, task words, docs/research and artifactSignals.research preserved; AgentConfigResult.handoff stays a field, its READY value is light-implement | static audit plus public behavior tests |
| A6 | Ports retain methods; metadata/name/Light calls and attribution fact only. Mature kb-init has exactly 3 named frozen-file changes with old hashes retained and inverse-token byte verification | fixed-baseline source diff and frozen-name-amendments.json; independent two-axis rechecks clean |
| A7 | bilingual current references, all 12 mappings and recovery guide; existing tracked release history and released changelog segments unchanged; commands blocked where no published migration source exists | documentation/structural evidence; preflight detected existing unrelated release |
| A8 | actual Skills CLI 1.7.0, two orders × default/copy: 74 packages with Light 36 and fixed upstream 38, matching complete intended payloads; actual default symlinks observed for additional project-local target | installation; final exact 79d15fd snapshot reconciled; parent independently rehashed installed payloads and all current Light package files |
| A9 | actual Codex CLI 0.160.0 explicit Light/upstream and app-server attempts stop before model/discovery with Operation not permitted | not tested / required runtime evidence BLOCKED; no global config/Skills writes authorized or performed |
| A10 | full pytest previously 519 passed; focused final path/doc/release checks pass; unittest 156 passed; compileall and public docs gate pass; final implementation tests and two-axis review complete; fresh Evaluator pending | tests and review are separate evidence types |
| R1 | bilingual draft with required title/12 mapping/upgrade/other changes and Light-only public wording | blocked draft; release version occupied and remote baseline has advanced |
| R2 | no candidate Receipt; drafts relocated to release-draft to preserve existing released v0.2.6 paths | cannot form same-version official release candidate |
| R3 | remote preflight confirms existing annotated v0.2.6 and formal Release; see publication-blocker.md | BLOCKED by D7; no push, new tag, or candidate CI |
| R4 | candidate coexistence installation is A8 only | not tested for published candidate; existing v0.2.6 points to a different tree |
| R5 | no namespace Release or post-release receipt created | BLOCKED; existing travel release is not namespace publication |

## Commands and results

- `python3 -m pytest -q`: 519 passed before final blocker-document presentation changes. Subsequent full pass will be appended with its exact implementation identity.
- Focused namespace/frozen/implement/socratic/manuscript check: 52 passed; later release/manuscript/namespace check: 106 passed; final catalog/discovery check: 7 passed.
- `python3 -m unittest discover -s tests`: 156 tests, OK after candidate-version test uses isolated directories.
- `PYTHONPYCACHEPREFIX=/private/tmp/namespace-20261006-pycache python3 -m compileall -q skills tests scripts`: exit 0. Initial compile using the inherited cache prefix was denied outside writable roots; no compilation PASS was claimed for that attempt.
- `python3 scripts/check_public_docs.py`: PASS; `git diff --check`: exit 0. Local links inspected separately.
- Travel-page existing changes: generated disposable template using create.mjs, lockfile `npm ci`, `npm test`, `node tests/prepare-build-fixture.mjs`, `npm run validate`, `npm run build`, and nonempty `dist/assets/tickets/fixture.png` check; all commands completed successfully. This covers this fixed checkout's travel implementation, not newer remote AI/handbook changes.

## Historical path handling

`tests/check_helpers.py:relocated_path` maps only immutable old evidence paths to canonical current packages. `package_dir` still accepts only the actual name. No discoverable or callable old-name alias is added. The 3 frozen kb-init amendments preserve their baseline hashes and must reverse exactly to original bytes; all other frozen files keep the original guard.

## Publication/environment limits

The fixed SPEC baseline is behind remote main and remote v0.2.6 is a different published version. The candidate remains local. No remote CI, tag push, namespace Release or receipt is claimed. A9 requires actual Codex discovery, entry selection and dependency-read evidence before candidate PASS; installer/static observations do not satisfy it. Version/baseline changes belong to the decision owner.

## Final implementation snapshot checks

Implementation: `79d15fd410f1295f84d9761d66c601895ff9ee31`. Full pytest: **521 passed in 40.37s**. Unittest: **158 tests, OK**. Compilation, public docs gate and diff whitespace checks passed. Travel generated fixture: **37 tests passed**, validation returned ok, PDF preview PNG built despite nonfatal font cache warnings.

Final A8: [installation-final.json](installation-final.json) binds all four fresh cases to exact implementation and fixed upstream; its SHA-256 is `bbc939787007adc984101f36489b94d4111274f42b7d5c7df2578abf957d2676`. Light package manifest is `fe58ea6e7af0e7ffa4b52fc484c9b78cdbffc6e8c22cf1a28b0596779c191041` (36 packages, 367 intended files). Parent reran every installed payload hash comparison for both targets and reconciled every current Light file to this manifest. Host limitations remain in [installation-host.md](installation-host.md).

Independent review convergence: [review-summary.md](review-summary.md). A2 actual selector and A9 actual discovery/invocation/dependency reads remain unobserved; final acceptance must not be PASS. R3 remains blocked by an existing published tag; R4/R5 have not occurred for the namespace candidate.
