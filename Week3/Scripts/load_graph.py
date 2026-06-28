from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
from pathlib import Path
import os
import re

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
)

DATA_PATH = Path("Week3/Resolved/resolved_extractions.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"Loaded {len(documents)} documents.")


def normalize_label(label: str) -> str:
    label = label.strip()

    # Only fix labels that are completely uppercase
    if label.isupper():
        label = label.capitalize()

    # Replace invalid Neo4j characters with underscores
    label = re.sub(r"[^A-Za-z0-9_]", "_", label)

    return label


def load_node(tx, entity, source_document):
    label = normalize_label(entity["type"])
    name = entity["name"]

    query = f"""
    MERGE (n:{label} {{name: $name}})
    SET n.source_document = $source_document
    """

    tx.run(
        query,
        name=name,
        source_document=source_document,
    )


def load_relationship(tx, relationship, source_document):
    relation = re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        relationship["relation"].strip().upper(),
    )

    query = f"""
    MATCH (source {{name:$source}})
    MATCH (target {{name:$target}})
    MERGE (source)-[r:{relation}]->(target)
    SET r.source_document=$source_document
    """

    tx.run(
        query,
        source=relationship["source"],
        target=relationship["target"],
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

    print("✅ All nodes loaded successfully!")

finally:
    driver.close()
