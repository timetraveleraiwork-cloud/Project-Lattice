from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.query_service import (
    answer_question,
    semantic_search,
    ask_hybrid,
    HybridResponse,
)
from app.schemas import (
    ErrorResponse,
    QueryResponse,
    QuestionRequest,
    SemanticSearchRequest,
    SemanticSearchResponse,
)

app = FastAPI(
    title="Project Lattice",
    version="1.0.0",
)


@app.get("/")
def root() -> dict[str, str]:
    """Health check endpoint."""

    return {"message": "Project Lattice Text-to-Cypher API"}


@app.post(
    "/ask",
    response_model=QueryResponse,
    responses={400: {"model": ErrorResponse}},
)
def ask(request: QuestionRequest):
    """Answer a natural language question using the knowledge graph."""

    try:
        return answer_question(request.question)

    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                question=request.question,
                error=str(exc),
            ).model_dump(),
        )


@app.post(
    "/semantic_search",
    response_model=SemanticSearchResponse,
)
def search(request: SemanticSearchRequest):
    """Semantic document search."""

    return semantic_search(
        question=request.question,
        top_k=request.top_k,
    )


@app.post(
    "/ask_hybrid",
    response_model=HybridResponse,
)
def ask_hybrid_endpoint(request: QuestionRequest):
    """Answer a question using the hybrid GraphRAG pipeline."""

    return ask_hybrid(request.question)
