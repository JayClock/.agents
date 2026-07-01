#!/usr/bin/env python3
"""Validate a Fulfillment Modeling graph or add-only changes payload."""

from __future__ import annotations

import argparse
import json
import re
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
        "Other Evidence",
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
    "Other Evidence": "evidence",
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
    "Evidence",
    "Role",
    "Party",
    "Thing",
)
GENERAL_IMPLEMENTATION_TERMS = (
    "api",
    "sdk",
    "endpoint",
    "controller",
    "database",
    "datatable",
    "messagequeue",
    "kafka",
    "rabbitmq",
    "ui",
    "接口",
    "数据库",
    "数据表",
    "消息队列",
    "队列",
    "部署",
    "登录页面",
    "页面交互",
    "app交互",
    "播放器实现",
    "推荐算法",
)
DOMAIN_ROLE_IMPLEMENTATION_TERMS = (
    "api",
    "sdk",
    "engine",
    "queue",
    "gateway",
    "database",
    "系统",
    "引擎",
    "队列",
    "网关",
    "数据库",
    "数据表",
    "规则引擎",
    "风控服务",
    "支付网关",
    "推荐服务",
)
ENTITY_NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
MOMENT_EVIDENCE_KINDS = {"Fulfillment Confirmation", "Other Evidence"}
EVIDENCE_KINDS_REQUIRING_ACTUAL_PARTY = {
    "RFP",
    "Proposal",
    "Fulfillment Request",
    "Fulfillment Confirmation",
    "Other Evidence",
}
RELATIONSHIP_KINDS = {
    "association",
    "rolePlaying",
    "crossContextAssociation",
}
THIRD_PARTY_ROLE_TARGETS = {
    ("Evidence", "Fulfillment Confirmation"),
    ("Evidence", "Other Evidence"),
    ("Role", "Evidence As Role"),
}
CONTEXT_ROLE_TARGETS = {
    ("Evidence", "Fulfillment Confirmation"),
    ("Evidence", "Other Evidence"),
    ("Role", "Evidence As Role"),
}
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
CALCULATION_RULE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)\s*(.+?)\s*$")
ASSIGNMENT_RE = re.compile(r"(?<![!<>=])=(?![=])")
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
    errors.extend(validate_attribute_references(entities))
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
        relationship_kind = normalize(relationship.get("relationshipKind"))
        if relationship_kind is not None and relationship_kind not in RELATIONSHIP_KINDS:
            errors.append(
                f"relationships[{index}] relationshipKind must be one of {sorted(RELATIONSHIP_KINDS)} when provided; found '{relationship_kind}'."
            )
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
        if name is not None and ENTITY_NAME_RE.fullmatch(name) is None:
            errors.append(
                f"Entity '{entity_id}' name '{name}' must be an ASCII PascalCase identifier."
            )
        if name is not None and name.endswith(TYPE_NAME_SUFFIXES):
            errors.append(
                f"Entity '{entity_id}' name '{name}' must not end with an FM type suffix; put the type in kind and filename only."
            )
        if normalize(entity.get("label")) is None:
            errors.append(f"Entity '{entity_id}' label must be a non-empty string.")

        implementation_hits = forbidden_term_hits(entity_search_text(entity), GENERAL_IMPLEMENTATION_TERMS)
        if implementation_hits:
            errors.append(
                f"Entity '{entity_id}' appears to model implementation detail(s) {implementation_hits}; FM entities should stay business-level."
            )
        if (category, kind) == ("Role", "Domain Role"):
            role_hits = forbidden_term_hits(entity_search_text(entity), DOMAIN_ROLE_IMPLEMENTATION_TERMS)
            if role_hits:
                errors.append(
                    f"Domain Role entity '{entity_id}' uses implementation/system term(s) {role_hits}; name the business capability or evaluator instead."
                )

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

        errors.extend(validate_attributes(entity_id, entity))

    return errors


