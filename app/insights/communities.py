from app.insights.models import RawFinding
from app.neo4j import run_query


LOUVAIN_QUERY = """
CALL gds.louvain.stream("lattice_communities")
YIELD nodeId, communityId
WITH
    communityId,
    collect(gds.util.asNode(nodeId)) AS nodes

CALL (nodes) {
    UNWIND nodes AS node

    MATCH (node)-[r]-(other)
    WHERE other IN nodes
      AND elementId(node) < elementId(other)

    RETURN collect(DISTINCT {
        type: type(r),
        from: coalesce(node.name, elementId(node)),
        to: coalesce(other.name, elementId(other))
    }) AS relationships
}

RETURN
    communityId,
    size(nodes) AS size,
    [node IN nodes | {
        label: labels(node)[0],
        name: coalesce(node.name, elementId(node)),
        source_document: node.source_document
    }] AS entities,
    relationships
ORDER BY communityId
"""


def _build_community_findings(
    rows: list[dict],
) -> list[RawFinding]:
    findings: list[RawFinding] = []

    for row in rows:
        if row["size"] < 3:
            continue

        entities = row["entities"]

        label_counts: dict[str, int] = {}

        for entity in entities:
            label = entity["label"]
            label_counts[label] = label_counts.get(label, 0) + 1

        dominant_label = max(
            label_counts,
            key=label_counts.get,
        )

        source_documents = sorted(
            {
                entity["source_document"]
                for entity in entities
                if entity.get("source_document")
            }
        )

        findings.append(
            RawFinding(
                title=f"Community {row['communityId']}",
                category="community",
                nodes=[entity["name"] for entity in entities if entity.get("name")],
                source_documents=source_documents,
                raw_data={
                    "community_id": row["communityId"],
                    "size": row["size"],
                    "dominant_label": dominant_label,
                    "label_distribution": label_counts,
                    "entities": entities,
                    "relationships": row["relationships"],
                },
            )
        )

    return findings


def get_community_findings() -> list[RawFinding]:
    rows = run_query(LOUVAIN_QUERY)

    return _build_community_findings(rows)
