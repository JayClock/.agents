---
name: fm-domain-architect
description: Fulfillment Modeling domain architecture for turning software or business requirements into Smart Domain/DDD Diagram models or proposal diffs. Use when Codex needs to analyze requirements with Fulfillment Modeling, identify Contract-centered contexts, Party Roles, RFP/Proposal, Fulfillment Request/Fulfillment Confirmation pairs, Evidence/Role/Context nodes, validate FM edges, or create/update a domain diagram proposal.
---

# FM Domain Architect

## Purpose

Model requirements with Fulfillment Modeling (FM): start from contracts and business fulfillment responsibilities, then derive contexts, roles, evidences, requests, confirmations, and valid control-flow edges. Prefer business semantics over technical components.

## Workflow

1. Identify Contract contexts first. Treat one Contract as one primary fulfillment chain; if multiple contracts exist, model each chain independently.
2. Extract Party Roles for every business subject and connect them to the relevant Contract. Add Participant Party nodes only when the real-world party identity matters across roles or contexts.
3. Add optional presales Evidence only when present in the requirement: RFP before Proposal, Proposal before Contract.
4. Model each responsibility as a Fulfillment Request -> Fulfillment Confirmation pair. Include reverse or exception flows such as refund, cancellation, suspension, or reversal as their own request/confirmation pairs.
5. Add Other Evidence for internal business documents produced by confirmations. If the evidence bridges contexts, model it as Evidence As Role instead and do not keep a duplicate Other Evidence node.
6. Add Domain, Third Party, Context, or Evidence roles only when they represent real business participation. Name Domain Logic and Third Party roles as human job/position semantics from the pre-software world, not as technical systems.
7. Parent every business-chain node under its Context. Keep Participant Party nodes outside Context containers.
8. Create edges from cause to result or initiator to action so the diagram reads left-to-right as business flow.
9. Run `scripts/self_check_fm_proposal.py` on the generated proposal JSON before returning any machine-readable model or proposal.

## Output Guidance

When the user asks for a diagram or proposal diff, return a structured proposal with:

- `summary`: concise explanation plus add/update/delete counts.
- `operations`: ordered operations using `ADD_NODE`, `UPDATE_NODE`, `DELETE_NODE`, `ADD_EDGE`, `UPDATE_EDGE`, or `DELETE_EDGE`.

For new diagrams, prefer `ADD_NODE` operations before `ADD_EDGE` operations. Node payloads use `node.id`, `node.parent`, and `node.localData`. Do not invent update/delete targets; if the existing diagram is unavailable or ambiguous, add a new proposal instead of guessing destructive changes.

Use stable virtual ids such as `node-1`, `node-2`, and `edge-1`. Every edge endpoint must reference an existing node id from the same output.

## Executable Self-Check

After drafting proposal JSON, save it to a temporary file and run the bundled checker from this skill directory:

```bash
python3 scripts/self_check_fm_proposal.py /tmp/proposal.json
```

Fix every reported error before returning the proposal. The script checks JSON shape, valid node types/subtypes, parent references, edge endpoints, Party Role participation, Request -> Confirmation pairing, Proposal/Request routing, cross-context bridge constraints, Evidence As Role constraints, and Third Party/Context Role participation constraints.

Manually review semantic duplication after the script passes: the same business semantic must not be modeled as both Other Evidence and Evidence As Role.

## Reference

Read `references/fm-modeling-rules.md` when generating a complete diagram/proposal, reviewing an FM model, or resolving edge cases around multi-contract contexts, Evidence As Role, role participation constraints, or node subtype mapping.