def entity_search_text(entity: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("id", "name", "label", "kind", "category", "notes"):
        value = entity.get(key)
        if isinstance(value, str):
            parts.append(value)
    for attribute in entity.get("attributes") or []:
        if isinstance(attribute, dict):
            for key in ("name", "label", "meaning", "calculationRule", "precondition", "notes"):
                value = attribute.get(key)
                if isinstance(value, str):
                    parts.append(value)
    return " ".join(parts)


def forbidden_term_hits(text: str, terms: tuple[str, ...]) -> list[str]:
    lower_text = text.lower()
    hits: list[str] = []
    for term in terms:
        normalized_term = term.lower()
        if normalized_term.isascii() and re.fullmatch(r"[a-z0-9]+", normalized_term):
            pattern = rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])"
            if re.search(pattern, lower_text):
                hits.append(term)
        elif normalized_term in lower_text:
            hits.append(term)
    return hits


def validate_attributes(entity_id: str, entity: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    attributes = entity.get("attributes")
    if attributes is None:
        return errors
    if not isinstance(attributes, list):
        return [f"Entity '{entity_id}' attributes must be an array when provided."]

    for index, attribute in enumerate(attributes):
        if not isinstance(attribute, dict):
            errors.append(f"Entity '{entity_id}' attributes[{index}] must be an object.")
            continue

        attribute_name = normalize(attribute.get("name"))
        if attribute_name is None:
            errors.append(f"Entity '{entity_id}' attributes[{index}] name must be a non-empty string.")
        elif IDENTIFIER_RE.fullmatch(attribute_name) is None:
            errors.append(
                f"Entity '{entity_id}' attributes[{index}] name '{attribute_name}' must be an ASCII identifier."
            )

        calculation_rule = attribute.get("calculationRule")
        if calculation_rule is not None:
            if not isinstance(calculation_rule, str) or not calculation_rule.strip():
                errors.append(
                    f"Entity '{entity_id}' attributes[{index}] calculationRule must be a non-empty string when provided."
                )
            else:
                match = CALCULATION_RULE_RE.match(calculation_rule)
                if match is None:
                    errors.append(
                        f"Entity '{entity_id}' attributes[{index}] calculationRule must be a single assignment '<attributeName> = <expression>'."
                    )
                elif attribute_name is not None and match.group(1) != attribute_name:
                    errors.append(
                        f"Entity '{entity_id}' attributes[{index}] calculationRule must assign to its own attribute '{attribute_name}', found '{match.group(1)}'."
                    )

        precondition = attribute.get("precondition")
        if precondition is not None:
            if not isinstance(precondition, str) or not precondition.strip():
                errors.append(
                    f"Entity '{entity_id}' attributes[{index}] precondition must be a non-empty string when provided."
                )
            elif ASSIGNMENT_RE.search(precondition):
                errors.append(
                    f"Entity '{entity_id}' attributes[{index}] precondition must be a boolean expression, not an assignment."
                )

    return errors


ENTITY_ATTRIBUTE_PATH_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b"
)


def validate_attribute_references(entities: dict[str, dict[str, Any]]) -> list[str]:
    """Check Entity.attribute references in calculationRule/precondition expressions."""
    errors: list[str] = []
    attribute_names_by_entity: dict[str, set[str]] = {}
    entity_display_to_id: dict[str, str] = {}

    for entity_id, entity in entities.items():
        display_name = normalize(entity.get("name")) or entity_id
        entity_display_to_id[display_name] = entity_id
        attribute_names: set[str] = set()
        for attribute in entity.get("attributes") or []:
            if isinstance(attribute, dict):
                attribute_name = normalize(attribute.get("name"))
                if attribute_name is not None:
                    attribute_names.add(attribute_name)
        attribute_names_by_entity[display_name] = attribute_names

    for entity_id, entity in entities.items():
        for index, attribute in enumerate(entity.get("attributes") or []):
            if not isinstance(attribute, dict):
                continue
            for field in ("calculationRule", "precondition"):
                expression = attribute.get(field)
                if not isinstance(expression, str):
                    continue
                for referenced_entity, referenced_attribute in ENTITY_ATTRIBUTE_PATH_RE.findall(expression):
                    if referenced_entity not in entity_display_to_id:
                        errors.append(
                            f"Entity '{entity_id}' attributes[{index}] {field} references unknown entity '{referenced_entity}'."
                        )
                        continue
                    if referenced_attribute not in attribute_names_by_entity.get(referenced_entity, set()):
                        errors.append(
                            f"Entity '{entity_id}' attributes[{index}] {field} references unknown attribute '{referenced_entity}.{referenced_attribute}'."
                        )
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

    errors.extend(validate_actual_party_participation(entities, adjacency))
    errors.extend(validate_fulfillment_structure(entities, directed_relationships))
    errors.extend(validate_proposal_request_routing(entities, directed_relationships))
    errors.extend(validate_contract_relationships(entities, directed_relationships))
    errors.extend(validate_relationship_kind_usage(entities, relationships))
    errors.extend(validate_role_relationship_constraints(entities, directed_relationships, adjacency))
    return errors


