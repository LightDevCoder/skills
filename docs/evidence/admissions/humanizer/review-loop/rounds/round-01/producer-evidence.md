# Producer evidence — humanizer admission (round 01)

Producer: collection owner session, 2026-08-30. Evidence classes are labeled
per docs/SKILL_ADMISSION.md ("Static, inferred, simulated, or keyword-only
checks must be labeled by their actual evidence class").

## Structural evidence (scripted)

- Package tree: `SKILL.md`, `references/zh-adaptation.md`, `ATTRIBUTION.md`,
  `agents/openai.yaml`. No placeholder directories, no scripts, no runtime
  executables.
- Verbatim carry check (scripted diff): the `SKILL.md` body, excluding the
  collection frontmatter and the added `## Language routing` section, is
  byte-identical to upstream blader/humanizer `SKILL.md` at pinned revision
  `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5` (`metadata.version: 2.11.2`).
- Frontmatter: `name: humanizer` matches the package directory; description
  is a literal block covering English and Chinese triggers; no
  `disable-model-invocation` (model-invoked); no `license`/`metadata` fields
  (license and pinned revision live in `ATTRIBUTION.md`).
- Link validation: `references/zh-adaptation.md` resolves; remaining links
  are external `https://` or in-page anchors. (Re-asserted by
  `tests/test_collection_discovery.py` across the whole repository.)

## Installation and discovery evidence (scripted, isolated fresh copy)

- Complete package copied to a fresh temporary host root
  (`humanizer-fresh-ld79076x`): file set identical (4 files), all SHA-256
  hashes match, no source-checkout content inside the copy.
- Discovery scan against the copy only (not the source checkout) found:
  `name: humanizer`, description present, model-invoked frontmatter, matching
  `allow_implicit_invocation: true`, all four openai.yaml fields, resolving
  zh reference, `ATTRIBUTION.md` present. Result: PASS.
- Boundary: this is local-source fresh-copy admission evidence, not proof of
  a released install command. The pinned `#v0.2.0 --skill humanizer` command
  becomes verifiable only after the collection tag is re-published and a
  fresh released-repository install is recorded (docs/INSTALLATION.md).

## Behavioral evidence (producer observations, real runs of the rewrite process)

Each fixture was processed by following `SKILL.md` (draft → two audit
questions → final rewrite), with `references/zh-adaptation.md` applied for
Chinese input. Inputs are quoted in full; outputs are the recorded finals.

### Fixture A — English AI-slop (success case). Result: PASS

Input:

> The new analytics platform represents a pivotal shift in the data landscape. Additionally, it boasts a seamless, intuitive, and powerful interface, ensuring that teams can unlock actionable insights. This isn't just a dashboard — it's a decision-making revolution. Industry experts believe it will play a crucial role in the evolving data ecosystem. The future looks bright.

Patterns hit: §1 (pivotal shift, crucial role, evolving landscape), §4
(seamless, unlock actionable insights), §5 (industry experts believe), §7
(additionally, boasts, landscape), §9 (isn't just X, it's Y), §10 (seamless,
intuitive, powerful), §14 (em dash), §25 (future looks bright).

Final rewrite:

> The new analytics platform is a dashboard that gives teams a simpler way to read their data. Its interface is easy to use.

Audit answers: (1) remaining AI patterns — none; the rewrite is thin because
the source made almost no concrete claims. (2) Added/removed claims — added
none; removed the unsourced expert claim and the closing optimism. PASS:
every surviving claim is in the source; no em/en dashes; no §7 words.

### Fixture B — clean human English (boundary case). Result: PASS

Input:

> We shipped the migration on Friday. Honestly, it went smoother than I expected — the trick was running the dedupe pass before the cutover, not after. Two customers wrote in about stale caches. We fixed both by Monday. I still don't love the rollback story, but it's better than last quarter's.

Final rewrite: unchanged (returned as-is).

Audit answers: the em dash is mid-sentence in a first-person voice (a sole
tell, explicitly listed under "What not to flag"); "Honestly" is mid-sentence,
not a standalone opener; "Two customers wrote in about stale caches" is
specific, unusual detail. No cluster of tells. PASS: over-editing avoided;
human details kept.

### Fixture C — Chinese AI-slop (success case, zh adaptation active). Result: PASS

Input:

> 此次产品升级具有重要意义，标志着公司在人工智能赛道上迈出了关键一步。新版本不仅性能卓越，而且操作便捷，更具备强大的生态适配能力，为用户赋能，彰显了公司深耕行业的深厚积淀。新版本秉持“以用户为中心”的设计理念。此外，据公开资料显示，该产品有望成为行业新标杆。未来可期，让我们拭目以待。

Patterns hit (via zh mappings): §1/§4 (标志着/关键一步/赛道/深耕/彰显/卓越),
§9 (不仅……而且……更……), §7 zh vocabulary (赋能/生态/此外), §21+§23
(据公开资料显示), §25 (未来可期/拭目以待).

Final rewrite:

> 此次产品升级改进了性能，简化了操作，并适配了主流生态，设计上“以用户为中心”。

Audit answers: (1) remaining AI patterns — none. (2) Added/removed claims —
added none; removed the sourceless "行业新标杆" claim (§21: state what is
unknown or cut) and the formulaic ending. The Chinese quotation marks
“以用户为中心” were preserved, not converted to straight quotes — the §19
override in `references/zh-adaptation.md` held. PASS.

### Fixture D — fabrication pressure (failure/boundary case). Result: PASS

Input:

> 我们团队最近完成了一次重要的系统重构。

The only humanizing move that keeps every claim is near-invariance. The
rewrite returned:

> 团队完成了一次系统重构。

The tempting repair — adding plausible specifics ("历时三个月、涉及12个微服务、
性能提升40%") — was rejected: §3 of "What to do" and §4 of
`references/zh-adaptation.md` forbid invented details, and the vague claim
became a plain claim instead. PASS: no fabrication under pressure.

## Invocation evidence (structural + declared)

- `SKILL.md` frontmatter has no `disable-model-invocation`;
  `agents/openai.yaml` sets `allow_implicit_invocation: true` — the declared
  model-invoked contract is consistent (re-asserted by the collection
  contract tests).
- Trigger surface: the bilingual description names the English and Chinese
  de-AI tasks; the Language routing section defines behavior per input
  language. Invocation direction: model-invoked capability; it invokes no
  other Skill.

## Attribution evidence (inspectable)

- `ATTRIBUTION.md` records the upstream repository, original path, pinned
  revision `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5` (2.11.2), both MIT
  notices in full (Siqi Chen; 歸藏), the op7418/Humanizer-zh vocabulary
  reference with its pinned revision, the Wikipedia ultimate source, and a
  numbered transformation summary.

## Collection quality (scripted)

- Full repository suite (`python -m unittest discover -s tests`, plus
  package suites) run after registration; results recorded in the admission
  record README.
