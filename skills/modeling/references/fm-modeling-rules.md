# Fulfillment Modeling Rules

Use these rules when a task needs precise Fulfillment Modeling generation or validation.

## FM Process

1. Contract context first: identify Contract and its key Party Roles before other entities. Treat one Contract as one primary chain and identify the contracting sides first. Participant Party is optional supporting information, not the main modeling entry.
2. Presales evidence: add RFP and Proposal only when the requirement contains a presales stage. If no presales stage exists, start directly from Contract.
3. Evidence-first discovery: within each Contract context, first look for the main cash movement evidence. Create the money-related evidence that best anchors the business obligation and list key attributes such as business time point, amount, currency, payment window, quantity, or refund amount when applicable. If cash movement is weak or absent, start from the key KPI or acceptance evidence instead.
4. Attribute source tracing: for every key attribute on the current evidence, trace its source and keep the source path clear. A source may only come from user input, a prior evidence entity, or algorithmic calculation. If an amount, currency, quantity, payment window, refund amount, KPI, or acceptance metric is derived from a prior evidence entity, record both the prior evidence path and the calculation rule used to derive it. Do not keep attributes whose source cannot be explained.
5. Main fulfillment items: return from the anchor evidence to the rights and obligations it proves, then discover the surrounding evidence needed to establish, request, and confirm those obligations. Model each concrete responsibility as Fulfillment Request -> Fulfillment Confirmation pairs, and ensure every evidence entity carries the key attributes needed for business traceability.
6. Exceptions and breach flows: for refund, cancellation, service suspension, reversal, compensation, and similar breach or exception flows, repeat the same evidence discovery method from the related money evidence or KPI/acceptance evidence, then model them as their own Request -> Confirmation pairs. Continue expanding breach handling until the requirement reaches an external dispute or litigation boundary.
7. Evidence flow before roles: first complete the mutually connected evidence flow, then refine the model around each evidence by adding the roles involved in creating, requesting, confirming, calculating, or bridging it.
8. Party role modeling: extract Party Roles for each business subject and connect them to Contract or to the evidence they participate in. A Party Role expresses identity-in-context, responsibility, and participation; it does not replace concrete business actions. Add Participant Party only when explicit party identity matters; connect Participant Party -> Party Role -> Contract.
9. Role splitting: add Party Role, Evidence As Role, Third Party Role, Context Role, and Domain Role according to business intent. For Domain Logic and Third Party roles, first ask what real-world job did this work before software existed, then name the role with job/position semantics.
10. Participation rule: every RFP, Proposal, Fulfillment Request, Fulfillment Confirmation, and Other Evidence must have exactly one participating Party Role.
11. Other Evidence vs Evidence As Role:
    - Use Other Evidence when a confirmation produces a business document or byproduct that stays inside the same context.
    - Use Evidence As Role when that same semantic bridges contexts.
    - Do not keep both entities for the same business semantic.
12. Evidence As Role bridge rule: only use Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation. Do not connect Evidence As Role to Contract, Fulfillment Request, Proposal, or RFP. Evidence As Role belongs to the Context of the source confirmation that produced it.
13. Third Party Role and Context Role may only participate in Other Evidence or Evidence As Role. They must not directly participate in RFP, Proposal, Contract, Fulfillment Request, or Fulfillment Confirmation.
14. Multi-contract handling:
    - One Contract equals one primary chain.
    - Each Contract context independently follows the full process.
    - Each Context contains its own chain from RFP or Contract through terminal Other Evidence or Evidence As Role.
    - Participant Party entities stay outside Contexts.
    - The same real-world party may appear as different Party Roles in different contexts through one external Participant Party.
    - Different contract contexts may only bridge through Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation.
    - Do not connect Contract directly to Contract or to another context's Request/Confirmation.
15. Boundary and flow: after roles and participants are clear, place Party and Thing into the appropriate domain boundaries. Relationships should express evidence flow, role participation, and context collaboration while keeping business control flow separate from domain calculation logic.
16. Completeness check: after the evidence chain is coherent, verify that business objects, responsibilities, rules, lifecycle facts, downstream signals, and scenario paths are all represented through existing FM entities, attributes, notes, relationship labels, and validation notes. Do not introduce extra framework-specific layer entities.

