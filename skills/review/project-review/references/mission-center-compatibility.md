# Mission Center Compatibility

`review-loop` can operate without Mission Center. If the target project has a
`MissionCenter/` directory, keep the two systems complementary:

- Mission Center owns its task lifecycle and task-management artifacts.
- `.project-review/charter.md`, `state.md`, round evidence, and `verdict.md` own
  acceptance state for this review loop.
- A task ID, smoke-test ID, snapshot path, or final verdict path may be linked
  from the other system when the pointer is stable and useful.
- Do not copy a second task board, change Mission Center's task ordering, create
  HUD/visual assets, or require Mission Center to be installed.
- Use Mission Center's recorded verification as Producer evidence only after
  checking that it matches the current Charter revision and actual project state.

If the Mission Center integration is unavailable, record `Mission Center:
not used` or the exact access error. It must not change the review verdict.
