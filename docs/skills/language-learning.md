# `language-learning` user guide

[中文指南](../zh-CN/skills/language-learning.md)

The behavior authority is [skills/language-learning/SKILL.md](../../skills/language-learning/SKILL.md).
This page explains usage without creating a second contract.

## Purpose

`language-learning` is a user-invoked tutor for any target language. It runs
through six study modes: daily lessons, flashcards, conversation practice,
grammar decoding, progress quizzes, and immersion translation. It reuses the
session's target language, learner level, native language, and recently
learned vocabulary instead of re-asking, and it corrects selectively rather
than teaching through a fixed template each time.

## Invoke

Select it explicitly:

```text
$language-learning
```

Or invoke a mode directly, for example:

```text
$language-learning Spanish, flashcards for: perro, gato, casa
```

It must not run automatically. It adapts to the level already established in
the conversation, defaults to beginner when the level is unknown, and keeps the
learner producing the language.

## Expected results

- **Success:** the requested mode completes its contract — a 30-minute lesson,
  one card per given item, a held conversation, a decoded rule, a 10-question
  quiz, or an adapted translation with comprehension questions.
- **Boundary:** a mixed or unclear request routes to one primary mode and offers
  the second instead of inventing a new capability.
- **Failure:** re-asking for language, level, and mode on every invocation, or
  listing every learner mistake, violates the teaching contract.

`language-learning` never invokes another user-invoked Skill. A durable
continuation record requires a separate user choice such as `handoff`; final
acceptance remains owned by `project-review`. An incomplete or `BLOCKED`
admission does not change the package contract.

## Verification and release state

Run [the package tests](../../skills/language-learning/tests/) and inspect
`agents/openai.yaml` for `allow_implicit_invocation: false`. The prompt-only
fast-track `PASS` admission evidence is recorded in the
[admission record](../evidence/admissions/language-learning/README.md).

`language-learning` is released in v0.1.2. Install it with
`npx skills add LightDevCoder/skills --skill language-learning --yes --copy --agent '*'`,
refresh, and confirm discovery without the source checkout under
[the installation policy](../INSTALLATION.md).

## Behavior sources

This skill is an original first-party design. No upstream Skill code or prompt
text is copied into this package.
