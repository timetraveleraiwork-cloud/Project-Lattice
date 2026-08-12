from typing import Any

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    claim: str
    nodes: list[str] = Field(default_factory=list)
    source_document: str


class RawFinding(BaseModel):
    """
    Evidence produced by the graph analysis layer before LLM narration.
    """

    title: str
    category: str
    raw_data: dict[str, Any] = Field(default_factory=dict)

    nodes: list[str] = Field(default_factory=list)
    paths: list[str] = Field(default_factory=list)
    source_documents: list[str] = Field(default_factory=list)


class NarratedFinding(BaseModel):
    """
    Analyst-style finding produced from one evidence packet.
    """

    title: str
    severity_1to5: int
    plain_language_summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    suggested_verification_query: str

    @property
    def cited_sources(self) -> list[str]:
        return [item.source_document for item in self.evidence]


class InsightsResponse(BaseModel):
    findings: list[NarratedFinding] = Field(default_factory=list)
