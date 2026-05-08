#!/usr/bin/env python3
"""Apply a Fulfillment Modeling changes payload to a base React Flow graph."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


NODE_CHANGE_KEYS = ("addNodes", "updateNodes", "deleteNodes")
EDGE_CHANGE_KEYS = ("addEdges", "updateEdges", "deleteEdges")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply FM changes JSON to a base graph and write the merged full graph.",
    )
    parser.add_argument("base_graph", help="Path to the base full graph JSON.")
    parser.add_argument("changes", help="Path to a JSON object with a changes payload.")
    parser.add_argument(
        "output",
        nargs="?",
        default="-",
        help="Output path for merged graph JSON, or '-' for stdout.",
    )
    args = parser.parse_args()

    try:
        base = read_json(args.base_graph)
        patch = read_json(args.changes)
        merged = apply_changes(base, patch)
    except ValueError as error:
        print(f"apply_fm_changes failed: {error}", file=sys.stderr)
        return 1

    text = json.dumps(merged, ensure_ascii=False, indent=2) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        Path(args.output).write_text(text, encoding="utf-8")
    return 0


def read_json(path: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not valid JSON: {error.msg}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def apply_changes(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    changes = patch.get("changes", patch)
    if not isinstance(changes, dict):
        raise ValueError("changes payload must be an object")

    merged = copy.deepcopy(base)
    nodes = list_of_objects(merged.get("nodes"), "base.nodes")
    edges = list_of_objects(merged.get("edges"), "base.edges")

    merged["nodes"] = apply_collection(nodes, changes, "node", NODE_CHANGE_KEYS)
    merged["edges"] = apply_collection(edges, changes, "edge", EDGE_CHANGE_KEYS)
    validate_edge_endpoints(merged["nodes"], merged["edges"])
    merged["_meta"] = merge_meta(base.get("_meta"), patch.get("_meta"))
    if "summary" in patch:
        merged["summary"] = patch["summary"]
    merged.pop("changes", None)
    return merged


def list_of_objects(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        if not normalize(item.get("id")):
            raise ValueError(f"{label}[{index}] must have a non-empty id")
    return copy.deepcopy(value)


def apply_collection(
    items: list[dict[str, Any]],
    changes: dict[str, Any],
    item_label: str,
    keys: tuple[str, str, str],
) -> list[dict[str, Any]]:
    add_key, update_key, delete_key = keys
    by_id = {item["id"]: item for item in items}
    order = [item["id"] for item in items]

    for raw_delete in changes.get(delete_key, []):
        item_id = change_id(raw_delete)
        if item_id is None:
            raise ValueError(f"{delete_key} entries must provide id or targetId")
        if item_id not in by_id:
            raise ValueError(
                f"{delete_key} references unknown existing {item_label} id '{item_id}'"
            )
        del by_id[item_id]
        order = [existing_id for existing_id in order if existing_id != item_id]

    for raw_update in changes.get(update_key, []):
        if not isinstance(raw_update, dict):
            raise ValueError(f"{update_key} entries must be objects")
        item_id = change_id(raw_update)
        if item_id is None:
            raise ValueError(f"{update_key} entries must provide id or targetId")
        if item_id not in by_id:
            raise ValueError(
                f"{update_key} references unknown existing {item_label} id '{item_id}'"
            )
        update_data = copy.deepcopy(raw_update)
        update_data.pop("targetId", None)
        by_id[item_id] = deep_merge(by_id[item_id], update_data)

    for raw_add in changes.get(add_key, []):
        if not isinstance(raw_add, dict):
            raise ValueError(f"{add_key} entries must be objects")
        item_id = normalize(raw_add.get("id"))
        if item_id is None:
            raise ValueError(f"{add_key} entries must provide id")
        if item_id in by_id:
            raise ValueError(
                f"{add_key} duplicates existing {item_label} id '{item_id}'"
            )
        by_id[item_id] = copy.deepcopy(raw_add)
        order.append(item_id)

    return [by_id[item_id] for item_id in order]


def validate_edge_endpoints(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> None:
    node_ids = {node["id"] for node in nodes}
    for edge in edges:
        edge_id = edge["id"]
        source = normalize(edge.get("source"))
        target = normalize(edge.get("target"))
        if source not in node_ids:
            raise ValueError(
                f"edge '{edge_id}' source '{source}' does not reference an existing node; "
                "delete incident edges when deleting a node"
            )
        if target not in node_ids:
            raise ValueError(
                f"edge '{edge_id}' target '{target}' does not reference an existing node; "
                "delete incident edges when deleting a node"
            )


def change_id(item: Any) -> str | None:
    if isinstance(item, str):
        return normalize(item)
    if isinstance(item, dict):
        return normalize(item.get("targetId")) or normalize(item.get("id"))
    return None


def deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in update.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def merge_meta(base_meta: Any, patch_meta: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(base_meta, dict):
        result.update(copy.deepcopy(base_meta))
    if isinstance(patch_meta, dict):
        result = deep_merge(result, patch_meta)
    return result


def normalize(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    raise SystemExit(main())
