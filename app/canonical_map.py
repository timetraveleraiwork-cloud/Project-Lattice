from __future__ import annotations

from app.schema import NodeType, RelType


# ==========================================================
# Canonical Node Mapping
# ==========================================================

NODE_MAP: dict[str, str | None] = {
    # People
    "Person": NodeType.PERSON.value,
    "Employee": NodeType.PERSON.value,
    "Staff": NodeType.PERSON.value,
    "Staff_Member": NodeType.PERSON.value,
    "Manager": NodeType.PERSON.value,
    # Departments
    "Department": NodeType.DEPARTMENT.value,
    "Dept": NodeType.DEPARTMENT.value,
    "Team": NodeType.DEPARTMENT.value,
    # Vendors / organizations
    "Vendor": NodeType.VENDOR.value,
    "Company": NodeType.VENDOR.value,
    "Organization": NodeType.VENDOR.value,
    "Organisation": NodeType.VENDOR.value,
    # Contracts
    "Contract": NodeType.CONTRACT.value,
    "Agreement": NodeType.CONTRACT.value,
    # Projects
    "Project": NodeType.PROJECT.value,
    # Transactions
    "Transaction": NodeType.TRANSACTION.value,
    "Payment": NodeType.TRANSACTION.value,
    # Keep Invoice as its own node
    "Invoice": NodeType.INVOICE.value,
    # Documents
    "Document": NodeType.DOCUMENT.value,
    "Email": NodeType.DOCUMENT.value,
    "Memo": NodeType.DOCUMENT.value,
    "Meeting Notes": NodeType.DOCUMENT.value,
    "Report": NodeType.DOCUMENT.value,
    # Risks
    "Risk": NodeType.RISK.value,
    "Incident": NodeType.RISK.value,
    # Services
    "Service": NodeType.SERVICE.value,
    # Attribute-like nodes — drop
    "Amount": None,
    "Budget": None,
    "Budget_Code": None,
    "Currency": None,
    "Date": None,
    "Role": None,
    "Skill": None,
    "Location": None,
}


# ==========================================================
# Canonical Relationship Mapping
# ==========================================================

REL_MAP: dict[str, str | None] = {
    # Organization structure
    "WORKS_FOR": RelType.WORKS_IN.value,
    "WORKS_IN": RelType.WORKS_IN.value,
    "REPORTS_TO": RelType.REPORTS_TO.value,
    "ASSIGNED_TO": RelType.ASSIGNED_TO.value,
    "RESPONSIBLE_FOR": RelType.ASSIGNED_TO.value,
    # Financial workflow
    "APPROVED": RelType.APPROVED.value,
    "PAID": RelType.PAID_TO.value,
    "PAID_TO": RelType.PAID_TO.value,
    "HAS_INVOICE": RelType.HAS_INVOICE.value,
    # Risk & services
    "HAS_RISK": RelType.HAS_RISK.value,
    "PROVIDED_BY": RelType.PROVIDED_BY.value,
    # Communication & documents
    "COMMUNICATED_WITH": RelType.COMMUNICATED_WITH.value,
    "MENTIONS": RelType.MENTIONS.value,
    # Ownership
    "OWNS": RelType.OWNS.value,
    "RELATIVE_OF": RelType.RELATIVE_OF.value,
    # Generic fallback
    "RELATED_TO": RelType.RELATED_TO.value,
    # Legacy relationships — drop
    "HAS_ROLE": None,
    "FOR_DEPARTMENT": None,
    "FINALIZED_AGREEMENT_WITH": None,
}


def map_node_type(raw: str) -> str | None:
    """Return the canonical node type or None if it should be dropped."""

    if raw in NODE_MAP:
        return NODE_MAP[raw]

    if raw in {node.value for node in NodeType}:
        return raw

    return None


def map_rel_type(raw: str) -> str | None:
    """Return the canonical relationship type or None if it should be dropped."""

    if raw in REL_MAP:
        return REL_MAP[raw]

    if raw in {rel.value for rel in RelType}:
        return raw

    return None
