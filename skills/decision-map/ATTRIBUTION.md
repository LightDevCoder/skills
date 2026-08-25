# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/engineering/wayfinder/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream package was inspected as a reuse candidate. It is a full
wayfinding system with a tracker-integrated map, child decision tickets,
blocking, and frontier logic. No files, templates, or verbatim instructions
were copied.

## First-party transformation

`decision-map` is an owner-authored Light stage with a narrower, repo-local
contract. It stores the map and child tickets as local markdown files per
`docs/agents/issue-tracker.md` Wayfinding operations
(`.scratch/<effort>/map.md`, `.scratch/<effort>/issues/NN-<slug>.md`,
`Type:`, `Status: claimed/resolved`, `Blocked by:`, `Frontier`, `Claim`,
`Resolve`). It composes `research`/`prototype`/`socratic`/`to-questionnaire`
per ticket Type and hands off to `project-spec` when fog clears. It does not
reimplement upstream grilling/domain-modeling chains or require an external
issue tracker.

ADAPT per SPEC §15: retained the wayfinder map/ticket/blocking/frontier
model but mapped it to Light's local-markdown tracker and Light's
clarification family (`socratic` for grilling-type tickets).

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
