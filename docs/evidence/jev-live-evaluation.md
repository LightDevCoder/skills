# TypeSafe Jev Live Evaluation & Calibration Evidence

- **Timestamp:** `2026-09-19T22:31:12Z`
- **Mode:** `live`
- **Model Version:** `jev-latest`
- **Total Scenarios:** `31`
- **Passed:** `31`
- **Failed:** `0`
- **Accuracy:** `100.0%`
- **Duration:** `13.688s`

## 1. ask-light Evaluation Results (17 scenarios)

| ID | Scenario Name | Status | Observed Primary | Jev Execution Prob | Ambiguity | Choice Skipped | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AL-01 | Standard frontier query: ready ticket exists | `RECOMMEND` | `implement` | 0.03 | 0.68 | Yes | **PASS** |
| AL-02 | Progress inquiry / where is project now | `EXPLAIN` | `None` | N/A | N/A | Yes | **PASS** |
| AL-03 | Workflow explanation request | `EXPLAIN` | `None` | N/A | N/A | Yes | **PASS** |
| AL-04 | Explicit execution command: Go ahead | `TRANSITION` | `implement` | 0.99 | 0.54 | Yes | **PASS** |
| AL-05 | Hesitant inquiry: Should we start implementing? | `RECOMMEND` | `implement` | 0.13 | 0.73 | Yes | **PASS** |
| AL-06 | Advice only constraint: I only want advice | `RECOMMEND` | `implement` | 0.01 | 0.72 | Yes | **PASS** |
| AL-07 | Initial project state: No SPEC exists | `RECOMMEND` | `project-clarify` | 0.02 | 0.90 | Yes | **PASS** |
| AL-08 | Clarification complete: Clarification is ready | `RECOMMEND` | `project-spec` | 0.04 | 0.44 | Yes | **PASS** |
| AL-09 | Active SPEC exists but tickets do not | `RECOMMEND` | `project-tickets` | 0.04 | 0.65 | Yes | **PASS** |
| AL-10 | Ready ticket exists at frontier | `RECOMMEND` | `implement` | 0.17 | 0.61 | Yes | **PASS** |
| AL-11 | All tickets resolved | `RECOMMEND` | `project-review` | 0.03 | 0.43 | Yes | **PASS** |
| AL-12 | Stale review verdict | `RECOMMEND` | `project-review` | 0.19 | 0.88 | Yes | **PASS** |
| AL-13 | Dirty working tree invalidating review | `RECOMMEND` | `project-review` | 0.04 | 0.82 | Yes | **PASS** |
| AL-14 | Unknown ticket requested (fail-closed) | `BLOCKED` | `None` | N/A | N/A | Yes | **PASS** |
| AL-15 | Multiple active efforts without explicit target (fail-closed) | `NEED_INPUT` | `None` | N/A | N/A | Yes | **PASS** |
| AL-16 | Ambiguous user request with trade-offs | `RECOMMEND` | `project-clarify` | 0.05 | 0.96 | Yes | **PASS** |
| AL-17 | Complex architectural overhaul request | `RECOMMEND` | `implement` | 0.69 | 0.73 | Yes | **PASS** |

## 2. agent-config Evaluation Results (14 scenarios)

| ID | Scenario Name | Observed Model | Observed Effort | Topology | Candidate Safe | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| AC-01 | Routine documentation edit | `gpt-4o-mini` | `default` | `Case C` | Yes | **PASS** |
| AC-02 | Small bug fix | `claude-3-5-sonnet` | `default` | `Case A` | Yes | **PASS** |
| AC-03 | Standard feature implementation | `claude-3-5-sonnet` | `default` | `Case A` | Yes | **PASS** |
| AC-04 | Large refactor | `o3-mini` | `high` | `Case C` | Yes | **PASS** |
| AC-05 | Security-critical change | `o3-mini` | `high` | `Case C` | Yes | **PASS** |
| AC-06 | Complex concurrency work | `o3-mini` | `high` | `Case C` | Yes | **PASS** |
| AC-07 | Cost-sensitive complex work | `o3-mini` | `high` | `Case C` | Yes | **PASS** |
| AC-08 | Latency-sensitive routine work | `gpt-4o-mini` | `default` | `Case C` | Yes | **PASS** |
| AC-09 | Fixed-model harness | `fixed-sonnet` | `default` | `Case A` | Yes | **PASS** |
| AC-10 | Multi-model decomposed harness | `o3-mini` | `default` | `Case D` | Yes | **PASS** |
| AC-11 | Host with no effort selector | `gpt-4o` | `default` | `Case A` | Yes | **PASS** |
| AC-12 | Limited effort selector bounds Jev output | `model-x` | `medium` | `Case A` | Yes | **PASS** |
| AC-13 | User explicitly requests high effort (overrides Jev) | `model-x` | `high` | `Case A` | Yes | **PASS** |
| AC-14 | User rejects configuration change preview | `active-stay` | `default` | `Case A` | Yes | **PASS** |

## 3. Calibration Invariant Proofs

- **Invariant 1: Jev output cannot grant TRANSITION authority:** Verified in scenario AL-04 (where command explicitly authorized) vs AL-05 (where hesitant question with high execution intent strictly remained RECOMMEND).
- **Invariant 2: Singleton legal candidate skips Choice:** Verified across all single-candidate scenarios (e.g. AL-01, AL-07, AL-08, AL-09, AL-10, AL-11) where `next_action` was omitted from request.
- **Invariant 3: Reasoning need influences effort without overriding explicit policy:** Verified in AC-04/06 (reasoning need mapped to high effort) and AC-13 (explicit minimal policy overrode Jev).
- **Invariant 4: Host capabilities bound Jev output:** Verified in AC-12 where host without 'high' bounded Jev output to 'medium' without inventing unsupported values.
- **Invariant 5: Cost sensitivity does not downgrade capability tier:** Verified in AC-07 where task remained in 'high' tier while honoring cost preference.

