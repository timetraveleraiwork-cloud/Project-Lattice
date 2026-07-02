from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.query_service import answer_question
from app.schemas import QuestionRequest, QueryResponse

app = FastAPI(
    title="Project Lattice",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Project Lattice Text-to-Cypher API"}


@app.post("/ask", response_model=QueryResponse)
def ask(request: QuestionRequest):
    try:
        return answer_question(request.question)

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "question": request.question,
                "error": str(e),
            },
        )
