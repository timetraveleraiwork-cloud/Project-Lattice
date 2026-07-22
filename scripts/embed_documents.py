# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.embeddings import embed

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
OUTPUT_FILE = PROJECT_ROOT / "data" / "document_embeddings.json"

MAX_CHARS = 1500

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
)


def main() -> None:
    documents = sorted(
        f
        for f in CORPUS_DIR.rglob("*")
        if f.is_file()
        and f.suffix.lower() in {".txt", ".md"}
        and f.name != "cast_list.md"
    )

    print(f"Found {len(documents)} documents")

    embeddings = []

    for document in documents:
        print(f"Embedding {document.relative_to(CORPUS_DIR)}...")

        text = document.read_text(encoding="utf-8")

        payload = f"{document.relative_to(CORPUS_DIR).as_posix()}\n\n{text[:MAX_CHARS]}"

        vector = embed(payload)

        embeddings.append(
            {
                "source_document": document.name,
                "title": document.stem,
                "embedding": vector,
            }
        )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(embeddings, f, indent=2)

        with driver.session() as session:
            for item in embeddings:
                result = session.run(
                    """
                 MATCH (d:Document {source_document: $source_document})
                 SET d.embedding = $embedding
                 """,
                    source_document=item["source_document"],
                    embedding=item["embedding"],
                )
                summary = result.consume()
                print(item["source_document"], summary.counters.properties_set)

    print("Uploaded embeddings to Neo4j.")

    print(f"\nSaved embeddings to {OUTPUT_FILE}")

    driver.close()


if __name__ == "__main__":
    main()
