# Clarify examples

## Example 1 — Vague idea → frontier round

**User**: `$clarify I want a tool that helps me learn Japanese`

Ask `socratic`:
- Current understanding: goal is a Japanese learning tool, no constraints.
- Open decisions: D1 target audience (beginner vs intermediate), D2 platform
  (mobile vs web), D3 session format (guided practice vs open immersion) — all
  independent.
- Frontier: D1, D2, D3.

**Return**:

> I understand that you want a Japanese-learning tool. Let’s settle a few
> independent choices in one round.
>
> Q1 — Audience
> A. Beginner
> B. Intermediate
> Recommended: A. Beginner gives the first version a clearer learning path.
>
> Q2 — Platform
> A. Mobile
> B. Web
> Recommended: A. Mobile suits daily practice, if that matters to you.
>
> Q3 — Session format
> A. Guided practice
> B. Open immersion
> Recommended: A. Guided practice is more tractable for a first tool.

The next normal user reply continues this same session; `1A, 2B, 3A` or prose
are both accepted.

## Example 2 — Fact gap is not a user question

**User**: `$clarify Should we use the DeepL API or Google Translate? I don't
know their pricing.`

- This contains a fact (pricing) that `research` can answer, not a pure user
  tradeoff.
- Socratic records: `Dependency: DeepL vs Google pricing → research`.
- `clarify` reports:
```text
Dependencies and fact-finding gaps: API pricing (external fact → research
not yet authorized); blocks decision API choice. Current frontier: (blocked)
Next step: separately authorize fact work or choose to defer the API decision
```
It does not invent pricing or convert the fact into "Which do you prefer?"

## Example 3 — No SPEC, explicit stop

After two turns, frontier is empty except for a blocked dependency.
`clarify` does not create a formal SPEC. It reports the gap and recommends:
"If pricing is needed, run `$research`; if this becomes a project, run
`$project-clarify`" and stops.

## Example 4 — Shared-understanding confirmation

After the user settles the final decisions:

> So the tool is for beginner Japanese learners, starts as a mobile app, uses
> short guided practice rather than open-ended immersion, and progress stays
> local for the first version. If that matches what you mean, this
> clarification is complete.

"Yes" completes the session. A correction updates the decision state and asks
the next useful round without another `$clarify` invocation.