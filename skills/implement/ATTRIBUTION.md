# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/engineering/implement/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream package was inspected as a reuse candidate. It is a short
user-invoked implementation Skill that reads a spec or ticket, drives
`tdd` at pre-agreed seams (red→green), typechecks and tests during the run,
runs `code-review` at close-out, and commits one bounded diff per ticket.
No files, scripts, templates, or verbatim instructions were copied.

## First-party transformation

`implement` is an owner-authored Light execution stage adapted to a
general-purpose bounded executor. It keeps the upstream five-beat rhythm
(read the work item → tdd at seams → typecheck/tests → review) but widens
the scope beyond code to document, configuration, research artifact, Skill,
and generic project task. It adds a general flow
`inspect relevant context → agent-config when useful → execute (branch by
artifact type) → verify → review-loop when appropriate`, routes
`code → tdd → code-review` and `non-code → artifact → generic-review` as
composable calls, and explains how to consume `project-tickets`' local
single-ticket files (`.scratch/<feature>/issues/NN-<slug>.md`) one per fresh
context window — without duplicating the full instructions of
`agent-config`, `tdd`, `review-loop`, `code-review`, or `generic-review`
into `SKILL.md`. Detailed workflow and artifact-type examples live in
`references/`.

ADAPT per SPEC §15: retained the `implement` read/seam/tdd/review rhythm
and one-ticket-per-context discipline from the upstream baseline, but mapped
the executor to Light's `.scratch` tracker, introduced host-aware routing via
`agent-config`, generalized the verification and review branches for
non-code artifacts, and separated the concise entry from the detailed
workflow in `references/`.

## MIT notice

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
