from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Frozen node labels for the Project Lattice knowledge graph."""

    PERSON = "Person"
    DEPARTMENT = "Department"
    VENDOR = "Vendor"
    CONTRACT = "Contract"
    PROJECT = "Project"
    TRANSACTION = "Transaction"
    COMMUNICATION = "Communication"
    INCIDENT = "Incident"


class RelType(str, Enum):
    """Frozen relationship types for the Project Lattice knowledge graph."""

    WORKS_FOR = "WORKS_FOR"
    REPORTS_TO = "REPORTS_TO"
    OWNS = "OWNS"
    SIGNED = "SIGNED"
    PAID = "PAID"
    APPROVED = "APPROVED"
    COMMUNICATED_WITH = "COMMUNICATED_WITH"
    ASSIGNED_TO = "ASSIGNED_TO"
    RELATED_TO = "RELATED_TO"


class ExtractedEntity(BaseModel):
    """A validated entity extracted from a document."""

    name: str = Field(..., min_length=1)
    type: NodeType
    properties: dict[str, Any] = Field(default_factory=dict)


class ExtractedRelationship(BaseModel):
    """A validated relationship extracted from a document."""

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    type: RelType
    source_document: str = Field(..., min_length=1)
