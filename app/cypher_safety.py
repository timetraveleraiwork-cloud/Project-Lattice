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
}


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

    # Block dangerous operations
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            raise ValueError(f"Unsafe query detected. Forbidden keyword: {keyword}")

    # Ensure it returns data
    if "RETURN" not in query_upper:
        raise ValueError("Query must contain RETURN.")

    # Require LIMIT somewhere in the query
    if re.search(r"\bLIMIT\s+\d+\b", query_upper) is None:
        raise ValueError("Query must contain a LIMIT clause.")

    return query
