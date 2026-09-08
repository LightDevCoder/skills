# Agent Config maintenance verification — 2026-09-08

## Scope and frozen sources

User-authorized maintenance: repair five collection-review findings, include the existing Pi adapter work, and push both repositories to main without a tag or new release.

- Skills source baseline: `0cad18a4bdc4c0affefd7a852982ee168186bda0`; reviewed implementation: `39bbc3d`.
- Companion source baseline: `9838442a8da177f0f180ae2a18ef91a316c5fa63`; reviewed implementation: `3c97180` (includes `0cbd4ac`, `be67e41`, `e10311a`).
- Requirements: the user-approved review findings, package invocation contracts, repository maintenance/review policy, and the Pi limitations in the companion's `docs/adapters/pi.md`.
- Exclusions: a new release, global host reconfiguration, live Pi task execution, and acceptance of every supported host. Pi configuration mutation is restricted to the source-verified version 0.85.1; extension dispatch remains unconfirmed.

## Findings and dispositions

| Finding | Disposition and evidence |
| --- | --- |
| Codex TOML edits can change named profiles and falsely validate | Fixed with parsed root reads and bounded root edits; regression covers profiles, quoted keys, multiline strings/arrays and malformed input. |
| Unknown preview can validate successfully | Fixed: canonical expected configuration or known preview required; preview workspace/host must match; adapter remains bound to the preview. |
| highest-supported chooses a hardcoded lower level | Fixed: selects the final evidenced level; regression includes max and nonstandard ordered values. |
| agent-config can auto-start a user-invoked stage | Fixed: return to an active authorized caller, or recommend the explicit next invocation and stop. |
| Codex environment contaminates MCP tests | Fixed: reset actual runtime indicators in test setup; full suite passes inside Codex without a caller-side environment workaround. |
| Pi extension, version, scope, provider, trust and thinking evidence | Existing Pi implementation hardened against installed source documentation; dedicated negative cases preserve these boundaries. |
| Pi provider drift and per-model thinking priority | Fixed in be67e41: independent pair resolution and effective target override validation; wrong provider and inherited override regressions. |
| Pi same model name under different providers shares effort | Fixed in e10311a: target provider/model lookup and full active-pair comparison. |
| Pi rejects canonical default reasoning policy | Fixed in 3c97180: canonical default supported, configured retained as alias; ReasoningSchema-based rendering regression. |

## Verification evidence

- **Structural/contract:** `python3 -m pytest -q` in Skills: **303 passed**; collection discovery/composition checks included. `git diff --check` clean.
- **Executable behavior with isolated fixtures:** `npm test -- --reporter=dot` in companion at 3c97180: **642 passed**, 30 test files. Dedicated Pi suite: **24 passed**.
- **Build:** `npm run typecheck` and `npx tsc` succeeded. Runtime schema-validation dependencies are direct production dependencies.
- **Installation:** final compiled companion packaged with `npm pack --ignore-scripts --json --pack-destination <temporary-dir>`, installed into a new prefix with `npm install --prefix <fresh-prefix> --ignore-scripts --no-audit --no-fund <tarball>`. Independent server process completed MCP initialize, listed exactly eight canonical tools, and rejected an unknown preview via the public tool interface.
- **Skill copy/discovery:** clean copies of agent-config and implement retained their SKILL.md, agents/openai.yaml and resources. This is file-level installation evidence, not an actual host activation claim.
- **Invocation scenario inspection:** independent Spec reviewer checked standalone READY, active implement READY, NEED_PROJECT_TICKETS and companion-absent cases against the final prompt. This is scenario inspection, not live execution of downstream stages.

## Independent review

- Standards reviewer (fresh Sol/High): STANDARDS-1 rechecked fixed at 3c97180; no remaining findings.
- Spec reviewer (separate fresh Sol/High): provider/override findings rechecked fixed at e10311a; no remaining findings. The final canonical-default patch was separately checked by Standards.
- An earlier Pi audit and an earlier final Evaluator attempt hit usage limits. Neither is counted as a successful final evaluation.
- Final independent Evaluator (`acceptance_final`, fresh Sol/High, independence: full): **Findings: []** for skills@39bbc3d and companion@3c97180; no unmet frozen maintenance criteria. Producer accepts this bounded repair. This does not accept every supported host or a new release.

Local tarball verification does not verify an installation command against a new release. Existing versions and tags are unchanged.
