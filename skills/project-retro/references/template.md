# Retrospective Report Template

Use this format when presenting retrospective findings:

```markdown
# Session Retrospective

## Overview
- **Session / Project Scope:** [Brief description of what was built or debugged]
- **Session Duration / Complexity:** [Estimated turns, files modified, or outcome]
- **Friction Trigger:** [Why this retrospective was conducted, e.g. missing guardrails, navigation delays]

## Key Findings (Ordered by Severity)

### 1. [Category]: [Concise Title] (Severity: High / Medium / Low)
- **Observed Friction:** [What happened during the session, with exact file or command references]
- **Root Cause:** [Why the agent struggled or why the error escaped early detection]
- **Actionable Recommendation:** [Concrete fix: e.g. add pre-commit hook, add navigation pointer in AGENTS.md, prune no-op rule]
- **Mechanical vs Judgment:** [Automated check preferred vs prose standard]

### 2. [Category]: [Concise Title] (Severity: High / Medium / Low)
...

## Immediate Next Steps (Pending User Approval)
- [ ] 1. [Specific bounded change, e.g. wire `npm run lint` into CI]
- [ ] 2. [Specific documentation update, e.g. add directory pointer to `AGENTS.md`]
```
