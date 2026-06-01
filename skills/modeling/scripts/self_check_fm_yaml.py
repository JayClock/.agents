#!/usr/bin/env python3
"""Validate a Fulfillment Modeling model stored as YAML files.

Expected layout:
  fm-model/
    summary.yaml
    entities/<friendly-entity-name>.yaml
    relationships/<friendly-source>_to_<friendly-target>.yaml

Each YAML file must contain exactly one object. Entity name values are used as
stable references. Relationship source/target values reference entity names.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment issue
    yaml = None  # type: ignore[assignment]

from fm_graph_validation import validate_graph

DISALLOWED_TRANSPORT_KEYS = {
    "operation",
    "mode",
    "changes",
    "addEntities",
    "updateEntities",
    "deleteEntities",
    "addRelationships",
    "updateRelationships",
    "deleteRelationships",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Self-check a Fulfillment Modeling model stored as YAML files."
    )
    parser.add_argument("model_dir", help="Directory containing FM YAML files.")
    args = parser.parse_args()

    if yaml is None:
        print("FM YAML self-check failed:", file=sys.stderr)
        print("- PyYAML is required to read YAML files.", file=sys.stderr)
        return 1

    root = Path(args.model_dir)
    errors = validate_yaml_model(root)
    if errors:
        print("FM YAML self-check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("FM YAML self-check passed.")
    return 0


def validate_yaml_model(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.exists():
        return [f"model directory '{root}' does not exist."]
    if not root.is_dir():
        return [f"model path '{root}' must be a directory."]

    yaml_files = sorted(
        path
        for pattern in ("*.yaml", "*.yml")
        for path in root.rglob(pattern)
        if path.is_file()
    )
    if not yaml_files:
        return [f"model directory '{root}' contains no .yaml or .yml files."]

    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    relationship_file_stems: set[str] = set()
    summary_count = 0

    for path in yaml_files:
        rel = path.relative_to(root)
        try:
            docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except OSError as error:
            errors.append(f"cannot read {rel}: {error}")
            continue
        except yaml.YAMLError as error:
            errors.append(f"{rel} is not valid YAML: {error}")
            continue

        non_empty_docs = [doc for doc in docs if doc is not None]
        if len(non_empty_docs) != 1:
            errors.append(
                f"{rel} must contain exactly one YAML object; found {len(non_empty_docs)}."
            )
            continue

        doc = non_empty_docs[0]
        if not isinstance(doc, dict):
            errors.append(f"{rel} must contain a YAML object.")
            continue

        disallowed = sorted(DISALLOWED_TRANSPORT_KEYS.intersection(doc.keys()))
        if disallowed:
            errors.append(
                f"{rel} must not contain transport/diff field(s): {', '.join(disallowed)}."
            )

        doc_type = normalize(doc.get("type"))
        if doc_type == "summary":
            summary_count += 1
            if normalize(doc.get("summary")) is None:
                errors.append(f"{rel} summary must be a non-empty string.")
            continue
        if doc_type == "entity":
            if "entities" not in rel.parts:
                errors.append(f"entity file {rel} should be under entities/.")
            graph_entity = entity_for_graph(doc, rel, errors)
            entities.append(graph_entity)
            continue
        if doc_type == "relationship":
            if "relationships" not in rel.parts:
                errors.append(f"relationship file {rel} should be under relationships/.")
            if path.stem in relationship_file_stems:
                errors.append(f"duplicate relationship filename stem '{path.stem}'.")
            relationship_file_stems.add(path.stem)
            graph_relationship = relationship_for_graph(doc, path.stem, rel, errors)
            relationships.append(graph_relationship)
            continue

        errors.append(
            f"{rel} type must be one of summary, entity, or relationship; found {doc.get('type')!r}."
        )

    if summary_count == 0:
        errors.append("model should include summary.yaml with type: summary.")
    if not entities:
        errors.append("model must include at least one entity YAML file.")
    if not relationships:
        errors.append("model must include at least one relationship YAML file.")

    if entities or relationships:
        errors.extend(validate_graph({"entities": entities, "relationships": relationships}))

    return errors


def entity_for_graph(doc: dict[str, Any], rel: Path, errors: list[str]) -> dict[str, Any]:
    if "id" in doc:
        errors.append(f"{rel} should use name as the entity reference key; remove id.")
    if "contextId" in doc:
        errors.append(f"{rel} should use context with the Context name; replace contextId.")

    entity = strip_type(doc)
    entity.pop("id", None)
    context_name = entity.pop("context", None)
    fallback_context_id = entity.pop("contextId", None)
    if context_name is not None and fallback_context_id is not None:
        errors.append(f"{rel} should provide only one context reference.")

    name = normalize(entity.get("name"))
    entity["id"] = name or f"__missing_entity_name__{rel.as_posix()}"
    context_reference = normalize(context_name) or normalize(fallback_context_id)
    if context_reference is not None:
        entity["contextId"] = context_reference
    return entity


def relationship_for_graph(
    doc: dict[str, Any], file_stem: str, rel: Path, errors: list[str]
) -> dict[str, Any]:
    if "id" in doc:
        errors.append(f"{rel} should use its filename as the relationship identity; remove id.")

    relationship = strip_type(doc)
    relationship.pop("id", None)
    relationship["id"] = file_stem
    return relationship


def strip_type(doc: dict[str, Any]) -> dict[str, Any]:
    result = dict(doc)
    result.pop("type", None)
    return result


def normalize(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    raise SystemExit(main())
