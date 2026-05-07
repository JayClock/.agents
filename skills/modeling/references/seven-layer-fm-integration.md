# Seven-Layer Model Integration

Use this reference when a task asks how general ontology-driven software modeling maps into Fulfillment Modeling (FM), or when an FM graph must preserve object, behavior, rule, scenario, subject, exception, and quality semantics.

## Principle

Treat the seven-layer model as an upper ontology for coverage checking. Treat FM as the contract-centered fulfillment specialization.

Do not replace FM's core chain:

`RFP -> Proposal -> Contract -> Fulfillment Request -> Fulfillment Confirmation`

Do not create generic M1-M7 nodes unless the user explicitly asks for a seven-layer artifact. In normal FM output, encode seven-layer semantics through existing FM nodes, attributes, notes, edge labels, and validation notes.

## Mapping

| Seven-layer model | FM representation | Modeling rule |
| --- | --- | --- |
| M1 Object Model | Contract, Evidence, Thing, and evidence attributes | Put stable business facts, lifecycle time, amount, quantity, status, KPI, and acceptance facts on the evidence or thing that owns them. Keep attribute source paths clear. |
| M2 Behavior Model | Fulfillment Request -> Fulfillment Confirmation pair | Model concrete responsibilities, actions, decisions, and lifecycle transitions as request/confirmation pairs. Do not put actions on Party Role nodes. |
| M3 Rule Model | Domain Role plus calculationRule/precondition attributes | Express reusable calculation, validation, derivation, eligibility, risk, and acceptance logic as parseable `calculationRule` or `precondition`. Add a Domain Role only when a real-world calculator/assessor role matters. |
| M4 Scenario Model | Evidence flow, context chain, exception chain, and cross-context bridge | Use cause -> result edges for the business scenario. Use separate request/confirmation pairs for alternative, cancellation, refund, suspension, reversal, or compensation flows. |
| M5 Subject Model | Party, Party Role, Third Party Role, Context Role | Model identity-in-context and participation through roles. A Party Role expresses responsibility and capacity, not the action itself. |
| M6 Exception Compensation Model | Exception or breach request/confirmation pairs | Model reverse and breach handling as first-class fulfillment chains until the external dispute/litigation boundary. Use the same evidence-first discovery method as the main flow. |
| M7 Quality Constraint Model | Evidence attributes, deadlines, KPI/acceptance metrics, notes, validation notes | Capture SLA, deadline, availability, consistency, audit, idempotency, and concurrency concerns only when present or clearly implied. Prefer evidence attributes for measurable business commitments. |

## Integration Workflow

1. Start with FM discovery, not M1-M7 enumeration: identify Contract context, Party Roles, and the main cash, KPI, or acceptance evidence.
2. Build the main fulfillment chain as evidence and request/confirmation pairs.
3. Add exception and breach chains as separate request/confirmation pairs.
4. After the FM graph is coherent, run a seven-layer coverage pass:
   - M1: Are the key objects and evidence facts present with sourceable attributes?
   - M2: Are concrete responsibilities modeled as request/confirmation pairs?
   - M3: Are derived values and decisions expressed as rules instead of prose?
   - M4: Can the main and alternative scenarios be read from cause -> result edges?
   - M5: Does each evidence node have the correct participating Party Role?
   - M6: Are refund, cancellation, reversal, compensation, or breach flows modeled explicitly?
   - M7: Are measurable deadlines, KPI, acceptance, audit, or reliability commitments captured where relevant?
5. Put missing coverage into existing FM structures before introducing new constructs.

## Boundary Decisions

- Use FM as the source of truth for fulfillment semantics. The seven-layer model checks completeness; it does not loosen FM edge constraints.
- Keep object lifecycle facts on Evidence attributes when they prove a business state. Use Thing for the business subject being fulfilled, such as goods, service, subscription, account, shipment, or invoice.
- Use `calculationRule` for machine-checkable derivations. Use `notes` only for short business explanation.
- Keep UI/UX, infrastructure deployment, database implementation, and low-level code design outside FM unless the user explicitly asks for a separate artifact.

## Output Guidance

When the user asks for integration analysis, return a short conceptual mapping and the recommended FM modeling order.

When the user asks for a graph, return only the FM graph shape. If useful, add a `_meta.validationNotes` item that the seven-layer coverage pass was applied and list unresolved coverage gaps.
