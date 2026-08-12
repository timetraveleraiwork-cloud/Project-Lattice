from app.insights.models import RawFinding
from app.neo4j import run_query


VENDOR_CONCENTRATION_QUERY = """
MATCH (t:Transaction)-[:PAID]->(v:Vendor)
OPTIONAL MATCH (d:Department)-[:RELATED_TO|APPROVED*..2]-(t)
WITH
    v,
    count(DISTINCT t) AS transactions,
    count(DISTINCT d) AS departments,
    collect(DISTINCT t.name)[..10] AS sample_transactions

WITH
    v,
    transactions,
    departments,
    sample_transactions,
    sum(transactions) OVER () AS total_transactions

RETURN
    v.name AS vendor,
    transactions,
    departments,
    CASE
        WHEN total_transactions = 0 THEN 0.0
        ELSE toFloat(transactions) / total_transactions
    END AS transaction_share,
    v.source_document AS source_document,
    sample_transactions
ORDER BY transaction_share DESC
LIMIT 10
"""


def _build_vendor_concentration_findings(
    rows: list[dict],
) -> list[RawFinding]:
    if not rows:
        return []

    source_documents = sorted(
        {row["source_document"] for row in rows if row.get("source_document")}
    )

    top_vendors = [
        {
            "vendor": row["vendor"],
            "transactions": row["transactions"],
            "departments": row["departments"],
            "transaction_share": row["transaction_share"],
            "sample_transactions": row["sample_transactions"],
        }
        for row in rows
    ]

    top_vendor = rows[0]

    return [
        RawFinding(
            title="Vendor Concentration Risk",
            category="vendor",
            nodes=[row["vendor"] for row in rows if row.get("vendor")],
            source_documents=source_documents,
            raw_data={
                "analysis": "vendor_concentration",
                "vendors_analyzed": len(rows),
                "top_vendor": {
                    "vendor": top_vendor["vendor"],
                    "transactions": top_vendor["transactions"],
                    "departments": top_vendor["departments"],
                    "transaction_share": top_vendor["transaction_share"],
                },
                "top_vendors": top_vendors,
            },
        )
    ]


def get_vendor_concentration_findings() -> list[RawFinding]:
    rows = run_query(VENDOR_CONCENTRATION_QUERY)

    return _build_vendor_concentration_findings(rows)
