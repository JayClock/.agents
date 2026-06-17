---
name: modeling
description: General Fulfillment Modeling guidance for analyzing business/software requirements into contract-centered, presentation-neutral graph models written directly as YAML files by default. Use when Codex needs to create or update FM model YAML files, identify Contract contexts, Party Roles, presales evidence, Fulfillment Request and Fulfillment Confirmation evidence, Other Evidence, Evidence As Role, multi-contract boundaries, valid FM relationship constraints, business rules, downstream signals, or scenario paths without binding to a physical database schema or screen schema. For database table design from FM graphs, use the fm-database-design skill instead.
---

# Fulfillment Modeling

## Purpose

Model requirements with Fulfillment Modeling (FM): start from contracts and business fulfillment responsibilities, then derive contexts, roles, evidences, requests, confirmations, and valid business-flow relationships. Prefer business semantics over technical components.

FM is a pure business-semantic model. Keep database tables, APIs, services, modules, deployment, frameworks, screen concerns, and other technical implementation details outside the model unless the user explicitly asks for a separate implementation artifact. Business objects, responsibilities, rules, downstream signals, and scenario paths must be expressed through FM's existing Contract/Evidence/Request/Confirmation/Role/Context entity kinds and relationship constraints.

## Workflow

1. Identify Contract contexts first. Treat one Contract as one primary fulfillment chain; if multiple contracts exist, model each chain independently.
2. Extract Party Roles for every business subject and connect them to the relevant Contract. Distinguish Participant Party from Party Role: a Participant Party is the global real-world person or organization identity; a Party Role is that Party's identity, responsibility, and authority inside one Contract/Context. The number of global Parties depends on how many independent real-world people or organizations the business must distinguish. For key contracting sides, beneficiaries, fulfillers, or cross-context identity tracking, create or reuse the Participant Party and connect `Participant Party -> Party Role -> Contract`; if the Participant Party is omitted, it should be because the physical identity is not important or is unknown in the current model.
3. Add optional presales Evidence only when present in the requirement: RFP before Proposal, Proposal before Contract.
4. Add Fulfillment Request and Fulfillment Confirmation evidence only when the requirement needs request or result traceability. Do not force both to appear together; include reverse or exception flows such as refund, cancellation, suspension, or reversal according to the business evidence that must be retained.
5. Add Other Evidence for internal business documents produced by confirmations. If the evidence bridges contexts, model it as Evidence As Role instead and do not keep duplicate Other Evidence for the same semantic.
6. Add Domain, Third Party, Context, or Evidence roles only when they represent real business participation. Name Domain Logic and Third Party roles as human job/position semantics from the pre-software world, not as technical systems.
7. Assign business-chain entities to their Context with `context`, using the Context entity `name`. Keep Participant Party outside Context containers.
8. Create relationships from cause to result or initiator to action so the model reads left-to-right as business flow. Each relationship is a single 1:1 source-to-target relation; model aggregate one-to-many relationships as multiple independent 1:1 relationships.
9. Write the model directly to YAML files by default. Use the user-provided model directory when specified; otherwise use `fm-model/` under the current working directory. Store each entity as one YAML file under `entities/`, each relationship as one YAML file under `relationships/`, and a short model summary in `summary.yaml`. Treat the YAML files as the source of truth. After writing files, run the YAML model self-check and fix every reported issue before responding.

## Output Guidance

The model's semantic core is graph entities and relationships. Persist the graph as YAML files by default. Write files and respond with changed file paths plus check status.

Default directory layout:

```text
fm-model/
  summary.yaml
  entities/
    SalesFulfillmentContext.yaml
    SellerFulfillmentRole.yaml
    SalesContract.yaml
  relationships/
    SalesContract_to_DeliveryRequest.yaml
    DeliveryRequest_to_DeliveryConfirmation.yaml
```

Each YAML file contains exactly one semantic object. Use friendly, stable filenames based on business `name` values. The entity `name` is the stable reference key used by relationships and context membership.

Example `summary.yaml`:

```yaml
type: summary
summary: 销售履约模型
```

Example entity file `entities/SalesContract.yaml`:

```yaml
type: entity
category: Evidence
kind: Contract
name: SalesContract
label: 销售合同
context: SalesFulfillmentContext
attributes:
  - name: contractAmount
    label: 合同金额
    valueType: Money
    required: true
    meaning: 双方约定的履约金额
```

Example relationship file `relationships/SalesContract_to_DeliveryRequest.yaml`:

```yaml
type: relationship
source: SalesContract
target: DeliveryRequest
label: 合同触发交付申请
```

For a new/initial model, create the directory layout and write every entity and relationship file. For an existing model, update files in place: create new YAML files for new graph elements, overwrite existing YAML files for changed graph elements, and delete YAML files for removed graph elements. The files on disk are the source of truth.

Filename rules: entity filenames should be derived from entity `name`, such as `SalesContract.yaml`. Relationship filenames should be derived from the source and target entity names, such as `SalesContract_to_DeliveryRequest.yaml`. If a filename collides, append a short meaningful qualifier or numeric suffix. Use ASCII letters, numbers, `_`, and `-` in filenames.

Entity `name` values must be non-empty and unique across all entity files. Relationship filenames must be unique across all relationship files. Each relationship must use scalar string `source` and `target` entity names that reference existing entity files. When deleting an entity, also delete every incident relationship file; never leave dangling relationships.

Do not introduce project-specific persistence payload fields, enum spellings, validation fields, or screen/presentation fields unless another skill or the user provides that target schema.

## Executable Self-Check

After writing or updating YAML files, run the YAML model self-check against the model directory:

```bash
python3 scripts/self_check_fm_yaml.py fm-model/
```

Use the user-provided model directory instead of `fm-model/` when applicable. Fix every reported issue before responding.

The check must cover valid YAML files, one object per file, supported `type` values, presentation-neutral entity/relationship structure, supported FM categories/kinds, duplicate entity names, endpoint existence, Context references through `context`, Party Role participation, Proposal/Request routing, cross-context bridge constraints, Evidence As Role constraints, and Third Party/Context Role participation constraints.

Manually review semantic duplication after the script passes:

- The same business semantic is not modeled as both Other Evidence and Evidence As Role.

## Reference

Read `references/fm-modeling-rules.md` when generating or reviewing a complete FM model, especially for the FM entity type dictionary, multi-contract contexts, Evidence As Role, role participation constraints, file output, file updates, business-rule placement, or boundary rules.

Use `$fm-database-design` instead when the user asks to turn an FM graph into database tables, physical schema, SQL DDL, immutable evidence persistence, or storage design.
