# Fulfillment Modeling Rules

Use these rules when a task needs precise Fulfillment Modeling generation or validation.

## FM Process

1. Contract context first: identify Contract and its key Party Roles before other entities. Treat one Contract as one primary chain and identify the contracting sides first. Participant Party is optional supporting information, not the main modeling entry.
2. Presales evidence: add RFP and Proposal only when the requirement contains a presales stage. If no presales stage exists, start directly from Contract.
3. Evidence-first discovery: within each Contract context, first look for the main cash movement evidence. Create the money-related evidence that best anchors the business obligation and list key attributes such as business time point, amount, currency, payment window, quantity, or refund amount when applicable. If cash movement is weak or absent, start from the key KPI or acceptance evidence instead.
4. Attribute source tracing: for every key attribute on the current evidence, trace its source and keep the source path clear. A source may only come from user input, a prior evidence node, or algorithmic calculation. If an amount, currency, quantity, payment window, refund amount, KPI, or acceptance metric is derived from a prior evidence node, record both the prior evidence path and the calculation rule used to derive it. Do not keep attributes whose source cannot be explained.
5. Main fulfillment items: return from the anchor evidence to the rights and obligations it proves, then discover the surrounding evidence needed to establish, request, and confirm those obligations. Model each concrete responsibility as Fulfillment Request -> Fulfillment Confirmation pairs, and ensure every evidence node carries the key attributes needed for business traceability.
6. Exceptions and breach flows: for refund, cancellation, service suspension, reversal, compensation, and similar breach or exception flows, repeat the same evidence discovery method from the related money evidence or KPI/acceptance evidence, then model them as their own Request -> Confirmation pairs. Continue expanding breach handling until the requirement reaches an external dispute or litigation boundary.
7. Evidence flow before roles: first complete the mutually connected evidence flow, then refine the model around each evidence by adding the roles involved in creating, requesting, confirming, calculating, or bridging it.
8. Party role modeling: extract Party Roles for each business subject and connect them to Contract or to the evidence they participate in. A Party Role expresses identity-in-context, responsibility, and participation; it does not replace concrete business actions. Add Participant Party only when explicit party identity matters; connect Participant Party -> Party Role -> Contract.
9. Role splitting: add Party Role, Evidence As Role, Third Party Role, Context Role, and Domain Role according to business intent. For Domain Logic and Third Party roles, first ask what real-world job did this work before software existed, then name the role with job/position semantics.
10. Participation rule: every RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence must have exactly one participating Party Role.
11. Other Evidence vs Evidence As Role:
   - Use Other Evidence when a confirmation produces a business document or byproduct that stays inside the same context.
   - Use Evidence As Role when that same semantic bridges contexts.
   - Do not keep both nodes for the same business semantic.
12. Evidence As Role bridge rule: only use Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation. Do not connect Evidence As Role to Contract, Fulfillment Request, Proposal, or RFP. Evidence As Role belongs to the Context of the source confirmation that produced it.
13. Third Party Role and Context Role may only participate in Other Evidence or Evidence As Role. They must not directly participate in RFP, Proposal, Contract, Fulfillment Request, or Fulfillment Confirmation.
14. Multi-contract handling:
   - One Contract equals one primary chain.
   - Each Contract context independently follows the full process.
   - Each Context contains its own chain from RFP or Contract through terminal Other Evidence or Evidence As Role.
   - Context does not contain Participant Party nodes.
   - The same real-world party may appear as different Party Roles in different contexts through one external Participant Party.
   - Different contract contexts may only bridge through Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.
   - Do not connect Contract directly to Contract or to another context's Request/Confirmation.
15. Boundary and flow: after roles and participants are clear, place Party and Thing into the appropriate domain boundaries. Edges should express evidence flow, role participation, and context collaboration while keeping business control flow separate from domain calculation logic.
16. Completeness check: after the evidence chain is coherent, verify that business objects, responsibilities, rules, lifecycle facts, downstream signals, and scenario paths are all represented through existing FM nodes, attributes, notes, edge labels, and validation notes. Do not introduce extra framework-specific layer nodes.

## Business Semantics Completeness

Keep FM focused on business semantics rather than technical implementation:

- Include business contracts, obligations, roles, evidence, business objects, lifecycle facts, rules, downstream signals, and scenario paths.
- Exclude database tables, API endpoints, service modules, framework classes, deployment components, queues, jobs, and integration mechanisms unless the user explicitly asks for implementation design.
- Name Domain Role and Third Party Role with real-world business job, institution, or responsibility semantics instead of system names.

Place each business semantic in the existing FM model this way:

- Business objects and stable facts belong in Contract, Thing, Evidence, Evidence attributes, Context, Party, or Party Role.
- Business responsibilities belong in Fulfillment Request -> Fulfillment Confirmation pairs. A request is the business instruction or attempted transition; a confirmation is the business result that proves the responsibility was fulfilled or rejected.
- Business rules belong in `precondition`, `calculationRule`, Domain Role, evidence attributes, and `_meta.validationNotes`.
- Downstream business signals belong in Confirmation-driven evidence flow. Same-context signal effects become downstream requests, confirmations, or Other Evidence. Cross-context signal effects must use the allowed Fulfillment Confirmation -> Evidence As Role -> downstream Fulfillment Confirmation bridge.
- Business relationships belong in FM edges, participation edges, role-play edges, context containment, and allowed cross-context bridges. Each edge remains a single 1:1 React Flow edge.
- Business scenarios belong in coherent evidence chains that cover main flow, alternative flow, exception flow, cancellation, refund, suspension, reversal, compensation, and terminal business outcomes.

When a source requirement describes an atomic business behavior with fields such as actor, owner entity, trigger, preconditions, applied rules, postconditions, or produced events, translate it into FM like this:

- Actor becomes a Party Role or other allowed Role participating in the relevant Evidence.
- Owner entity becomes the Contract, Thing, or Evidence whose attributes carry the business fact being changed.
- Trigger becomes the incoming edge into the Fulfillment Request, or the source Confirmation/Evidence that makes the request meaningful.
- Preconditions become request attributes with `precondition`, eligibility attributes with `calculationRule`, or validation notes when the source rule is not machine-checkable.
- Applied rules become parseable `calculationRule` values where possible, Domain Role responsibility where a business actor performs a decision, or validation notes where the source rule is not machine-checkable.
- Postconditions become Fulfillment Confirmation attributes and downstream Evidence.
- Produced business signals become downstream evidence flow or Evidence As Role bridges, not a generic event node by default.

