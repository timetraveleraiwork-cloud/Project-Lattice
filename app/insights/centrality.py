from app.insights.models import RawFinding
from app.neo4j import run_query


BETWEENNESS_QUERY = """
CALL gds.betweenness.stream("lattice")
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
WHERE node:Person
RETURN
    coalesce(node.name, elementId(node)) AS name,
    score,
    elementId(node) AS node_id,
    node.source_document AS source_document
ORDER BY score DESC
LIMIT 10
"""


PAGERANK_QUERY = """
CALL gds.pageRank.stream("lattice")
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS node, score
RETURN
    labels(node)[0] AS label,
    coalesce(node.name, elementId(node)) AS name,
    score,
    elementId(node) AS node_id,
    node.source_document AS source_document
ORDER BY score DESC
LIMIT 10
"""


def _source_documents(rows: list[dict]) -> list[str]:
    return sorted(
        {row["source_document"] for row in rows if row.get("source_document")}
    )


def get_centrality_findings() -> list[RawFinding]:
    """
    Run centrality algorithms and return raw findings.

    Betweenness is used as evidence for the key-person
    dependency pattern.

    PageRank is retained as supplementary structural evidence.
    """

    betweenness = run_query(BETWEENNESS_QUERY)
    pagerank = run_query(PAGERANK_QUERY)

    findings: list[RawFinding] = []

    if betweenness:
        findings.append(
            RawFinding(
                title="Key Bridge Entities",
                category="centrality",
                nodes=[row["name"] for row in betweenness if row.get("name")],
                source_documents=_source_documents(betweenness),
                raw_data={
                    "algorithm": "betweenness",
                    "top_entities": betweenness,
                },
            )
        )

    if pagerank:
        findings.append(
            RawFinding(
                title="Most Influential Entities",
                category="centrality",
                nodes=[row["name"] for row in pagerank if row.get("name")],
                source_documents=_source_documents(pagerank),
                raw_data={
                    "algorithm": "pagerank",
                    "top_entities": pagerank,
                },
            )
        )

    return findings
