# Clarify examples

## Example 1 — Vague idea → single frontier question

**User**: `$clarify I want a tool that helps me learn Japanese`

Ask `socratic`:
- Current understanding: goal is a Japanese learning tool, no constraints.
- Open decisions: D1 target audience (beginner vs intermediate), D2 platform
  (mobile vs web) — D2 is independent.
- Frontier: D1, D2 (ask one at a time; recommendation order D1 first).

**Return**:

> I understand that you want a Japanese-learning tool, but the learner level
> is still open. Beginner would need guided grammar; intermediate could focus
> on immersion. I'd start with beginners because it gives the first version a
> clearer learning path. Which audience do you want?

The next normal user reply continues this same session.

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

After the user settles the final decision:

> So the tool is for beginner Japanese learners, starts as a web app, and uses
> short guided practice rather than open-ended immersion. The remaining
> assumption is that progress stays local for the first version. If that
> matches what you mean, this clarification is complete.

"Yes" completes the session. A correction updates the decision state and asks
the next useful question without another `$clarify` invocation.