## Business Semantics Completeness

Keep FM focused on business semantics rather than technical implementation:

- Include business contracts, obligations, roles, evidence, business objects, lifecycle facts, rules, downstream signals, and scenario paths.
- Exclude database tables, API endpoints, service modules, framework classes, deployment components, queues, jobs, integration mechanisms, and display-layer concerns unless the user explicitly asks for implementation design.
- Name Domain Role and Third Party Role with real-world business job, institution, or responsibility semantics instead of system names.

Place each business semantic in the existing FM model this way:

- Business objects and stable facts belong in Contract, Thing, Evidence, Evidence attributes, Context, Party, or Party Role.
- Business responsibilities belong in Fulfillment Request -> Fulfillment Confirmation pairs. A request is the business instruction or attempted transition; a confirmation is the business result that proves the responsibility was fulfilled or rejected.
- Business rules belong in `precondition`, `calculationRule`, Domain Role, evidence attributes, and entity/relationship notes where needed.
- Downstream business signals belong in Confirmation-driven evidence flow. Same-context signal effects become downstream requests, confirmations, or Other Evidence. Cross-context signal effects must use the allowed Fulfillment Confirmation -> Evidence As Role -> downstream Fulfillment Confirmation bridge.
- Business relationships belong in FM relationships, participation relationships, role-play relationships, context membership, and allowed cross-context bridges. Each relationship remains a single 1:1 source-to-target relation.
- Business scenarios belong in coherent evidence chains that cover main flow, alternative flow, exception flow, cancellation, refund, suspension, reversal, compensation, and terminal business outcomes.

When a source requirement describes an atomic business behavior with fields such as actor, owner entity, trigger, preconditions, applied rules, postconditions, or produced events, translate it into FM like this:

- Actor becomes a Party Role or other allowed Role participating in the relevant Evidence.
- Owner entity becomes the Contract, Thing, or Evidence whose attributes carry the business fact being changed.
- Trigger becomes the incoming relationship into the Fulfillment Request, or the source Confirmation/Evidence that makes the request meaningful.
- Preconditions become request attributes with `precondition`, eligibility attributes with `calculationRule`, or validation notes when the source rule is not machine-checkable.
- Applied rules become parseable `calculationRule` values where possible, Domain Role responsibility where a business actor performs a decision, or validation notes where the source rule is not machine-checkable.
- Postconditions become Fulfillment Confirmation attributes and downstream Evidence.
- Produced business signals become downstream evidence flow or Evidence As Role bridges, not a generic event entity by default.

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

FM does not model lifecycle as standalone status entities. Express lifecycle by proving each meaningful state change through business evidence.

Use this mapping:

- State: an Evidence, Thing, or Contract attribute such as `supplierStatus`, `fulfillmentStatus`, `inspectionStatus`, `riskStatus`, or `terminated`.
- Initial state: the Contract, presales evidence, admission request, creation request, or first Fulfillment Confirmation attribute that establishes the lifecycle.
- State transition: a Fulfillment Request -> Fulfillment Confirmation pair.
- Trigger behavior: the Fulfillment Request and its incoming cause relationship.
- Guard condition: request `precondition`, eligibility flag, or parseable `calculationRule`.
- Transition result: Fulfillment Confirmation attributes such as `confirmedStatus`, `effectiveStatus`, `terminated`, `suspendedAt`, or `effectiveAt`.
- Follow-up event: downstream Fulfillment Request/Confirmation, Other Evidence, or Evidence As Role bridge.
- Terminal state: terminal Confirmation or terminal status attribute; do not create a terminal state entity by default.

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

```yaml
name: suspendable
label: 是否可暂停
valueType: Boolean
required: true
meaning: 供应商是否满足暂停合作条件
calculationRule: suspendable = SupplierQualityConfirmation.qualityScore < 60 || SupplierBreachConfirmation.majorDeliveryBreach == true
```

```yaml
name: effectiveSupplierStatus
label: 生效后的供应商状态
valueType: Enum
required: true
meaning: 供应商暂停确认完成后生效的生命周期状态
precondition: SupplierSuspensionRequest.suspendable == true
calculationRule: effectiveSupplierStatus = "SUSPENDED"
```

