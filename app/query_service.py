from app.text_to_cypher import generate_cypher
from app.cypher_safety import validate_query
from app.neo4j import run_query
from app.schemas import QueryResponse


def answer_question(question: str) -> QueryResponse:
    cypher = generate_cypher(question)

    validate_query(cypher)

    results = run_query(cypher)

    return QueryResponse(
        question=question,
        cypher=cypher,
        results=results,
        supporting_nodes=results,
    )
