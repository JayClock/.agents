---
name: fm-database-design
description: Map Fulfillment Modeling (FM) graphs into append-only microservice database table designs, physical schemas, SQL DDL, and ontology M1 object-model storage. Use when Codex needs to derive Contract, Fulfillment Request, Fulfillment Confirmation, Other Evidence, Participant, foreign keys, immutable evidence persistence, table naming, idempotency constraints, outbox/inbox handoff tables, or read-model projections from an FM graph or FM-style requirements.
---

# FM Database Design

## Purpose

Design physical database tables from Fulfillment Modeling (FM) without collapsing business evidence into mutable status tables. Treat the FM graph as the source of truth for table boundaries, timestamps, foreign keys, and append-only write behavior.

## Workflow

1. Start from an existing FM graph when provided. If the user gives only requirements, first identify the minimum FM chain needed for storage design: Contract, Request, Confirmation, Other Evidence, Participant, Thing, Context, and cross-context bridges.
2. Group tables by Bounded Context or microservice boundary. Treat Context as a service/schema/module boundary, not a normal business row table.
3. Map each concrete FM Evidence node to an independent source-of-truth table. Do not merge Contract, Request, Confirmation, and Other Evidence into one wide table with mutable status.
4. Apply append-only persistence: business progress creates new Evidence rows. Corrections, reversals, cancellations, and compensation are new rows referencing prior evidence.
5. Preserve lifecycle timestamps as required columns: Contract `signed_at`; RFP/Proposal/Request `started_at` and `expired_at`; Confirmation `confirmed_at`; Other Evidence `created_at`.
6. Separate static commitments from dynamic realized facts. Put agreed/planned values on Contract or Request tables; put actual/paid/shipped/recognized/refunded values on Confirmation or Other Evidence tables.
7. Translate FM edges into foreign keys and traceability constraints: Request -> Contract, Confirmation -> Request, Other Evidence -> producing Confirmation, and cross-context handoffs through immutable evidence plus outbox/inbox or bridge records.
8. Use FM labels as ubiquitous language for table names, converted to the local database naming convention.
9. Add idempotency, uniqueness, and projection/read-model guidance where relevant.

## Output Guidance

For table design output, group by context and include for each table:

- Source FM node or edge.
- Purpose.
- Key columns and required timestamps.
- Primary key, foreign keys, unique constraints, and idempotency keys.
- Append-only notes and whether the table is source-of-truth evidence or a derived projection.

Generate SQL DDL only when requested or when it materially clarifies the design. When generating SQL, prefer explicit scalar columns for money, currency, quantity, business time, external receipt ids, and audit identifiers. Use JSON only for genuinely variable payloads.

## Reference

Read `references/table-mapping-rules.md` before producing database schema, SQL DDL, physical table lists, or persistence guidance from FM graphs.
