# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.canonical_map import map_node_type, map_rel_type

STAGING_FILE = PROJECT_ROOT / "data" / "staging" / "raw_extractions.json"


def main() -> None:
    with STAGING_FILE.open("r", encoding="utf-8") as f:
        documents = json.load(f)

    node_counter = Counter()
    rel_counter = Counter()

    for doc in documents:
        for entity in doc.get("entities", []):
            node_counter[entity["type"]] += 1

        for rel in doc.get("relationships", []):
            rel_counter[rel["relation"]] += 1

    unmapped_nodes: list[str] = []
    unmapped_relationships: list[str] = []

    print("=" * 60)
    print("NODE TYPES")
    print("=" * 60)

    for label, count in sorted(node_counter.items()):
        mapped = map_node_type(label)

        if mapped is None:
            status = "DROP"
            unmapped_nodes.append(label)
        else:
            status = mapped

        print(f"{label:<35} -> {status:<20} ({count})")

    print("\n" + "=" * 60)
    print("RELATIONSHIP TYPES")
    print("=" * 60)

    for rel, count in sorted(rel_counter.items()):
        mapped = map_rel_type(rel)

        if mapped is None:
            status = "DROP"
            unmapped_relationships.append(rel)
        else:
            status = mapped

        print(f"{rel:<35} -> {status:<20} ({count})")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"Unique Node Types         : {len(node_counter)}")
    print(f"Unique Relationship Types : {len(rel_counter)}")
    print(f"Node Types Dropped        : {len(unmapped_nodes)}")
    print(f"Relationship Types Dropped: {len(unmapped_relationships)}")

    if unmapped_nodes:
        print("\nNode Types Marked for Removal:")
        for node in unmapped_nodes:
            print(f"  - {node}")

    if unmapped_relationships:
        print("\nRelationship Types Marked for Removal:")
        for rel in unmapped_relationships:
            print(f"  - {rel}")


if __name__ == "__main__":
    main()