Classify rules by intent before placing them:

- Validation rules check whether an operation is allowed. Prefer `precondition` on the request or validation notes.
- Calculation rules derive amounts, quantities, deadlines, eligibility, status, risk, scores, or flags. Prefer attribute-level `calculationRule`.
- Decision rules choose between business paths or outcomes. Prefer Domain Role plus decision Evidence attributes, or a confirmation attribute with a parseable decision result.
- Derivation rules infer a new business fact from existing evidence. Prefer derived Evidence attributes.
- Constraint rules express quality, SLA, audit, consistency, idempotency, or cardinality requirements. Prefer evidence attributes or validation notes.

Use this completeness check before finalizing:

- Every important business object has a home in Contract, Thing, Evidence, or attributes.
- Every meaningful behavior is represented by a Request -> Confirmation pair.
- Every non-trivial rule is traceable to a precondition, calculation rule, Domain Role, or validation note.
- Every significant downstream business signal is represented as evidence flow or an Evidence As Role bridge.
- Every scenario path has a readable evidence chain from contract or presales evidence through terminal evidence.

## Lifecycle Modeling in FM

FM does not model lifecycle as standalone status nodes. Express lifecycle by proving each meaningful state change through business evidence.

Use this mapping:

- State: an Evidence, Thing, or Contract attribute such as `supplierStatus`, `fulfillmentStatus`, `inspectionStatus`, `riskStatus`, or `terminated`.
- Initial state: the Contract, presales evidence, admission request, creation request, or first Fulfillment Confirmation attribute that establishes the lifecycle.
- State transition: a Fulfillment Request -> Fulfillment Confirmation pair.
- Trigger behavior: the Fulfillment Request and its incoming cause edge.
- Guard condition: request `precondition`, eligibility flag, or parseable `calculationRule`.
- Transition result: Fulfillment Confirmation attributes such as `confirmedStatus`, `effectiveStatus`, `terminated`, `suspendedAt`, or `effectiveAt`.
- Follow-up event: downstream Fulfillment Request/Confirmation, Other Evidence, or Evidence As Role bridge.
- Terminal state: terminal Confirmation or terminal status attribute; do not create a terminal state node by default.

For each lifecycle transition, capture the complete dynamic business semantics:

- Who or what role initiates the transition.
- Which prior evidence, contract, or object makes the transition possible.
- Which guard condition or business rule must hold.
- Which confirmation proves the transition occurred.
- Which status, timestamp, amount, quantity, risk flag, or other business fact changed.
- Which downstream actions or documents are triggered.

Example lifecycle mapping:

```text
合格供应商 -> 暂停合作

FM expression:
SupplierSuspensionRequest
  precondition: supplier is qualified and quality score or breach condition allows suspension
  participant: ProcurementDirectorRole
  -> SupplierSuspensionConfirmation
     attributes:
       confirmedAt
       effectiveSupplierStatus = "SUSPENDED"
       suspendedAt
  -> downstream RFQCloseRequest / RFQCloseConfirmation
  -> downstream InTransitOrderRiskMarkRequest / InTransitOrderRiskMarkConfirmation
```

Recommended attribute pattern:

```json
{
  "name": "suspendable",
  "label": "是否可暂停",
  "valueType": "Boolean",
  "required": true,
  "meaning": "供应商是否满足暂停合作条件",
  "calculationRule": "suspendable = SupplierQualityConfirmation.qualityScore < 60 || SupplierBreachConfirmation.majorDeliveryBreach == true"
}
```

```json
{
  "name": "effectiveSupplierStatus",
  "label": "生效后的供应商状态",
  "valueType": "Enum",
  "required": true,
  "meaning": "供应商暂停确认完成后生效的生命周期状态",
  "precondition": "SupplierSuspensionRequest.suspendable == true",
  "calculationRule": "effectiveSupplierStatus = \"SUSPENDED\""
}
```

If the user asks for a lifecycle state diagram, generate it as a derived view from the FM evidence chain. The source of truth remains the FM graph: states are derived from attributes, and transitions are derived from Request -> Confirmation pairs.

## Entity Categories

- Evidence: RFP, Proposal, Contract, Fulfillment Request, Fulfillment Confirmation, Other Evidence.
- Participant: Party, Thing.
- Role: Party Role, Domain Role, Third Party Role, Context Role, Evidence As Role.
- Context: bounded business context containers such as payment, inventory, invoice, delivery, subscription, service, or support.

## Entity Type Dictionary

Use this dictionary to choose node kinds and avoid semantic drift. Treat Evidence as time-bearing business facts, Participant as static placeholders, Role as responsibility or calculation participants, and Context as bounded business containers.

### Evidence

Evidence nodes represent business actions, commitments, or result artifacts that actually happened at a business time point. They form the dynamic business control flow and must carry lifecycle timestamps:

- Contract: the main modeling starting point. It represents the physical moment when buyer and seller form a transaction agreement and defines rights and obligations. Require `signedAt`.
- RFP: presales evidence for an initial customer intention, inquiry, or requirements request. Require `startedAt` and `expiredAt`.
- Proposal: presales evidence for the concrete offer, solution, or quotation commitment responding to an RFP, usually with a validity window. Require `startedAt` and `expiredAt`.
- Fulfillment Request: the initiating instruction for a forward or reverse action derived from a Contract, such as payment, shipment, refund, or cancellation. It starts an execution responsibility. Require `startedAt` and business deadline `expiredAt`.
- Fulfillment Confirmation: the paired delivery result for a Fulfillment Request, whether success or failure. Require `confirmedAt`.
- Other Evidence: static business documents or byproducts produced after confirmation and kept inside the same business context, such as revenue recognition records, electronic invoices, or warehouse receipt documents. Require `createdAt`.

### Participant

Participant nodes represent objectively existing physical entities or business objects. In FM graphs they are static domain skeleton placeholders, not expanded field models. Connect them to Contract or presales Evidence through roles or direct business association when the identity or object matters.

