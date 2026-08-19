# `kb-init` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/kb-init/`
- Invocation type: user-invoked only
- Profile: `review-loop` `agent-skill`
- Stable-release boundary: v0.1.6 contains `kb-init` as the ninth package
- Admission status: `PASS` under the full admission path; released in v0.1.6 as the formal kb-init package

## Evidence summary

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Source | PASS | Owner-authored first-party design; no copied third-party code or assets; no `ATTRIBUTION.md` required. |
| Structure | PASS | Package `SKILL.md`, `agents/openai.yaml`, eight reference documents, `evals/evals.json`, and a contract test are present and non-empty; contract test runs `OK`. |
| Invocation | PASS | `disable-model-invocation: true` in `SKILL.md`; `allow_implicit_invocation: false` in `agents/openai.yaml`; explicit-only section forbids self-trigger and user-invoked Skill chaining. |
| Fast-track classification | PASS | Prompt-only fast track does not apply because the interview/implementation can use tools, call the model-invoked `research` capability, and create files or state. |
| Documentation synchronization | PASS | README, catalog, installation guide, maintenance baseline, changelog, and bilingual guides consistently describe nine packages on the current branch and eight in released v0.1.5; all relative links resolve. |
| Independent review | PASS | Fresh read-only Evaluator confirmed eligibility, package structure, invocation boundary, documentation synchronization, and contract-test result; final verdict `PASS`. |

Full records are under [review-loop/](review-loop/).

Local-source and structural evidence is admission evidence. The v0.1.6
released-tag install verification is recorded under
docs/evidence/releases/v0.1.6/.
