# Reusable source review method

## Purpose

Assess source material and return a source-backed Method Contract.

## Triggers

Use when a user supplies a workflow source that may contain a repeatable method.

## Invocation

The resulting capability is user-invoked.

## Inputs

Source transcript, provenance, project rules, and exact commands or paths.

## Ordered Method

1. Inspect the source and separate durable procedure from one-off narration.
2. Extract decisions, constraints, failure modes, resources, and outputs.
3. Verify every required field and report the smallest source gap.

## Decisions

Promote only when every required method field is evidenced.

## Constraints

Preserve exact commands and do not invent missing fields.

## Failure Modes

Return BLOCKED for missing source evidence or conflicting invocation evidence.

## Outputs

An internal Method Contract, learning summary, or precise BLOCKED record.

## Resources

none

## Verification

Run the source-sufficiency hook and confirm the result is internally complete.
