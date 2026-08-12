# ruff: noqa: E402

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.embeddings import embed
from app.neo4j import close, run_query


OUTPUT_FILE = PROJECT_ROOT / "data" / "node_embeddings.json"


def build_description(node: dict) -> str:
    """Build a textual description of a graph node."""

    lines = []

    label = node["labels"][0]
    props = node["properties"]

    lines.append(f"{label}: {props.get('name', '')}")

    if "source_document" in props:
        lines.append(f"Source document: {props['source_document']}")

    for neighbor in node["neighbors"]:
        if neighbor["rel"] is None or neighbor["neighbor"] is None:
            continue

        lines.append(f"{neighbor['rel']}: {neighbor['neighbor']}")

    return "\n".join(lines)


def main() -> None:
    start = time.perf_counter()

    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN
        elementId(n) AS id,
        labels(n) AS labels,
        properties(n) AS properties,
        collect({
            rel: type(r),
            neighbor: m.name
        }) AS neighbors
    ORDER BY id
    """

    nodes = run_query(query)

    print(f"Loaded {len(nodes)} nodes")

    embeddings = []

    for i, node in enumerate(nodes, start=1):
        name = node["properties"].get("name", "Unnamed")
        print(f"[{i}/{len(nodes)}] Embedding: {name}")

        description = build_description(node)
        vector = embed(description)

        embeddings.append(
            {
                "id": node["id"],
                "labels": node["labels"],
                "name": name,
                "embedding": vector,
            }
        )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(embeddings, f, indent=2)

    close()

    elapsed = time.perf_counter() - start

    print(f"\nSaved embeddings to {OUTPUT_FILE}")
    print(f"Completed in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
