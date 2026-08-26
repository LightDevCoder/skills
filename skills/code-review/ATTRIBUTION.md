# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/engineering/code-review/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream package was inspected as a reuse candidate. It is a two-axis
read-only reviewer that pins a user-supplied fixed point, validates the diff
is non-empty, locates the originating Spec and repository standards, spawns
parallel sub-agents (Standards with repo standards plus a twelve-smell Fowler
baseline, Spec against the Spec's requirements), and aggregates their reports
under separate `## Standards` / `## Spec` headings with a per-axis worst-issue
summary. No files, templates, or verbatim instructions were copied.

## First-party transformation

`code-review` is retained as a Light read-only specialist reviewer with the
same two-axis, parallel-sub-agent, separate-aggregation contract, but it is
exposed as a `review-loop` / `project-review` composable reviewer. It keeps
the Standards axis (repo standards override the fixed Fowler baseline, smells
are labelled judgement calls, tooling-enforced rules are skipped) and the Spec
axis (missing Spec yields “no spec available”), adds the explicit guard
`Do not invoke /code-review or spawn additional agents — perform this review
directly` to each sub-agent brief to prevent the known fan-out bug, and
records that the specialist never self-repairs, never runs the repair loop,
and never decides the final `PASS` / `FAIL` / `BLOCKED` — `project-review` Core
owns the diagnosis, disposition, bounded repair gate, and final verdict per
its `software` Profile; `review-loop` is the convergence engine. Detailed
prompts, the smell catalogue, and examples are kept in `references/` rather
than in `SKILL.md`.

ADAPT per SPEC §15: retained the upstream two-axis parallel review and
per-axis aggregation, but mapped the reviewer to Light's first-party tracker
and `project-review` / `review-loop` lifecycle, added the fan-out guard,
and separated the concise entry from the detailed workflow in `references/`.

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
