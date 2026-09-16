# Attribution — humanizer

This package is a Light first-party capability adapted from upstream Skills
(ownership gate: substantially transformed into a distinct, owned capability).

- **Source repository:** [https://github.com/blader/humanizer](https://github.com/blader/humanizer)
- **Original Skill path:** `SKILL.md` (pattern book, voice calibration, detection guidance, rewrite process, output modes)
- **Pinned revision:** `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5` (upstream `main`, 2026-08; `SKILL.md` self-reports `metadata.version: 2.11.2`; nearest tag `v2.11.1` plus 2 commits)
- **License:** MIT — Copyright (c) 2025 Siqi Chen — see upstream `LICENSE`. The MIT notice is preserved below; no original authorship is claimed for the upstream material.
- **Chinese vocabulary reference:** [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) (MIT — Copyright (c) 2026 歸藏), pinned `91f3d394db8419c20d67ebe22a96cf8fee0a404b`. Its Chinese AI-vocabulary list and pattern mappings informed `references/zh-adaptation.md`. That translation is based on an upstream generation (~2.8.x) whose worked examples modeled invented specifics; this package follows the upstream 2.9+ anti-fabrication guidance instead and keeps none of those examples.
- **Ultimate source:** Wikipedia ["Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup (CC BY-SA; used as the documented conceptual source via both repositories above).

## Transformation summary

ADAPT — upstream pattern content is preserved; the following Light changes
were applied:

1. Frontmatter aligned to collection conventions: bilingual trigger
   description; the upstream `license` and `metadata.version` fields are
   recorded here instead of in `SKILL.md`.
2. Added the concise **Language routing** section (English / Chinese / mixed
   input) ahead of the pattern book.
3. Added `references/zh-adaptation.md`: a thin Chinese adaptation layer —
   rule overrides for §14/§17/§19/§26, Chinese pattern mappings for the
   remaining patterns, a Chinese AI-vocabulary list, an explicit
   anti-fabrication rule for Chinese rewrites, and Chinese-specific
   false-positive exemptions.
4. Adapted upstream `agents/openai.yaml` for Light host discovery: updated
   `short_description`/`default_prompt` for the bilingual scope and set
   `policy.allow_implicit_invocation: true` (model-invoked).
5. Added this `ATTRIBUTION.md`.
6. No runtime dependency on `https://github.com/blader/humanizer` or
   `https://github.com/op7418/Humanizer-zh` remains; the package is
   self-contained.

Verification: `SKILL.md` frontmatter `name: humanizer` matches the package
directory; `agents/openai.yaml` is valid; all pattern sections and examples
outside the numbered changes above are carried from the pinned upstream
revision unchanged.

## MIT notice (blader/humanizer)

MIT License

Copyright (c) 2025 Siqi Chen

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

## MIT notice (op7418/Humanizer-zh, Chinese vocabulary reference)

MIT License

Copyright (c) 2026 歸藏

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