def validate_actual_party_participation(
    entities: dict[str, dict[str, Any]], adjacency: dict[str, list[str]]
) -> list[str]:
    errors: list[str] = []
    for entity_id, entity in entities.items():
        category, kind = entity_kind(entity)
        if category != "Evidence":
            continue

        actual_parties = actual_party_ids(entity_id, entities, adjacency)
        if kind == "Contract":
            if len(actual_parties) != 2:
                errors.append(
                    f"Contract entity '{entity_id}' must trace to exactly two Participant Party entities, directly or through Party Role; found {len(actual_parties)}."
                )
            continue

        if kind in EVIDENCE_KINDS_REQUIRING_ACTUAL_PARTY and len(actual_parties) != 1:
            errors.append(
                f"Evidence entity '{entity_id}' ({kind}) must trace to exactly one responsible Participant Party, directly or through Party Role; found {len(actual_parties)}."
            )
    return errors


def actual_party_ids(
    entity_id: str,
    entities: dict[str, dict[str, Any]],
    adjacency: dict[str, list[str]],
) -> set[str]:
    actual_parties: set[str] = set()
    for neighbor_id in adjacency.get(entity_id, []):
        neighbor_kind = entity_kind(entities[neighbor_id])
        if neighbor_kind == ("Participant", "Party"):
            actual_parties.add(neighbor_id)
            continue
        if neighbor_kind != ("Role", "Party Role"):
            continue
        for role_neighbor_id in adjacency.get(neighbor_id, []):
            if role_neighbor_id == entity_id:
                continue
            if entity_kind(entities[role_neighbor_id]) == ("Participant", "Party"):
                actual_parties.add(role_neighbor_id)
    return actual_parties


def validate_fulfillment_structure(
    entities: dict[str, dict[str, Any]], relationships: list[tuple[str, str, int]]
) -> list[str]:
    """Check that each request participates in a contract-to-confirmation chain."""
    errors: list[str] = []
    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    for source, target, _index in relationships:
        if source not in entities or target not in entities:
            continue
        outgoing[source].append(target)
        incoming[target].append(source)

    for entity_id, entity in entities.items():
        if entity_kind(entity) != ("Evidence", "Fulfillment Request"):
            continue
        if not reachable_evidence_kind(
            entity_id, ("Evidence", "Contract"), incoming, entities
        ):
            errors.append(
                f"Fulfillment Request entity '{entity_id}' must be traceable back to a Contract through directed same-context Evidence relationships."
            )
        if not reachable_evidence_kind(
            entity_id, ("Evidence", "Fulfillment Confirmation"), outgoing, entities
        ):
            errors.append(
                f"Fulfillment Request entity '{entity_id}' must be traceable forward to at least one Fulfillment Confirmation through directed same-context Evidence relationships."
            )
    return errors


def reachable_evidence_kind(
    start_id: str,
    target_kind: tuple[str, str],
    links: dict[str, list[str]],
    entities: dict[str, dict[str, Any]],
) -> bool:
    visited: set[str] = set()
    queue = list(links.get(start_id, []))
    while queue:
        entity_id = queue.pop(0)
        if entity_id in visited:
            continue
        visited.add(entity_id)
        if entity_id not in entities:
            continue
        if not same_context_scope(entities, start_id, entity_id):
            continue
        kind = entity_kind(entities[entity_id])
        if kind == target_kind:
            return True
        if kind[0] != "Evidence":
            continue
        queue.extend(links.get(entity_id, []))
    return False


def same_context_scope(
    entities: dict[str, dict[str, Any]], left_id: str, right_id: str
) -> bool:
    left_context = context_id(entities, left_id)
    right_context = context_id(entities, right_id)
    return left_context is None or right_context is None or left_context == right_context


