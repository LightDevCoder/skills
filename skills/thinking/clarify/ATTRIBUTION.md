# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/productivity/grill-me/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream entry package was inspected as a reuse candidate. It is a one-line
wrapper around the upstream grilling Skill and was not copied into this package.

## First-party transformation

`clarify` is an owner-authored, explicit-only standalone entry with a distinct
Light contract. It invokes the locally defined model engine `socratic` only
after an explicit `$clarify` request, returns an inspectable
current/resolved/unresolved state, separates fact gaps from user decisions,
and stops. It explicitly avoids automatic user-invoked chaining, fact-work
execution, project mutation, and formal SPEC generation. It contains no
upstream files, scripts, templates, or verbatim wrapper instruction.

ADAPT per SPEC §15: replaced the upstream `grill-me → grilling` wrapper with
`clarify → socratic`, added Light Unknown routing, and kept the Skill concise
with supporting docs in `references/`.

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
