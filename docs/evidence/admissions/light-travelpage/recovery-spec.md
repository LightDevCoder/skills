# Bounded recovery Spec verification

Date: 2026-09-13. Reviewer: independent Spec agent. Reviewed HEAD: `d13b229164dcc54244e0f27ac8716ea5ed095912`; fixed comparison: `836e086..d13b229`. Inputs: `.project-review/resume-01.md`, `REQUIREMENTS.md` revision 1, and only the confirmed retry snapshot / nearby recovery handoff implementation. No implementation, credentials, cloud resource, or native browser changes were made.

The specific successful-POST / failed-follow-up-GET snapshot delivery defect is repaired, and mixed batches deliver the successful ledger result regardless of adapter order. One adjacent recovery path still violates requirement 3's preservation of edits during failed saves. This is a bounded finding, not a whole-Skill acceptance verdict.

## Normalized findings

```json
[
  {
    "id": "SPEC-RESUME-01",
    "severity": "P1",
    "axis": "Spec",
    "title": "Keep the original pending mutation's draft identity after a rejected second save",
    "requirement": "REQUIREMENTS.md item 3: preserve edits during polling and failed saves; resume scope: clear only submitted draft and preserve later edits",
    "file": "candidate/light-travelpage/assets/template/ledger.js",
    "lines": [1814, 1815],
    "related_lines": [1132],
    "observed": "After a 20 CNY bill commits but loses its response, change the draft to 25 CNY and submit normally once more. The adapter rejects this second submission before sending because the first mutation remains pending. The catch block nevertheless replaces recoveredMutation with the newer generation/afterSuccess. Retrying the original mutation then succeeds, and recoverSavedMutation treats the unsent 25 CNY draft as the confirmed draft and clears it. This reproduces with the following GET unavailable.",
    "expected": "The successful exact retry must consume the 20 CNY snapshot while retaining the later 25 CNY amount and note, because that newer submission never reached the server.",
    "evidence": "node --test evidence/recovery-spec-test.mjs: 6 passed, 1 failed; final test asserts retained amount 25 but observes empty string. The same test confirms only one initial POST was sent before retry and confirms the saved bill remains 2000 cents.",
    "repair_direction": "Bind recovery metadata to the actual pending request, and do not replace it when an ordinary save is rejected by the existing-pending guard. Preserve the original generation and afterSuccess until that request is resolved."
  }
]
```

## Independent evidence

Environment: macOS, Node `v26.7.0`, installed Happy DOM `20.14.5`. The retained, self-contained probe is `evidence/recovery-spec-test.mjs`. It uses the actual `runtime-storage.js`, `ledger.js`, `sync-ui.js`, authentication and `server/sync.js` handler; the database is an in-memory Node SQLite D1 interface shim. Fetch is intercepted locally to deliver requests into that handler, lose a response only after the handler has committed, reject later GETs, and fail a separate todo adapter. Authentication values are synthetic test-only strings. This is Node/DOM/SQLite integration evidence, not live D1 or native-browser evidence.

Commands and results:

- `npm test` from `candidate/light-travelpage/assets/template`: 23/23 passed (17 core, 6 Happy DOM).
- `node --test evidence/recovery-spec-test.mjs`: 6/7 passed. The six passing combinations cross unchanged/later-edited bill drafts with no second adapter, failed second adapter first, and failed second adapter last.
- Negative control before adding the seventh case: `REVIEW_BASELINE=836e086 node --test evidence/recovery-spec-test.mjs` used the same six independent cases and the historical source without changing working files: 0/6 passed. No-second-adapter and failed-adapter-last cases missed the confirmed snapshot; failed-adapter-first cases never reached the successful ledger retry.

Each of the six passing cases verifies server commit before the synthetic response loss, byte-identical retry bodies, no revision increment on receipt replay, confirmed bill delivery to the ledger, appropriate draft clearing/preservation, and a subsequent deliberate new bill save without deleting or duplicating the earlier confirmed bill. The no-second-adapter cases also verify that sync-ui attempted a GET, displayed `GET unavailable`, and still consumed the POST state first. Mixed batches retain a visible retry button and the other adapter's pending/error state while delivering the ledger success. The seventh case adds an ordinary resubmit of the newer draft before recovery and reveals the remaining loss of that draft.

No claim is made about full admission, production deployment, or unrelated Skill requirements.