- Party: a real transaction participant, such as a specific customer company, supplier, or natural person. Add it only when the model must distinguish physical identity from business role.
- Thing: the concrete object around which the transaction or fulfillment action occurs, such as goods, paid content, or virtual assets. Use it to answer what the contract sells or fulfills.

### Role

Role nodes answer who initiates, calculates, executes, receives, or bridges Evidence. Connect them to Evidence with participation/support semantics; do not model actions as roles.

- Party Role: the identity, responsibility, and authority of a participant inside the current context, such as buyer, seller, or purchaser. Every Evidence node that requires participation must have exactly one Party Role participant.
- Domain Role: a black-box business calculator, verifier, or rule performer, such as a price assessor or discount approver. Name it as a real-world job or position, not as a software system.
- Third Party Role: an external system or institution outside internal control, such as a payment institution or tax invoice platform. It may connect only to Other Evidence or Evidence As Role, never directly into the core internal fulfillment flow.
- Context Role: another internal business domain acting as a downstream agent, such as warehouse context or points context. Use only for cross-context collaboration.
- Evidence As Role: a special bridge where a source-context Evidence becomes a role-like trigger for another context. Enforce the exact bridge pattern `Fulfillment Confirmation -> Evidence As Role -> downstream Fulfillment Confirmation`.

### Context

- Bounded Context: a macroscopic business boundary container, such as payment, inventory, fulfillment, subscription, or invoicing. Each Context must contain a complete independent chain from Contract to terminal Evidence. Contexts are decoupled and may cooperate only through asynchronous Evidence As Role bridges.

## Graph Output

For a new model, return the complete model as React Flow-shaped nodes plus edges:

```json
{
  "summary": "短摘要",
  "nodes": [
    {
      "id": "node-1",
      "type": "Evidence",
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
      "label": "合同触发交付申请",
      "data": {
        "sourceRelation": "1",
        "targetRelation": "1"
      }
    },
    {
      "id": "edge-2",
      "source": "node-1",
      "target": "node-3",
      "type": "smoothstep",
      "label": "合同触发付款申请",
      "data": {
        "sourceRelation": "1",
        "targetRelation": "1"
      }
    }
  ],
  "_meta": {
    "validationNotes": [],
    "registeredEdgeTypes": []
  }
}
```

Use stable AI-generated ids with explicit prefixes: node ids must start with `node-`, such as `node-1`, and edge ids must start with `edge-`, such as `edge-1`. These prefixes distinguish newly generated model elements from persisted production records. Node ids must be unique across `nodes`; node `data.name` values must be non-empty and unique across `nodes`; edge ids must be unique across `edges`. Every edge endpoint must reference a node id in the same model unless the caller provided an existing model with those ids.

Each React Flow edge in `edges` is a scalar 1:1 relation: `source` is exactly one node id and `target` is exactly one node id. Do not use arrays, comma-separated ids, wildcards, or custom endpoint payloads to express one-to-many. When a Contract has multiple Fulfillment Requests, return multiple independent edge objects that reuse the Contract as `source` and point to one Fulfillment Request each.

Put endpoint cardinality display text in `edge.data.sourceRelation` and `edge.data.targetRelation`. Because each edge is always 1:1, both values must be `"1"`. A React Flow custom edge may read these values and render them near the source and target endpoints with `EdgeLabelRenderer`. Keep `type: "smoothstep"` for portable output. Use a custom edge `type`, such as `"relationship"`, only when the target React Flow app has registered it in `edgeTypes`; in that case list it in `_meta.registeredEdgeTypes`.

Recommended node fields:

- `id`: stable identifier. For newly generated nodes, always use a `node-` prefix.
- `type`: must equal `data.category`, one of `Evidence`, `Participant`, `Role`, or `Context`. The self-check script enforces this so rendering type stays aligned with FM semantics.
- `position`: always return `{ "x": 0, "y": 0 }` for generated nodes. Do not compute layout positions; the frontend owns all layout calculation.
- `parentId`: parent Context node id for child nodes inside a context. Context nodes must appear before their children.
- `extent`: use `"parent"` when child movement should stay inside the context container.
- `data.label`: human-readable business label.
- `data.name`: concise technical or English identifier; must be unique across nodes in the same model.
- `data.category`: `Evidence`, `Participant`, `Role`, or `Context`.
- `data.kind`: concrete FM kind such as `Bounded Context`, `Contract`, `Party Role`, `Fulfillment Request`, `Fulfillment Confirmation`, `Evidence As Role`, or `Other Evidence`.
- `data.attributes`: optional array for intrinsic business attributes of the node, including lifecycle time semantics when relevant. Each item should include `name`, `label`, `valueType`, `required`, and `meaning` when known.
  Evidence lifecycle attributes are mandatory for these kinds: RFP/Proposal/Fulfillment Request include `startedAt` and `expiredAt`; Contract includes `signedAt`; Fulfillment Confirmation includes `confirmedAt`; Other Evidence includes `createdAt`. Each mandatory lifecycle item must use `valueType: "DateTime"` and `required: true`.
  Any derived attribute should include `calculationRule`. This applies to lifecycle times, amounts, quantities, refund values, KPI metrics, acceptance metrics, eligibility flags, and other values derived from prior evidence or algorithmic calculation. When prior evidence is used, `calculationRule` must include the source evidence attribute path, such as `refundAmount = ColumnSubscriptionContract.columnPrice`. When the value is derived from attributes on the same evidence, local attribute names are acceptable, such as `expiredAt = startedAt + duration("PT30M")`. Direct user-input values may omit `calculationRule`. See "Attribute Calculation Rules" for expression style.
- `data.notes`: optional short explanation.

### Attribute Calculation Rules

Use parseable expression-style rules for derived attributes. Treat these fields as a small DSL contract for parser implementation, not as free text.

