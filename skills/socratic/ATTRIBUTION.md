# Attribution

## Source considered

- Repository: `mattpocock/skills`
- Source path: `skills/productivity/grilling/`
- Pinned release: `v1.2.3`
- Pinned commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- License: MIT License
- Copyright notice: `Copyright (c) 2026 Matt Pocock`

The upstream package was inspected as a reuse candidate. It uses a design-tree
interview with a frontier and was not copied into this package.

## First-party transformation

`socratic` is an owner-authored clarification-state engine with a different
public contract. It records current understanding, user-owned open decisions,
fact-finding dependencies, newly resolved decisions, and a dynamically
recomputed frontier. It separates inspectable/researchable/experimentable facts
from user choices; reports unavailable fact-finding capabilities without
inventing work; and forbids execution, automatic user-invoked chaining, and
formal SPEC generation. It contains no upstream files, scripts, templates, or
verbatim interview format.

ADAPT per SPEC §15: retained the frontier interview idea from `grilling` but
replaced its design-tree exposition with a Light decision-state model,
explicit Unknown routing to `research`/`prototype`/`to-questionnaire`, and a
bounded engine boundary compatible with `clarify`/`project-clarify`/
`decision-map`.

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
