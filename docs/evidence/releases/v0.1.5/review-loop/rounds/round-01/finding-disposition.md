# Finding Disposition - Round 1

Core validation of the Critic candidates.

| Finding | Severity | Disposition | Reason |
| --- | --- | --- | --- |
| F-001 | High | confirmed | Reproduced: no `v0.1.5` tag exists (`git tag -l` shows v0.1.0–v0.1.4), yet README/CATALOG/INSTALLATION and two test files asserted a published state. In-scope bounded repair: candidate framing until the tag exists, published framing in the post-release commit. |
| F-002 | High | confirmed | Reproduced: api.md line 4 said v1.0.5 while SKILL.md/guides say v1.0.6. In-scope bounded repair: sync api.md to the SKILL.md sentence. |
| F-003 | Medium | confirmed | Reproduced: discovery red on missing review-record links while the receipt pre-asserted PASS. In-scope bounded repair: reworded gate row; the committed candidate must carry a green suite run. |

All three are confirmed, in-scope, bounded repairs — permitted under the
frozen Charter (no scope expansion). The Core directed the Producer to
apply them.
