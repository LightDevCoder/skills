# Clarify routing

`clarify` does not execute fact work. It uses `socratic` for user-owned
decisions and reports fact gaps.

## Routing

Same as `socratic`'s Unknown table (see `../../socratic/references/ROUTING.md`):

- user must decide → `socratic` (frontier question)
- external fact → `research`
- needs experiment → `prototype`
- held by another → `to-questionnaire`

`clarify` keeps the gap visible and stops. It does not auto-launch any of the
fact capabilities. A blocked fact keeps its downstream decision out of the
frontier.

## Composition note

Do not copy `socratic` instructions into this package. Call the `socratic`
engine and use its returned `Current understanding / Open decisions /
Dependencies / Frontier` fields.
