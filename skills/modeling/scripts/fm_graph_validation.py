#!/usr/bin/env python3
"""Validate a Fulfillment Modeling graph or add-only changes payload."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any


CATEGORIES = {"Evidence", "Participant", "Role", "Context"}
KINDS_BY_CATEGORY = {
    "Evidence": {
        "RFP",
        "Proposal",
        "Contract",
        "Fulfillment Request",
        "Fulfillment Confirmation",
        "Proof",
    },
    "Participant": {"Party", "Thing"},
    "Role": {
        "Party Role",
        "Domain Role",
        "Third Party Role",
        "Context Role",
        "Evidence As Role",
    },
    "Context": {"Bounded Context"},
}
KIND_SLUGS = {
    "Bounded Context": "context",
    "Contract": "contract",
    "RFP": "rfp",
    "Proposal": "proposal",
    "Fulfillment Request": "request",
    "Fulfillment Confirmation": "confirmation",
    "Proof": "proof",
    "Party": "party",
    "Thing": "thing",
    "Party Role": "party-role",
    "Domain Role": "domain-role",
    "Third Party Role": "third-party-role",
    "Context Role": "context-role",
    "Evidence As Role": "evidence-as-role",
}
TYPE_NAME_SUFFIXES = (
    "Context",
    "Contract",
    "Rfp",
    "RFP",
    "Proposal",
    "Request",
    "Confirmation",
    "Proof",
    "Role",
    "Party",
    "Thing",
)
MOMENT_EVIDENCE_KINDS = {"Fulfillment Confirmation", "Proof"}
EVIDENCE_KINDS_REQUIRING_PARTY_ROLE = {
    "RFP",
    "Proposal",
    "Fulfillment Request",
    "Fulfillment Confirmation",
    "Proof",
}
THIRD_PARTY_ROLE_TARGETS = {
    ("Evidence", "Proof"),
    ("Role", "Evidence As Role"),
}
CONTEXT_ROLE_TARGETS = {
    ("Evidence", "Fulfillment Confirmation"),
    ("Evidence", "Proof"),
    ("Role", "Evidence As Role"),
}
FORBIDDEN_EVIDENCE_AS_ROLE_NEIGHBORS = {
    ("Evidence", "Contract"),
    ("Evidence", "RFP"),
    ("Evidence", "Proposal"),
    ("Evidence", "Fulfillment Request"),
}
ENTITY_CHANGE_KEYS = ("addEntities", "updateEntities", "deleteEntities")
RELATIONSHIP_CHANGE_KEYS = (
    "addRelationships",
    "updateRelationships",
    "deleteRelationships",
)
LEGACY_ENTITY_CHANGE_KEYS = ("addNodes", "updateNodes", "deleteNodes")
LEGACY_RELATIONSHIP_CHANGE_KEYS = ("addEdges", "updateEdges", "deleteEdges")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Self-check a Fulfillment Modeling entities/relationships graph or add-only changes payload."
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

    if "_meta" in graph:
        return ["Graph must not contain non-semantic metadata fields."]
    if "validationNotes" in graph:
        return ["Graph must not contain top-level validation notes."]

    entities_value = collection_value(graph, "entities", "nodes")
    relationships_value = collection_value(graph, "relationships", "edges")
    if (
        entities_value is None
        and relationships_value is None
        and isinstance(graph.get("changes"), dict)
    ):
        changes = graph["changes"]
        change_errors = validate_change_id_uniqueness(changes)
        if change_errors:
            return change_errors
        try:
            entities_value = change_array(changes, "addEntities", "addNodes")
            relationships_value = change_array(
                changes, "addRelationships", "addEdges"
            )
        except ValueError as error:
            return [str(error)]

    if not isinstance(entities_value, list):
        return [
            "Graph must contain entities as an array, or changes.addEntities as an array."
        ]
    if not isinstance(relationships_value, list):
        return [
            "Graph must contain relationships as an array, or changes.addRelationships as an array."
        ]

    errors: list[str] = []
    entities = collect_entities(entities_value, errors)
    relationships = collect_relationships(relationships_value, errors)

    errors.extend(validate_entities(entities))
    errors.extend(validate_relationships(entities, relationships))
    return errors


def collection_value(graph: dict[str, Any], key: str, legacy_key: str) -> Any:
    if key in graph and legacy_key in graph:
        return None
    if key in graph:
        return graph[key]
    return graph.get(legacy_key)


def change_array(changes: dict[str, Any], key: str, legacy_key: str) -> list[Any]:
    if key in changes and legacy_key in changes:
        raise ValueError(f"Provide only changes.{key}; do not mix legacy changes.{legacy_key}.")
    value = changes.get(key, changes.get(legacy_key, []))
    if not isinstance(value, list):
        raise ValueError(f"changes.{key} must be an array when provided.")
    return value


def validate_change_id_uniqueness(changes: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entity_ids: dict[str, str] = {}
    relationship_ids: dict[str, str] = {}

    for key, legacy_key in zip(ENTITY_CHANGE_KEYS, LEGACY_ENTITY_CHANGE_KEYS):
        try:
            value = change_array(changes, key, legacy_key)
        except ValueError as error:
            errors.append(str(error))
            continue
        collect_change_ids(key, value, entity_ids, errors)

    for key, legacy_key in zip(RELATIONSHIP_CHANGE_KEYS, LEGACY_RELATIONSHIP_CHANGE_KEYS):
        try:
            value = change_array(changes, key, legacy_key)
        except ValueError as error:
            errors.append(str(error))
            continue
        collect_change_ids(key, value, relationship_ids, errors)

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


def collect_entities(
    entities_value: list[Any], errors: list[str]
) -> dict[str, dict[str, Any]]:
    entities: dict[str, dict[str, Any]] = {}
    for index, entity in enumerate(entities_value):
        if not isinstance(entity, dict):
            errors.append(f"entities[{index}] must be an object.")
            continue
        entity_id = normalize(entity.get("id"))
        if entity_id is None:
            errors.append(f"entities[{index}] must provide id.")
            continue
        if entity_id in entities:
            errors.append(f"Duplicate entity id '{entity_id}'.")
            continue
        entities[entity_id] = entity
    return entities


def collect_relationships(
    relationships_value: list[Any], errors: list[str]
) -> list[tuple[str, str, str, int, dict[str, Any]]]:
    relationships: list[tuple[str, str, str, int, dict[str, Any]]] = []
    relationship_ids: set[str] = set()
    for index, relationship in enumerate(relationships_value):
        if not isinstance(relationship, dict):
            errors.append(f"relationships[{index}] must be an object.")
            continue
        relationship_id = normalize(relationship.get("id"))
        source = normalize(relationship.get("source"))
        target = normalize(relationship.get("target"))
        if relationship_id is None:
            errors.append(f"relationships[{index}] must provide id.")
            continue
        if relationship_id in relationship_ids:
            errors.append(f"Duplicate relationship id '{relationship_id}'.")
            continue
        relationship_ids.add(relationship_id)
        if not isinstance(relationship.get("source"), str) or not isinstance(
            relationship.get("target"), str
        ):
            errors.append(
                f"relationships[{index}] source and target must each be one entity id string; use multiple 1:1 relationship objects for one-to-many relationships."
            )
            continue
        if source is None or target is None:
            errors.append(
                f"relationships[{index}] must provide non-empty source and target."
            )
            continue
        relationships.append((relationship_id, source, target, index, relationship))
    return relationships


def validate_entities(entities: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    entity_names: dict[str, str] = {}
    for entity_id, entity in entities.items():
        name = normalize(entity.get("name"))
        if name is None:
            errors.append(f"Entity '{entity_id}' name must be a non-empty string.")
        else:
            previous_entity_id = entity_names.get(name)
            if previous_entity_id is not None:
                errors.append(
                    f"Duplicate entity name '{name}' on entities '{previous_entity_id}' and '{entity_id}'."
                )
            else:
                entity_names[name] = entity_id

        category, kind = entity_kind(entity)
        if category not in CATEGORIES:
            errors.append(
                f"Entity '{entity_id}' category must be one of {sorted(CATEGORIES)}; found '{category}'."
            )
        elif kind not in KINDS_BY_CATEGORY[category]:
            errors.append(
                f"Entity '{entity_id}' kind must be one of {sorted(KINDS_BY_CATEGORY[category])} for category {category}; found '{kind}'."
            )
        if kind is None:
            errors.append(f"Entity '{entity_id}' kind must be a non-empty string.")
        if name is not None and name.endswith(TYPE_NAME_SUFFIXES):
            errors.append(
                f"Entity '{entity_id}' name '{name}' must not end with an FM type suffix; put the type in kind and filename only."
            )
        if normalize(entity.get("label")) is None:
            errors.append(f"Entity '{entity_id}' label must be a non-empty string.")

        context = normalize(entity.get("contextId"))
        if context is not None:
            parent = entities.get(context)
            if parent is None:
                errors.append(
                    f"Entity '{entity_id}' contextId '{context}' does not exist."
                )
            elif entity_kind(parent) != ("Context", "Bounded Context"):
                errors.append(
                    f"Entity '{entity_id}' contextId '{context}' is not a Context entity."
                )

        if entity_kind(entity) == ("Participant", "Party") and context is not None:
            errors.append(f"Participant Party entity '{entity_id}' must stay outside Context.")

    return errors


def validate_relationships(
    entities: dict[str, dict[str, Any]],
    relationships: list[tuple[str, str, str, int, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []
    adjacency: dict[str, list[str]] = defaultdict(list)
    directed_relationships: list[tuple[str, str, int]] = []

    for relationship_id, source, target, index, relationship in relationships:
        if source not in entities or target not in entities:
            errors.append(
                f"relationships[{index}] '{relationship_id}' references undefined entity(s): {source} -> {target}."
            )
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
        directed_relationships.append((source, target, index))

    errors.extend(validate_party_role_participation(entities, adjacency))
    errors.extend(validate_proposal_request_routing(entities, directed_relationships))
    errors.extend(validate_role_relationship_constraints(entities, directed_relationships, adjacency))
    return errors


def validate_party_role_participation(
    entities: dict[str, dict[str, Any]], adjacency: dict[str, list[str]]
) -> list[str]:
    errors: list[str] = []
    for entity_id, entity in entities.items():
        category, kind = entity_kind(entity)
        if category != "Evidence" or kind not in EVIDENCE_KINDS_REQUIRING_PARTY_ROLE:
            continue
        party_role_neighbors = [
            neighbor_id
            for neighbor_id in adjacency.get(entity_id, [])
            if entity_kind(entities[neighbor_id]) == ("Role", "Party Role")
        ]
        if len(party_role_neighbors) != 1:
            errors.append(
                f"Evidence entity '{entity_id}' ({kind}) must have exactly one adjacent Party Role; found {len(party_role_neighbors)}."
            )
    return errors


def validate_proposal_request_routing(
    entities: dict[str, dict[str, Any]], relationships: list[tuple[str, str, int]]
) -> list[str]:
    errors: list[str] = []
    for source, target, index in relationships:
        if entity_kind(entities.get(source)) == ("Evidence", "Proposal") and entity_kind(
            entities.get(target)
        ) == ("Evidence", "Fulfillment Request"):
            errors.append(
                f"relationships[{index}] Proposal must not connect directly to Fulfillment Request."
            )
    return errors


def validate_role_relationship_constraints(
    entities: dict[str, dict[str, Any]],
    relationships: list[tuple[str, str, int]],
    adjacency: dict[str, list[str]],
) -> list[str]:
    errors: list[str] = []

    for source, target, index in relationships:
        source_kind = entity_kind(entities.get(source))
        target_kind = entity_kind(entities.get(target))
        source_context = context_id(entities, source)
        target_context = context_id(entities, target)

        if (
            source_context is not None
            and target_context is not None
            and source_context != target_context
            and not is_allowed_cross_context_relationship(source_kind, target_kind)
        ):
            errors.append(
                f"relationships[{index}] invalid cross-context relationship {source} -> {target}; only moment evidence (Fulfillment Confirmation/Proof) direct links or Evidence As Role bridges are allowed."
            )

        if source_kind == ("Role", "Evidence As Role") and target_kind == (
            "Evidence",
            "Fulfillment Request",
        ):
            errors.append(
                f"relationships[{index}] Evidence As Role must not point to Fulfillment Request."
            )

    for entity_id, entity in entities.items():
        kind = entity_kind(entity)
        if kind == ("Role", "Evidence As Role"):
            for neighbor_id in adjacency.get(entity_id, []):
                neighbor_kind = entity_kind(entities[neighbor_id])
                if neighbor_kind in FORBIDDEN_EVIDENCE_AS_ROLE_NEIGHBORS:
                    errors.append(
                        f"Evidence As Role '{entity_id}' must not connect to {neighbor_kind[1]} entity '{neighbor_id}'."
                    )
        allowed_targets: set[tuple[str | None, str | None]] | None = None
        allowed_targets_label: str | None = None
        if kind == ("Role", "Third Party Role"):
            allowed_targets = THIRD_PARTY_ROLE_TARGETS
            allowed_targets_label = "Proof or Evidence As Role"
        elif kind == ("Role", "Context Role"):
            allowed_targets = CONTEXT_ROLE_TARGETS
            allowed_targets_label = "Fulfillment Confirmation, Proof, or Evidence As Role"

        if allowed_targets is not None:
            for neighbor_id in adjacency.get(entity_id, []):
                neighbor_kind = entity_kind(entities[neighbor_id])
                if neighbor_kind not in allowed_targets:
                    errors.append(
                        f"Role '{entity_id}' ({kind[1]}) may only connect to {allowed_targets_label}; found '{neighbor_id}' ({neighbor_kind[0]}/{neighbor_kind[1]})."
                    )
    return errors


def is_allowed_cross_context_relationship(
    source_kind: tuple[str | None, str | None], target_kind: tuple[str | None, str | None]
) -> bool:
    return (
        is_moment_evidence(source_kind) and is_moment_evidence(target_kind)
    ) or (
        is_moment_evidence(source_kind) and target_kind == ("Role", "Evidence As Role")
    ) or (
        source_kind == ("Role", "Evidence As Role") and is_moment_evidence(target_kind)
    )


def is_moment_evidence(kind: tuple[str | None, str | None]) -> bool:
    return kind[0] == "Evidence" and kind[1] in MOMENT_EVIDENCE_KINDS


def context_id(entities: dict[str, dict[str, Any]], entity_id: str) -> str | None:
    entity = entities.get(entity_id)
    if entity is None:
        return None
    if entity_kind(entity) == ("Context", "Bounded Context"):
        return entity_id
    return normalize(entity.get("contextId"))


def entity_kind(entity: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not isinstance(entity, dict):
        return (None, None)
    return (normalize(entity.get("category")), normalize(entity.get("kind")))


def normalize(value: Any) -> str | None:
    if value is None or not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    raise SystemExit(main())