- `calculationRule` must be exactly one assignment expression in the form `<targetAttribute> = <expression>`.
- The left side of `calculationRule` must be the current attribute `name`. Do not assign to another attribute, multiple attributes, a node path, or a nested field.
- `precondition` must be exactly one boolean expression. It must not include an assignment operator.
- Use ASCII identifiers only: `[A-Za-z_][A-Za-z0-9_]*`. Prefer PascalCase for node `data.name` values and camelCase for attribute `name` values.
- Refer to prior evidence attributes with explicit `NodeName.attributeName` paths, such as `PaymentConfirmation.paidAmount` or `ShipmentConfirmation.confirmedAt`.
- Use local `attributeName` references only for attributes on the same evidence, such as `expiredAt = startedAt + duration("PT30M")`.
- Do not use labels, spaces, Chinese punctuation, natural-language phrases, or display names inside expressions.
- Supported literals are numbers, double-quoted strings, booleans `true` / `false`, and `null`. Do not use single-quoted strings.
- Supported arithmetic operators are `+`, `-`, `*`, `/`, and `%`.
- Supported comparison operators are `==`, `!=`, `<`, `<=`, `>`, and `>=`.
- Supported boolean operators are `&&`, `||`, and unary `!`.
- Parentheses may be used for grouping and should be used whenever precedence could be unclear.
- Supported function calls are limited to `isNull(value)`, `notNull(value)`, `if(condition, whenTrue, whenFalse)`, `duration(iso8601Duration)`, `min(a, b)`, `max(a, b)`, `round(value, digits)`, `floor(value)`, `ceil(value)`, and `abs(value)`.
- Use explicit null checks such as `isNull(ShipmentConfirmation.confirmedAt)` and `notNull(PaymentConfirmation.confirmedAt)`. Do not write `x == null` unless a direct null equality check is required for a simple data comparison.
- Use conditional expressions when a value must fall back to another value: `cancelledQuantity = if(OrderCancellationRequest.cancelable == true, OrderSalesContract.quantity, 0)`.
- Prefer a separate `precondition` field when the attribute only exists or is only valid under a business condition. In that case, keep `calculationRule` focused on the value calculation.
- Time offsets must use explicit ISO 8601 duration notation through `duration(...)`, such as `expiredAt = startedAt + duration("PT30M")`, `expiredAt = startedAt + duration("PT48H")`, or `expiredAt = startedAt + duration("P7D")`.
- Avoid mixing explanation and calculation. Put business explanation in `meaning` or `notes`, and put only the executable or machine-checkable rule in `calculationRule` and `precondition`.
- Do not use natural-language fragments such as `is absent`, `when ...`, `before shipment`, `after payment`, `within 7 days`, or `if paid then ...` inside `calculationRule` or `precondition`.

Recommended parser precedence, from highest to lowest:

1. Function calls and parenthesized expressions.
2. Unary `!` and unary `-`.
3. `*`, `/`, `%`.
4. `+`, `-`.
5. `<`, `<=`, `>`, `>=`.
6. `==`, `!=`.
7. `&&`.
8. `||`.

Minimal grammar shape:

```text
calculationRule := identifier "=" expression
precondition    := booleanExpression
path            := identifier | identifier "." identifier
functionCall    := identifier "(" arguments? ")"
arguments       := expression ("," expression)*
```

Type rules:

- `precondition` must evaluate to `Boolean`.
- The right side of `calculationRule` must be compatible with the current attribute `valueType`.
- Comparison operands should have compatible types; string, number, boolean, datetime, and money values should not be compared across incompatible domains.
- `duration(...)` may only be added to or subtracted from DateTime-like values.
- `if(condition, whenTrue, whenFalse)` requires a Boolean `condition`; `whenTrue` and `whenFalse` should resolve to compatible result types.

Prefer machine-checkable expressions for these derived attribute scenarios:

- Lifecycle windows and deadlines: `expiredAt = startedAt + duration("PT30M")`.
- Amount propagation: `payableAmount = OrderSalesContract.orderAmount`.
- Amount calculation, including refund, compensation, penalty, fee, tax, discount, commission, and settlement values: `refundAmount = PaymentConfirmation.paidAmount - CouponConfirmation.discountAmount`.
- Quantity propagation and calculation, including ordered, reserved, shipped, accepted, cancelled, returned, and available quantities: `availableQuantity = InventoryConfirmation.totalQuantity - InventoryConfirmation.reservedQuantity`.
- Eligibility, permission, or capability flags: `cancelable = notNull(PaymentConfirmation.confirmedAt) && isNull(ShipmentConfirmation.confirmedAt)`.
- Acceptance or quality metrics: `accepted = QualityInspectionConfirmation.defectRate <= QualityContract.maxDefectRate`.
- SLA and breach detection: `slaBreached = DeliveryConfirmation.confirmedAt > ShipmentFulfillmentRequest.expiredAt`.
- Conditional compensation or fallback values: `compensationAmount = if(slaBreached == true, PaymentConfirmation.paidAmount * 0.1, 0)`.
- Status classification derived from evidence completion: `fulfillmentStatus = if(notNull(DeliveryAcceptanceConfirmation.confirmedAt), "COMPLETED", "IN_PROGRESS")`.
- Risk, review, or escalation decisions: `manualReviewRequired = OrderSalesContract.orderAmount >= 5000 || BuyerRiskConfirmation.riskLevel == "HIGH"`.
- Cross-evidence consistency checks: `amountMatched = PaymentConfirmation.paidAmount == OrderSalesContract.orderAmount`.

Example:

```json
{
  "name": "cancelable",
  "label": "是否可取消",
  "valueType": "Boolean",
  "required": true,
  "meaning": "订单是否满足发货前取消条件",
  "calculationRule": "cancelable = notNull(PaymentConfirmation.confirmedAt) && isNull(ShipmentConfirmation.confirmedAt)"
}
```

```json
{
  "name": "cancelledQuantity",
  "label": "取消数量",
  "valueType": "Number",
  "required": true,
  "meaning": "取消履约的商品数量",
  "precondition": "OrderCancellationRequest.cancelable == true",
  "calculationRule": "cancelledQuantity = OrderSalesContract.quantity"
}
```

Recommended edge fields:

