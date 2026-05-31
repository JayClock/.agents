---
name: modeling
description: General Fulfillment Modeling guidance for analyzing business/software requirements into contract-centered graph models shaped like React Flow nodes/edges and transported as addNodes/addEdges changes by default. Use when Codex needs to output initial graph additions, update an existing model with changes, identify Contract contexts, Party Roles, presales evidence, Fulfillment Request/Fulfillment Confirmation pairs, Other Evidence, Evidence As Role, multi-contract boundaries, valid FM edge constraints, business rules, lifecycle facts, downstream signals, or scenario paths without binding to a physical database schema. For database table design from FM graphs, use the fm-database-design skill instead.
---

# Fulfillment Modeling

## Purpose

Model requirements with Fulfillment Modeling (FM): start from contracts and business fulfillment responsibilities, then derive contexts, roles, evidences, requests, confirmations, and valid business-flow edges. Prefer business semantics over technical components.

FM is a pure business-semantic model. Keep database tables, APIs, services, modules, deployment, frameworks, and other technical implementation details outside the model unless the user explicitly asks for a separate implementation artifact. Business objects, responsibilities, rules, lifecycle facts, downstream signals, and scenario paths must be expressed through FM's existing Contract/Evidence/Request/Confirmation/Role/Context node kinds and edge constraints.

## Workflow

1. Identify Contract contexts first. Treat one Contract as one primary fulfillment chain; if multiple contracts exist, model each chain independently.
2. Extract Party Roles for every business subject and connect them to the relevant Contract. Add Participant Party only when real-world party identity matters across roles or contexts.
3. Add optional presales Evidence only when present in the requirement: RFP before Proposal, Proposal before Contract.
4. Model each responsibility as a Fulfillment Request -> Fulfillment Confirmation pair. Include reverse or exception flows such as refund, cancellation, suspension, or reversal as their own request/confirmation pairs.
5. Add Other Evidence for internal business documents produced by confirmations. If the evidence bridges contexts, model it as Evidence As Role instead and do not keep duplicate Other Evidence for the same semantic.
6. Add Domain, Third Party, Context, or Evidence roles only when they represent real business participation. Name Domain Logic and Third Party roles as human job/position semantics from the pre-software world, not as technical systems.
7. Put business-chain nodes inside their Context. Keep Participant Party outside Context containers.
8. Create edges from cause to result or initiator to action so the model reads left-to-right as business flow. Each React Flow edge is a single 1:1 source-to-target relation; model aggregate one-to-many relationships as multiple independent 1:1 edges. Put endpoint relationship display text in `edge.data.sourceRelation` and `edge.data.targetRelation`, both set to `"1"`.
9. Express lifecycle through evidence, not standalone status nodes. Put lifecycle facts such as current status, effective status, terminal status, lifecycle timestamps, and eligibility flags in Evidence, Thing, or Contract attributes. Model every meaningful state transition as a Fulfillment Request -> Fulfillment Confirmation pair, with guard conditions in `precondition` or `calculationRule`, transition results in Confirmation attributes, and follow-up effects as downstream evidence flow or Evidence As Role bridges.
10. Before finalizing, check that each important business object has a home in Contract, Thing, Evidence, or attributes; each meaningful responsibility is a Request -> Confirmation pair; each non-trivial rule is traceable to `precondition`, `calculationRule`, Domain Role, or validation notes; each downstream business signal is represented as evidence flow or an Evidence As Role bridge; and each main, alternative, or exception scenario has a readable evidence chain.
11. Return a `changes` payload by default for both initial modeling and existing-model updates. For the first/initial response, put every generated node in `changes.addNodes` and every generated edge in `changes.addEdges`, with update/delete arrays empty. For existing-model updates, validate the diff by applying it locally to the provided base model with `scripts/apply_fm_changes.py` and running `scripts/self_check_fm_graph.py` on the merged full graph before returning. If the user explicitly asks for the complete model, return that validated full graph instead of the `changes` payload.

## Output Guidance

