# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/engineering/to-tickets/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream package was inspected as a reuse candidate. It breaks a plan,
spec, or conversation into tracer-bullet vertical slices with blocking edges,
quizzes the user, and publishes one file per ticket locally (or native blocking
links on a real tracker) with a frontier of unblocked, unclaimed work. No
files, templates, or verbatim instructions were copied.

## First-party transformation

`project-tickets` is an owner-authored Light planning stage with a local-
markdown contract. It verifies a formal SPEC at `.scratch/<feature>/spec.md`
(normally from `project-spec`) before drafting slices; retains the upstream
tracer-bullet, dependencies, ready work, and parallelizable groups model and
the user-quiz loop; supports the upstream wide-refactor expand–contract
exception in supporting docs; and publishes to the local-markdown location
`.scratch/<feature>/issues/NN-<slug>.md` with tracker-native `Blocked by:` /
`Status:` fields compatible with `docs/agents/issue-tracker.md:21` Wayfinding
operations. It keeps `SKILL.md` as a concise execution entry and places the
detailed ticket template, dependency rules, and examples in supporting files.

ADAPT per SPEC §15: retained the `to-tickets` slice/depend/quiz/publish model
but mapped the tracker to Light's local markdown issues, added the
`project-spec → project-tickets` handoff validation, and separated the
concise entry from the detailed workflow in `references/`.

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
