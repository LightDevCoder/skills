# Core Review Rubric

The Core does not impose artifact-specific review axes. Select only the axes,
evidence requirements, specialist reviewers, severity guidance, acceptance
conditions, and failure cases supplied by the frozen Charter and selected
Profile. Record omitted optional axes only when the Profile asks for that
decision.

## Generic Profile

The generic Profile adds no axes or special evidence requirements. The Core
still checks that the baseline is frozen, evidence labels are accurate,
candidates have dispositions, repairs stay in scope, state is resumable, and
the final verdict follows the stopping rules.

## Severity

- `Critical`: the finding prevents safe or meaningful acceptance of the frozen
  goal.
- `High`: a required frozen criterion is not met.
- `Medium`: a material in-scope gap that must be resolved before `PASS` unless
  the Charter records an approved exception.
- `Low`: a limited-impact observation that does not block the verdict unless the
  Charter says otherwise.

Severity is impact against the frozen baseline, not estimated repair effort.

## PASS gate

The Evaluator may return `PASS` only when every frozen criterion and selected
Profile requirement has evidence of the correct class, all required validation
scenarios were actually performed or have an approved exception, no confirmed
blocking finding remains, the Charter did not silently change, and the required
independence declaration is recorded.
