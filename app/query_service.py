from __future__ import annotations

import logging

from app.cypher_safety import validate_query
from app.llm import call_model
from app.neo4j import run_query
from app.retrieval import (
    build_context,
    expand_graph,
    get_context_documents,
    retrieve_anchors,
    serialize_paths,
)
from app.schemas import (
    HybridResponse,
    QueryResponse,
    SemanticSearchResponse,
)
from app.text_to_cypher import (
    correct_cypher,
    generate_cypher,
)

logger = logging.getLogger(__name__)


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
    """Perform semantic document search."""

    anchors = retrieve_anchors(
        question=question,
        top_k=top_k,
    )

    return SemanticSearchResponse(
        question=question,
        results=anchors,
    )


def generate_grounded_answer(
    question: str,
    context: str,
) -> HybridResponse:
    """Generate a grounded answer using the supplied context."""

    prompt = f"""
You are an assistant answering questions about the Project Lattice knowledge base.

Rules:

1. Use ONLY the supplied context.
2. Never use outside knowledge.
3. Every factual claim must be supported by the supplied context.
4. citations must contain ONLY source_document filenames.
5. graph_paths should contain the graph triples you used.
6. anchors_used should contain the source documents that were most useful.
7. If the answer cannot be found, reply exactly:

INSUFFICIENT_EVIDENCE

================ CONTEXT ================

{context}

================ QUESTION ================

{question}
"""

    return call_model(
        prompt,
        HybridResponse,
    )


def validate_citations(
    response: HybridResponse,
    valid_sources: list[str],
) -> HybridResponse:
    """Remove citations not present in the retrieval context."""

    valid = set(valid_sources)

    removed = [citation for citation in response.citations if citation not in valid]

    if removed:
        logger.warning(
            "Removed hallucinated citations: %s",
            removed,
        )

    response.citations = [
        citation for citation in response.citations if citation in valid
    ]

    response.anchors_used = [
        anchor for anchor in response.anchors_used if anchor in valid
    ]

    if response.answer == "INSUFFICIENT_EVIDENCE":
        response.citations = []
        response.graph_paths = []
        response.anchors_used = []

    return response


def ask_hybrid(
    question: str,
) -> HybridResponse:
    """Hybrid GraphRAG question answering pipeline."""

    anchors = retrieve_anchors(question)

    paths = expand_graph(anchors)

    triples = serialize_paths(paths)

    documents = get_context_documents(
        anchors,
        triples,
    )

    context, sources = build_context(
        triples,
        documents,
    )

    response = generate_grounded_answer(
        question=question,
        context=context,
    )

    return validate_citations(
        response,
        sources,
    )
