# ruff: noqa: E402
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.llm import call_model
from app.schemas import ExtractionResult

# ==========================
# Configuration
# ==========================

DOCUMENTS_DIR = ROOT / "Week_2" / "data" / "corpus" / "docs"
OUTPUT_FILE = ROOT / "Week3" / "Staging" / "raw_extractions.json"

BATCH_SIZE = 20

PROMPT_TEMPLATE = """
You are an expert information extraction system.

Extract all entities and relationships from the document.

Rules:

- Return ONLY valid JSON.
- Do not explain anything.
- Every entity must contain:
    - type
    - name

- Every relationship must contain:
    - source
    - target
    - relation

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

            results.append(
                {
                    "document": file.name,
                    "entities": [entity.model_dump() for entity in extraction.entities],
                    "relationships": [
                        relation.model_dump() for relation in extraction.relationships
                    ],
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