- `id`: stable identifier. For newly generated edges, always use an `edge-` prefix.
- `source`: exactly one source node id string. Do not use arrays or combined ids.
- `target`: exactly one target node id string. Do not use arrays or combined ids.
- `type`: React Flow edge path type such as `smoothstep`, `step`, `straight`, or `default`. Prefer `smoothstep` for generated FM graphs unless the caller provides a renderer-specific convention.
- `label`: short business phrase explaining the relationship.
- `data.sourceRelation`: endpoint cardinality text rendered near the source side by a custom edge. Must be `"1"` because every edge is a 1:1 relation.
- `data.targetRelation`: endpoint cardinality text rendered near the target side by a custom edge. Must be `"1"` because every edge is a 1:1 relation.
- `sourceHandle` / `targetHandle`: optional handle ids when a custom node exposes multiple ports.
- `markerEnd`: optional React Flow marker config, for example `{ "type": "arrowclosed" }`.
- `style`: optional React Flow CSS style object, for example `{ "strokeDasharray": "6 4" }`.

React Flow separates edge path shape from visual styling. Its built-in edge `type` values control routing/shape; arrows and dashed lines are expressed with `markerEnd` and `style`, or with a registered custom edge when the frontend needs richer behavior. A custom edge is a replacement renderer for that edge type, not an automatic extension of the built-in edge UI; implement it with React Flow helpers such as `BaseEdge`, path utilities, and `EdgeLabelRenderer` when you want the built-in visual path plus endpoint relationship labels. Use these FM visual classes:

- Default flow edge: use a solid line for normal evidence flow, participation, request/confirmation, thing-to-evidence, and same-context business relationships. Set `type: "smoothstep"` and omit `style.strokeDasharray` unless the caller asks for a different visual theme.
- Role-play edge: use a dashed arrow when a Participant Party or Thing plays a Role, such as Participant Party -> Party Role or Thing -> Domain Role. Set `type: "smoothstep"`, `markerEnd: { "type": "arrowclosed" }`, and `style: { "strokeDasharray": "6 4" }`.
- Cross-context association edge: use a dashed line for allowed cross-context bridges, specifically Fulfillment Confirmation -> Evidence As Role and Evidence As Role -> Fulfillment Confirmation. Set `type: "smoothstep"` and `style: { "strokeDasharray": "3 3" }`. Do not use this visual class to bypass the cross-context semantic rule.

Do not use custom edge `type` values such as `relationship`, `role-play`, or `cross-context-association` unless the target React Flow app has registered matching `edgeTypes`. When portability matters, keep the built-in path `type` and express visual differences with `markerEnd`, `style`, and `data.sourceRelation` / `data.targetRelation`. If a custom edge type is used, declare it in `_meta.registeredEdgeTypes`.

For an update to an existing model, return only changes by default after locally validating the merged full graph:

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

Diff id rules:

- `updateNodes` and `deleteNodes` must reference existing `node.id` values from the provided base model. Do not generate a new id when changing an existing node's label, attributes, parent, or position.
- `updateEdges` and `deleteEdges` must reference existing `edge.id` values from the provided base model.
- `addNodes` and `addEdges` must use new ids that do not exist in the base model.
- `addEdges.source` and `addEdges.target` may reference existing node ids or node ids introduced in the same `addNodes` array.
- When deleting a node, explicitly include every edge connected to that node in `deleteEdges`; do not rely on the frontend or merge script to infer cascading edge deletion.
- Never repeat the same id across add/update/delete arrays for the same graph element type.

Complete example for a medium-sized model:

This example shows multiple bounded contexts, one Contract branching to independent Fulfillment Request nodes, a reverse refund flow, same-context Other Evidence, and Evidence As Role cross-context bridges. Each edge is still a single 1:1 React Flow edge.

