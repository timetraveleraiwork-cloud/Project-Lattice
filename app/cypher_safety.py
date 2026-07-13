from __future__ import annotations

import re

FORBIDDEN_KEYWORDS = {
    "CREATE",
    "MERGE",
    "DELETE",
    "SET",
    "REMOVE",
    "DROP",
    "CALL",
    "LOAD CSV",
    "FOREACH",
    "DETACH",
    "DBMS",
    "APOC",
}

LIMIT_PATTERN = re.compile(r"\bLIMIT\s+\d+\b", re.IGNORECASE)


def validate_query(query: str) -> str:
    """
    Validate that a generated Cypher query is safe to execute.

    Rules:
    - Read-only queries only
    - No schema modifications
    - Must contain RETURN
    - Must contain LIMIT
    """

    query_upper = query.upper()

    _validate_forbidden_keywords(query_upper)
    _validate_return_clause(query_upper)
    _validate_limit_clause(query)

    return query


def _validate_forbidden_keywords(query: str) -> None:
    """Reject queries containing forbidden Cypher operations."""

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query:
            raise ValueError(f"Unsafe query detected. Forbidden keyword: {keyword}")


def _validate_return_clause(query: str) -> None:
    """Ensure the query returns data."""

    if "RETURN" not in query:
        raise ValueError("Query must contain a RETURN clause.")


def _validate_limit_clause(query: str) -> None:
    """Ensure the query contains a LIMIT clause."""

    if LIMIT_PATTERN.search(query) is None:
        raise ValueError("Query must contain a LIMIT clause.")
