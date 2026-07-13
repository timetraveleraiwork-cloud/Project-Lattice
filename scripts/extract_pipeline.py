# ruff: noqa: E402
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.llm import call_model
from app.schemas import ExtractionResult

# ==========================
# Configuration
# ==========================

DOCUMENTS_DIR = ROOT / "data" / "corpus" / "docs"
OUTPUT_FILE = ROOT / "data" / "staging" / "raw_extractions.json"

BATCH_SIZE = 20

PROMPT_TEMPLATE = """
You are an expert information extraction system building a
high-quality business knowledge graph.

Accuracy is more important than extracting many entities.

Your task is to extract entities and relationships from the document.

Return ONLY valid JSON matching the provided schema.

=========================================================
ALLOWED NODE TYPES
=========================================================

- Person
- Department
- Vendor
- Project
- Document
- Transaction
- Invoice
- Risk
- Service
- Contract

DO NOT invent any new node type.

If an entity does not fit perfectly, choose the closest allowed type.

Store extra information (dates, amounts, currencies, titles,
document type, invoice number, etc.) inside entity properties,
NOT as separate entities.

=========================================================
ENTITY COVERAGE
=========================================================

Extract ALL significant entities.

This includes:
- People
- Departments
- Vendors
- Projects
- Contracts
- Services
- Transactions
- Invoices
- Risks
- Documents

Do not skip an entity simply because it appears only once.

Every extracted relationship must reference extracted entities.

=========================================================
ALLOWED RELATIONSHIP TYPES
=========================================================

- WORKS_IN
- REPORTS_TO
- ASSIGNED_TO
- RESPONSIBLE_FOR
- APPROVED
- PAID_TO
- HAS_INVOICE
- HAS_RISK
- PROVIDED_BY
- COMMUNICATED_WITH
- MENTIONS
- OWNS
- RELATIVE_OF
- RELATED_TO

Never invent a new relationship type.

Use RELATED_TO only as a last resort.

Before using RELATED_TO, consider whether one of the following is more appropriate:

- WORKS_IN
- ASSIGNED_TO
- RESPONSIBLE_FOR
- PROVIDED_BY
- PAID_TO
- APPROVED
- HAS_INVOICE
- HAS_RISK
- COMMUNICATED_WITH
- MENTIONS

=========================================================
RELATIONSHIP DIRECTIONS
=========================================================

WORKS_IN:
Person -> Department

REPORTS_TO:
Person -> Person

ASSIGNED_TO:
Person -> Project

RESPONSIBLE_FOR:
Person/Department -> Project/Risk

APPROVED:
Person -> Transaction

PAID_TO:
Transaction -> Vendor

HAS_INVOICE:
Transaction -> Invoice

HAS_RISK:
Project/Department -> Risk

PROVIDED_BY:
Service -> Vendor

COMMUNICATED_WITH:
Person -> Person

MENTIONS:
Document -> Any Entity

OWNS:
Person -> Vendor

RELATIVE_OF:
Person -> Person

RELATED_TO:
Any -> Any

=========================================================
RELATIONSHIP QUALITY
=========================================================

Only extract relationships that are explicitly stated or can be
directly inferred from the document.

Do NOT guess.

If two entities merely appear in the same document, do NOT connect
them unless the document clearly describes their relationship.

=========================================================
IMPORTANT RULES
=========================================================

- Return ONLY JSON.
- Never explain your reasoning.
- Never invent node labels.
- Never invent relationship types.
- Extract every important entity.
- Extract every meaningful relationship.
- Do not create duplicate entities. If the same real-world entity appears multiple times in the document, extract it only once.
- Use the exact spelling from the document.
- If unsure, use RELATED_TO rather than creating a new relationship.
- Dates, amounts, currencies, IDs, and document metadata belong in properties.
- Use RELATED_TO only as a last resort. Always prefer one of the specific relationship types whenever possible.
- Preserve the original spelling exactly as written in the document.
- Do not abbreviate names.
- Do not normalize names.
- Do not invent names.
- Every extracted entity and relationship belongs to the current document. Do not invent references to other documents.

Document:

{document}
"""


def load_existing():
    """
    Load previous extractions if they exist.
    """

    if not OUTPUT_FILE.exists():
        return []

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return []


def save_results(results):
    """
    Save all extractions.
    """

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)


def main():
    existing = load_existing()

    processed = {doc["document"] for doc in existing}

    all_documents = sorted(DOCUMENTS_DIR.glob("*.txt"))

    remaining = [doc for doc in all_documents if doc.name not in processed]

    if not remaining:
        print("All documents already processed.")
        return

    batch = remaining[:BATCH_SIZE]

    print(f"\nFound {len(all_documents)} documents")
    print(f"Already processed: {len(processed)}")
    print(f"Processing this batch: {len(batch)}\n")

    results = existing

    for i, file in enumerate(batch, start=1):
        print(f"[{i}/{len(batch)}] Processing {file.name}")

        try:
            text = file.read_text(encoding="utf-8")

            prompt = PROMPT_TEMPLATE.format(document=text)

            extraction = call_model(
                prompt,
                ExtractionResult,
            )
            entities = []
            for entity in extraction.entities:
                data = entity.model_dump()
                data["source_document"] = file.name
                entities.append(data)

            relationships = []
            for relationship in extraction.relationships:
                data = relationship.model_dump()
                data["source_document"] = file.name
                relationships.append(data)

            results.append(
                {
                    "document": file.name,
                    "entities": entities,
                    "relationships": relationships,
                }
            )

            save_results(results)

            print("   ✓ Success")

        except Exception as e:
            print(f"   ✗ Failed: {e}")

    print("\n==============================")
    print("Extraction Complete")
    print("==============================")
    print(f"Total documents processed: {len(results)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
