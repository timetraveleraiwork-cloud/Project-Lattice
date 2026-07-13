from __future__ import annotations

from app.schema import NodeType, RelType

# Maps legacy or unexpected node labels to the frozen ontology.
# Returning None means "drop this node".

NODE_MAP: dict[str, str | None] = {
    # Vendors
    "Company": NodeType.VENDOR.value,
    "Organization": NodeType.VENDOR.value,
    "Organisation": NodeType.VENDOR.value,
    # People
    "Employee": NodeType.PERSON.value,
    "Staff": NodeType.PERSON.value,
    "Staff_Member": NodeType.PERSON.value,
    "Manager": NodeType.PERSON.value,
    # Departments
    "Dept": NodeType.DEPARTMENT.value,
    "Team": NodeType.DEPARTMENT.value,
    # Contracts
    "Agreement": NodeType.CONTRACT.value,
    # Transactions
    "Payment": NodeType.TRANSACTION.value,
    # Documents
    "Email": NodeType.DOCUMENT.value,
    "Memo": NodeType.DOCUMENT.value,
    "Meeting Notes": NodeType.DOCUMENT.value,
    "Report": NodeType.DOCUMENT.value,
    # Risks
    "Incident": NodeType.RISK.value,
    # Drop attribute-like nodes
    "Amount": None,
    "Budget": None,
    "Budget_Code": None,
    "Currency": None,
    "Date": None,
    "Role": None,
    "Skill": None,
    "Location": None,
}


REL_MAP: dict[str, str | None] = {
    "WORKS_FOR": RelType.WORKS_IN.value,
    "WORKS_IN": RelType.WORKS_IN.value,
    "REPORTS_TO": RelType.REPORTS_TO.value,
    "ASSIGNED_TO": RelType.ASSIGNED_TO.value,
    "RESPONSIBLE_FOR": RelType.RESPONSIBLE_FOR.value,
    "APPROVED": RelType.APPROVED.value,
    "PAID": RelType.PAID_TO.value,
    "PAID_TO": RelType.PAID_TO.value,
    "HAS_INVOICE": RelType.HAS_INVOICE.value,
    "HAS_RISK": RelType.HAS_RISK.value,
    "PROVIDED_BY": RelType.PROVIDED_BY.value,
    "COMMUNICATED_WITH": RelType.COMMUNICATED_WITH.value,
    "OWNS": RelType.OWNS.value,
    "RELATIVE_OF": RelType.RELATIVE_OF.value,
    "MENTIONS": RelType.MENTIONS.value,
    "RELATED_TO": RelType.RELATED_TO.value,
    # Legacy relationships
    "HAS_ROLE": None,
    "FOR_DEPARTMENT": None,
    "FINALIZED_AGREEMENT_WITH": None,
}


def map_node_type(raw: str) -> str | None:
    """Return the canonical node type or None if it should be dropped."""

    if raw in {node.value for node in NodeType}:
        return raw

    return NODE_MAP.get(raw)


def map_rel_type(raw: str) -> str | None:
    """Return the canonical relationship type or None if it should be dropped."""

    if raw in {rel.value for rel in RelType}:
        return raw

    return REL_MAP.get(raw)
