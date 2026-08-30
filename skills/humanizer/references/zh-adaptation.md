# Chinese adaptation (中文适配层)

Read this file whenever the text to humanize is Chinese or contains Chinese
spans. It adapts the pattern book in `SKILL.md` to Chinese. The core rules —
keep every claim, never invent facts, match the voice — are
language-independent and always apply, and the rewrite process and output
modes are unchanged.

Pattern numbers below refer to the English pattern book in `SKILL.md`.

## 1. Rule overrides for Chinese

| Pattern | Chinese handling |
| --- | --- |
| §14 Em and en dashes | Inserted paired dashes (插语式 `——……——`) are a strong AI tell: split them into sentences or replace with commas/colons. A single `——` doing real work (explanation, topic shift, sound lengthening) is legitimate Chinese punctuation — keep it. Do not apply the English blanket ban to Chinese; apply the paired-insertion test. |
| §17 Title case in headings | Not applicable — Chinese has no letter case. Ignore this pattern; flag nothing for it. |
| §19 Curly quotation marks | Inverted for Chinese: `“”` (U+201C/201D) **is** the standard Chinese quotation mark. Never convert Chinese `“”` to straight quotes `"`. The pattern applies only to English text. |
| §26 Hyphenated word pairs | Not applicable — Chinese has no hyphenation. Ignore. |

## 2. Pattern mappings

| Pattern | Chinese manifestation |
| --- | --- |
| §3 Shallow -ing analysis | Sentence-tail elaboration clauses tacked on for fake depth: “……，彰显了……”、“……，确保了……”、“……，反映了……”、“……，为……注入了……”、“……，奠定了……基础”。 Cut the tail or state the fact plainly. |
| §8 Avoiding is/are | “作为/充当/标志着/代表着” replacing plain “是/有”: “该公司作为行业领先企业” → “该公司是行业领先企业”（或重组句子）。 |
| §7 Overused AI words | Use the Chinese vocabulary list in §3 below instead of the English list. The English list still applies to English words inside Chinese text. |
| §10 Forced groups of three | Same behavior: 排比三连（“更高效、更智能、更安全”）。 Prefer two items or restructure. |
| §9 Not X but Y | “不仅……而且……”、“这不仅仅是……，更是……”、“不是……而是……” when formulaic. Keep a genuine contrast that states new information. |
| §1, §4 Inflated importance; sales language | “标志着……的重要里程碑”、“具有深远意义”、“致力于打造”、“匠心打造”、“卓越”、“顶级”、“赋能”（装饰性用法）。 |
| §5 Vague sources | “专家表示”、“业内人士认为”、“有分析指出”、“研究表明”（说不出是哪项研究）。 |
| §21 Knowledge-limit disclaimers and guesses | “据公开资料显示，推测……”、“详细信息暂未披露，但有观点认为……”. State what is unknown, or cut. Never dress a guess as a fact. |
| §23 Filler phrases | “值得注意的是”、“需要指出的是”、“众所周知”、“在这个问题上”。 |
| §25 Generic positive endings | “未来可期”、“让我们拭目以待”、“相信……会越来越好”。 Cut; end on the last concrete fact. |
| §27, §28, §31–§33 Deeper truth, announcements, punchlines, sayings, fake candor | Same behavior: “说到底，问题的本质在于……”、“让我们深入探讨”、“每一个字都掷地有声”式金句、“X 是 Y 的钥匙”式格言、“说白了”、“讲真”。 |

## 3. Chinese AI vocabulary to watch

High-frequency words in post-2023 Chinese AI text. They usually co-occur;
a cluster is evidence, a single word is not:

- **Connectors:** 此外、与此同时、值得注意的是、需要指出的是、综上所述、总而言之、总的来说、首先/其次/最后（机械分点）
- **Inflated verbs:** 赋能、助力、深耕、布局、凸显、彰显、聚焦、夯实、沉淀（比喻义）
- **Business buzzwords:** 抓手、闭环、颗粒度、底层逻辑、组合拳、打法、拉齐、对齐（会议用语）、生态（泛用）、赛道
- **Inflated nouns:** 格局、画卷、篇章（比喻义）、新篇章、里程碑、底色、注脚、缩影、护城河（比喻义）
- **Formulaic praise:** 卓越、非凡、无缝、极致、匠心、一站式、全方位、多维度、全链路

## 4. Do not invent details (特别强调)

Chinese AI text often "fixes" a vague claim by adding a plausible-looking
specific — a year, an institution, a number, a quote. That is fabrication,
not humanizing. A vague claim becomes a plain claim（删掉装饰，或直接说明
“没有公开来源”）, never an invented specific. If a sentence needs a real
detail to work, ask the user for it or write the plain version.

## 5. False positives specific to Chinese

- **四字成语与四字格本身不是痕迹。** 成语是正常中文。只有当四字套话成串堆砌、替代具体信息时才是 tell。
- **公文与新闻通稿的固定格式不是痕迹。** “根据……规定”、“特此通知”、“据悉”是文体要求，不属于 §21 或 §5。
- **正式文体的被动结构不必强改。** 中文公文、学术文本的被动与无主句常是文体常态，§13 只在主动更清楚时使用。
- **单次“——”或省略号有合法用法。** 见 §14 覆盖规则；不要见标点就删。
