from __future__ import annotations

from app.cypher_safety import validate_query
from app.neo4j import run_query
from app.schemas import QueryResponse
from app.text_to_cypher import correct_cypher, generate_cypher

from app.embeddings import embed
from app.neo4j import driver
from app.schemas import (
    SemanticSearchResponse,
    SemanticSearchResult,
)


def answer_question(question: str) -> QueryResponse:
    """Generate, validate and execute a Cypher query."""

    cypher = generate_cypher(question)

    for attempt in range(2):
        try:
            validate_query(cypher)

            results = run_query(cypher)

            return QueryResponse(
                question=question,
                cypher=cypher,
                results=results,
                supporting_nodes=results,
            )

        except Exception as exc:
            if attempt == 1:
                raise

            cypher = correct_cypher(
                question=question,
                failed_query=cypher,
                error_message=str(exc),
            )

    raise RuntimeError("Unexpected failure in answer_question().")


def semantic_search(
    question: str,
    top_k: int = 5,
) -> SemanticSearchResponse:
    """Perform semantic document search using Neo4j vector index."""

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
                node.name AS name,
                node.source_document AS source_document,
                score
            """,
            embedding=query_embedding,
            top_k=top_k,
        )

        results = [
            SemanticSearchResult(
                name=record["name"],
                source_document=record["source_document"],
                score=round(record["score"], 4),
            )
            for record in result
        ]

    return SemanticSearchResponse(
        question=question,
        results=results,
    )