```json
{
  "summary": "用户购买付费专栏，完成支付后平台开通阅读权限；若专栏长期断更，用户可申请全额退款。",
  "nodes": [
    {
      "id": "node-context-1",
      "type": "Context",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "专栏订阅上下文",
        "name": "ColumnSubscriptionContext",
        "category": "Context",
        "kind": "Bounded Context"
      }
    },
    {
      "id": "node-context-2",
      "type": "Context",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "支付上下文",
        "name": "PaymentContext",
        "category": "Context",
        "kind": "Bounded Context"
      }
    },
    {
      "id": "node-1",
      "type": "Participant",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "平台用户",
        "name": "PlatformUser",
        "category": "Participant",
        "kind": "Party"
      }
    },
    {
      "id": "node-2",
      "type": "Participant",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "专栏平台",
        "name": "ColumnPlatform",
        "category": "Participant",
        "kind": "Party"
      }
    },
    {
      "id": "node-3",
      "type": "Participant",
      "position": { "x": 0, "y": 0 },
      "data": {
        "label": "付费专栏",
        "name": "PaidColumn",
        "category": "Participant",
        "kind": "Thing"
      }
    },
    {
      "id": "node-4",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "订阅用户",
        "name": "SubscriberRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-5",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "专栏服务提供方",
        "name": "ColumnProviderRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-6",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "专栏订阅订单",
        "name": "ColumnSubscriptionContract",
        "category": "Evidence",
        "kind": "Contract",
        "attributes": [
          {
            "name": "signedAt",
            "label": "签署时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户提交订阅订单并形成订阅合同的业务时间"
          },
          {
            "name": "orderedAt",
            "label": "下单时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户提交专栏订阅订单的业务时间"
          },
          {
            "name": "columnPrice",
            "label": "专栏价格",
            "valueType": "Money",
            "required": true,
            "meaning": "专栏订阅应付金额"
          }
        ]
      }
    },
    {
      "id": "node-7",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "阅读权限开通申请",
        "name": "AccessProvisionRequest",
        "category": "Evidence",
        "kind": "Fulfillment Request",
        "attributes": [
          {
            "name": "startedAt",
            "label": "开始时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "平台收到支付成功后发起权限开通的时间"
          },
          {
            "name": "expiredAt",
            "label": "失效时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "阅读权限开通申请的业务失效时间"
          },
          {
            "name": "subscriptionOrderId",
            "label": "订阅订单号",
            "valueType": "String",
            "required": true,
            "meaning": "对应的专栏订阅订单标识"
          }
        ]
      }
    },
    {
      "id": "node-8",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "阅读权限开通确认",
        "name": "AccessProvisionConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "平台完成专栏阅读权限开通的业务时间"
          },
          {
            "name": "accessExpiresAt",
            "label": "权限到期时间",
            "valueType": "DateTime",
            "required": false,
            "meaning": "如有限期则记录阅读权限到期时间"
          }
        ]
      }
    },
    {
      "id": "node-9",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "全额退款申请",
        "name": "FullRefundRequest",
        "category": "Evidence",
        "kind": "Fulfillment Request",
        "attributes": [
          {
            "name": "startedAt",
            "label": "开始时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户因专栏长期断更发起退款申请的时间"
          },
          {
            "name": "expiredAt",
            "label": "失效时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "退款申请的业务失效时间"
          },
          {
            "name": "refundAmount",
            "label": "退款金额",
            "valueType": "Money",
            "required": true,
            "meaning": "申请退回的全额金额",
            "calculationRule": "refundAmount = ColumnSubscriptionContract.columnPrice"
          },
          {
            "name": "breachReason",
            "label": "退款原因",
            "valueType": "String",
            "required": true,
            "meaning": "触发退款的长期断更原因说明"
          }
        ]
      }
    },
    {
      "id": "node-10",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "全额退款确认",
        "name": "FullRefundConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "平台确认执行全额退款的业务时间"
          },
          {
            "name": "refundAmount",
            "label": "退款金额",
            "valueType": "Money",
            "required": true,
            "meaning": "实际确认退回的金额",
            "calculationRule": "refundAmount = FullRefundRequest.refundAmount"
          }
        ]
      }
    },
    {
      "id": "node-11",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "付款方",
        "name": "PayerRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-12",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "收款方",
        "name": "PayeeRole",
        "category": "Role",
        "kind": "Party Role"
      }
    },
    {
      "id": "node-13",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付订单",
        "name": "PaymentContract",
        "category": "Evidence",
        "kind": "Contract",
        "attributes": [
          {
            "name": "signedAt",
            "label": "签署时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付订单建立并形成支付合同的业务时间"
          },
          {
            "name": "createdAt",
            "label": "创建时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付订单建立的业务时间"
          },
          {
            "name": "payableAmount",
            "label": "应付金额",
            "valueType": "Money",
            "required": true,
            "meaning": "本次支付订单需要支付的金额",
            "calculationRule": "payableAmount = ColumnSubscriptionContract.columnPrice"
          },
          {
            "name": "paymentMethod",
            "label": "支付方式",
            "valueType": "String",
            "required": true,
            "meaning": "移动支付方式标识"
          }
        ]
      }
    },
    {
      "id": "node-14",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付申请",
        "name": "PaymentRequest",
        "category": "Evidence",
        "kind": "Fulfillment Request",
        "attributes": [
          {
            "name": "startedAt",
            "label": "开始时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "用户发起移动支付的业务时间"
          },
          {
            "name": "expiredAt",
            "label": "失效时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付申请的业务失效时间",
            "calculationRule": "expiredAt = startedAt + duration(\"PT15M\")"
          },
          {
            "name": "amount",
            "label": "支付金额",
            "valueType": "Money",
            "required": true,
            "meaning": "本次支付申请金额",
            "calculationRule": "amount = PaymentContract.payableAmount"
          }
        ]
      }
    },
    {
      "id": "node-15",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付成功确认",
        "name": "PaymentSuccessConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "移动支付成功的业务时间"
          },
          {
            "name": "paidAmount",
            "label": "实付金额",
            "valueType": "Money",
            "required": true,
            "meaning": "实际支付成功的金额",
            "calculationRule": "paidAmount = PaymentRequest.amount"
          },
          {
            "name": "paymentChannelTxnId",
            "label": "渠道流水号",
            "valueType": "String",
            "required": true,
            "meaning": "第三方支付渠道返回的交易流水号"
          }
        ]
      }
    },
    {
      "id": "node-16",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付成功凭证",
        "name": "PaymentSuccessEvidenceRole",
        "category": "Role",
        "kind": "Evidence As Role"
      }
    },
    {
      "id": "node-17",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-1",
      "extent": "parent",
      "data": {
        "label": "退款确认凭证",
        "name": "RefundConfirmationEvidenceRole",
        "category": "Role",
        "kind": "Evidence As Role"
      }
    },
    {
      "id": "node-18",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "退款出款确认",
        "name": "RefundPayoutConfirmation",
        "category": "Evidence",
        "kind": "Fulfillment Confirmation",
        "attributes": [
          {
            "name": "confirmedAt",
            "label": "确认时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "退款资金退回完成的业务时间"
          },
          {
            "name": "refundAmount",
            "label": "退款金额",
            "valueType": "Money",
            "required": true,
            "meaning": "实际退回用户的金额",
            "calculationRule": "refundAmount = RefundApprovalConfirmation.refundAmount"
          }
        ]
      }
    },
    {
      "id": "node-19",
      "type": "Role",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "移动支付机构",
        "name": "MobilePaymentInstitutionRole",
        "category": "Role",
        "kind": "Third Party Role"
      }
    },
    {
      "id": "node-20",
      "type": "Evidence",
      "position": { "x": 0, "y": 0 },
      "parentId": "node-context-2",
      "extent": "parent",
      "data": {
        "label": "支付渠道回单",
        "name": "PaymentChannelReceipt",
        "category": "Evidence",
        "kind": "Other Evidence",
        "attributes": [
          {
            "name": "createdAt",
            "label": "创建时间",
            "valueType": "DateTime",
            "required": true,
            "meaning": "支付成功确认后生成渠道回单的业务时间",
            "calculationRule": "createdAt = PaymentSuccessConfirmation.confirmedAt"
          },
          {
            "name": "receiptAmount",
            "label": "回单金额",
            "valueType": "Money",
            "required": true,
            "meaning": "支付渠道回单记录的实付金额",
            "calculationRule": "receiptAmount = PaymentSuccessConfirmation.paidAmount"
          },
          {
            "name": "paymentChannelTxnId",
            "label": "渠道流水号",
            "valueType": "String",
            "required": true,
            "meaning": "支付机构回单中的渠道交易流水号",
            "calculationRule": "paymentChannelTxnId = PaymentSuccessConfirmation.paymentChannelTxnId"
          }
        ]
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-4",
      "type": "smoothstep",
      "markerEnd": { "type": "arrowclosed" },
      "style": { "strokeDasharray": "6 4" },
      "label": "用户扮演订阅用户",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-2",
      "source": "node-2",
      "target": "node-5",
      "type": "smoothstep",
      "markerEnd": { "type": "arrowclosed" },
      "style": { "strokeDasharray": "6 4" },
      "label": "平台扮演服务提供方",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-3",
      "source": "node-1",
      "target": "node-11",
      "type": "smoothstep",
      "markerEnd": { "type": "arrowclosed" },
      "style": { "strokeDasharray": "6 4" },
      "label": "用户扮演付款方",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-4",
      "source": "node-2",
      "target": "node-12",
      "type": "smoothstep",
      "markerEnd": { "type": "arrowclosed" },
      "style": { "strokeDasharray": "6 4" },
      "label": "平台扮演收款方",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-5",
      "source": "node-3",
      "target": "node-6",
      "type": "smoothstep",
      "label": "专栏是订阅标的",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-6",
      "source": "node-4",
      "target": "node-6",
      "type": "smoothstep",
      "label": "订阅用户参与订单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-7",
      "source": "node-5",
      "target": "node-6",
      "type": "smoothstep",
      "label": "服务提供方参与订单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-8",
      "source": "node-6",
      "target": "node-7",
      "type": "smoothstep",
      "label": "订单触发权限开通申请",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-9",
      "source": "node-5",
      "target": "node-7",
      "type": "smoothstep",
      "label": "服务提供方发起开通申请",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-10",
      "source": "node-7",
      "target": "node-8",
      "type": "smoothstep",
      "label": "申请得到开通确认",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-11",
      "source": "node-5",
      "target": "node-8",
      "type": "smoothstep",
      "label": "服务提供方确认开通",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-12",
      "source": "node-6",
      "target": "node-9",
      "type": "smoothstep",
      "label": "订单可触发退款申请",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-13",
      "source": "node-4",
      "target": "node-9",
      "type": "smoothstep",
      "label": "订阅用户发起退款申请",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-14",
      "source": "node-9",
      "target": "node-10",
      "type": "smoothstep",
      "label": "申请得到退款确认",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-15",
      "source": "node-5",
      "target": "node-10",
      "type": "smoothstep",
      "label": "服务提供方确认退款",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-16",
      "source": "node-11",
      "target": "node-13",
      "type": "smoothstep",
      "label": "付款方参与支付订单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-17",
      "source": "node-12",
      "target": "node-13",
      "type": "smoothstep",
      "label": "收款方参与支付订单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-18",
      "source": "node-13",
      "target": "node-14",
      "type": "smoothstep",
      "label": "支付订单触发支付申请",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-19",
      "source": "node-11",
      "target": "node-14",
      "type": "smoothstep",
      "label": "付款方发起支付申请",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-20",
      "source": "node-14",
      "target": "node-15",
      "type": "smoothstep",
      "label": "申请得到支付成功确认",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-21",
      "source": "node-12",
      "target": "node-15",
      "type": "smoothstep",
      "label": "收款方确认收款成功",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-22",
      "source": "node-15",
      "target": "node-16",
      "type": "smoothstep",
      "style": { "strokeDasharray": "3 3" },
      "label": "支付成功产生跨上下文凭证",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-23",
      "source": "node-16",
      "target": "node-8",
      "type": "smoothstep",
      "style": { "strokeDasharray": "3 3" },
      "label": "支付成功支撑权限开通确认",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-24",
      "source": "node-10",
      "target": "node-17",
      "type": "smoothstep",
      "style": { "strokeDasharray": "3 3" },
      "label": "退款确认产生跨上下文凭证",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-25",
      "source": "node-17",
      "target": "node-18",
      "type": "smoothstep",
      "style": { "strokeDasharray": "3 3" },
      "label": "退款确认支撑退款出款确认",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-26",
      "source": "node-12",
      "target": "node-18",
      "type": "smoothstep",
      "label": "收款方确认退款出款",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-27",
      "source": "node-15",
      "target": "node-20",
      "type": "smoothstep",
      "label": "支付成功确认生成渠道回单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-28",
      "source": "node-12",
      "target": "node-20",
      "type": "smoothstep",
      "label": "收款方接收渠道回单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    },
    {
      "id": "edge-29",
      "source": "node-19",
      "target": "node-20",
      "type": "smoothstep",
      "label": "支付机构提供渠道回单",
      "data": { "sourceRelation": "1", "targetRelation": "1" }
    }
  ],
  "_meta": {
    "validationNotes": [
      "示例同时展示了主合同上下文、支付上下文、退款异常流、同上下文 Other Evidence，以及通过 Evidence As Role 进行的跨上下文确认桥接。",
      "PaymentChannelReceipt 是支付上下文内部的衍生凭证，所以建模为 Other Evidence；支付成功触发订阅上下文开通时，才使用 Evidence As Role。",
      "建模时仍应根据具体需求补充属性来源说明，例如 columnPrice 来自 Proposal 或商品定价规则，PaymentRequest.expiredAt 来自 startedAt 加15分钟算法计算。"
    ],
    "registeredEdgeTypes": []
  }
}
```

