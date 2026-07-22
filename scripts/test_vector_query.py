# ruff: noqa: E402
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from neo4j import GraphDatabase
from app.embeddings import embed

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD"),
    ),
)

question = "money problems with suppliers"

query_embedding = embed(question)

with driver.session() as session:
    result = session.run(
        """
        CALL db.index.vector.queryNodes(
            'doc_embeddings',
            5,
            $embedding
        )
        YIELD node, score

        RETURN
            node.name AS name,
            node.source_document AS source_document,
            score
        """,
        embedding=query_embedding,
    )

    print(f"\nQuery: {question}\n")

    for record in result:
        print(f"{record['score']:.4f} | {record['source_document']} | {record['name']}")

driver.close()
