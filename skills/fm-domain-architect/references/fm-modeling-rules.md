# Fulfillment Modeling Rules

Use these rules when a task needs precise FM diagram generation or validation.

## FM Process

1. Contract context first: identify Contract and its key Party Roles before other entities. Participant Party is optional supporting information, not the main modeling entry.
2. Party role modeling: extract Party Roles for each business subject and connect them to Contract. Add Participant Party only when explicit party identity matters; connect Participant Party -> Party Role -> Contract.
3. Presales evidence: add RFP and Proposal only when the requirement contains a presales stage.
4. Main fulfillment items: model contract responsibilities as Fulfillment Request -> Fulfillment Confirmation pairs.
5. Exceptions and breach flows: refund, cancellation, service suspension, reversal, and similar flows also use Request -> Confirmation pairs.
6. Role splitting: add Party Role, Evidence As Role, Third Party Role, Context Role, and Domain Role according to business intent. For Domain Logic and Third Party roles, first ask what real-world job did this work before software existed, then name the role with job/position semantics.
7. Participation rule: every RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence node must have exactly one participating Party Role.
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

## Node Rules

Every node requires:

- unique virtual `id`, preferably `node-1`, `node-2`, etc.
- `parent`; root nodes use `parent=null`, child nodes use `parent.id=<context-node-id>`.
- `localData.name`, `localData.label`, `localData.type`, and `localData.subType`.

Actual JSON shape:

```json
{
  "id": "node-1",
  "parent": null,
  "localData": {
    "name": "SalesContract",
    "label": "销售合同 signed_at",
    "type": "EVIDENCE",
    "subType": "contract"
  }
}
```

Allowed `localData.type` values:

- `EVIDENCE`
- `PARTICIPANT`
- `ROLE`
- `CONTEXT`

Allowed `localData.subType` values:

- `EVIDENCE`: `rfp`, `proposal`, `contract`, `fulfillment_request`, `fulfillment_confirmation`, `other_evidence`
- `PARTICIPANT`: `party`, `thing`
- `ROLE`: `party`, `domain`, `3rd system`, `context`, `evidence`
- `CONTEXT`: `bounded_context`

Type mapping:

- `EVIDENCE`: RFP, Proposal, Contract, Fulfillment Request, Fulfillment Confirmation, Other Evidence.
- `PARTICIPANT`: Party, Thing.
- `ROLE`: Party, Domain, Third Party, Other Context, Evidence As Role.
- `CONTEXT`: business context containers such as payment, inventory, invoice, delivery, subscription, service, or support.

Naming:

- Include evidence category and key time semantics where helpful: `started_at`, `expired_at`, `confirmed_at`, `signed_at`, `created_at`.
- Other Evidence and Evidence As Role should usually carry `created_at`.
- Domain Logic and Third Party roles must use human job/position names, not technical component names such as rule engine, SDK, queue, risk service, or payment gateway.

Context parenting:

- Context nodes are containers.
- Put all in-context RFP/Proposal/Contract/Request/Confirmation/Role/Evidence nodes under the Context.
- Keep Participant Party outside Context.
- Evidence As Role parent remains the source confirmation's Context, even when it connects to a different Context.

## Edge Rules

Every edge requires `sourceNode.id` and `targetNode.id` referencing existing nodes. Remove any edge whose endpoint is unknown.

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
- Domain Logic Role connects to RFP, Proposal, or Request as a business calculator.
- Third Party Role and Context Role only connect to Other Evidence or Evidence As Role.
- Evidence As Role is only for cross-context bridges and only in the chain Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.

Direction:

- Use cause -> result or initiator -> action.
- Avoid meaningless cycles.
- Ensure the main flow can be read left-to-right.

## Proposal Operation Rules

Top-level proposal fields:

- `summary`
- `operations`

Actual summary shape:

```json
{
  "message": "新增订单履约主链",
  "addNodes": 6,
  "addEdges": 5,
  "updateNodes": 0,
  "updateEdges": 0,
  "deleteNodes": 0,
  "deleteEdges": 0
}
```

Supported operation types:

- `ADD_NODE`
- `UPDATE_NODE`
- `DELETE_NODE`
- `ADD_EDGE`
- `UPDATE_EDGE`
- `DELETE_EDGE`

Payload rules:

- `ADD_NODE` embeds a complete `node`.
- `ADD_EDGE` embeds a complete `edge`.
- `UPDATE_NODE` and `UPDATE_EDGE` include `targetId` and the replacement payload.
- `DELETE_NODE` and `DELETE_EDGE` include only `targetId`.
- `ADD_EDGE` source and target ids must refer to nodes introduced by `ADD_NODE` in the same proposal, unless the user supplied an existing diagram with those ids.
- If update/delete targets are unreliable, prefer additions and avoid guessed destructive operations.

Operation examples:

```json
{
  "type": "ADD_EDGE",
  "edge": {
    "sourceNode": { "id": "node-1" },
    "targetNode": { "id": "node-2" }
  },
  "reason": "合同触发履约申请"
}
```

Do not wrap JSON responses in Markdown fences when the caller needs machine-readable proposal JSON.

## Executable Self-Check

Before returning machine-readable proposal JSON, run:

```bash
python3 scripts/self_check_fm_proposal.py /tmp/proposal.json
```

The script checks:

- Required `summary` and `operations` shape.
- Summary add/update/delete counts match the operations array.
- All edge source/target ids exist.
- No endpoint is `{}`, `null`, `undefined`, empty, `node-unknown`, or invented only in edges.
- Each RFP/Proposal/Request/Confirmation/Other Evidence has exactly one Party Role neighbor.
- Cross-context edges are limited to Fulfillment Confirmation -> Evidence As Role and Evidence As Role -> Fulfillment Confirmation.
- Evidence As Role does not point to Fulfillment Request.
- Third Party Role and Context Role only connect to Other Evidence or Evidence As Role.
- Unfixable invalid edges or uncertain nodes are removed.

After the script passes, manually review semantic duplication:

- Other Evidence and Evidence As Role must not duplicate the same business semantic in the same diagram.
