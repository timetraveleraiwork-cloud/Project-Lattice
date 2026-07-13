from __future__ import annotations

from app.schema import NodeType, RelType

# Maps old / drifted node labels to the frozen schema.
# Returning None means "drop this node".

NODE_MAP: dict[str, str | None] = {
    # Organizations
    "Company": NodeType.VENDOR.value,
    "Organization": NodeType.VENDOR.value,
    "Organisation": NodeType.VENDOR.value,
    "Vendor": NodeType.VENDOR.value,
    # People
    "Employee": NodeType.PERSON.value,
    "Staff": NodeType.PERSON.value,
    "Staff_Member": NodeType.PERSON.value,
    "Manager": NodeType.PERSON.value,
    "Person": NodeType.PERSON.value,
    # Departments
    "Dept": NodeType.DEPARTMENT.value,
    "Team": NodeType.DEPARTMENT.value,
    "Department": NodeType.DEPARTMENT.value,
    # Contracts
    "Agreement": NodeType.CONTRACT.value,
    "Contract": NodeType.CONTRACT.value,
    # Transactions
    "Invoice": NodeType.TRANSACTION.value,
    "Payment": NodeType.TRANSACTION.value,
    "Transaction": NodeType.TRANSACTION.value,
    # Communications
    "Email": NodeType.COMMUNICATION.value,
    "Memo": NodeType.COMMUNICATION.value,
    "Meeting": NodeType.COMMUNICATION.value,
    "Communication": NodeType.COMMUNICATION.value,
    # Projects
    "Project": NodeType.PROJECT.value,
    # Incidents
    "Incident": NodeType.INCIDENT.value,
    # Attribute-like labels → drop
    "Amount": None,
    "Budget": None,
    "Budget_Code": None,
    "Currency": None,
    "Date": None,
    "Role": None,
    "Skill": None,
    "Location": None,
    "Document": None,
}


REL_MAP: dict[str, str | None] = {
    "WORKS_IN": RelType.WORKS_FOR.value,
    "WORKS_FOR": RelType.WORKS_FOR.value,
    "REPORTS_TO": RelType.REPORTS_TO.value,
    "HAS_ROLE": RelType.RELATED_TO.value,
    "APPROVED": RelType.APPROVED.value,
    "PAID_TO": RelType.PAID.value,
    "PAID": RelType.PAID.value,
    "FOR_DEPARTMENT": RelType.RELATED_TO.value,
    "PROVIDED_BY": RelType.RELATED_TO.value,
    "FINALIZED_AGREEMENT_WITH": RelType.SIGNED.value,
    "RESPONSIBLE_FOR": RelType.ASSIGNED_TO.value,
    "COMMUNICATED_WITH": RelType.COMMUNICATED_WITH.value,
    "ASSIGNED_TO": RelType.ASSIGNED_TO.value,
    "RELATED_TO": RelType.RELATED_TO.value,
    # Relationships we don't want to preserve
    "HAS_AMOUNT": None,
    "HAS_INVOICE": None,
    "HAS_RISK": None,
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
