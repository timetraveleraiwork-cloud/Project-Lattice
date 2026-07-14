# ruff : noqa: E402
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
from pathlib import Path
import os
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.canonical_map import map_node_type, map_rel_type

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
)

DATA_PATH = PROJECT_ROOT / "data" / "resolved" / "resolved_extractions.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"Loaded {len(documents)} documents.")


def normalize_label(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", label.strip())


def normalize_relationship(rel: str) -> str:
    return re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        rel.strip().upper(),
    )


def load_node(tx, entity, source_document):
    mapped = map_node_type(entity["type"])

    if mapped is None:
        return

    label = normalize_label(mapped)
    name = entity["name"]

    properties = entity.copy()
    properties.pop("name", None)
    properties.pop("type", None)

    query = f"""
    MERGE (n:{label} {{name: $name}})
    SET n += $properties
    SET n.source_document = $source_document
    """

    tx.run(
        query,
        name=name,
        properties=properties,
        source_document=source_document,
    )


def load_relationship(tx, relationship, source_document):
    mapped = map_rel_type(relationship["relation"])

    if mapped is None:
        return

    relation = normalize_relationship(mapped)

    properties = relationship.copy()
    properties.pop("source", None)
    properties.pop("target", None)
    properties.pop("relation", None)

    query = f"""
    MATCH (source {{name: $source}})
    MATCH (target {{name: $target}})
    MERGE (source)-[r:{relation}]->(target)
    SET r += $properties
    SET r.source_document = $source_document
    """

    tx.run(
        query,
        source=relationship["source"],
        target=relationship["target"],
        properties=properties,
        source_document=source_document,
    )


try:
    driver.verify_connectivity()
    print("✅ Connected to Neo4j successfully!")

    with driver.session() as session:
        for document in documents:
            source_document = document["document"]

            for entity in document["entities"]:
                session.execute_write(
                    load_node,
                    entity,
                    source_document,
                )

            for relationship in document["relationships"]:
                session.execute_write(
                    load_relationship,
                    relationship,
                    source_document,
                )

    print("✅ All nodes and relationships loaded successfully!")

finally:
    if driver:
        driver.close()
