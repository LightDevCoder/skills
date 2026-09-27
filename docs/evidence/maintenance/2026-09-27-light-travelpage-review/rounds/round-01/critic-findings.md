# Code-review findings — Round 1

Fixed point: `7a98ed9574e6ffb69f533cdcbdf16a22633ef0e6`; candidate: `a16e9c210ba19448913e5724d20f1beed7872b83`.

## Standards
Findings: []

## Spec
- F-001, Medium: `assets/template/scripts/build-map.mjs` inherited the template schematic disclaimer in geographic mode, contradicting the real-outline default. Charter AC-2 and AC-3. Confirmed.
