from app.llm import call_model
from app.schemas import CypherQuery

SCHEMA = """
Node Labels:
Person
Department
Vendor
Transaction
Project
Risk
Invoice
Agreement
Service
Role
Amount
Document

Relationship Types:
WORKS_IN
REPORTS_TO
HAS_ROLE
APPROVED
PAID_TO
HAS_AMOUNT
FOR_DEPARTMENT
HAS_INVOICE
PROVIDED_BY
FINALIZED_AGREEMENT_WITH
HAS_RISK
RESPONSIBLE_FOR

Rules:
- Generate ONLY a read-only Cypher query.
- Never use CREATE, MERGE, DELETE, SET, REMOVE, DROP.
- Always return valid Cypher.
- Add LIMIT 50 unless the user explicitly requests more.
"""


def generate_cypher(question: str) -> str:
    prompt = f"""
You are an expert Neo4j Cypher generator.

Database Schema:

{SCHEMA}

Return ONLY JSON in this format:

{{
    "query": "<cypher query>"
}}

Question:
{question}
"""

    response = call_model(prompt, CypherQuery)

    return response.query


def correct_cypher(
    question: str,
    failed_query: str,
    error_message: str,
) -> str:
    prompt = f"""
You are an expert Neo4j Cypher developer.

The previous query failed.

Database Schema:

{SCHEMA}

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

    response = call_model(prompt, CypherQuery)

    return response.query