Example update response for the same model:

```json
{
  "summary": "将支付申请有效期从15分钟调整为30分钟，并同步说明支付渠道回单的接收角色。",
  "changes": {
    "addNodes": [],
    "updateNodes": [
      {
        "id": "node-14",
        "data": {
          "attributes": [
            {
              "name": "startedAt",
              "label": "开始时间",
              "valueType": "DateTime",
              "required": true,
              "meaning": "用户发起移动支付的业务时间"
            },
            {
              "name": "expiredAt",
              "label": "失效时间",
              "valueType": "DateTime",
              "required": true,
              "meaning": "支付申请的业务失效时间",
              "calculationRule": "expiredAt = startedAt + duration(\"PT30M\")"
            },
            {
              "name": "amount",
              "label": "支付金额",
              "valueType": "Money",
              "required": true,
              "meaning": "本次支付申请金额",
              "calculationRule": "amount = PaymentContract.payableAmount"
            }
          ]
        }
      },
      {
        "id": "node-20",
        "data": {
          "notes": "渠道回单留在支付上下文内部，用于对账和审计，不作为跨上下文触发凭证。"
        }
      }
    ],
    "deleteNodes": [],
    "addEdges": [],
    "updateEdges": [
      {
        "id": "edge-28",
        "label": "收款方接收并归档渠道回单"
      }
    ],
    "deleteEdges": []
  },
  "_meta": {
    "validationNotes": [
      "该 diff 使用已有 node/edge id 更新节点和边；返回前应先应用到 base graph 并对 merged full graph 运行 self_check_fm_graph.py。"
    ],
    "registeredEdgeTypes": []
  }
}
```

