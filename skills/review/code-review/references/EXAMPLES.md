# Code-review examples

## Example — Aggregate report shape

Direct invocation: `$code-review main`

> Fixed point `main` resolves at `a1b2c3`. `git diff main...HEAD` is non-empty
> (3 files, 120 added / 8 removed). `git log main..HEAD --oneline` lists
> `Add session middleware` and `Fix expiry guard`.

Standards sources found: none documented (fallback to smell baseline only).
Spec source: `.scratch/auth/spec.md` — section `Session middleware must
reject expired tokens with 401` (line 22).
Previous findings: none.

Report:

```markdown
## Standards

- id: F-001
  state: new
  severity: low
  location: src/auth/middleware.ts:14
  problem: possible Mysterious Name — `handle(input)` hides token-to-session mapping
  reason: smell baseline; quoted hunk `function handle(input) { … }`
  suggestion: rename or isolate the mapping
- id: F-002
  state: new
  severity: low
  location: src/auth/middleware.ts:18
  problem: duplicate token guard also appears in api/routes.ts:44
  reason: Duplicated Code baseline; quoted hunk `if (!token) return 401`

Under 400 words.

## Spec

- id: F-003
  state: new
  severity: medium
  location: src/auth/middleware.ts:27
  problem: expired tokens return bare 401 without `code: EXPIRED`
  reason: Spec line 22 requires a 401 body with `code: EXPIRED`

Under 400 words.

Standards: 2 findings; worst: Mysterious Name. Spec: 1 finding; worst:
partial EXPIRED body.
```

No merge across axes occurred. The worst per-axis summary is separate, as
required; no single winner was picked.

## Example — No spec available

> Spec axis source: none found via `docs/agents/issue-tracker.md` or the
> passed argument.

```markdown
## Standards

- (one cited finding) …

## Spec

Findings: []
No spec available — skipped.

Standards: 1 finding; worst: … Spec: 0 findings; no spec available.
```

The empty Spec axis is reported rather than inferred from the code.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing →
  **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's
  conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.

## Negative — empty diff

> Fixed point `HEAD` against `HEAD` yields an empty diff.

Outcome: report `empty diff — no reviewable change at this fixed point` and
stop. Do not expand the window to manufacture a diff.

## Negative — bad ref

> Fixed point `branch/does-not-exist` fails `git rev-parse branch/does-not-exist`.

Outcome: report the bad ref and stop. Do not retry inside sub-agents.
