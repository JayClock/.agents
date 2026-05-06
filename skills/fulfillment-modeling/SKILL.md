---
name: fulfillment-modeling
description: General Fulfillment Modeling guidance for analyzing business/software requirements into contract-centered graph models shaped like React Flow nodes/edges. Use when Codex needs to output complete nodes/edges, update an existing model with changes, identify Contract contexts, Party Roles, presales evidence, Fulfillment Request/Fulfillment Confirmation pairs, Other Evidence, Evidence As Role, multi-contract boundaries, or valid FM edge constraints without binding to a specific project persistence schema.
---

# Fulfillment Modeling

## Purpose

Model requirements with Fulfillment Modeling (FM): start from contracts and business fulfillment responsibilities, then derive contexts, roles, evidences, requests, confirmations, and valid business-flow edges. Prefer business semantics over technical components.

## Workflow

1. Identify Contract contexts first. Treat one Contract as one primary fulfillment chain; if multiple contracts exist, model each chain independently.
2. Extract Party Roles for every business subject and connect them to the relevant Contract. Add Participant Party only when real-world party identity matters across roles or contexts.
3. Add optional presales Evidence only when present in the requirement: RFP before Proposal, Proposal before Contract.
4. Model each responsibility as a Fulfillment Request -> Fulfillment Confirmation pair. Include reverse or exception flows such as refund, cancellation, suspension, or reversal as their own request/confirmation pairs.
5. Add Other Evidence for internal business documents produced by confirmations. If the evidence bridges contexts, model it as Evidence As Role instead and do not keep duplicate Other Evidence for the same semantic.
6. Add Domain, Third Party, Context, or Evidence roles only when they represent real business participation. Name Domain Logic and Third Party roles as human job/position semantics from the pre-software world, not as technical systems.
7. Put business-chain nodes inside their Context. Keep Participant Party outside Context containers.
8. Create edges from cause to result or initiator to action so the model reads left-to-right as business flow.
9. Run `scripts/self_check_fm_graph.py` on the generated graph JSON before returning any machine-readable model.

## Output Guidance

The model's semantic core is graph nodes and edges. Shape the output like React Flow so it can be rendered directly and extended with custom nodes/edges. Return the model in the format requested by the user or caller.

For a new model, default to a complete graph:

```json
{
  "summary": "短摘要",
  "nodes": [],
  "edges": [],
  "_meta": {
    "validationNotes": []
  }
}
```

For an update to a large existing model, return only the changes when that is more efficient:

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
  },
  "_meta": {
    "validationNotes": []
  }
}
```

Use the complete `nodes`/`edges` model to express "what the domain model is". Keep validation and diagnostic notes under `_meta.validationNotes`, not as top-level graph fields. Node ids must be unique across `nodes`; node `data.name` values must be non-empty and unique across `nodes`; edge ids must be unique across `edges`. In `changes`, ids must not be duplicated across add/update/delete arrays for the same graph element type. Use `changes` only as an editing/transport optimization for existing models. Do not introduce project-specific persistence payload fields, enum spellings, operation names, or validation scripts unless another skill or the user provides that target schema.

## Executable Self-Check

After drafting graph JSON, save it to a temporary file and run:

```bash
python3 .agents/skills/fulfillment-modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

Fix every reported error before returning the graph. The script checks React Flow-shaped node/edge structure, duplicate ids, duplicate node `data.name` values, endpoint existence, parent Context references, Party Role participation, Request -> Confirmation pairing, Proposal/Request routing, cross-context bridge constraints, Evidence As Role constraints, and Third Party/Context Role participation constraints.

Manually review semantic duplication after the script passes:

- The same business semantic is not modeled as both Other Evidence and Evidence As Role.

## Reference

Read `references/fm-modeling-rules.md` when generating or reviewing a complete FM model, especially for multi-contract contexts, Evidence As Role, role participation constraints, React Flow-shaped graph output, patch output, or boundary rules.
