# FM Database Table Mapping Rules

Use this reference when a task asks to map Fulfillment Modeling (FM) graphs into microservice database tables, physical schema, SQL DDL, or ontology M1 object-model storage design.

## Core Laws

Apply these laws before choosing any table shape:

1. Node independence: map each business evidence node kind to its own physical table. Do not collapse Contract, Request, Confirmation, and Other Evidence into one status-driven wide table.
2. Append-only evidence: treat Evidence rows like accounting vouchers. Allow Create and Read by default; avoid Update and Delete for business-state progression.
3. Business-time traceability: carry over business time attributes when they appear in the FM graph or requirements because they support control flow, SLA checks, audit, and reconciliation.
4. Ubiquitous language: name tables from FM business terms so graph labels, code, and database tables share the same vocabulary.

## Node-To-Table Mapping

Map concrete FM nodes to independent tables:

- Contract: create the main contract table, such as `subscription_contract`. Store static transaction commitments, contracting parties, target Thing, signing time when present, agreed amount, duration, quantity, and terms.
- Fulfillment Request: create one request ledger table per action, such as `payment_request`, `shipment_request`, or `refund_request`. Store who initiated the action, target contract, requested amount or quantity, request-specific parameters, and business timing fields when present.
- Fulfillment Confirmation: create one confirmation receipt table per result, such as `payment_confirmation`, `shipment_confirmation`, or `refund_confirmation`. Store a related request id only when the FM graph links the confirmation to a request; also store confirmation time when present, actual result, actual amount or quantity, and external receipt identifiers when relevant.
- Other Evidence: create a concrete business-document table, such as `revenue_recognition`, `electronic_invoice`, `warehouse_receipt`, or `delivery_note`. Store the producing confirmation id, document creation time when present, document number, amount, tax, and document-specific facts.
- Participant Party and Thing: create or reference static entity tables such as `party`, `user_account`, `merchant`, `product`, `sku`, or `virtual_asset`. Usually connect these to Contract with foreign keys. Add direct foreign keys to Request or Confirmation only when the evidence itself needs that participant or object for traceability.
- Role nodes: normally do not become state tables. Represent Party Role through foreign key columns or join tables when one contract/evidence has explicit participants. Represent Domain Role calculation output as columns or separate evidence only when the calculation result is an auditable business fact.
- Context: use service/database/schema/module boundaries, not a row table, unless the platform already stores context metadata.
- Evidence As Role: persist the source confirmation and downstream confirmation independently. Use an outbox, inbox, event log, or bridge table to record the asynchronous cross-context handoff; do not replace either context's evidence tables with a shared table.

## Append-Only Write Rules

Model business progress by inserting new evidence rows:

- Do not update `refund_request.status` from requested to approved. Insert `refund_confirmation` with `request_id`, `confirmed_at`, result, and amount.
- Do not delete or overwrite an incorrect voucher. Insert a reversal, correction, cancellation, or compensation evidence row that references the original row.
- Keep operational retry metadata separate from business evidence where possible. Technical retry counters may live in infrastructure tables; business truth remains immutable evidence.
- Use uniqueness constraints and idempotency keys to prevent duplicate inserts for the same business command or external receipt.
- If a physical system must maintain a read-optimized current-state projection, mark it as a projection/cache derived from append-only evidence, not as the source of truth.

## Common Columns

Use snake_case for database columns even when graph attributes use camelCase:

- Contract tables usually include `id`, participant foreign keys, Thing foreign key when relevant, and static commitments such as `contract_amount`, `currency`, `quantity`, or terms. Include signing or term time columns only when present in the FM graph or requirements.
- RFP and Proposal tables usually include `id`, proposal/request payload columns, validity-window columns when present, and natural keys when relevant.
- Fulfillment Request tables usually include `id`, `contract_id` or an upstream evidence id, initiating Party Role reference, request payload columns, idempotency key when commands may be retried, and business timing columns when present.
- Fulfillment Confirmation tables usually include `id`, `request_id`, confirming Party Role reference, result columns, actual amount/quantity/time fields, and confirmation time when present.
- Other Evidence tables usually include `id`, producing evidence foreign key, document number or natural key when present, document-specific facts, and document time columns when present.
- Cross-context handoff tables or outbox records usually include source evidence id, event type, occurred time when present, payload reference, delivery status, and downstream correlation id when available.

## Static And Dynamic Data

Separate static commitments from dynamic realized facts:

- Put agreed, expected, receivable, or planned values on Contract or Request tables.
- Put actual, paid, received, shipped, recognized, refunded, invoiced, accepted, or failed values on Confirmation or Other Evidence tables.
- Keep money fields explicit: amount, currency, tax, discount, fee, commission, and settlement values should not be hidden in JSON unless the domain truly requires flexible attributes.
- Preserve calculation lineage. When a field is derived from prior evidence, document or encode the source path, such as `refund_confirmation.refund_amount = refund_request.refund_amount`.

## Foreign Key And Traceability Rules

Use foreign keys to preserve FM graph edges:

- Request tables usually reference the Contract table with `contract_id`.
- Confirmation tables reference a Request table with `request_id` only when the FM graph contains that relationship.
- Other Evidence tables must reference the Confirmation or Evidence that produced them.
- Participant and Thing tables usually connect to Contract; add extra references to evidence only when that evidence needs independent audit identity.
- Cross-context collaboration must reference immutable source evidence and immutable downstream evidence. Do not connect unrelated context tables by mutable status columns.

## Naming Rules

Name tables directly from FM node labels:

- `<request> 支付申请` becomes `payment_request`.
- `<confirmation> 支付确认` becomes `payment_confirmation`.
- `<contract> 订阅合同` becomes `subscription_contract`.
- `Revenue Recognition` becomes `revenue_recognition`.

Prefer singular table names if that is the local convention, but keep the FM suffixes `contract`, `request`, `confirmation`, and specific evidence names intact. Do not name source-of-truth tables around transient statuses, such as `order_status`, when the FM graph names concrete evidence.

## Output Guidance

When producing database design from an FM graph:

1. List tables grouped by bounded context.
2. For each table, state the source FM node, purpose, key columns, business time columns present in the graph or requirements, foreign keys, uniqueness/idempotency constraints, and append-only notes.
3. Call out any read-model/projection tables separately from source-of-truth evidence tables.
4. Include SQL DDL only when requested or when it materially clarifies the design.
5. Flag any attempted wide-table or status-update design as a mismatch with FM.
