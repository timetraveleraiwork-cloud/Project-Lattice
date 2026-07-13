# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.schema import NodeType, RelType

INPUT_FILE = PROJECT_ROOT / "data" / "staging" / "raw_extractions.json"


def validate() -> None:
    """Validate that extracted data conforms to the frozen ontology."""

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        documents = json.load(f)

    node_stats = Counter()
    rel_stats = Counter()

    valid_node_types = {node.value for node in NodeType}
    valid_rel_types = {rel.value for rel in RelType}

    errors = []

    for document in documents:
        entity_names = {entity["name"] for entity in document.get("entities", [])}

        for entity in document.get("entities", []):
            if entity["type"] not in valid_node_types:
                errors.append(
                    f"{document['document']}: Invalid node type '{entity['type']}'"
                )
            else:
                node_stats["valid"] += 1

        for relationship in document.get("relationships", []):
            if relationship["relation"] not in valid_rel_types:
                errors.append(
                    f"{document['document']}: Invalid relationship '{relationship['relation']}'"
                )
            else:
                rel_stats["valid"] += 1

            if (
                relationship["source"] not in entity_names
                or relationship["target"] not in entity_names
            ):
                rel_stats["orphaned"] += 1

    print("=" * 60)
    print("Validation Report")
    print("=" * 60)
    print(f"Valid entities       : {node_stats['valid']}")
    print(f"Valid relationships  : {rel_stats['valid']}")
    print(f"Orphan relationships : {rel_stats['orphaned']}")
    print(f"Validation errors    : {len(errors)}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f" - {error}")

        raise ValueError("Validation failed.")

    print("\n✓ Validation passed successfully.")


if __name__ == "__main__":
    validate()
