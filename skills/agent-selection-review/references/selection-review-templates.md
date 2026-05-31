# Agent Selection and Review Templates

This file contains only output templates and common pattern cues for `agent-selection-review`. The seven veins, six forms, double-axis orthogonality rules, and Compound Error definition are in `agent-double-axis-framework.md`.

## Common pattern cues

| Coordinate | Patterns/mechanisms to consider |
|---|---|
| Perception × Route | Context Triage: first decide which context deserves to enter the model |
| Perception × Chain | Retrieval → rerank → summarize/compress → task input |
| Memory × Chain | Working memory / event log / short-term state |
| Memory × Route | Retrieve preferences, facts, past cases, or procedural skills by task |
| Memory × Loop | Failure Journals / Experience Replay; use failure experience to correct later attempts |
| Reasoning × Chain | Structured Reasoning: stable decomposition and step-by-step synthesis |
| Reasoning × Route | Complexity Routing: simple tasks take a fast path, complex tasks take a slower path |
| Reasoning × Orchestrate | Plan-and-Execute: planner decomposes, executor performs, synthesizer summarizes |
| Reasoning × Loop | Iterative hypothesize, validate, revise; must have a stop condition |
| Action × Route | Tool Dispatch / risk-based action routing |
| Action × Orchestrate | Planned execution, compensation steps, transactional tool calls |
| Reflection × Chain | Generator-Critic: a critic checks evidence and criteria after generation |
| Reflection × Loop | Self-Heal Loop: diagnose, patch, and retry after failure; must limit iterations |
| Collaboration × Parallel | Parallel Specialists: security/performance/testing experts inspect in parallel |
| Collaboration × Hierarchy | Hierarchical Delegation: parent agent owns the goal, child agents own local work |
| Governance × Route | Approval Gate: risk-tiered auto-execute / human-approve / deny |
| Governance × Chain | Audit Trail / Hooks Pipeline: record, validate, and intercept before/after execution |
| Governance × Orchestrate | Observability Harness: centrally collect traces, logs, metrics, and alerts |
| Governance × Hierarchy | Multi-level sandbox, permission-inheritance control, blast-radius isolation |

## A. Agent Pattern Selection Card

```markdown
# Agent Selection Card: [System/Scenario Name]

## 1. Requirement summary
- Goal:
- Users/callers:
- Key constraints: latency / cost / accuracy / compliance / explainability / recoverability

## 2. Seven-vein scoring
| Cognitive function | None/Light/Heavy | Rationale | Required in v1? |
|---|---:|---|---|
| Perception |  |  |  |
| Memory |  |  |  |
| Reasoning |  |  |  |
| Action |  |  |  |
| Reflection |  |  |  |
| Collaboration |  |  |  |
| Governance |  |  |  |

## 3. Primary topology decision
- Recommended primary topology:
- Why not the alternatives:
- Main error-propagation path:

## 4. v1 pattern set (keep to 3-7 items)
| Priority | Coordinate | Pattern/mechanism | Problem solved | Failure mode | Validation method |
|---:|---|---|---|---|---|

## 5. Intentionally empty cells
| Empty coordinate/capability | Reason for omission | When to upgrade |
|---|---|---|

## 6. Minimum viable governance
- Permission boundary:
- Approval gate:
- Audit/trace:
- Stop condition / circuit breaker:

## 7. v2 upgrade path
- Trigger conditions:
- New coordinates:
- Expected benefit:
- New risks:
```

## B. Agent Architecture Review

```markdown
# Agent Architecture Review: [Proposal Name]

## Overall assessment
- Verdict: pass / conditional pass / not recommended for launch yet
- Largest risk:
- Highest-priority fix:

## Double-axis map
| Coordinate | Existing design evidence | Assessment | Risk |
|---|---|---|---|

## Seven-vein gaps
| Function | Current strength | Target strength | Gap | Recommendation |
|---|---:|---:|---|---|

## Error propagation and test strategy
| Topology | Main error | Must-test scenarios | Observability metrics |
|---|---|---|---|

## Pre-launch blockers
1.
2.
3.

## Evolution recommendations
- v1:
- v2:
- v3:
```

## C. Evolution Roadmap

```markdown
# Agent Evolution Roadmap: [System/Scenario Name]

## Current state
- Current primary coordinates:
- Current largest bottleneck:
- Capabilities that should not be upgraded yet:

## Upgrade trigger conditions
| Trigger signal | Explanation | Required new coordinate |
|---|---|---|

## Phased roadmap
| Phase | New coordinate | Benefit | New risk | Validation/rollback method |
|---|---|---|---|---|

## Upgrades not recommended
| Candidate upgrade | Reason to defer | Re-evaluation condition |
|---|---|---|
```