Use `changes` as the default update transport, but validate updates against the merged full graph before returning success. Generate the diff, apply it locally to the provided base graph, run the full graph self-check, and only then return the diff. Within `changes`, update/delete arrays must target existing ids, add arrays must introduce new ids, and the same id must not repeat across add/update/delete arrays for the same graph element type. Return full `nodes` and `edges` for new models or when the caller has not provided existing ids. When the caller explicitly asks for the complete updated model, return the validated merged full graph instead of the diff.

Use `_meta` for non-rendered diagnostics. Put validation notes, assumptions, and manual review reminders in `_meta.validationNotes`. Do not put `validationNotes` at the top level.

## Naming

- Keep `data.label` as a human-readable business label. Do not append lifecycle timestamp suffixes such as `started_at`, `expired_at`, `confirmed_at`, `signed_at`, or `created_at` to node labels.
- Return key time semantics as items in `data.attributes` when helpful.
- Return entity attributes in `data.attributes`; do not encode them in `data.label`.
- Keep `data.attributes` for state or facts owned by that node.
- Required lifecycle attributes must be present in `data.attributes` with `valueType: "DateTime"` and `required: true`:
  - RFP, Proposal, and Fulfillment Request must include `startedAt` and `expiredAt`.
  - Contract must include `signedAt`.
  - Fulfillment Confirmation must include `confirmedAt`.
  - Other Evidence must include `createdAt`.
- Model concrete business actions, decisions, calculations, and lifecycle transitions with Fulfillment Request/Fulfillment Confirmation nodes and flow edges.
- Evidence As Role should usually include a `createdAt` DateTime item in `data.attributes`.
- Domain Logic and Third Party roles must use human job/position names, not technical component names such as rule engine, SDK, queue, risk service, or payment gateway.

## Edge Rules

React Flow representation:

- Edges must use the React Flow edge object shape documented at `https://reactflow.dev/`: `id`, `source`, `target`, `type`, optional `label`, optional `sourceHandle` / `targetHandle`, optional `markerEnd`, optional `style`, and optional `data`.
- Relationship cardinality is represented by separate React Flow edges, not by custom edge endpoints or overloaded labels. Each edge is always a single source-to-single target 1:1 relation. When a business relationship is one-to-many, model it as multiple independent 1:1 edges from the shared source node to each target node.
- Do not use a single edge to imply multiple targets. React Flow edges have exactly one `source` and one `target`.
- Cardinality display must use `data.sourceRelation` and `data.targetRelation`, both set to `"1"`. Do not put `1:n` on an individual edge. If the aggregate business relationship is one-to-many, the graph will show multiple 1:1 edges from the same source.
- Use `label` for the business relationship phrase, not as the source of truth for cardinality.
- Use a registered custom edge only for UI rendering, such as drawing `data.sourceRelation` and `data.targetRelation` near both endpoints. The FM semantics remain in `source`, `target`, `label`, and `data`.

Main chain:

- RFP -> Proposal -> Contract -> Fulfillment Request -> Fulfillment Confirmation.
- If no presales stage exists, start from Contract.
- Proposal -> Contract is required when Proposal exists.
- Contract -> Fulfillment Request is required; do not create standalone Fulfillment Request.
- Proposal must not connect directly to Fulfillment Request.
- Contract -> Fulfillment Request is usually one-to-many at the model level, but each edge is still 1:1: one Contract may have multiple outgoing edges to distinct Fulfillment Request nodes, and each edge connects exactly one Contract to exactly one Fulfillment Request.
- Fulfillment Request -> Fulfillment Confirmation is one-to-one: each Fulfillment Request must have exactly one direct Fulfillment Confirmation successor, and that Confirmation should not be shared as the direct confirmation for multiple Requests.
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
python3 .agents/skills/modeling/scripts/self_check_fm_graph.py /tmp/fm-graph.json
```

The script checks:

- Node ids, node `data.name` values, and edge ids are not duplicated.
- Every node `type` equals its `data.category`.
- Evidence lifecycle attributes are present with `valueType: "DateTime"` and `required: true`: RFP/Proposal/Fulfillment Request require `startedAt` and `expiredAt`; Contract requires `signedAt`; Fulfillment Confirmation requires `confirmedAt`; Other Evidence requires `createdAt`.
- Every mandatory edge has known endpoints.
- Every edge uses a supported built-in React Flow `type`, or a custom type listed in `_meta.registeredEdgeTypes`.
- Every edge follows React Flow's single-source and single-target shape; one-to-many relationships are expressed as multiple independent 1:1 edges from the same source to separate targets.
- Every edge provides `data.sourceRelation: "1"` and `data.targetRelation: "1"` for endpoint relationship rendering.
- Role-play edges use dashed arrows with `markerEnd.type: "arrowclosed"` and `style.strokeDasharray: "6 4"`.
- Cross-context association edges use dashed lines with `style.strokeDasharray: "3 3"` and no arrow marker.
- Default edges stay solid and omit `style.strokeDasharray`.
- Every RFP/Proposal/Request/Confirmation/Other Evidence has exactly one Party Role neighbor.
- Every Fulfillment Request has one direct Contract predecessor and one Fulfillment Confirmation successor.
- Every Fulfillment Request -> Fulfillment Confirmation relationship is 1:1; do not share one direct Confirmation across multiple Requests.
- Contract -> Fulfillment Request relationships may be 1:n at the aggregate level, but each individual edge is 1:1; model each Request with its own edge from the Contract.
- Cross-context edges are limited to Fulfillment Confirmation -> Evidence As Role and Evidence As Role -> Fulfillment Confirmation.
- Evidence As Role does not point to Fulfillment Request.
- Unfixable invalid edges or uncertain nodes are removed or marked unresolved.

After the script passes, manually review semantic duplication:

- Other Evidence and Evidence As Role do not duplicate the same semantic in the same model.
