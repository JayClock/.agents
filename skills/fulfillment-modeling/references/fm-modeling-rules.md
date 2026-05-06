# Fulfillment Modeling Rules

Use these rules when a task needs precise Fulfillment Modeling generation or validation.

## FM Process

1. Contract context first: identify Contract and its key Party Roles before other entities. Participant Party is optional supporting information, not the main modeling entry.
2. Party role modeling: extract Party Roles for each business subject and connect them to Contract. A Party Role expresses identity-in-context, responsibility, and participation; it does not replace concrete business actions. Add Participant Party only when explicit party identity matters; connect Participant Party -> Party Role -> Contract.
3. Presales evidence: add RFP and Proposal only when the requirement contains a presales stage.
4. Main fulfillment items: model contract responsibilities as Fulfillment Request -> Fulfillment Confirmation pairs.
5. Exceptions and breach flows: refund, cancellation, service suspension, reversal, and similar flows also use Request -> Confirmation pairs.
6. Role splitting: add Party Role, Evidence As Role, Third Party Role, Context Role, and Domain Role according to business intent. For Domain Logic and Third Party roles, first ask what real-world job did this work before software existed, then name the role with job/position semantics.
7. Participation rule: every RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence must have exactly one participating Party Role.
8. Other Evidence vs Evidence As Role:
   - Use Other Evidence when a confirmation produces a business document or byproduct that stays inside the same context.
   - Use Evidence As Role when that same semantic bridges contexts.
   - Do not keep both nodes for the same business semantic.
9. Evidence As Role bridge rule: only use Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation. Do not connect Evidence As Role to Contract, Fulfillment Request, Proposal, or RFP. Evidence As Role belongs to the Context of the source confirmation that produced it.
10. Third Party Role and Context Role may only participate in Other Evidence or Evidence As Role. They must not directly participate in RFP, Proposal, Contract, Fulfillment Request, or Fulfillment Confirmation.
11. Multi-contract handling:
   - One Contract equals one primary chain.
   - Each Contract context independently follows the full process.
   - Each Context contains its own chain from RFP or Contract through terminal Other Evidence or Evidence As Role.
   - Context does not contain Participant Party nodes.
   - The same real-world party may appear as different Party Roles in different contexts through one external Participant Party.
   - Different contract contexts may only bridge through Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.
   - Do not connect Contract directly to Contract or to another context's Request/Confirmation.
12. Boundary and flow: edges should express evidence flow, role participation, and context collaboration while keeping business control flow separate from domain calculation logic.

## Entity Categories

- Evidence: RFP, Proposal, Contract, Fulfillment Request, Fulfillment Confirmation, Other Evidence.
- Participant: Party, Thing.
- Role: Party Role, Domain Role, Third Party Role, Context Role, Evidence As Role.
- Context: bounded business context containers such as payment, inventory, invoice, delivery, subscription, service, or support.

## Graph Output

For a new model, return the complete model as React Flow-shaped nodes plus edges:

```json
{
  "summary": "短摘要",
  "nodes": [
    {
      "id": "node-1",
      "type": "fmEvidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "data": {
        "label": "销售合同",
        "name": "SalesContract",
        "category": "Evidence",
        "kind": "Contract",
        "attributes": [
          {
            "name": "signedAt",
            "label": "签署时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "合同签署完成的业务时间"
          },
          {
            "name": "contractAmount",
            "label": "合同金额",
            "valueType": "Money",
            "required": true,
            "meaning": "双方约定的履约金额"
          }
        ],
        "notes": "可选说明"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2",
      "type": "smoothstep",
      "label": "合同触发履约申请",
      "data": {
        "kind": "precedes"
      }
    }
  ],
  "_meta": {
    "validationNotes": []
  }
}
```

Use stable ids such as `node-1` and `edge-1`. Node ids must be unique across `nodes`; edge ids must be unique across `edges`. Every edge endpoint must reference a node id in the same model unless the caller provided an existing model with those ids.

Recommended node fields:

- `id`: stable identifier.
- `type`: render type, such as `fmContext`, `fmEvidence`, `fmParticipant`, or `fmRole`; use `group` for generic context containers when no custom renderer exists.
- `position`: React Flow-compatible position. Use `{ "x": 0, "y": 0 }` when layout will be computed later.
- `parentId`: parent Context node id for child nodes inside a context. Context nodes must appear before their children.
- `extent`: use `"parent"` when child movement should stay inside the context container.
- `data.label`: human-readable business label.
- `data.name`: concise technical or English identifier.
- `data.category`: `Evidence`, `Participant`, `Role`, or `Context`.
- `data.kind`: concrete FM kind such as `Contract`, `Party Role`, `Fulfillment Request`, `Fulfillment Confirmation`, `Evidence As Role`, or `Other Evidence`.
- `data.attributes`: optional array for intrinsic business attributes of the node, including lifecycle time semantics when relevant. Each item should include `name`, `label`, `valueType`, `required`, and `meaning` when known.
- `data.notes`: optional short explanation.

