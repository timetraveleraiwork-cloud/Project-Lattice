# ruff: noqa: E402
from __future__ import annotations
import yaml
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

REVIEW_DIR = PROJECT_ROOT / "data" / "review"
REVIEW_CANDIDATES_FILE = REVIEW_DIR / "review_candidates.jsonl"

REVIEW_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_MAP_FILE = REVIEW_DIR / "canonical_map.yaml"

SIMILARITY_THRESHOLD = 92

TITLES = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"^\[.*\]$"),
    re.compile(r"^<.*>$"),
]

PLACEHOLDER_NAMES = {
    "staff",
    "employee",
    "manager",
    "vendor",
    "client",
    "authorized representative",
    "authorized signatory",
    "representative",
    "signatory",
    "unknown",
    "n/a",
    "na",
    "tbd",
}

ORG_SUFFIXES = {
    "pvt ltd",
    "private limited",
    "ltd",
    "limited",
    "inc",
    "corp",
    "corporation",
    "llc",
    "co",
    "company",
}

DEPARTMENT_SUFFIXES = {
    "department",
    "dept",
    "team",
}

REVIEWABLE_TYPES = {
    "Department",
    "Vendor",
    "Person",
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


def normalize_organization(name: str) -> str:
    """Normalize organization and department names."""

    normalized = normalize_name(name)

    words = normalized.split()

    while words:
        last = " ".join(words[-2:])

        if last in ORG_SUFFIXES:
            words = words[:-2]
            continue

        if words[-1] in ORG_SUFFIXES:
            words.pop()
            continue

        if words[-1] in DEPARTMENT_SUFFIXES:
            words.pop()
            continue

        break

    return " ".join(words).strip()


def preferred_name(name1: str, name2: str) -> str:
    """
    Prefer shorter canonical names.

    Finance < Finance Department
    IT < IT Department
    CloudKart Services < CloudKart Services Pvt Ltd
    """

    n1 = normalize_organization(name1)
    n2 = normalize_organization(name2)

    if n1 != n2:
        return name1

    if len(name1) <= len(name2):
        return name1

    return name2


def is_duplicate(name1: str, name2: str) -> bool:
    """Return True if two names refer to the same entity."""

    return fuzz.token_sort_ratio(name1, name2) >= SIMILARITY_THRESHOLD


def is_placeholder(name: str) -> bool:
    """Return True if the entity name is a placeholder."""

    if not name:
        return True

    cleaned = normalize_name(name)

    if cleaned in PLACEHOLDER_NAMES:
        return True

    return any(pattern.match(name.strip()) for pattern in PLACEHOLDER_PATTERNS)


def is_suspect_name(name: str) -> bool:
    return "/" in name or "(" in name or ")" in name or "'" in name


def add_review_candidate(
    review_candidates: list[dict],
    entity_a: dict,
    entity_b: dict,
    similarity: float,
) -> None:
    """Record a possible duplicate for manual review."""

    review_candidates.append(
        {
            "a": entity_a["name"],
            "b": entity_b["name"],
            "label": entity_a["type"],
            "similarity": round(similarity, 2),
            "status": "pending",
            "decision": None,
            "decided_by": None,
            "decided_at": None,
        }
    )


def load_canonical_map() -> dict[tuple[str, str], str]:
    """Load manually approved canonical mappings."""

    if not CANONICAL_MAP_FILE.exists():
        return {}

    with CANONICAL_MAP_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = yaml.safe_load(f) or {}

    mappings = {}

    for label, pairs in data.items():
        for alias, canonical in pairs.items():
            mappings[(label, alias)] = canonical

    return mappings


def resolve_person_fragments(person_names: list[str]):
    """
    Merge unique first-name fragments into their matching full names.

    Returns:
        merge_map: {"Priya": "Priya Nair"}
        review: [{"fragment": "...", "candidates": [...]}]
    """

    merge_map = {}
    review = []

    full_names = [n for n in person_names if len(n.split()) > 1]

    for name in person_names:
        if len(name.split()) != 1:
            continue

        candidates = [
            full for full in full_names if full.split()[0].lower() == name.lower()
        ]

        if len(candidates) == 1:
            merge_map[name] = candidates[0]

        elif len(candidates) > 1:
            review.append(
                {
                    "fragment": name,
                    "candidates": sorted(candidates),
                }
            )

    return merge_map, review


# ==========================================================
# Entity Resolution
# ==========================================================


def resolve_entities(documents: list[dict]):
    manual_map = load_canonical_map()
    """Resolve duplicate entities across all documents."""

    canonical_entities: list[dict] = []
    canonical_name_map: dict[str, str] = {}
    review_candidates: list[dict] = []

    duplicates_removed = 0
    placeholders_removed = 0

    # --------------------------------------------------
    # Resolve single-token person fragments
    # --------------------------------------------------

    person_names = []

    for document in documents:
        for entity in document.get("entities", []):
            if entity["type"] == "Person":
                person_names.append(entity["name"])

    merge_map, _ = resolve_person_fragments(person_names)

    for document in documents:
        resolved_entities = []

        for entity in document.get("entities", []):
            entity_name = entity["name"]

            entity_name = merge_map.get(
                entity_name,
                entity_name,
            )
            manual_key = (
                entity["type"],
                entity_name,
            )

            if manual_key in manual_map:
                entity_name = manual_map[manual_key]

            if is_placeholder(entity_name):
                placeholders_removed += 1
                continue

            normalized = normalize_organization(entity_name)

            matched_entity = None

            for existing in canonical_entities:
                if entity["type"] != existing["type"]:
                    continue
                existing_normalized = normalize_organization(existing["name"])

                score = fuzz.token_sort_ratio(
                    normalized,
                    existing_normalized,
                )

                if score >= SIMILARITY_THRESHOLD:
                    matched_entity = existing

                    canonical = preferred_name(
                        matched_entity["name"],
                        entity_name,
                    )

                    if canonical != matched_entity["name"]:
                        aliases = matched_entity.setdefault("aliases", [])
                        aliases.append(matched_entity["name"])
                        matched_entity["name"] = canonical

                    aliases = matched_entity.setdefault("aliases", [])

                    if (
                        entity_name != matched_entity["name"]
                        and entity_name not in aliases
                    ):
                        aliases.append(entity_name)

                    break

                elif (
                    entity["type"] in REVIEWABLE_TYPES
                    and entity["type"] == existing["type"]
                    and 70 <= score < SIMILARITY_THRESHOLD
                ):
                    add_review_candidate(
                        review_candidates,
                        entity,
                        existing,
                        score,
                    )

            if matched_entity:
                duplicates_removed += 1
                aliases = matched_entity.setdefault("aliases", [])

                if entity_name != matched_entity["name"] and entity_name not in aliases:
                    aliases.append(entity_name)

                resolved_entities.append(matched_entity)

            else:
                entity["name"] = entity_name
                canonical_entities.append(entity)
                resolved_entities.append(entity)

        document["entities"] = resolved_entities

        # --------------------------------------------------
        # Build canonical name lookup (after ALL entities)
        # --------------------------------------------------

        canonical_name_map = {}

        for entity in canonical_entities:
            canonical = entity["name"]
            canonical_name_map[normalize_organization(canonical)] = canonical

        for alias in entity.get("aliases", []):
            canonical_name_map[normalize_organization(alias)] = canonical

    print(canonical_name_map.get("Finance department"))
    print(canonical_name_map.get("Procurement department"))
    print(canonical_name_map.get("IT department"))

    for document in documents:
        filtered_relationships = []

        for relationship in document.get("relationships", []):
            if is_placeholder(relationship["source"]) or is_placeholder(
                relationship["target"]
            ):
                continue

            normalized_source = normalize_organization(relationship["source"])

            if normalized_source in canonical_name_map:
                relationship["source"] = canonical_name_map[normalized_source]

            normalized_target = normalize_organization(relationship["target"])

            if normalized_target in canonical_name_map:
                relationship["target"] = canonical_name_map[normalized_target]

            filtered_relationships.append(relationship)

        document["relationships"] = filtered_relationships

    unique_candidates = {}

    for candidate in review_candidates:
        if "a" not in candidate:
            continue

        key = (
            tuple(sorted([candidate["a"], candidate["b"]])),
            candidate["label"],
        )

        if key not in unique_candidates:
            unique_candidates[key] = candidate
    review_candidates = list(unique_candidates.values())

    with REVIEW_CANDIDATES_FILE.open("w", encoding="utf-8") as f:
        for candidate in review_candidates:
            json.dump(candidate, f)
            f.write("\n")

    return (
        documents,
        canonical_entities,
        duplicates_removed,
        placeholders_removed,
        len(review_candidates),
    )


# ==========================================================
# Main
# ==========================================================


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"Input file not found:\n{INPUT_FILE}")
        return

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        documents = json.load(f)

    (
        resolved_documents,
        canonical_entities,
        duplicates_removed,
        placeholders_removed,
        review_candidates_count,
    ) = resolve_entities(documents)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            resolved_documents,
            f,
            indent=2,
        )

    print("=" * 60)
    print("Entity Resolution Complete")
    print("=" * 60)

    total_entities = len(canonical_entities)

    print(f"Canonical entities    : {total_entities}")
    print(f"Duplicates removed    : {duplicates_removed}")
    print(f"Placeholders removed  : {placeholders_removed}")
    print(f"Review candidates     : {review_candidates_count}")
    print(f"Output written to     : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