If the user asks for a lifecycle state diagram, generate it as a derived view from the FM evidence chain. The source of truth remains the FM graph: states are derived from attributes, and transitions are derived from Request -> Confirmation pairs.

## Entity Categories

- Evidence: RFP, Proposal, Contract, Fulfillment Request, Fulfillment Confirmation, Other Evidence.
- Participant: Party, Thing.
- Role: Party Role, Domain Role, Third Party Role, Context Role, Evidence As Role.
- Context: bounded business context containers such as payment, inventory, invoice, delivery, subscription, service, or support.

## Entity Type Dictionary

Use this dictionary to choose entity kinds and avoid semantic drift. Treat Evidence as time-bearing business facts, Participant as static placeholders, Role as responsibility or calculation participants, and Context as bounded business containers.

### Evidence

Evidence entities represent business actions, commitments, or result artifacts that actually happened at a business time point. They form the dynamic business control flow and must carry lifecycle timestamps:

- Contract: the main modeling starting point. It represents the physical moment when buyer and seller form a transaction agreement and defines rights and obligations. Require `signedAt`.
- RFP: presales evidence for an initial customer intention, inquiry, or requirements request. Require `startedAt` and `expiredAt`.
- Proposal: presales evidence for the concrete offer, solution, or quotation commitment responding to an RFP, usually with a validity window. Require `startedAt` and `expiredAt`.
- Fulfillment Request: the initiating instruction for a forward or reverse action derived from a Contract, such as payment, shipment, refund, or cancellation. It starts an execution responsibility. Require `startedAt` and business deadline `expiredAt`.
- Fulfillment Confirmation: the paired delivery result for a Fulfillment Request, whether success or failure. Require `confirmedAt`.
- Other Evidence: static business documents or byproducts produced after confirmation and kept inside the same business context, such as revenue recognition records, electronic invoices, or warehouse receipt documents. Require `createdAt`.

### Participant

Participant entities represent objectively existing physical entities or business objects. In FM graphs they are static domain skeleton placeholders, not expanded field models. Connect them to Contract or presales Evidence through roles or direct business association when the identity or object matters.

- Party: a real transaction participant, such as a specific customer company, supplier, or natural person. Add it only when the model must distinguish physical identity from business role.
- Thing: the concrete object around which the transaction or fulfillment action occurs, such as goods, paid content, or virtual assets. Use it to answer what the contract sells or fulfills.

### Role

Role entities answer who initiates, calculates, executes, receives, or bridges Evidence. Connect them to Evidence with participation/support semantics; do not model actions as roles.

- Party Role: the identity, responsibility, and authority of a participant inside the current context, such as buyer, seller, or purchaser. Every Evidence entity that requires participation must have exactly one Party Role participant.
- Domain Role: a black-box business calculator, verifier, or rule performer, such as a price assessor or discount approver. Name it as a real-world job or position, not as a software system.
- Third Party Role: an external institution outside internal control, such as a payment institution or tax invoice platform. It may connect only to Other Evidence or Evidence As Role, never directly into the core internal fulfillment flow.
- Context Role: another internal business domain acting as a downstream agent, such as warehouse context or points context. Use only for cross-context collaboration.
- Evidence As Role: a special bridge where a source-context Evidence becomes a role-like trigger for another context. Enforce the exact bridge pattern `Fulfillment Confirmation -> Evidence As Role -> downstream Fulfillment Confirmation`.

### Context

- Bounded Context: a macroscopic business boundary container, such as payment, inventory, fulfillment, subscription, or invoicing. Each Context must contain a complete independent chain from Contract to terminal Evidence. Contexts are decoupled and may cooperate only through Evidence As Role bridges.

## File Output

For a new/initial model, write YAML files directly to disk. Use the directory requested by the user; if none is specified, use `fm-model/` under the current working directory. The files on disk are the source of truth.

Recommended directory layout:

