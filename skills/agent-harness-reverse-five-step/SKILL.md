---
name: agent-harness-reverse-five-step
description: Reverse engineer Agent Harness / agent framework repositories into an evidence-backed engineering map using Detect → Classify → Filter → Map → Verify. Use this skill whenever the user gives a source repository, code directory, or framework implementation and asks to analyze, compare, explain, document, or review a coding agent, tool-calling runtime, sandboxed agent, multi-agent system, or Agent framework such as Claude Code, Codex CLI, Aider, OpenHands, OpenCode, OpenClaw, Hermes Agent, DeerFlow. Especially use it when the user asks where the main loop is, how context/tools/memory/state/permissions/sandbox work in code, how errors propagate, or wants an architecture diagram, matrix, heatmap, review checklist, or source-code evidence table. If the task is business architecture selection, PRD review, or v1/v2 planning without source evidence, use agent-selection-review instead.
---

# Agent Harness Reverse Engineering: Five-Step Method

Use this method to turn an unfamiliar Agent Harness / Agent framework codebase from “a pile of files” into a verifiable, comparable, and reviewable engineering map.

Core sequence: **Detect → Classify → Filter → Map → Verify** — find the main loop, classify components, filter noise, map to a matrix, and verify with source evidence.

- When you need the seven veins, six forms, double-axis orthogonality rules, or Compound Error definition, read `references/agent-double-axis-framework.md`.
- When you need checklists, grep queries, Mermaid diagrams, and report templates, read `references/reverse-five-step-templates.md`.

## Scope

Prefer this skill when:

- The user provides a repository, directory, source file, or specific framework implementation.
- The user is not satisfied with the README and wants to understand “what kind of runtime this system puts the model into.”
- The user asks where the main loop, context construction, model call, tool dispatch, state update, permissions, sandbox, event log, or subagent boundary lives.
- The user wants a source-evidence table, architecture diagram, matrix/heatmap, first-pass reading list, or noise-filtering advice.

Do not prefer this skill when:

- The user only provides business requirements, a PRD, or a proposal draft and wants Agent architecture selection or launch review.
- The user primarily asks “should we add memory / reflection / multi-agent / approval,” but does not require source-code evidence.

Use `agent-selection-review` for those scenarios.

## Working principles

1. **Build an expected framework before verifying in source.** Do not start by wandering through README feature lists or keyword hits.
2. **Find the control plane before implementation details.** Prioritize code that changes context, decisions, actions, state, or permissions.
3. **Be willing to skip files temporarily.** CLI arguments, UI glue, provider wrappers, serialization, and test fixtures can be marked as noise unless they change the Agent control plane.
4. **Every conclusion must trace back to evidence.** Judgments without source code, tests, or official docs must be labeled “assumption.”
5. **Separate product interpretation from engineering argument.** “Supports memory/tool/sandbox” is not a conclusion; explain where it takes effect, which topology it uses, and what the failure mode is.
6. **Keep the double axis orthogonal.** Write complete judgments as `Cognitive Function × Execution Topology`, not just Memory, Tool, Loop, or Orchestrator.
7. **Treat topology as an error-propagation path.** Choosing Chain/Route/Parallel/Orchestrate/Loop/Hierarchy means choosing how errors cascade, misroute, aggregate, decompose incorrectly, compound, or get amplified/isolated by hierarchy.

## Step 0: Clarify input and boundaries

Before starting, quickly confirm or infer:

- What is the target repository/directory/document path? Does the version or commit matter?
- Does the user want a quick overview, deep source evidence, or framework comparison?
- What output form is expected: Markdown report, table, diagram, code comments, Obsidian note, or PR review?

If the user does not specify an output, default to a Markdown architecture reverse-engineering report.

## Step 1 Detect: find the main loop first

First locate the heart of the Agent Harness: the loop that connects user input, context assembly, model calls, tool actions, result feedback, and state updates.

Prioritize three questions:

1. Where does user input enter?
2. Where does the LLM / model call happen?
3. How do tool results feed back into the next round of context?

The main loop usually touches **messages, model call, and tool dispatch** together. Files that only handle UI, configuration, or a single tool implementation are usually not the main loop.

Suggested search queries are in `references/reverse-five-step-templates.md`.

## Step 2 Classify: map components to the seven cognitive veins

After finding the main loop, do not immediately drill all the way down the call stack. Classify key components around the main loop by “which resource budget they manage.”

Classify by runtime effect, not file name. A component can span multiple veins, but on the first pass, mark the **primary vein** and then secondary veins. For example:

- An event log may primarily be Memory (state continuity) and secondarily Governance (auditability).
- A sandbox may primarily be Governance (trust boundary) and secondarily Action (limits external state changes).
- A subagent may primarily be Collaboration and secondarily Perception (isolated observation scope).

See `references/agent-double-axis-framework.md` for the seven-vein quick reference, and `references/reverse-five-step-templates.md` for the classification table template.

## Step 3 Filter: actively discard 70% of the noise

Use this question to filter files:

> Does this file change the Agent's decisions, context, state, actions, or permissions?

If no, mark it as `boilerplate / later`. If yes, decide which control point it changes: what the Agent sees, remembers, how it reasons, what it can do, how it corrects, who does the work, or what boundaries/permissions/ledger apply.

In the first pass, you can usually postpone: CLI argument parsing, UI layout, error copy, telemetry adapters, schema type definitions, provider SDK wrappers, serialization/deserialization, platform compatibility branches, and ordinary fixtures.

However, if test files reveal sandbox, permission, memory, or subagent boundaries, promote them to strong evidence.

## Step 4 Map: build the “Cognitive Function × Execution Topology” matrix

Turn key components into comparable engineering objects. Do not only write “this is Memory” or “this is Tool.” A complete coordinate must answer **What (cognitive function) × How (execution topology) × Why (engineering consequence)**.

Each matrix entry should explain at least:

1. Which cognitive-function problem does it solve? In other words, which resource budget?
2. Which execution topology does it use? How do capability, information, control, and error flow?
3. What is the benefit? Lower cost, higher quality, risk isolation, or recovery/audit support?
4. What is the failure mode or cost? How do errors propagate or compound?
5. Where is the evidence?

Note: `EventLog`, `Sandbox`, `Approval Gate`, `Shared State`, and similar terms are often implementation mechanisms or governance/memory components; they do not directly replace the six forms. When mapping, first identify which vein the mechanism serves, then identify whether it flows through Chain, Route, Parallel, Orchestrate, Loop, or Hierarchy.

## Step 5 Verify: tie every judgment back to source

Give evidence for every important judgment. Evidence strength, from strongest to weakest:

1. **Source code**: actual implementation of the main loop, permissions, sandbox, event store, tool dispatcher, etc.
2. **Tests**: especially boundary-condition tests, which often state system guarantees more clearly than implementation code.
3. **Official documentation**: use it to confirm public semantics and design intent.

When evidence is missing, explicitly write “unverified assumption” instead of presenting it as a conclusion.

## Quick mode

If the user only wants a quick overview, do not write a full report:

1. Provide a 5-8 line main-loop sketch.
2. List the 5 source files most worth reading next.
3. List 3 noisy areas to postpone.
4. Provide 3 key assumptions to verify in source.

## Common traps

- **README hallucination**: README says what the system can do, not how its runtime works.
- **Keyword wandering**: grepping `agent/tool/memory/context` and reading every hit becomes source-code tourism.
- **Entry-function rabbit hole**: drilling from `main()` downward often gets stuck in config, UI, or serialization branches.
- **Label-only matrix**: Memory/Action labels are not enough; explain topology, benefits, failure modes, and evidence.
- **Evidence-free narrative**: architectural judgments that cannot return to source/tests/docs are only assumptions.
