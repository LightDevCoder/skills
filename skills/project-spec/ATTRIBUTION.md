# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/engineering/to-spec/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream package was inspected as a reuse candidate. It synthesizes the
current conversation and codebase understanding into a formal SPEC with a
seam sketch, a templated SPEC body, and a publish-to-tracker step. No files,
templates, or verbatim instructions were copied.

## First-party transformation

`project-spec` is an owner-authored Light planning stage with a narrower,
tracker-local contract. It consumes already-clarified material — a
`project-clarify` handoff (`Project clarification handoff`) or a
`decision-map` map plus resolved ticket `## Answer` records — and does not
reopen an interview. It adds a local inspection pass only to ground
Implementation/Testing decisions in inspectable source locations (domain
glossary, ADRs, existing seams) and to decide whether a truly blocking
user-owned decision forces a return to `project-clarify`. It retains the
upstream seam-first idea but generalizes the SPEC template to Light's
general-purpose project types (code, document, configuration, Skill) and
publishes to the local-markdown location `.scratch/<feature>/spec.md` per
`docs/agents/issue-tracker.md`. It hands off to `project-tickets` via the
verified SPEC path rather than auto-chaining.

ADAPT per SPEC §15: retained the `to-spec` synthesis-and-publish model but
mapped it to Light's `project-clarify`/`decision-map` outputs, local tracker
publishing, and concise-entry plus supporting-docs package shape.

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