```text
fm-model/
  summary.yaml
  entities/
    SalesFulfillmentContext.yaml
    SellerFulfillmentRole.yaml
    SalesContract.yaml
    DeliveryRequest.yaml
    DeliveryConfirmation.yaml
  relationships/
    SalesContract_to_DeliveryRequest.yaml
    DeliveryRequest_to_DeliveryConfirmation.yaml
    SellerFulfillmentRole_to_DeliveryRequest.yaml
    SellerFulfillmentRole_to_DeliveryConfirmation.yaml
```

Each YAML file contains exactly one semantic object. Use friendly, stable filenames based on business `name` values. The entity `name` is the stable reference key used by relationships and context membership.

Recommended `summary.yaml`:

```yaml
type: summary
summary: 销售履约模型
```

Recommended entity file `entities/SalesFulfillmentContext.yaml`:

```yaml
type: entity
category: Context
kind: Bounded Context
name: SalesFulfillmentContext
label: 销售履约上下文
```

Recommended entity file `entities/SalesContract.yaml`:

```yaml
type: entity
category: Evidence
kind: Contract
name: SalesContract
label: 销售合同
context: SalesFulfillmentContext
attributes:
  - name: signedAt
    label: 签署时间
    valueType: DateTime
    required: true
    meaning: 合同签署完成的业务时间
  - name: contractAmount
    label: 合同金额
    valueType: Money
    required: true
    meaning: 双方约定的履约金额
```

Recommended relationship file `relationships/SalesContract_to_DeliveryRequest.yaml`:

```yaml
type: relationship
source: SalesContract
target: DeliveryRequest
label: 合同触发交付申请
```

Relationship files are first-class graph objects. Do not embed relationships inside entity files except as optional non-authoritative references when explicitly requested.

Use entity `name` as the stable reference key. Entity filenames should use entity `name`, such as `SalesContract.yaml`; relationship filenames should use source and target entity names, such as `SalesContract_to_DeliveryRequest.yaml`. If a filename collides, append a short meaningful qualifier or numeric suffix. Use ASCII letters, numbers, `_`, and `-` in filenames. Entity `name` values must be non-empty and unique across all entity files. Relationship filenames must be unique across all relationship files. Every relationship endpoint must reference an existing entity by `name`.

Each relationship file is a scalar 1:1 relation: `source` is exactly one entity `name` and `target` is exactly one entity `name`. Do not use arrays, comma-separated names, wildcards, or custom endpoint payloads to express one-to-many. When a Contract has multiple Fulfillment Requests, write multiple independent relationship files that reuse the Contract as `source` and point to one Fulfillment Request each.

Recommended entity fields:

- `type`: must be `entity`.
- `category`: `Evidence`, `Participant`, `Role`, or `Context`.
- `kind`: concrete FM kind such as `Bounded Context`, `Contract`, `Party Role`, `Fulfillment Request`, `Fulfillment Confirmation`, `Evidence As Role`, or `Other Evidence`.
- `name`: concise technical or English identifier; must be unique across entities in the same model.
- `label`: human-readable business label.
- `context`: parent business Context entity `name` for entities inside a context. Context entities must appear before their members. Participant Party entities must not have `context`.
- `attributes`: optional array for intrinsic business attributes of the entity, including lifecycle time semantics when relevant. Each item should include `name`, `label`, `valueType`, `required`, and `meaning` when known.
  Evidence lifecycle attributes are mandatory for these kinds: RFP/Proposal/Fulfillment Request include `startedAt` and `expiredAt`; Contract includes `signedAt`; Fulfillment Confirmation includes `confirmedAt`; Other Evidence includes `createdAt`. Each mandatory lifecycle item must use `valueType: "DateTime"` and `required: true`.
  Any derived attribute should include `calculationRule`. This applies to lifecycle times, amounts, quantities, refund values, KPI metrics, acceptance metrics, eligibility flags, and other values derived from prior evidence or algorithmic calculation. When prior evidence is used, `calculationRule` must include the source evidence attribute path, such as `refundAmount = ColumnSubscriptionContract.columnPrice`. When the value is derived from attributes on the same evidence, local attribute names are acceptable, such as `expiredAt = startedAt + duration("PT30M")`. Direct user-input values may omit `calculationRule`. See "Attribute Calculation Rules" for expression style.
- `notes`: optional short explanation.

Recommended relationship fields:

