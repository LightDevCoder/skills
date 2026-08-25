# Clarify examples

## Example 1 — Vague idea → single frontier question

**User**: `$clarify I want a tool that helps me learn Japanese`

Ask `socratic`:
- Current understanding: goal is a Japanese learning tool, no constraints.
- Open decisions: D1 target audience (beginner vs intermediate), D2 platform
  (mobile vs web) — D2 is independent.
- Frontier: D1, D2 (ask one at a time; recommendation order D1 first).

**Return**:
```text
Current understanding: tool for learning Japanese, no platform or audience yet
Resolved decisions: (none)
Still unresolved decisions: target audience, platform
Dependencies and fact-finding gaps: none
Current question or next step: What learner level should this serve? Beginner
needs guided grammar; intermediate needs immersion tools. Recommendation depends
on scope you prefer.
```
Then stop.

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
`clarify` does not create a formal SPEC. It returns the summary, recommends:
"If pricing is needed, run `$research`; if this becomes a project, run
`$project-clarify`" and stops.

