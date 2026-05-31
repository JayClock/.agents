# Agent Double-Axis Framework: Seven Veins × Six Forms

This file is the shared theoretical foundation for Agent architecture skills. Read it when you need to map Agent requirements, designs, or source components onto engineering coordinates; each skill still defines its own workflow.

## 1. Core principle

The double-axis framework separates Agent design into two orthogonal questions:

- **Vertical axis: Cognitive function** — Which resource budget is the Agent managing?
- **Horizontal axis: Execution topology** — How do information, capability, control, and errors flow?

A complete judgment should be written as: `Cognitive Function × Execution Topology`.

Why this matters:

- The same cognitive function has different engineering consequences under different topologies. For example, `Reasoning × Chain` has predictable cost and latency, but an early decomposition mistake cascades; `Reasoning × Loop` can self-correct, but cost, latency, and stop conditions are harder to control.
- The same topology means different things under different cognitive functions. Orchestrate in reasoning may be Plan-and-Execute; in governance it may be an Observability Harness; in collaboration it may be manager-worker.
- Saying only memory, tool, loop, subagent, or guardrail is not enough; explain which vein it serves, which error-propagation path it chooses, and what the tradeoff is.

## 2. Seven veins: cognitive functions

| Vein | Resource budget | Diagnostic question | Common mechanisms/components | Failure when missing |
|---|---|---|---|---|
| Perception | Attention budget | What enters the model, and what stays outside? | context builder, RAG, repo map, file index, rerank, context triage | token/attention runaway |
| Memory | Continuity budget | What is retained, retrieved, updated, or forgotten across steps/sessions? | conversation history, event log, state store, summary, long-term memory | continuity runaway, or stale information dragging the system down |
| Reasoning | Uncertainty budget | How does the system decompose, judge, trade off, verify, and backtrack? | planner, router, task graph, prompt strategy, structured reasoning | judgment runaway, or overthinking everything |
| Action | Irreversibility budget | Which tools can be called, and which external states can change? | tool registry, tool dispatcher, executor, runtime, code edit, shell, API call | external-world state runaway |
| Reflection | Correction budget | How does the system check, critique, revise, retry, and stop? | validator, critic, test runner, retry loop, self-heal, experience replay | errors go unnoticed, or the system over-patches and rationalizes itself |
| Collaboration | Division-of-labor budget | Who does the task, and how are context, tools, and responsibility separated? | subagent, handoff, multi-agent router, specialist workers | scale runaway, context pollution, responsibility confusion |
| Governance | Trust budget | How are permission, approval, audit, traceability, and accountability handled? | permission policy, sandbox, approval gate, audit log, observability, hooks | trust runaway; the more capable the system, the higher the risk |

Recommended build order: first stabilize the inner loop (Perception/Memory/Reasoning/Action), then add reliability (Reflection), and finally expand production readiness (Collaboration/Governance). However, any Agent that can change the external world must discuss governance.

## 3. Six forms: execution topologies

| Form | Verb | Best fit | Main error-propagation path | What to inspect during reverse engineering/review |
|---|---|---|---|---|
| Chain | pass | Stable steps, clear dependencies, definable inputs/outputs | Cascading error; upstream mistakes are prettified downstream | pipeline, sequential steps, prompt chain, intermediate schema |
| Route | choose | Classify then dispatch; complexity/risk/cost tiering | Misrouting; once the entrance is wrong, later stages struggle to recover | classifier, router, policy decision, model/tool selection, fallback |
| Parallel | fan out | Multiple independent branches, then merge | Aggregation error; a poor merge parallelizes noise | fan-out/gather, workers, merge, dedup, rank, vote |
| Orchestrate | coordinate | A central node understands the whole, decomposes, dispatches, and synthesizes | Decomposition error; wrong plan boundaries make execution drift harder | planner/executor, task graph, coordinator, synthesizer |
| Loop | iterate | Generate, evaluate, revise until acceptable | Compound error; over-reflection, drift, or failure to stop | max iterations, stop condition, critic signal, retry/self-heal |
| Hierarchy | delegate | Multi-level delegation where parents own goals and children own local work | Error amplification or failed isolation; permission/context inheritance can avalanche | subagent tree, handoff boundary, context isolation, permission inheritance |

Choosing a topology means choosing how errors move.

## 4. Double-axis mapping rules

For every important matrix entry, answer at least:

1. **What: cognitive function** — Which resource-budget problem does it solve?
2. **How: execution topology** — How do information, capability, control, and errors flow?
3. **Why: engineering consequence** — Does it reduce cost, improve quality, isolate risk, support recovery/audit, or fail fast?
4. **Failure: failure mode** — Will errors cascade, misroute, aggregate, decompose incorrectly, compound, or leak through hierarchy?
5. **Evidence / Validation** — Source code, tests, docs, business constraints, launch metrics, or acceptance cases.

Generic matrix fields:

| Coordinate | Mechanism/component | Engineering benefit | Error propagation/failure mode | Evidence or validation method |
|---|---|---|---|---|
| `Function × Topology` |  |  |  |  |

## 5. Compound Error check

Long-chain Agents suffer from compounded step-level error rates. When useful, roughly estimate: `overall success rate ≈ per-step success rate ^ number of steps`. For example, 95% per-step accuracy over 10 steps is about 60% overall.

When evaluating any pattern, ask whether it does at least one of the following:

1. **Reduce steps**: do not split into ten steps when one reliable step is enough.
2. **Improve per-step quality**: better context, clearer tool schema, stricter output format, or more reliable test signal.
3. **Add verification**: insert critic, tests, external fact checks, or audit points into intermediate states.
4. **Fail fast**: stop on obvious failure instead of continuing with dirty state.

If it does none of these, it may be decorative.