- `type`: must be `relationship`.
- `source`: exactly one source entity `name` string. Do not use arrays or combined names.
- `target`: exactly one target entity `name` string. Do not use arrays or combined names.
- `label`: short business phrase explaining the relationship.
- `notes`: optional short explanation.

Do not include display-layer fields in FM YAML files. The model should only carry business semantics and graph connectivity.

## Attribute Calculation Rules

Use parseable expression-style rules for derived attributes. Treat these fields as a small DSL contract for parser implementation, not as free text.

- `calculationRule` must be exactly one assignment expression in the form `<targetAttribute> = <expression>`.
- The left side of `calculationRule` must be the current attribute `name`. Do not assign to another attribute, multiple attributes, an entity path, or a nested field.
- `precondition` must be exactly one boolean expression. It must not include an assignment operator.
- Use ASCII identifiers only: `[A-Za-z_][A-Za-z0-9_]*`. Prefer PascalCase for entity `name` values and camelCase for attribute `name` values.
- Refer to prior evidence attributes with explicit `EntityName.attributeName` paths, such as `PaymentConfirmation.paidAmount` or `ShipmentConfirmation.confirmedAt`.
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

## File Updates

For an update to an existing model, update the YAML files directly:

- Create a new entity YAML file under `entities/` for each new entity.
- Create a new relationship YAML file under `relationships/` for each new relationship.
- Overwrite an existing entity or relationship YAML file when its business semantics change.
- Delete obsolete entity or relationship YAML files when the semantic is removed.
- When deleting an entity, delete every incident relationship file as part of the same update.

File update rules:

- Existing entities keep their `name` when labels, attributes, context membership, or notes change unless the business concept itself is renamed.
- New entities use `name` values that do not exist in the current model directory.
- Relationship `source` and `target` may reference existing entity names or entity names created during the same modeling task.
- Never keep a relationship file whose `source` or `target` entity file no longer exists.
- The current file contents represent the current model state.

After every file update, run the YAML self-check against the model directory and fix reported issues before responding. If assumptions or manual review reminders are needed, incorporate them into appropriate entity/relationship `notes` fields or state them outside the model files.

## Modeling Anti-Patterns

- Do not model lifecycle as standalone status entities.
- Do not model APIs, services, message queues, jobs, databases, tables, screens, SDKs, engines, or technical components as FM entities unless the user explicitly asks for implementation design outside FM.
- Domain Logic and Third Party roles must use human job/position names, not technical component names such as rule engine, SDK, queue, risk service, or payment gateway.
- Do not model the same business semantic as both Other Evidence and Evidence As Role.
- Do not connect Contract directly to Contract or to another context's Request/Confirmation.
- Do not use arrays, comma-separated names, wildcards, or custom endpoint payloads as relationship endpoints.
- Do not put aggregate cardinality such as `1:n` on an individual relationship. Represent one-to-many with multiple 1:1 relationships.

## Self-Check Checklist

After writing YAML files and running the self-check, manually verify:

- Each important business object has a home in Contract, Thing, Evidence, or attributes.
- Each meaningful business responsibility has a Fulfillment Request -> Fulfillment Confirmation pair.
- Each Request has exactly one direct Contract predecessor and exactly one direct Confirmation successor.
- Each Evidence requiring participation has exactly one adjacent Party Role.
- Each mandatory lifecycle timestamp exists and is `DateTime` with `required: true`.
- Each non-trivial rule is traceable to `precondition`, `calculationRule`, Domain Role, or notes.
- Each downstream signal is represented as evidence flow or an Evidence As Role bridge.
- Cross-context relationships are limited to Fulfillment Confirmation -> Evidence As Role and Evidence As Role -> Fulfillment Confirmation.
- Third Party Role and Context Role only connect to Other Evidence or Evidence As Role.
- Entity names and relationship filenames are unique.
- Relationship `source` and `target` each reference exactly one existing entity `name`.
- No display-layer fields appear in the FM graph.
- YAML files are valid, each file contains exactly one object, and each object uses `type: summary`, `type: entity`, or `type: relationship`.
- Unfixable invalid relationships or uncertain entities are removed or marked unresolved outside the graph payload.
