# Execution plan schema

Return one Markdown plan with these sections in this order.

```text
Status: READY | NEED-INPUT | BOUNDARY
Route: multi-model-multi-agent | single-model-multi-agent | single-model-single-agent
Reason: <evidence-based route choice and simplifications>

## Evidence ledger
| Claim | State | Evidence | Used for | Rejection or limitation |

## Role assignment
| Role | Assigned model or context | Responsibility | Independence and mutation boundary |

## Ownership matrix
| Change unit | Exact files | Explorer | Implementer | Reviewer | Dependencies |

## Execution waves
| Wave | Units | Maximum concurrent workers | Preconditions | Completion artifact |

## Review and merge gates
- Reviewer: <fresh independent context, or BLOCKED with smallest unblock>
- Merger: <exactly one role and integration rule>
- Final authority: <named acceptance authority>

## Unknowns, blocked gates, and one required decision (if any)
```

For `single-model-single-agent`, list Controller self-checks under **Review and
merge gates** as `self-check`, never `Reviewer`. For a partial `BOUNDARY`, mark
only the affected gate blocked and retain executable serial work separately.

The response has no hidden assignments: every active Explorer, Implementer,
Reviewer, and Merger appears in the role and ownership tables. A plan cannot
claim more concurrent workers than the evidenced cap. A role cannot be
assigned a model that the evidence ledger does not show as available.
