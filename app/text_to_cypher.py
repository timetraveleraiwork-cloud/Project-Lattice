from __future__ import annotations

from app.llm import call_model
from app.schemas import CypherQuery

DATABASE_SCHEMA = """
Node Labels:
- Person
- Department
- Vendor
- Project
- Contract
- Transaction
- Invoice
- Document
- Risk
- Service

Relationship Types:

- WORKS_IN           : (Person) -> (Department)
- REPORTS_TO         : (Person) -> (Person)
- ASSIGNED_TO        : (Person) -> (Project)
- RESPONSIBLE_FOR    : (Person) -> (Project)
- APPROVED           : (Person) -> (Transaction | Contract | Document | Invoice)
- PAID_TO            : (Transaction) -> (Vendor)
- HAS_INVOICE        : (Transaction) -> (Invoice)
- HAS_RISK           : (Project | Department) -> (Risk)
- PROVIDED_BY        : (Service) -> (Vendor)
- COMMUNICATED_WITH  : (Person | Department) -> (Person | Vendor | Department)
- MENTIONS           : (Document) -> (Any)
- RELATED_TO         : Generic fallback when no specific relationship exists.

Rules:
- Generate ONLY read-only Cypher.
- Never use CREATE, MERGE, DELETE, SET, REMOVE or DROP.
- Use ONLY the node labels and relationship types listed above.
- Never invent labels or relationships.
- If multiple relationship types are possible, prefer the most specific one over RELATED_TO.
- Add LIMIT 50 unless the user explicitly requests more.
"""


def _build_prompt(task: str) -> str:
    """Build a prompt using the current database schema."""

    return f"""
Database Schema:

{DATABASE_SCHEMA}

{task}
"""


def generate_cypher(question: str) -> str:
    """Generate a read-only Cypher query from a natural language question."""

    prompt = _build_prompt(
        f"""
You are an expert Neo4j Cypher generator.

Return ONLY JSON in this format:

{{
    "query": "<cypher query>"
}}

Question:
{question}
"""
    )

    response = call_model(prompt, CypherQuery)

    return response.query


def correct_cypher(
    question: str,
    failed_query: str,
    error_message: str,
) -> str:
    """Correct a Cypher query that failed execution."""

    prompt = _build_prompt(
        f"""
You are an expert Neo4j Cypher developer.

The previous query failed.

Original Question:
{question}

Failed Query:
{failed_query}

Neo4j Error:
{error_message}

Your task:
- Fix the query.
- Keep it READ ONLY.
- Never use CREATE, MERGE, DELETE, SET, REMOVE, DROP.
- Use only labels and relationships from the schema.
- Return ONLY JSON:

{{
    "query": "<corrected cypher query>"
}}
"""
    )

    response = call_model(prompt, CypherQuery)

    return response.query
