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
from app.schema import RELATION_SCHEMA

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


def is_valid_relationship(
    source_label: str,
    rel_type: str,
    target_label: str,
) -> bool:
    """Validate a relationship against the frozen ontology."""

    schema = RELATION_SCHEMA.get(rel_type)

    if schema is None:
        return False

    allowed_source, allowed_target = schema

    def matches(actual: str, allowed) -> bool:
        if allowed is None:
            return True

        if isinstance(allowed, tuple):
            return actual in {node.value for node in allowed}

        return actual == allowed.value

    return matches(source_label, allowed_source) and matches(
        target_label, allowed_target
    )


def normalize_relationship(rel: str) -> str:
    return re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        rel.strip().upper(),
    )


def load_node(tx, entity, source_document):
    mapped = map_node_type(entity["type"])
    print(
        entity["type"],
        "->",
        mapped,
        entity["name"],
    )

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


def load_relationship(tx, relationship, entity_lookup, source_document):
    relation = map_rel_type(relationship["relation"])
    if relation is None:
        return

    source_name = relationship["source"]
    target_name = relationship["target"]

    source_label = entity_lookup.get(source_name)
    target_label = entity_lookup.get(target_name)

    if source_label is None or target_label is None:
        print(
            f"Missing endpoint:"
            f" source={source_name} ({source_label})"
            f" target={target_name} ({target_label})"
            f" in {source_document}"
        )
        return

    if source_label is None or target_label is None:
        return

    print(
        source_name,
        relation,
        target_name,
    )

    if not is_valid_relationship(source_label, relation, target_label):
        print(
            f"Skipped relationship: "
            f"{source_name} ({source_label}) "
            f"-[:{relation}]-> "
            f"{target_name} ({target_label})"
        )
        return

    query = f"""
    MATCH (source:{source_label} {{name:$source}})
    MATCH (target:{target_label} {{name:$target}})
    MERGE (source)-[r:{relation}]->(target)
    SET r.source_document=$source_document
    """

    result = tx.run(
        query,
        source=source_name,
        target=target_name,
        source_document=source_document,
    )

    summary = result.consume()

    if summary.counters.relationships_created == 0:
        print(
            f"Relationship already existed or nodes not found: "
            f"{source_name} ({source_label}) "
            f"-[:{relation}]-> "
            f"{target_name} ({target_label})"
        )


try:
    driver.verify_connectivity()
    print("✅ Connected to Neo4j successfully!")

    with driver.session() as session:
        for document in documents:
            source_document = document["document"]

            # -------------------------
            # Load Nodes
            # -------------------------
            for entity in document["entities"]:
                session.execute_write(
                    load_node,
                    entity,
                    source_document,
                )

            # -------------------------
            # Build lookup for this document
            # -------------------------
            entity_lookup = {
                entity["name"]: map_node_type(entity["type"])
                for entity in document["entities"]
            }

            # -------------------------
            # Load Relationships
            # -------------------------
            for relationship in document["relationships"]:
                session.execute_write(
                    load_relationship,
                    relationship,
                    entity_lookup,
                    source_document,
                )

    print("✅ All nodes and relationships loaded successfully!")

finally:
    driver.close()
