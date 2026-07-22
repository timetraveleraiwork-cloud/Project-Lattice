from __future__ import annotations

from app.embeddings import embed
from app.neo4j import driver
from app.schemas import (
    SemanticSearchResult,
)
from pathlib import Path

import re


def retrieve_anchors(
    question: str,
    top_k: int = 5,
) -> list[SemanticSearchResult]:
    query_embedding = embed(question)

    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.vector.queryNodes(
                'doc_embeddings',
                $top_k,
                $embedding
            )
            YIELD node, score

            RETURN
                elementId(node) AS element_id,
                node.name AS name,
                node.source_document AS source_document,
                score
            """,
            embedding=query_embedding,
            top_k=top_k,
        )

        records = list(result)

    anchors = []

    for record in records:
        anchors.append(
            SemanticSearchResult(
                element_id=record["element_id"],
                name=record["name"],
                source_document=record["source_document"],
                score=round(record["score"], 4),
            )
        )

    return anchors


def expand_graph(
    anchors: list[SemanticSearchResult],
    max_hops: int = 2,
    limit: int = 200,
) -> list[Path]:
    """
    Expand the graph around semantic anchors.

    Parameters
    ----------
    anchors
        Anchor nodes returned from semantic search.

    max_hops
        Maximum traversal depth.

    limit
        Maximum number of paths to return.
    """

    if not anchors:
        return []

    anchor_ids = [anchor.element_id for anchor in anchors]

    with driver.session() as session:
        result = session.run(
            f"""
            MATCH (a)
            WHERE elementId(a) IN $anchor_ids

            MATCH path = (a)-[*1..{max_hops}]-(m)

            RETURN path
            LIMIT $limit
            """,
            anchor_ids=anchor_ids,
            limit=limit,
        )

        return [record["path"] for record in result]


def serialize_paths(
    paths: list[Path],
) -> list[str]:
    """
    Convert Neo4j Path objects into readable triples.
    """

    unique_triples: set[str] = set()

    for path in paths:
        nodes = list(path.nodes)
        relationships = list(path.relationships)

        for left, rel, right in zip(
            nodes,
            relationships,
            nodes[1:],
        ):
            source = (
                rel.get("source_document")
                or left.get("source_document")
                or right.get("source_document")
                or "unknown"
            )

            unique_triples.add(
                f"{left.get('name', '<unnamed>')} "
                f"-{rel.type}-> "
                f"{right.get('name', '<unnamed>')} "
                f"[source: {source}]"
            )

    return list(unique_triples)


DOCS_DIR = Path("data/corpus/docs")


def get_context_documents(
    anchors: list[SemanticSearchResult],
    triples: list[str],
    max_documents: int = 10,
) -> list[dict[str, str]]:
    """
    Load documents for the hybrid retrieval context.

    Priority:
    1. Anchor documents.
    2. Documents referenced by graph triples.
    """

    ordered_files: list[str] = []
    seen: set[str] = set()

    # ---------------------------
    # First: Anchor documents
    # ---------------------------

    for anchor in anchors:
        filename = anchor.source_document

        if filename not in seen:
            ordered_files.append(filename)
            seen.add(filename)

    # ---------------------------
    # Then: Graph documents
    # ---------------------------

    pattern = re.compile(r"\[source:\s*(.*?)\]")

    for triple in triples:
        match = pattern.search(triple)

        if not match:
            continue

        filename = match.group(1)

        if filename not in seen:
            ordered_files.append(filename)
            seen.add(filename)

        if len(ordered_files) >= max_documents:
            break

    documents = []

    for filename in ordered_files:
        file_path = DOCS_DIR / filename

        if not file_path.exists():
            continue

        documents.append(
            {
                "source_document": filename,
                "text": file_path.read_text(encoding="utf-8"),
            }
        )

    return documents


def build_context(
    triples: list[str],
    documents: list[dict[str, str]],
) -> tuple[str, list[str]]:
    """
    Assemble the GraphRAG context.

    Returns
    -------
    context
        The context sent to the LLM.

    sources
        All valid source documents used in the context.
    """

    context_parts = []

    context_parts.append("=== GRAPH ===\n")
    context_parts.extend(sorted(triples))

    context_parts.append("\n=== DOCUMENTS ===\n")

    sources: list[str] = []

    for document in documents:
        source = document["source_document"]

        sources.append(source)

        context_parts.append(f"\nSource: {source}\n")

        context_parts.append(document["text"])

    context = "\n".join(context_parts)

    return context, sources
