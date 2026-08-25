# Host evidence schema

Supply a current, structured observation rather than a remembered inventory.
This is a bounded input contract, not a claim that every Agent Host exposes
these fields.

```json
{
  "schema_version": "1",
  "host": {"id": "opaque-current-host", "observed_at": "2026-08-24T00:00:00Z"},
  "models": [
    {
      "id": "opaque-model-id",
      "selectable": {"state": "available", "evidence": {"kind": "host-runtime", "locator": "host model selector", "observed_at": "2026-08-24T00:00:00Z"}}
    }
  ],
  "capabilities": {
    "subagents": {"state": "unknown", "evidence": null},
    "per_agent_model_selection": {"state": "unknown", "evidence": null},
    "parallelism": {"state": "unknown", "evidence": null},
    "reasoning_control": {"state": "unknown", "evidence": null},
    "session_threads": {"state": "unknown", "evidence": null},
    "worktrees": {"state": "unknown", "evidence": null},
    "concurrency_cap": {"state": "unknown", "limit": null, "evidence": null}
  }
}
```

## Claim rules

- `state` is exactly `available`, `unavailable`, or `unknown`.
- An `available` or `unavailable` claim has evidence from the current Host:
  `kind`, `locator`, and `observed_at`. `host-runtime` is the preferred kind
  for a selectable model or scheduling capability.
- `unknown` has `evidence: null`; it is not an error and must not be filled
  from model memory, a static role file, or an unverified user assertion.
- A `concurrency_cap` is available only when `limit` is a positive integer and
  the evidence verifies that limit. Do not derive it from a count of models or
  a documentation maximum.
- `session_threads` means the Host can create a fresh execution context. It
  does not alone prove an independent Reviewer; reviewer independence also
  requires a distinct, read-only assignment and no implementation ownership.
- `worktrees` means the Host can create and use isolated worktrees for the
  task. A generic filesystem or source-control tool does not prove this claim.

Reject a false inventory claim by normalizing it to `unknown` and recording
why: missing evidence, malformed evidence, stale evidence, contradictory
evidence, or a non-host source. Do not delete the rejected claim from the
evidence ledger.
