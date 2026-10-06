# v0.2.7 namespace producer evidence

- Acceptance source: `.scratch/light-skill-namespace/spec-revision-3.md`, Revision 3, SHA-256 `f64a5f266015961b362812b24148557aca57371ba6a6dc4b8bacb680e51b2ed4`.
- User decision: 2026-10-06, “我看了一下确实，应该发0.2.7”. Previous Revision 2 and its blocked acceptance remain historical.
- Fixed point: `97adf5f319b8800b6635057434dcb4aeda2ddecd`; published v0.2.6 retained.
- Scope: exactly twelve canonical name migrations; 24 retained identities, 36 packages; no aliases/global migration.

## Structural and source observations

`input.json` freezes all baseline identities and invocation/UI policy from the actual remote-main Git tree. `identity-policy-audit.json` compares all 36 policies and categories and twelve UI labels/default prompts against this baseline. All assertions pass; these are structural observations, not actual Host selection.

`baseline-preservation.json` compares all 224 tracked files in the travel package and published release directories against the baseline Git tree. Every byte is retained. No travel functionality is newly implemented by this migration.

## Behavioral checks

`python3 -m pytest -q skills/productivity/ask-light/tests/test_namespace_migration.py tests/test_manuscript_dependencies.py tests/test_functional_closure.py tests/test_release_integrity.py tests/test_external_boundary_guard.py`: 128 passed in 27.19 s. Includes old-only/mixed source fixtures, approval/ready-ticket routes, canonical optional dependencies, finite historical readers, exact frozen token amendment restoration and executable command-boundary negative cases.

The merged unchanged travel template passes `node --test tests/*.test.mjs` (80 assertions-bearing tests) in disposable `/private/tmp/light-namespace-travel-v027-20261006/site`, using the prior installed dependency directory. The generator `node --test skills/productivity/light-travelpage/scripts/tests/create.test.mjs` passes four tests. Logs remain beside that site. These are automated behaviors, not new browser/host/provider claims.

## Pending evidence

Full collection rerun passes 534 pytest tests (43.32 s) and 158 unittest tests (22.690 s). Compilation succeeds with `PYTHONPYCACHEPREFIX=/private/tmp/namespace-v027-pycache`; public documentation checks and `git diff --check` pass. The earlier merge-wide runs failed only on copied draft relative links (533 pytest and 157 unittest checks passed); those links and stale copied-version wording were repaired, then all checks rerun. Logs are `.scratch/light-skill-namespace/evidence/v027-{full-repaired,unittest-repaired,docs-repair}.log`. A8 actual Skills CLI matrix is complete for `ce4898e782f20cb185067fab5721aec6be9b31e4`; independent Standards/Spec/Evaluator review is pending. A2 actual Host selector and A9 actual invocation/dependency reads remain required. Prior initialization failures are retained under namespace-v0.2.6; the current Host diagnosis is separate. Remote CI/tag/pinned-source installation/Release/receipt are not completed. No release receipt exists for v0.2.7.

## Exact frozen-candidate installation

Actual Skills CLI 1.7.0 (distribution SHA-256 `fde68534019765fb69510a0038ca7df2810a6ffed4c26fef9beabdcf6cc6701c`) installed the complete candidate and fixed upstream revision in four fresh projects (two orders × default/copy), targeting Codex and Claude Code directories. All eight commands exited zero. Each target retains 74 packages / 489 files: Light 36 / 386, comparison source 38 / 103. Default Claude targets are 74 correct links to canonical packages; copy targets are independent directories. Codex's canonical root uses directories in both modes. No Claude runtime observation is claimed.

The parent independently rehashed every installed file and every current Light package against the full intended sources, independently checked upstream HEAD/clean state, all commands and link identities, and confirmed `installation-parent-recheck.json`. `installation-final.json` retains exact argv, exit results, file manifests and source paths. Light full-payload manifest SHA-256: `5a682a3356a501a1285735560ef2261d7bc81cf6c18c31292c54e44ef167926b` (sorted compact JSON of name → path → file SHA-256). Temporary root: `/private/tmp/light-namespace-host-20261006`; projects `v027-<order>-<mode>`. This is candidate-source installation A8, not public v0.2.7 installation R4 or Host invocation A9.

## Release integrity boundary

`python3 scripts/verify_release_integrity.py --tag v0.2.7 --release-commit ce4898e782f20cb185067fab5721aec6be9b31e4 --stage prepared` passed the mechanical clean-tree/tag-absence/manifest/navigation/notes/receipt-absence checks. Its log is `.scratch/light-skill-namespace/evidence/v027-integrity-local.log`. The script does not evaluate A2/A9 or independent acceptance; this success does not advance the lifecycle to PREPARED before required acceptance is satisfied.

## Current runtime diagnosis and unblock

`installation-host.md`, `host-diagnosis.json` and `host-raw/` preserve the current read-only endpoint investigation and preceding startup failures. The installed desktop server has no observed documented local listener; no private pipe, daemon, global Skills or configuration mutation was attempted. EPERM root cause remains unestablished. `observe-external.py` in the temporary evidence root is syntax-checked and prepared for an external Terminal; it only rehashes installed files and requests initialize/skills/list under a write restriction. It is not yet externally executed and would establish discovery only, not UI selector or explicit invocation/dependency selection. The user has been asked to run this bounded environment diagnostic while independent evaluation continues.

## External Terminal result and final diagnostic

The user ran the prepared observer and returned `initialized: false`, `project_skills: 0`, `No response to request 1`. Parent independently read the saved command, zero responses, exit 1 and EPERM stderr. A bounded backtrace diagnostic reproduced failure; its stack contains `File::set_times` but no failing path. Scoped macOS deny-log query returned no matching entry. See `host-external/README.md` and raw records. Required Host evidence remains missing; no global permission or acceptance criterion was weakened.

## Resumed real Host evidence

The owner approved the two exact runtime metadata exceptions. [Real Host observations](runtime/README.md) now supply actual initialization, two explicit source invocations, Light dependency reads, and genuine native labels. The package payload is unchanged. The earlier BLOCKED verdict remains historical; the new fresh evaluation is pending. The temporary transport adapter and earlier incomplete wrapper comparison are disclosed, not hidden or converted into PASS.

## Resumed verifier checks

The manual released-source workflow and first-party verifier fulfill R4 in an actual fresh hosted Linux user without repurposing HOME/CODEX_HOME. Focused positive/negative/mutation tests pass six cases. The expanded full suite passes 540 pytest tests (35.71 s), 164 unittest tests (20.290 s), compilation and public documentation checks. No future remote install result is claimed. Independent software axes and fresh final acceptance remain pending.

## Approved selected-host verification repair

The owner approved the concrete scope amendment and one fourth/final verifier recheck on 2026-10-06. The generic CLI registry parser was removed. Pinned/default whole installs declare Codex and Claude Code; native Codex global and three renamed Codex singles remain. Omitted declared targets and undeclared selections are rejected. The all-Agent exploratory preflight is not claimed byte-identical: Eve serializes/filters frontmatter. Both selected targets independently match 36 packages/386 files.

Target `cb61cee4eb89cc22aa07509dd5bef48929fa4d34` passes eight focused behavioral tests, 542 pytest tests (36.50 s), 166 unittest tests (20.717 s), compilation, documentation checks and diff checks. Full logs: local `.scratch/light-skill-namespace/evidence/v027-selected-{full,unittest}.log`. Fourth software recheck and fresh whole-candidate evaluation are separate observations; actual released-source R4 remains pending the public tag.
