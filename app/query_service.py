from app.text_to_cypher import generate_cypher, correct_cypher
from app.cypher_safety import validate_query
from app.neo4j import run_query
from app.schemas import QueryResponse


def answer_question(question: str) -> QueryResponse:
    cypher = generate_cypher(question)

    validate_query(cypher)

    try:
        results = run_query(cypher)

    except Exception as e:
        corrected = correct_cypher(
            question=question,
            failed_query=cypher,
            error_message=str(e),
        )

        validate_query(corrected)

        results = run_query(corrected)

        cypher = corrected

    return QueryResponse(
        question=question,
        cypher=cypher,
        results=results,
        supporting_nodes=results,
    )
