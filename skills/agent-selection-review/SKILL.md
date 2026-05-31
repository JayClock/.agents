---
name: agent-selection-review
description: Agent architecture selection and review assistant. Use this skill for business requirements, PRDs, technical proposals, existing Agent designs, launch-risk reviews, and v1/v2/v3 evolution planning. Proactively use this skill whenever the user wants to design an Agent, choose among Agent/Workflow/Multi-agent architectures, review whether a design is robust, decide whether to add memory/reflection/subagents/guardrails/approval/observability, or turn a vague Agent proposal into concrete engineering coordinates. If the user provides a source repository, directory path, or explicitly asks for code evidence around the main loop, context, tools, memory, state, permissions, or sandbox, prefer agent-harness-reverse-five-step.
---

# Agent Selection and Review Skill

Use the “double-axis framework” to move Agent discussions from “how many agents / how many tools” to reviewable engineering coordinates.

- When you need the seven veins, six forms, double-axis orthogonality rules, or Compound Error definition, read `references/agent-double-axis-framework.md`.
- When you need full output templates, read `references/selection-review-templates.md`.

## Scope

Prefer this skill when:

- The user provides business requirements and wants a v1 Agent architecture.
- The user provides a PRD, technical proposal, or existing Agent design and wants robustness or launch-risk review.
- The user asks whether to add memory, reflection, subagents, guardrails, approval, or observability.
- The user asks how to evolve from v1 to v2/v3, or when to move from workflow to agent / multi-agent.

Do not prefer this skill when:

- The user provides a source repository or code path and asks you to find the main loop, read the runtime, or build a source-evidence matrix.
- The user primarily asks how context / tools / memory / state / permissions / sandbox are implemented in a specific Agent Harness codebase.

Use `agent-harness-reverse-five-step` for those scenarios.

## Working method

### 0. First identify the task type

Choose output depth based on the user's intent:

1. **Quick selection**: the user gives business requirements; output a v1 Agent architecture selection card.
2. **Architecture review**: the user gives an existing proposal/design doc; output issues, risks, gaps, and recommendations.
3. **Evolution planning**: the user asks how to move from v1 to v2/v3; output an upgrade path and trigger conditions.
4. **Framework/source-related question**: if it is only architecture selection or technical proposal review, this skill is appropriate; if code evidence is required, switch to `agent-harness-reverse-five-step`.

When information is insufficient, give a “provisional judgment based on current information” and list the 3-5 most important clarifying questions; do not block on a long questionnaire.

## Three-step selection: ASSESS → ROUTE → SELECT

### 1. ASSESS: score the seven veins

Score each cognitive function as `None / Light / Heavy`, with one-sentence rationale. Do not discuss frameworks, tools, or number of agents first.

Assessment principles:

- A `Heavy` function needs at least one explicit pattern or mechanism to carry it.
- A `Light` function can be handled by simple state, logs, human process, or default tooling, but explain why that is enough.
- `None` must be an intentional omission, not an oversight.

If you need definitions of the seven veins, resource budgets, or missing-capability risks, read `references/agent-double-axis-framework.md`.

### 2. ROUTE: choose the primary topology

Choose the primary execution form before deciding pattern combinations.

Quick rules:

- Low collaboration + short task → `Chain / Route`
- Medium complexity + multi-step work → `Orchestrate / Loop`
- Multiple experts + broad task → `Parallel / Hierarchy`
- High-risk actions → prioritize `Governance × Route / Chain / Hierarchy`

When choosing a topology, explain the main error-propagation path: cascade, misrouting, aggregation, decomposition error, compound error, or hierarchy leakage.

### 3. SELECT: choose the v1 pattern set

For each `Heavy` function, choose at least one `Function × Topology` coordinate. A first version usually has **3 to 7 patterns** total; if there are more than 7, merge or downgrade non-critical capabilities first.

For each selection, explain three things:

1. Which resource-budget problem does it solve?
2. Which error-propagation path does it choose?
3. Does it reduce steps, improve per-step quality, add verification, or fail fast? If none of these apply, it may be decorative.

See `references/selection-review-templates.md` for common pattern cues and templates.

## Double-axis review method

When reviewing an existing Agent proposal, organize conclusions around five questions:

1. **What is the state of the seven veins?** Is each vein None, Light, or Heavy? What is the evidence?
2. **Which topology carries each Heavy function?** If this cannot be stated, it is not yet a design; it is a pile of capabilities.
3. **What are the main error-propagation paths?** How will chain cascades, misroutes, parallel merge errors, planning decomposition errors, loop compounding, and hierarchy leakage be tested?
4. **Which cells are intentionally empty?** Is long-term memory/governance/reflection omitted because it is unnecessary, or because it was forgotten?
5. **What is the v1-to-v2 upgrade path?** When should Chain become Loop? When should a single agent become parallel experts or hierarchical delegation? When is approval gating mandatory?

Translate vague feedback into coordinate-specific issues:

- Do not only say “this Agent is not robust”; say “`Reasoning × Loop` has no stop condition.”
- Do not only say “add a guardrail”; say “`Governance × Route` lacks an approval gate for high-risk actions.”
- Do not only say “needs memory”; say “`Memory × Chain` lacks current-task state, or `Memory × Route` lacks retrievable long-term facts.”

## Evolution planning method

When planning v1 → v2/v3, do not assume multi-agent is inherently more advanced. Stabilize inner-loop capabilities first, then add reflection, then expand collaboration and governance.

When outputting an upgrade roadmap, explain:

- **Trigger conditions**: which metrics, scenarios, or risks prove an upgrade is needed?
- **New coordinates**: which `Function × Topology` is added, not merely “add an agent.”
- **Expected benefit**: reduce steps, improve quality, add verification, fail fast, or isolate risk?
- **New risks**: merge, permission inheritance, context leakage, runaway loops, cost/latency increases, etc.
- **Rollback/downgrade**: how to return to a simpler Chain / Route / single-agent design if the upgrade fails.

## Quality requirements

- When giving conclusions, cite the user's requirements, documents, code, or logs as evidence where possible; mark uncertain points as “assumptions.”
- Do not invent pseudo-patterns just to fill the matrix. Empty cells are a design judgment.
- Do not assume multi-agent is more advanced by default.
- Any Agent that can change the external world must discuss governance; the stronger the capability, the stronger governance must be.
- If the user needs a full report structure, use the templates in `references/selection-review-templates.md`.
