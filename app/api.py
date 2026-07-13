from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.query_service import answer_question
from app.schemas import ErrorResponse, QueryResponse, QuestionRequest

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
