# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path

from neo4j import GraphDatabase
from dotenv import load_dotenv
from os import getenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

URI = getenv("NEO4J_URI")
USER = getenv("NEO4J_USERNAME")
PASSWORD = getenv("NEO4J_PASSWORD")

EMBEDDINGS_FILE = PROJECT_ROOT / "data" / "document_embeddings.json"


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as f:
        embeddings = json.load(f)

    with driver.session() as session:
        for item in embeddings:
            session.run(
                """
                MATCH (d:Document {source_document: $source_document})
                SET d.embedding = $embedding
                """,
                source_document=item["source_document"],
                embedding=item["embedding"],
            )

            print(f"Loaded {item['source_document']}")

    driver.close()

    print("\nAll embeddings uploaded!")


if __name__ == "__main__":
    main()