Recommended edge fields:

- `id`: stable identifier.
- `source`: source node id.
- `target`: target node id.
- `type`: React Flow edge type such as `smoothstep`, `step`, `straight`, or `default`.
- `label`: short business phrase explaining the relationship.
- `data.kind`: relationship intent, such as `precedes`, `fulfills`, `participates_in`, `produces`, `bridges_to`, or `contains`.
- `sourceHandle` / `targetHandle`: optional handle ids when a custom node exposes multiple ports.

For an update to a large existing model, return only changes when full output would be wasteful:

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

Use `changes` as an editing or transport optimization only. It must still preserve the conceptual model as nodes and edges. Within `changes`, do not repeat the same node id across `addNodes`, `updateNodes`, or `deleteNodes`, and do not repeat the same edge id across `addEdges`, `updateEdges`, or `deleteEdges`. Prefer full `nodes` and `edges` for new models, small models, or when the caller has not provided existing ids.

Use `_meta` for non-rendered diagnostics. Put validation notes, assumptions, and manual review reminders in `_meta.validationNotes`. Do not put `validationNotes` at the top level.

## Naming

- Keep `data.label` as a human-readable business label. Do not append lifecycle timestamp suffixes such as `started_at`, `expired_at`, `confirmed_at`, `signed_at`, or `created_at` to node labels.
- Return key time semantics as items in `data.attributes` when helpful.
- Return entity attributes in `data.attributes`; do not encode them in `data.label`.
- Keep `data.attributes` for state or facts owned by that node.
- Model concrete business actions, decisions, calculations, and lifecycle transitions with Fulfillment Request/Fulfillment Confirmation nodes and flow edges.
- Other Evidence and Evidence As Role should usually include a `createdAt` DateTime item in `data.attributes`.
- Domain Logic and Third Party roles must use human job/position names, not technical component names such as rule engine, SDK, queue, risk service, or payment gateway.

## Edge Rules

Main chain:

- RFP -> Proposal -> Contract -> Fulfillment Request -> Fulfillment Confirmation.
- If no presales stage exists, start from Contract.
- Proposal -> Contract is required when Proposal exists.
- Contract -> Fulfillment Request is required; do not create standalone Fulfillment Request.
- Proposal must not connect directly to Fulfillment Request.
- Contract -> Fulfillment Request is usually one-to-many.
- Fulfillment Request -> Fulfillment Confirmation is one-to-one.
- External second responses may cascade as Fulfillment Confirmation -> Fulfillment Confirmation.

Participants:

- Thing usually connects to Contract and may connect to RFP, Proposal, or Fulfillment Request.
- Prefer Party Role participation. Add Participant Party only as identity support.
- In multi-contract models, one Participant Party may connect to multiple Party Roles when they represent the same real-world subject.

Roles:

- RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence each connect to exactly one Party Role.
- Party Role names should describe the business capacity or responsibility, such as Customer, Supplier, Payer, or Service Provider. Model concrete actions, decisions, calculations, and lifecycle transitions with Fulfillment Request/Fulfillment Confirmation nodes and flow edges, not on the Party Role itself.
- Domain Logic Role connects to RFP, Proposal, or Request as a business calculator.
- Third Party Role and Context Role only connect to Other Evidence or Evidence As Role.
- Evidence As Role is only for cross-context bridges and only in the chain Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.

Direction:

- Use cause -> result or initiator -> action.
- Avoid meaningless cycles.
- Ensure the main flow can be read left-to-right.

## Executable Self-Check

Before returning machine-readable graph JSON, run:

```bash
python3 .agents/skills/fulfillment-modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

The script checks:

- Node ids and edge ids are not duplicated.
- Every mandatory edge has known endpoints.
- Every RFP/Proposal/Request/Confirmation/Other Evidence has exactly one Party Role neighbor.
- Every Fulfillment Request has one direct Contract predecessor and one Fulfillment Confirmation successor.
- Cross-context edges are limited to Fulfillment Confirmation -> Evidence As Role and Evidence As Role -> Fulfillment Confirmation.
- Evidence As Role does not point to Fulfillment Request.
- Unfixable invalid edges or uncertain nodes are removed or marked unresolved.

After the script passes, manually review semantic duplication:

- Other Evidence and Evidence As Role do not duplicate the same semantic in the same model.
