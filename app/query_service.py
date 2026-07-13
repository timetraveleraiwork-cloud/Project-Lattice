from __future__ import annotations

from app.cypher_safety import validate_query
from app.neo4j import run_query
from app.schemas import QueryResponse
from app.text_to_cypher import correct_cypher, generate_cypher


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
