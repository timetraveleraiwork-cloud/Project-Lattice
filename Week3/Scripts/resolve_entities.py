from __future__ import annotations

import json
import re
from pathlib import Path

from rapidfuzz import fuzz

# -----------------------------
# Configuration
# -----------------------------

INPUT_FILE = Path("Week3/Staging/raw_extractions.json")
OUTPUT_DIR = Path("Week3/Resolved")
OUTPUT_FILE = OUTPUT_DIR / "raw_extractions.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SIMILARITY_THRESHOLD = 92

TITLES = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
}

# -----------------------------
# Helper Functions
# -----------------------------


def normalize_name(name: str) -> str:
    """
    Normalize entity names for comparison.
    """

    name = name.lower()

    # Remove punctuation
    name = re.sub(r"[^\w\s]", "", name)

    # Remove titles
    words = [word for word in name.split() if word not in TITLES]

    # Collapse multiple spaces
    return " ".join(words).strip()


def is_duplicate(name1: str, name2: str) -> bool:
    """
    Returns True if two names are considered duplicates.
    """

    return fuzz.token_sort_ratio(name1, name2) >= SIMILARITY_THRESHOLD


# -----------------------------
# Main Resolution Logic
# -----------------------------


def resolve_entities(documents: list[dict]):
    """
    Resolve duplicate entities across ALL documents.
    """

    canonical_entities: dict[str, list[dict]] = {}

    duplicates_removed = 0

    for document in documents:
        resolved_entities = []

        for entity in document["entities"]:
            entity_type = entity["type"]
            entity_name = entity["name"]

            normalized = normalize_name(entity_name)

            if entity_type not in canonical_entities:
                canonical_entities[entity_type] = []

            matched_entity = None

            for existing in canonical_entities[entity_type]:
                existing_normalized = normalize_name(existing["name"])

                if is_duplicate(
                    normalized,
                    existing_normalized,
                ):
                    matched_entity = existing
                    break

            if matched_entity:
                duplicates_removed += 1

                # Replace duplicate with canonical entity
                resolved_entities.append(matched_entity)

            else:
                canonical_entities[entity_type].append(entity)

                resolved_entities.append(entity)

        document["entities"] = resolved_entities

    return documents, canonical_entities, duplicates_removed


# -----------------------------
# Main
# -----------------------------


def main():
    if not INPUT_FILE.exists():
        print("Input file not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        documents = json.load(f)

    (
        resolved_documents,
        canonical_entities,
        duplicates_removed,
    ) = resolve_entities(documents)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            resolved_documents,
            f,
            indent=4,
        )

    print("\n========== ENTITY RESOLUTION ==========\n")

    total_entities = 0

    for entity_type, entities in canonical_entities.items():
        print(f"{entity_type:<15}: {len(entities)} canonical entities")

        total_entities += len(entities)

    print()

    print(f"Duplicates removed : {duplicates_removed}")
    print(f"Canonical entities : {total_entities}")

    print(f"\nResolved file saved to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
