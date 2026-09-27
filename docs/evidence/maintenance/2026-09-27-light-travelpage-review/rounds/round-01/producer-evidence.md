# Producer evidence — Round 1

- `source`: Skill candidate `a16e9c210ba19448913e5724d20f1beed7872b83`, fixed point `7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6`, package `skills/productivity/light-travelpage/`.
- `structural`: `quick_validate.py` returned `Skill is valid!`; package remained model-invoked, with linked `references/` and executable `assets/template/`.
- `behavioral`: Project `npm run build && npm test && npm run validate` passed, 38 tests. Fresh template site created with `node scripts/create.mjs`, `npm ci`, `node tests/prepare-build-fixture.mjs`, `npm run build`, `npm test`: 39 tests passed, including geographic positive and out-of-bounds negative fixture.
- `manual`: At a 1200 px browser viewport, the second flight card became visible and index `2 / 2` after both next-button and mouse-wheel actions. Hokkaido coastline and itinerary inset rendered; 390 px view showed mobile map and zoom control. A physical touch device was not tested; overflow scrolling CSS remains present.
- `review`: Independent code-review returned Standards `Findings: []`, Spec F-001. This is candidate evidence, not acceptance.