def validate_proposal_request_routing(
    entities: dict[str, dict[str, Any]], relationships: list[tuple[str, str, int]]
) -> list[str]:
    errors: list[str] = []
    for source, target, index in relationships:
        source_kind = entity_kind(entities.get(source))
        target_kind = entity_kind(entities.get(target))
        if {source_kind, target_kind} == {
            ("Evidence", "Proposal"),
            ("Evidence", "Fulfillment Request"),
        }:
            errors.append(
                f"relationships[{index}] Proposal must not connect directly to Fulfillment Request; route through Contract."
            )
    return errors


def validate_contract_relationships(
    entities: dict[str, dict[str, Any]], relationships: list[tuple[str, str, int]]
) -> list[str]:
    errors: list[str] = []
    for source, target, index in relationships:
        if entity_kind(entities.get(source)) == ("Evidence", "Contract") and entity_kind(
            entities.get(target)
        ) == ("Evidence", "Contract"):
            errors.append(
                f"relationships[{index}] Contract must not connect directly to another Contract; use separate contract contexts and bridge them through moment evidence or Evidence As Role."
            )
    return errors


def validate_relationship_kind_usage(
    entities: dict[str, dict[str, Any]],
    relationships: list[tuple[str, str, str, int, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []
    for relationship_id, source, target, index, relationship in relationships:
        if source not in entities or target not in entities:
            continue
        relationship_kind = normalize(relationship.get("relationshipKind"))
        if relationship_kind is None:
            continue
        source_kind = entity_kind(entities.get(source))
        target_kind = entity_kind(entities.get(target))
        if relationship_kind == "rolePlaying" and source_kind[0] != "Role" and target_kind[0] != "Role":
            errors.append(
                f"relationships[{index}] '{relationship_id}' uses relationshipKind rolePlaying but neither endpoint is a Role."
            )
        if relationship_kind == "crossContextAssociation":
            source_context = context_id(entities, source)
            target_context = context_id(entities, target)
            if source_context is not None and source_context == target_context:
                errors.append(
                    f"relationships[{index}] '{relationship_id}' uses relationshipKind crossContextAssociation but both endpoints are in context '{source_context}'."
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
                f"relationships[{index}] invalid cross-context relationship {source} -> {target}; only moment evidence (Fulfillment Confirmation/Other Evidence) direct links or Evidence As Role bridges are allowed."
            )

        if {source_kind, target_kind} == {
            ("Role", "Evidence As Role"),
            ("Evidence", "Fulfillment Request"),
        }:
            errors.append(
                f"relationships[{index}] Evidence As Role must not connect to Fulfillment Request."
            )

    for entity_id, entity in entities.items():
        kind = entity_kind(entity)
        if kind == ("Role", "Evidence As Role"):
            moment_neighbors: list[str] = []
            for neighbor_id in adjacency.get(entity_id, []):
                neighbor_kind = entity_kind(entities[neighbor_id])
                if neighbor_kind in FORBIDDEN_EVIDENCE_AS_ROLE_NEIGHBORS:
                    errors.append(
                        f"Evidence As Role '{entity_id}' must not connect to {neighbor_kind[1]} entity '{neighbor_id}'."
                    )
                if neighbor_kind in {("Participant", "Party"), ("Role", "Party Role")}:
                    errors.append(
                        f"Evidence As Role '{entity_id}' must not connect to actual responsible party/party role '{neighbor_id}'. It is played by moment evidence, not by a party."
                    )
                if is_moment_evidence(neighbor_kind):
                    moment_neighbors.append(neighbor_id)
            if not moment_neighbors:
                errors.append(
                    f"Evidence As Role '{entity_id}' must be played by at least one moment evidence (Fulfillment Confirmation or Other Evidence)."
                )
        allowed_targets: set[tuple[str | None, str | None]] | None = None
        allowed_targets_label: str | None = None
        if kind == ("Role", "Third Party Role"):
            allowed_targets = THIRD_PARTY_ROLE_TARGETS
            allowed_targets_label = "Fulfillment Confirmation, Other Evidence, or Evidence As Role"
        elif kind == ("Role", "Context Role"):
            allowed_targets = CONTEXT_ROLE_TARGETS
            allowed_targets_label = "Fulfillment Confirmation, Other Evidence, or Evidence As Role"

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
