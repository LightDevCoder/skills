# Round 1 findings (resumption record)

Independent agents: `/root/standards_review` and `/root/spec_review`. This is the Producer's durable summary of their returned findings, not a verbatim replacement for the agent messages.

- STD-01, P1: damaged runtime backup lacking a snapshot could normalize into an empty replacement and delete shared data.
- STD-02, P2: server accepted unsupported currency codes which ledger normalization dropped, risking later deletion.
- SPEC-01, P1: active member/settings/bill editors prevented conflict rebase; explicit refresh could report success without enabling retry.
- SPEC-02, P1: retrying a pending todo/ticket mutation cleared an unrelated ledger draft.

All four are accepted for repair. Independent re-review is pending.
