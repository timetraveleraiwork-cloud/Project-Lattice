DOCUMENT_TYPES = (
    ["Org Chart Notes"] * 4
    + ["Employee Bio"] * 6
    + ["Vendor Agreement"] * 6
    + ["Project Memo"] * 6
    + ["Email Thread"] * 8
    + ["Expense Report"] * 7
    + ["Transaction Log"] * 5
    + ["Incident Report"] * 3
)

EMAIL_STYLES = [
    "formal",
    "quick_reply",
    "forwarded",
    "approval_request",
    "status_update",
    "meeting_followup",
]

PATTERNS = {
    "vendor_pair": "TechNova Solutions and DataWeave Analytics appear together.",
    "small_reimbursement": "Expense amount between ₹9,000 and ₹9,999.",
    "late_night_access": "Rahul Sharma and Ankit Gupta work between 2–4 AM.",
    "project_overlap": "Priya Nair, Arjun Verma and Meera Iyer collaborate.",
}
