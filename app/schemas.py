from pydantic import BaseModel
from typing import List
from typing import Any


class Entity(BaseModel):
    type: str
    name: str


class Relationship(BaseModel):
    source: str
    target: str
    relation: str


class ExtractionResult(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]


class CypherQuery(BaseModel):
    query: str


class QuestionRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    cypher: str
    results: list[dict[str, Any]]
    supporting_nodes: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    question: str
    error: str
