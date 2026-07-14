# ruff: noqa: E402
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.llm import call_model
from app.schemas import GeneratedDocument
from docs.corpus_plan import DOCUMENT_TYPES, EMAIL_STYLES, PATTERNS

# Project root
ROOT = Path(__file__).resolve().parents[2]

CAST_FILE = ROOT / "Week_2" / "data" / "corpus" / "cast_list.md"
OUTPUT_DIR = ROOT / "Week_2" / "data" / "corpus" / "docs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

cast = CAST_FILE.read_text(encoding="utf-8")

# Exact distribution of documents
document_types = (
    ["Org Chart Notes"] * 4
    + ["Employee Bio"] * 6
    + ["Vendor Agreement"] * 6
    + ["Project Memo"] * 6
    + ["Email Thread"] * 8
    + ["Expense Report"] * 7
    + ["Transaction Log"] * 5
    + ["Incident Report"] * 3
)

document_types = list(DOCUMENT_TYPES)
random.seed(42)
random.shuffle(document_types)


START = 33
END = 45

for i, doc_type in enumerate(document_types[START - 1 : END], start=START):
    style = ""
    if doc_type == "Email Thread":
        style = random.choice(EMAIL_STYLES)

    patterns = PATTERNS.get(doc_type, [])

    prompt = f"""
You are generating ONE realistic internal corporate document for a fictional company.

Company:
Lattice Dynamics Pvt. Ltd.

Use ONLY the following employees, vendors and departments.

{cast}

Document Type:
{doc_type}

Writing Style:
{style}

Requirements:

- Around 300–500 words
- Natural business writing
- Slightly messy formatting
- Different documents should have different writing styles
- Use ONLY employees from the cast list
- Never invent new employees
- Use ONLY vendors from the cast list
- Never invent new vendors
- Include realistic dates
- Include departments where appropriate
- Use realistic corporate abbreviations (FYI, ETA, EOD, ASAP, PFA)
- Include occasional formatting inconsistencies
- Some documents may contain bullet lists or tables
- Some emails can be short while others can be long
- Mention attachments naturally when appropriate
- Never mention AI

Specific formatting:

• Email Thread
  - Include From, To, CC, Subject, Date
  - Multiple replies
  - Different writing styles

• Expense Report
  - Expense ID
  - Employee
  - Vendor
  - Amount
  - Approved By
  - Date

• Vendor Agreement
  - Contract ID
  - Effective Date
  - Renewal Date
  - Signatories

• Transaction Log
  - Transaction ID
  - Invoice Number
  - Amount
  - Status

• Project Memo
  - Project Name
  - Team Members
  - Risks
  - Deadlines
  - Budget

• Incident Report
  - Incident ID
  - Time
  - Root Cause
  - Resolution

Naturally include these hidden patterns if appropriate:

{patterns}

These patterns must appear naturally and should never be explicitly described as patterns.

Return ONLY valid JSON in this format:

{{
    "title": "...",
    "content": "..."
}}
"""

    doc = call_model(prompt, GeneratedDocument)

    filename = f"{i:03}_{doc_type.lower().replace(' ', '_')}.txt"

    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        f.write(doc.title)
        f.write("\n\n")
        f.write(doc.content)

    print(f"Generated {filename}")

print(f"\nFinished generating {len(document_types)} documents.")
