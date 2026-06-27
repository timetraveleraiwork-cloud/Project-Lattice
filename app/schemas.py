from pydantic import BaseModel
from typing import List


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