The model's semantic core is graph nodes and edges. Shape the output like React Flow so it can be rendered directly and extended with custom nodes/edges. Return the model in the format requested by the user or caller.

For a new/initial model, default to an add-only `changes` response. Put the first batch of generated graph elements in `addNodes` and `addEdges`; leave update/delete arrays empty:

```json
{
  "summary": "短摘要",
  "changes": {
    "addNodes": [],
    "updateNodes": [],
    "deleteNodes": [],
    "addEdges": [],
    "updateEdges": [],
    "deleteEdges": []
  }
}
```

For an update to an existing model, default to a diff-only `changes` response, after locally validating the merged full graph:

```json
{
  "summary": "短摘要",
  "changes": {
    "addNodes": [],
    "updateNodes": [],
    "deleteNodes": [],
    "addEdges": [],
    "updateEdges": [],
    "deleteEdges": []
  }
}
```

Return `changes` by default, including for first-time model generation. Only return the complete `nodes`/`edges` model when the user explicitly asks for the final/full/complete model. For every update response, compute the diff first, apply it to the base model locally, and validate the merged graph. If validation passes, return the diff by default or the merged full graph when requested. Do not include non-rendered diagnostic payloads in the returned graph. Node ids must be unique across the full graph or across `changes.addNodes` for an initial response; node `data.name` values must be non-empty and unique; edge ids must be unique across the full graph or across `changes.addEdges` for an initial response. Each edge must use scalar string `source` and `target` node ids plus `data.sourceRelation: "1"` and `data.targetRelation: "1"` so a React Flow custom edge can render relation text near both endpoints. Default to built-in `type: "smoothstep"`; do not use custom edge `type` values unless the user or caller provides an explicit renderer contract outside the FM payload. In `changes`, ids must not be duplicated across add/update/delete arrays for the same graph element type. Do not introduce project-specific persistence payload fields, enum spellings, operation names, or validation scripts unless another skill or the user provides that target schema.

Diff id rules: `updateNodes` and `deleteNodes` must reference existing `node.id` values from the provided base model; `updateEdges` and `deleteEdges` must reference existing `edge.id` values. `addNodes` and `addEdges` must use new ids that do not exist in the base model. `addEdges.source` and `addEdges.target` may reference existing nodes or nodes added in the same diff. When deleting a node, also include every incident edge in `deleteEdges`; never leave dangling edges for the merge step to infer.

## Executable Self-Check

For any update diff, merge and validate the full graph before returning either diff or complete output:

```bash
python3 .agents/skills/modeling/scripts/apply_fm_changes.py /tmp/base-fm-graph.json /tmp/fm-changes.json /tmp/merged-fm-graph.json
python3 .agents/skills/modeling/scripts/self_check_fm_graph.py /tmp/merged-fm-graph.json
```

After drafting initial graph JSON as a `changes` payload or complete graph, save it to a temporary file and run:

```bash
python3 .agents/skills/modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

Fix every reported error before returning the graph. The script checks React Flow-shaped node/edge structure, supported built-in React Flow edge `type` values, per-edge endpoint relation data, FM line styling, node `type` equals `data.category`, duplicate ids, duplicate node `data.name` values, endpoint existence, parent Context references, Party Role participation, Request -> Confirmation pairing, Proposal/Request routing, cross-context bridge constraints, Evidence As Role constraints, and Third Party/Context Role participation constraints.

Manually review semantic duplication after the script passes:

- The same business semantic is not modeled as both Other Evidence and Evidence As Role.

## Reference

Read `references/fm-modeling-rules.md` when generating or reviewing a complete FM model, especially for the FM entity type dictionary, mandatory Evidence timestamps, multi-contract contexts, Evidence As Role, role participation constraints, React Flow-shaped graph output, patch output, lifecycle expression, business-rule placement, or boundary rules.

Use `$fm-database-design` instead when the user asks to turn an FM graph into database tables, physical schema, SQL DDL, immutable evidence persistence, or storage design.
