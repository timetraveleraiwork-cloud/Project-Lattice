# ruff: noqa: E402
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from rapidfuzz import fuzz

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# Configuration
# ==========================================================

INPUT_FILE = PROJECT_ROOT / "data" / "staging" / "raw_extractions.json"

OUTPUT_DIR = PROJECT_ROOT / "data" / "resolved"
OUTPUT_FILE = OUTPUT_DIR / "resolved_extractions.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SIMILARITY_THRESHOLD = 92

TITLES = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
}

# ==========================================================
# Helper Functions
# ==========================================================


def normalize_name(name: str) -> str:
    """Normalize names before fuzzy matching."""

    name = name.lower()

    name = re.sub(r"[^\w\s]", "", name)

    words = [word for word in name.split() if word not in TITLES]

    return " ".join(words).strip()


def is_duplicate(name1: str, name2: str) -> bool:
    """Return True if two names refer to the same entity."""

    return fuzz.token_sort_ratio(name1, name2) >= SIMILARITY_THRESHOLD


# ==========================================================
# Entity Resolution
# ==========================================================


def resolve_entities(documents: list[dict]):
    """Resolve duplicate entities across all documents."""

    canonical_entities: dict[str, list[dict]] = {}
    canonical_name_map: dict[tuple[str, str], str] = {}

    duplicates_removed = 0

    for document in documents:
        resolved_entities = []

        # --------------------------------------------------
        # Resolve duplicate entities
        # --------------------------------------------------
        for entity in document.get("entities", []):
            entity_type = entity["type"]
            entity_name = entity["name"]

            normalized = normalize_name(entity_name)

            canonical_entities.setdefault(entity_type, [])

            matched_entity = None

            for existing in canonical_entities[entity_type]:
                existing_normalized = normalize_name(existing["name"])

                if is_duplicate(normalized, existing_normalized):
                    matched_entity = existing
                    canonical_name_map[(entity_type, entity_name)] = existing["name"]
                    break

            if matched_entity:
                duplicates_removed += 1
                resolved_entities.append(matched_entity)

            else:
                canonical_entities[entity_type].append(entity)
                canonical_name_map[(entity_type, entity_name)] = entity_name
                resolved_entities.append(entity)

        document["entities"] = resolved_entities

        # --------------------------------------------------
        # Fast lookup for entity types
        # --------------------------------------------------
        entity_lookup = {entity["name"]: entity["type"] for entity in resolved_entities}

        # --------------------------------------------------
        # Rewrite relationship endpoints
        # --------------------------------------------------
        for relationship in document.get("relationships", []):
            source_type = entity_lookup.get(relationship["source"])
            target_type = entity_lookup.get(relationship["target"])

            if source_type:
                relationship["source"] = canonical_name_map.get(
                    (source_type, relationship["source"]),
                    relationship["source"],
                )

            if target_type:
                relationship["target"] = canonical_name_map.get(
                    (target_type, relationship["target"]),
                    relationship["target"],
                )

    return documents, canonical_entities, duplicates_removed


# ==========================================================
# Main
# ==========================================================


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"Input file not found:\n{INPUT_FILE}")
        return

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        documents = json.load(f)

    (
        resolved_documents,
        canonical_entities,
        duplicates_removed,
    ) = resolve_entities(documents)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            resolved_documents,
            f,
            indent=2,
        )

    print("=" * 60)
    print("Entity Resolution Complete")
    print("=" * 60)

    total_entities = 0

    for entity_type, entities in sorted(canonical_entities.items()):
        print(f"{entity_type:<15}: {len(entities)} canonical entities")
        total_entities += len(entities)

    print()
    print(f"Duplicates removed : {duplicates_removed}")
    print(f"Canonical entities : {total_entities}")
    print(f"Output written to  : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
