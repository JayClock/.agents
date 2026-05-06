#!/usr/bin/env python3
"""Validate Fulfillment Modeling proposal JSON emitted by fm-domain-architect."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any


VALID_TYPES = {
    "EVIDENCE": {
        "rfp",
        "proposal",
        "contract",
        "fulfillment_request",
        "fulfillment_confirmation",
        "other_evidence",
    },
    "PARTICIPANT": {"party", "thing"},
    "ROLE": {"party", "domain", "3rd system", "context", "evidence"},
    "CONTEXT": {"bounded_context"},
}

PARTY_ROLE = ("ROLE", "party")
EVIDENCE_AS_ROLE = ("ROLE", "evidence")
THIRD_OR_CONTEXT_ROLE_SUBTYPES = {"3rd system", "context"}
PARTY_REQUIRED_EVIDENCE = {
    "rfp",
    "proposal",
    "fulfillment_request",
    "fulfillment_confirmation",
    "other_evidence",
}
ROLE_LIMITED_TARGETS = {
    ("EVIDENCE", "other_evidence"),
    EVIDENCE_AS_ROLE,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Self-check a Fulfillment Modeling DraftDiagram proposal JSON."
    )
    parser.add_argument(
        "proposal",
        nargs="?",
        help="Path to proposal JSON. Reads stdin when omitted or set to '-'.",
    )
    args = parser.parse_args()

    raw = read_input(args.proposal)
    errors = validate_raw(raw)

    if errors:
        print("FM proposal self-check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("FM proposal self-check passed.")
    return 0


def read_input(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def validate_raw(raw: str) -> list[str]:
    if raw.strip().startswith("```"):
        return ["Proposal must be raw JSON, not Markdown fenced JSON."]

    try:
        proposal = json.loads(raw)
    except json.JSONDecodeError as error:
        return [f"Proposal is not valid JSON: {error.msg} at line {error.lineno}."]

    return validate_proposal(proposal)


def validate_proposal(proposal: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(proposal, dict):
        return ["Proposal root must be a JSON object."]

    operations = proposal.get("operations")
    if not isinstance(operations, list):
        return ["Proposal must contain operations as an array."]

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[tuple[str, str, int]] = []

    for index, operation in enumerate(operations):
        if not isinstance(operation, dict):
            errors.append(f"operations[{index}] must be an object.")
            continue

        operation_type = operation.get("type")
        if operation_type == "ADD_NODE":
            node = operation.get("node")
            node_id = normalize(node.get("id") if isinstance(node, dict) else None)
            if node_id is None:
                errors.append(f"operations[{index}] ADD_NODE must provide node.id.")
                continue
            if node_id in nodes:
                errors.append(f"Duplicate ADD_NODE id '{node_id}'.")
                continue
            nodes[node_id] = node
        elif operation_type == "ADD_EDGE":
            edge = operation.get("edge")
            source_id = ref_id(edge.get("sourceNode") if isinstance(edge, dict) else None)
            target_id = ref_id(edge.get("targetNode") if isinstance(edge, dict) else None)
            if source_id is None or target_id is None:
                errors.append(
                    f"operations[{index}] ADD_EDGE must provide edge.sourceNode.id and edge.targetNode.id."
                )
                continue
            edges.append((source_id, target_id, index))
        elif operation_type in {
            "UPDATE_NODE",
            "DELETE_NODE",
            "UPDATE_EDGE",
            "DELETE_EDGE",
        }:
            if normalize(operation.get("targetId")) is None:
                errors.append(f"operations[{index}] {operation_type} must provide targetId.")
        else:
            errors.append(f"operations[{index}] has unsupported type '{operation_type}'.")

    errors.extend(validate_nodes(nodes))
    errors.extend(validate_edges(nodes, edges))
    return errors


def validate_nodes(nodes: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for node_id, node in nodes.items():
        if not isinstance(node, dict):
            errors.append(f"Node '{node_id}' must be an object.")
            continue

        local_data = node.get("localData")
        if not isinstance(local_data, dict):
            errors.append(f"Node '{node_id}' must provide localData.")
            continue

        node_type = normalize(local_data.get("type"))
        subtype = normalize(local_data.get("subType"))
        if node_type not in VALID_TYPES:
            errors.append(f"Node '{node_id}' has invalid type '{node_type}'.")
            continue
        if subtype not in VALID_TYPES[node_type]:
            errors.append(
                f"Node '{node_id}' has invalid subType '{subtype}' for type '{node_type}'."
            )

        parent = node.get("parent")
        parent_id = ref_id(parent)
        if parent is not None and parent_id is None:
            errors.append(f"Node '{node_id}' parent must be null or an object with id.")
        if parent_id is not None:
            parent_node = nodes.get(parent_id)
            if parent_node is None:
                errors.append(f"Node '{node_id}' parent '{parent_id}' is not in ADD_NODE set.")
            elif node_kind(parent_node) != ("CONTEXT", "bounded_context"):
                errors.append(f"Node '{node_id}' parent '{parent_id}' is not a Context node.")

        if node_kind(node) == ("PARTICIPANT", "party") and parent_id is not None:
            errors.append(f"Participant Party node '{node_id}' must stay outside Context.")

    return errors


def validate_edges(
    nodes: dict[str, dict[str, Any]], edges: list[tuple[str, str, int]]
) -> list[str]:
    errors: list[str] = []
    adjacency: dict[str, list[str]] = defaultdict(list)

    for source_id, target_id, index in edges:
        if source_id not in nodes or target_id not in nodes:
            errors.append(
                f"operations[{index}] ADD_EDGE references undefined node(s): {source_id} -> {target_id}."
            )
            continue
        adjacency[source_id].append(target_id)
        adjacency[target_id].append(source_id)

    errors.extend(validate_party_role_participation(nodes, adjacency))
    errors.extend(validate_request_confirmation_chain(nodes, edges))
    errors.extend(validate_role_edge_constraints(nodes, edges, adjacency))
    return errors


def validate_party_role_participation(
    nodes: dict[str, dict[str, Any]], adjacency: dict[str, list[str]]
) -> list[str]:
    errors: list[str] = []
    for node_id, node in nodes.items():
        node_type, subtype = node_kind(node)
        if node_type != "EVIDENCE" or subtype not in PARTY_REQUIRED_EVIDENCE:
            continue
        party_role_neighbors = [
            neighbor_id
            for neighbor_id in adjacency.get(node_id, [])
            if node_kind(nodes[neighbor_id]) == PARTY_ROLE
        ]
        if len(party_role_neighbors) != 1:
            errors.append(
                f"Evidence node '{node_id}' ({subtype}) must have exactly one adjacent Party Role; found {len(party_role_neighbors)}."
            )
    return errors


def validate_request_confirmation_chain(
    nodes: dict[str, dict[str, Any]], edges: list[tuple[str, str, int]]
) -> list[str]:
    errors: list[str] = []
    for node_id, node in nodes.items():
        if node_kind(node) != ("EVIDENCE", "fulfillment_request"):
            continue

        contract_predecessors = [
            source_id
            for source_id, target_id, _ in edges
            if target_id == node_id and node_kind(nodes.get(source_id)) == ("EVIDENCE", "contract")
        ]
        confirmations = [
            target_id
            for source_id, target_id, _ in edges
            if source_id == node_id
            and node_kind(nodes.get(target_id)) == ("EVIDENCE", "fulfillment_confirmation")
        ]
        if len(contract_predecessors) != 1:
            errors.append(
                f"Fulfillment Request '{node_id}' must have exactly one direct Contract predecessor; found {len(contract_predecessors)}."
            )
        if len(confirmations) != 1:
            errors.append(
                f"Fulfillment Request '{node_id}' must have exactly one Fulfillment Confirmation successor; found {len(confirmations)}."
            )

    for source_id, target_id, index in edges:
        if node_kind(nodes.get(source_id)) == ("EVIDENCE", "proposal") and node_kind(
            nodes.get(target_id)
        ) == ("EVIDENCE", "fulfillment_request"):
            errors.append(
                f"operations[{index}] Proposal must not connect directly to Fulfillment Request."
            )
    return errors


def validate_role_edge_constraints(
    nodes: dict[str, dict[str, Any]],
    edges: list[tuple[str, str, int]],
    adjacency: dict[str, list[str]],
) -> list[str]:
    errors: list[str] = []

    for source_id, target_id, index in edges:
        source_kind = node_kind(nodes.get(source_id))
        target_kind = node_kind(nodes.get(target_id))
        source_context = context_id(nodes, source_id)
        target_context = context_id(nodes, target_id)

        if (
            source_context is not None
            and target_context is not None
            and source_context != target_context
            and not is_allowed_cross_context_edge(source_kind, target_kind)
        ):
            errors.append(
                f"operations[{index}] invalid cross-context edge {source_id} -> {target_id}; only Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation is allowed."
            )

        if source_kind == EVIDENCE_AS_ROLE and target_kind == (
            "EVIDENCE",
            "fulfillment_request",
        ):
            errors.append(
                f"operations[{index}] Evidence As Role must not point to Fulfillment Request."
            )

    forbidden_evidence_as_role_neighbors = {
        ("EVIDENCE", "contract"),
        ("EVIDENCE", "rfp"),
        ("EVIDENCE", "proposal"),
        ("EVIDENCE", "fulfillment_request"),
    }
    for node_id, node in nodes.items():
        kind = node_kind(node)
        if kind == EVIDENCE_AS_ROLE:
            for neighbor_id in adjacency.get(node_id, []):
                neighbor_kind = node_kind(nodes[neighbor_id])
                if neighbor_kind in forbidden_evidence_as_role_neighbors:
                    errors.append(
                        f"Evidence As Role '{node_id}' must not connect to {neighbor_kind[1]} node '{neighbor_id}'."
                    )

        if kind[0] == "ROLE" and kind[1] in THIRD_OR_CONTEXT_ROLE_SUBTYPES:
            for neighbor_id in adjacency.get(node_id, []):
                neighbor_kind = node_kind(nodes[neighbor_id])
                if neighbor_kind not in ROLE_LIMITED_TARGETS:
                    errors.append(
                        f"Role '{node_id}' ({kind[1]}) may only connect to Other Evidence or Evidence As Role; found '{neighbor_id}' ({neighbor_kind[0]}/{neighbor_kind[1]})."
                    )

    return errors


def is_allowed_cross_context_edge(
    source_kind: tuple[str | None, str | None], target_kind: tuple[str | None, str | None]
) -> bool:
    return (
        source_kind == ("EVIDENCE", "fulfillment_confirmation")
        and target_kind == EVIDENCE_AS_ROLE
    ) or (
        source_kind == EVIDENCE_AS_ROLE
        and target_kind == ("EVIDENCE", "fulfillment_confirmation")
    )


def context_id(nodes: dict[str, dict[str, Any]], node_id: str) -> str | None:
    node = nodes.get(node_id)
    if node is None:
        return None
    if node_kind(node) == ("CONTEXT", "bounded_context"):
        return node_id
    return ref_id(node.get("parent"))


def node_kind(node: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not isinstance(node, dict):
        return (None, None)
    local_data = node.get("localData")
    if not isinstance(local_data, dict):
        return (None, None)
    return (normalize(local_data.get("type")), normalize(local_data.get("subType")))


def ref_id(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return None
    return normalize(value.get("id"))


def normalize(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    raise SystemExit(main())
