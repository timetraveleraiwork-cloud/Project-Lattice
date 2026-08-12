from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Frozen node labels for the Project Lattice knowledge graph."""

    PERSON = "Person"
    DEPARTMENT = "Department"
    VENDOR = "Vendor"
    PROJECT = "Project"
    DOCUMENT = "Document"
    TRANSACTION = "Transaction"
    INVOICE = "Invoice"
    RISK = "Risk"
    SERVICE = "Service"
    CONTRACT = "Contract"


class RelType(str, Enum):
    """Frozen relationship types for the Project Lattice knowledge graph."""

    # Organization structure
    WORKS_IN = "WORKS_IN"
    REPORTS_TO = "REPORTS_TO"
    ASSIGNED_TO = "ASSIGNED_TO"
    RESPONSIBLE_FOR = "RESPONSIBLE_FOR"

    # Financial workflow
    APPROVED = "APPROVED"
    PAID_TO = "PAID_TO"
    HAS_INVOICE = "HAS_INVOICE"

    # Risk & services
    HAS_RISK = "HAS_RISK"
    PROVIDED_BY = "PROVIDED_BY"

    # Communication & documents
    COMMUNICATED_WITH = "COMMUNICATED_WITH"
    MENTIONS = "MENTIONS"

    # Ownership
    OWNS = "OWNS"
    RELATIVE_OF = "RELATIVE_OF"

    # Generic fallback
    RELATED_TO = "RELATED_TO"


RELATION_SCHEMA = {
    RelType.WORKS_IN: (NodeType.PERSON, NodeType.DEPARTMENT),
    RelType.REPORTS_TO: (NodeType.PERSON, NodeType.PERSON),
    RelType.ASSIGNED_TO: (NodeType.PERSON, NodeType.PROJECT),
    RelType.APPROVED: (NodeType.PERSON, NodeType.TRANSACTION),
    RelType.PAID_TO: (NodeType.TRANSACTION, NodeType.VENDOR),
    RelType.HAS_INVOICE: (NodeType.TRANSACTION, NodeType.INVOICE),
    RelType.HAS_RISK: (
        (NodeType.PROJECT, NodeType.DEPARTMENT),
        NodeType.RISK,
    ),
    RelType.PROVIDED_BY: (NodeType.SERVICE, NodeType.VENDOR),
    RelType.COMMUNICATED_WITH: (
        NodeType.PERSON,
        NodeType.PERSON,
    ),
    RelType.MENTIONS: (NodeType.DOCUMENT, None),
    RelType.OWNS: (NodeType.PERSON, NodeType.VENDOR),
    RelType.RELATIVE_OF: (NodeType.PERSON, NodeType.PERSON),
    RelType.RELATED_TO: (None, None),
}


class ExtractedEntity(BaseModel):
    """A validated entity extracted from a document."""

    name: str = Field(..., min_length=1)
    type: NodeType


class ExtractedRelationship(BaseModel):
    """A validated relationship extracted from a document."""

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    type: RelType
