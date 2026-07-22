from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from app.schema import NodeType, RelType


class Entity(BaseModel):
    """Represents an extracted entity."""

    type: NodeType
    name: str = Field(..., min_length=1)


class Relationship(BaseModel):
    """Represents a relationship between two entities."""

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    relation: RelType


class ExtractionResult(BaseModel):
    """Complete extraction result from the LLM."""

    entities: list[Entity]
    relationships: list[Relationship]


class CypherQuery(BaseModel):
    """Generated Cypher query."""

    query: str = Field(..., min_length=1)


class QuestionRequest(BaseModel):
    """API request containing a natural language question."""

    question: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    """API response returned to the client."""

    question: str
    cypher: str
    results: list[dict[str, Any]]
    supporting_nodes: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    """Error response returned by the API."""

    question: str
    error: str


class SemanticSearchRequest(BaseModel):
    question: str
    top_k: int = 5


class SemanticSearchResult(BaseModel):
    name: str
    source_document: str
    score: float


class SemanticSearchResponse(BaseModel):
    question: str
    results: list[SemanticSearchResult]
