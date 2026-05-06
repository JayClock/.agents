#!/usr/bin/env python3
"""Validate a generic Fulfillment Modeling graph shaped like React Flow."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any


CATEGORIES = {"Evidence", "Participant", "Role", "Context"}
EVIDENCE_KINDS_REQUIRING_PARTY_ROLE = {
    "RFP",
    "Proposal",
    "Fulfillment Request",
    "Fulfillment Confirmation",
    "Other Evidence",
}
REQUIRED_LIFECYCLE_ATTRIBUTES = {
    "RFP": ("startedAt", "expiredAt"),
    "Proposal": ("startedAt", "expiredAt"),
    "Fulfillment Request": ("startedAt", "expiredAt"),
    "Contract": ("signedAt",),
    "Fulfillment Confirmation": ("confirmedAt",),
    "Other Evidence": ("createdAt",),
}
THIRD_OR_CONTEXT_ROLE_KINDS = {"Third Party Role", "Context Role"}
ROLE_LIMITED_TARGETS = {
    ("Evidence", "Other Evidence"),
    ("Role", "Evidence As Role"),
}
FORBIDDEN_EVIDENCE_AS_ROLE_NEIGHBORS = {
    ("Evidence", "Contract"),
    ("Evidence", "RFP"),
    ("Evidence", "Proposal"),
    ("Evidence", "Fulfillment Request"),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Self-check a generic Fulfillment Modeling nodes/edges graph."
    )
    parser.add_argument(
        "graph",
        nargs="?",
        help="Path to graph JSON. Reads stdin when omitted or set to '-'.",
    )
    args = parser.parse_args()

    raw = read_input(args.graph)
    errors = validate_raw(raw)
    if errors:
        print("FM graph self-check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("FM graph self-check passed.")
    return 0


def read_input(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def validate_raw(raw: str) -> list[str]:
    if raw.strip().startswith("```"):
        return ["Graph must be raw JSON, not Markdown fenced JSON."]
    try:
        graph = json.loads(raw)
    except json.JSONDecodeError as error:
        return [f"Graph is not valid JSON: {error.msg} at line {error.lineno}."]
    return validate_graph(graph)


def validate_graph(graph: Any) -> list[str]:
    if not isinstance(graph, dict):
        return ["Graph root must be a JSON object."]

    meta_errors = validate_meta(graph.get("_meta"))
    if meta_errors:
        return meta_errors
    if "validationNotes" in graph:
        return ["Use _meta.validationNotes instead of top-level validationNotes."]

    nodes_value = graph.get("nodes")
    edges_value = graph.get("edges")
    if nodes_value is None and edges_value is None and isinstance(graph.get("changes"), dict):
        changes = graph["changes"]
        change_errors = validate_change_id_uniqueness(changes)
        if change_errors:
            return change_errors
        nodes_value = changes.get("addNodes", [])
        edges_value = changes.get("addEdges", [])

    if not isinstance(nodes_value, list):
        return ["Graph must contain nodes as an array, or changes.addNodes as an array."]
    if not isinstance(edges_value, list):
        return ["Graph must contain edges as an array, or changes.addEdges as an array."]

    errors: list[str] = []
    nodes = collect_nodes(nodes_value, errors)
    edges = collect_edges(edges_value, errors)

    errors.extend(validate_nodes(nodes))
    errors.extend(validate_edges(nodes, edges))
    return errors


def validate_meta(meta: Any) -> list[str]:
    if meta is None:
        return []
    if not isinstance(meta, dict):
        return ["_meta must be an object when provided."]
    validation_notes = meta.get("validationNotes")
    if validation_notes is not None and not isinstance(validation_notes, list):
        return ["_meta.validationNotes must be an array when provided."]
    return []


def validate_change_id_uniqueness(changes: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    node_ids: dict[str, str] = {}
    edge_ids: dict[str, str] = {}

    for key in ("addNodes", "updateNodes", "deleteNodes"):
        value = changes.get(key, [])
        if not isinstance(value, list):
            errors.append(f"changes.{key} must be an array when provided.")
            continue
        collect_change_ids(key, value, node_ids, errors)

    for key in ("addEdges", "updateEdges", "deleteEdges"):
        value = changes.get(key, [])
        if not isinstance(value, list):
            errors.append(f"changes.{key} must be an array when provided.")
            continue
        collect_change_ids(key, value, edge_ids, errors)

    return errors


def collect_change_ids(
    key: str, values: list[Any], seen: dict[str, str], errors: list[str]
) -> None:
    for index, item in enumerate(values):
        item_id = change_item_id(item)
        if item_id is None:
            errors.append(f"changes.{key}[{index}] must provide id or targetId.")
            continue
        previous = seen.get(item_id)
        if previous is not None:
            errors.append(
                f"Duplicate id '{item_id}' across changes.{previous} and changes.{key}."
            )
            continue
        seen[item_id] = key


def change_item_id(item: Any) -> str | None:
    if isinstance(item, str):
        return normalize(item)
    if isinstance(item, dict):
        return normalize(item.get("id")) or normalize(item.get("targetId"))
    return None


def collect_nodes(nodes_value: list[Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes_value):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] must be an object.")
            continue
        node_id = normalize(node.get("id"))
        if node_id is None:
            errors.append(f"nodes[{index}] must provide id.")
            continue
        if node_id in nodes:
            errors.append(f"Duplicate node id '{node_id}'.")
            continue
        nodes[node_id] = node
    return nodes


def collect_edges(edges_value: list[Any], errors: list[str]) -> list[tuple[str, str, str, int]]:
    edges: list[tuple[str, str, str, int]] = []
    edge_ids: set[str] = set()
    for index, edge in enumerate(edges_value):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object.")
            continue
        edge_id = normalize(edge.get("id"))
        source = normalize(edge.get("source"))
        target = normalize(edge.get("target"))
        if edge_id is None:
            errors.append(f"edges[{index}] must provide id.")
            continue
        if edge_id in edge_ids:
            errors.append(f"Duplicate edge id '{edge_id}'.")
            continue
        edge_ids.add(edge_id)
        if source is None or target is None:
            errors.append(f"edges[{index}] must provide source and target.")
            continue
        edges.append((edge_id, source, target, index))
    return edges


def validate_nodes(nodes: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    node_names: dict[str, str] = {}
    for node_id, node in nodes.items():
        data = node.get("data")
        if not isinstance(data, dict):
            errors.append(f"Node '{node_id}' must provide data.")
            continue
        name = normalize(data.get("name"))
        if name is None:
            errors.append(f"Node '{node_id}' data.name must be a non-empty string.")
        else:
            previous_node_id = node_names.get(name)
            if previous_node_id is not None:
                errors.append(
                    f"Duplicate node data.name '{name}' on nodes '{previous_node_id}' and '{node_id}'."
                )
            else:
                node_names[name] = node_id
        category, kind = node_kind(node)
        if category not in CATEGORIES:
            errors.append(
                f"Node '{node_id}' data.category must be one of {sorted(CATEGORIES)}; found '{category}'."
            )
        node_type = normalize(node.get("type"))
        if node_type is None:
            errors.append(f"Node '{node_id}' type must equal data.category; found empty type.")
        elif category in CATEGORIES and node_type != category:
            errors.append(
                f"Node '{node_id}' type must equal data.category; found type '{node_type}' and category '{category}'."
            )
        if kind is None:
            errors.append(f"Node '{node_id}' data.kind must be a non-empty string.")
        if normalize(data.get("label")) is None:
            errors.append(f"Node '{node_id}' data.label must be a non-empty string.")

        position = node.get("position")
        if not is_position(position):
            errors.append(f"Node '{node_id}' position must provide numeric x and y.")

        parent_id = normalize(node.get("parentId"))
        if parent_id is not None:
            parent = nodes.get(parent_id)
            if parent is None:
                errors.append(f"Node '{node_id}' parentId '{parent_id}' does not exist.")
            elif node_kind(parent) != ("Context", "Bounded Context"):
                errors.append(f"Node '{node_id}' parentId '{parent_id}' is not a Context node.")

        if node_kind(node) == ("Participant", "Party") and parent_id is not None:
            errors.append(f"Participant Party node '{node_id}' must stay outside Context.")

        errors.extend(validate_lifecycle_attributes(node_id, node))

    return errors


def validate_lifecycle_attributes(node_id: str, node: dict[str, Any]) -> list[str]:
    category, kind = node_kind(node)
    if category != "Evidence" or kind not in REQUIRED_LIFECYCLE_ATTRIBUTES:
        return []

    data = node.get("data")
    if not isinstance(data, dict):
        return []

    attributes = data.get("attributes")
    if not isinstance(attributes, list):
        return [
            f"Evidence node '{node_id}' ({kind}) must provide data.attributes with required lifecycle attributes: {', '.join(REQUIRED_LIFECYCLE_ATTRIBUTES[kind])}."
        ]

    by_name: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, attribute in enumerate(attributes):
        if not isinstance(attribute, dict):
            errors.append(f"Node '{node_id}' data.attributes[{index}] must be an object.")
            continue
        name = normalize(attribute.get("name"))
        if name is not None:
            by_name[name] = attribute

    for required_name in REQUIRED_LIFECYCLE_ATTRIBUTES[kind]:
        attribute = by_name.get(required_name)
        if attribute is None:
            errors.append(
                f"Evidence node '{node_id}' ({kind}) must include required DateTime lifecycle attribute '{required_name}'."
            )
            continue
        if attribute.get("valueType") != "DateTime":
            errors.append(
                f"Evidence node '{node_id}' lifecycle attribute '{required_name}' must have valueType 'DateTime'."
            )
        if attribute.get("required") is not True:
            errors.append(
                f"Evidence node '{node_id}' lifecycle attribute '{required_name}' must have required: true."
            )

    return errors


def validate_edges(
    nodes: dict[str, dict[str, Any]], edges: list[tuple[str, str, str, int]]
) -> list[str]:
    errors: list[str] = []
    adjacency: dict[str, list[str]] = defaultdict(list)
    directed_edges: list[tuple[str, str, int]] = []

    for edge_id, source, target, index in edges:
        if source not in nodes or target not in nodes:
            errors.append(
                f"edges[{index}] '{edge_id}' references undefined node(s): {source} -> {target}."
            )
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
        directed_edges.append((source, target, index))

    errors.extend(validate_party_role_participation(nodes, adjacency))
    errors.extend(validate_request_confirmation_chain(nodes, directed_edges))
    errors.extend(validate_role_edge_constraints(nodes, directed_edges, adjacency))
    return errors


def validate_party_role_participation(
    nodes: dict[str, dict[str, Any]], adjacency: dict[str, list[str]]
) -> list[str]:
    errors: list[str] = []
    for node_id, node in nodes.items():
        category, kind = node_kind(node)
        if category != "Evidence" or kind not in EVIDENCE_KINDS_REQUIRING_PARTY_ROLE:
            continue
        party_role_neighbors = [
            neighbor_id
            for neighbor_id in adjacency.get(node_id, [])
            if node_kind(nodes[neighbor_id]) == ("Role", "Party Role")
        ]
        if len(party_role_neighbors) != 1:
            errors.append(
                f"Evidence node '{node_id}' ({kind}) must have exactly one adjacent Party Role; found {len(party_role_neighbors)}."
            )
    return errors


def validate_request_confirmation_chain(
    nodes: dict[str, dict[str, Any]], edges: list[tuple[str, str, int]]
) -> list[str]:
    errors: list[str] = []
    for node_id, node in nodes.items():
        if node_kind(node) != ("Evidence", "Fulfillment Request"):
            continue
        contract_predecessors = [
            source
            for source, target, _ in edges
            if target == node_id and node_kind(nodes.get(source)) == ("Evidence", "Contract")
        ]
        confirmations = [
            target
            for source, target, _ in edges
            if source == node_id
            and node_kind(nodes.get(target)) == ("Evidence", "Fulfillment Confirmation")
        ]
        if len(contract_predecessors) != 1:
            errors.append(
                f"Fulfillment Request '{node_id}' must have exactly one direct Contract predecessor; found {len(contract_predecessors)}."
            )
        if len(confirmations) != 1:
            errors.append(
                f"Fulfillment Request '{node_id}' must have exactly one Fulfillment Confirmation successor; found {len(confirmations)}."
            )

    for source, target, index in edges:
        if node_kind(nodes.get(source)) == ("Evidence", "Proposal") and node_kind(
            nodes.get(target)
        ) == ("Evidence", "Fulfillment Request"):
            errors.append(
                f"edges[{index}] Proposal must not connect directly to Fulfillment Request."
            )
    return errors


def validate_role_edge_constraints(
    nodes: dict[str, dict[str, Any]],
    edges: list[tuple[str, str, int]],
    adjacency: dict[str, list[str]],
) -> list[str]:
    errors: list[str] = []

    for source, target, index in edges:
        source_kind = node_kind(nodes.get(source))
        target_kind = node_kind(nodes.get(target))
        source_context = context_id(nodes, source)
        target_context = context_id(nodes, target)

        if (
            source_context is not None
            and target_context is not None
            and source_context != target_context
            and not is_allowed_cross_context_edge(source_kind, target_kind)
        ):
            errors.append(
                f"edges[{index}] invalid cross-context edge {source} -> {target}; only Fulfillment Confirmation -> Evidence As Role -> Fulfillment Confirmation is allowed."
            )

        if source_kind == ("Role", "Evidence As Role") and target_kind == (
            "Evidence",
            "Fulfillment Request",
        ):
            errors.append(f"edges[{index}] Evidence As Role must not point to Fulfillment Request.")

    for node_id, node in nodes.items():
        kind = node_kind(node)
        if kind == ("Role", "Evidence As Role"):
            for neighbor_id in adjacency.get(node_id, []):
                neighbor_kind = node_kind(nodes[neighbor_id])
                if neighbor_kind in FORBIDDEN_EVIDENCE_AS_ROLE_NEIGHBORS:
                    errors.append(
                        f"Evidence As Role '{node_id}' must not connect to {neighbor_kind[1]} node '{neighbor_id}'."
                    )
        if kind[0] == "Role" and kind[1] in THIRD_OR_CONTEXT_ROLE_KINDS:
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
        source_kind == ("Evidence", "Fulfillment Confirmation")
        and target_kind == ("Role", "Evidence As Role")
    ) or (
        source_kind == ("Role", "Evidence As Role")
        and target_kind == ("Evidence", "Fulfillment Confirmation")
    )


def context_id(nodes: dict[str, dict[str, Any]], node_id: str) -> str | None:
    node = nodes.get(node_id)
    if node is None:
        return None
    if node_kind(node) == ("Context", "Bounded Context"):
        return node_id
    return normalize(node.get("parentId"))


def node_kind(node: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not isinstance(node, dict):
        return (None, None)
    data = node.get("data")
    if not isinstance(data, dict):
        return (None, None)
    return (normalize(data.get("category")), normalize(data.get("kind")))


def is_position(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return isinstance(value.get("x"), (int, float)) and isinstance(value.get("y"), (int, float))


def normalize(value: Any) -> str | None:
    if value is None or not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    raise SystemExit(main())
