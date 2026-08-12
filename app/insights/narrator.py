import json

from app.insights.models import Insight, NarratedReport
from app.llm import call_model


def _build_prompt(insights: list[Insight]) -> str:
    evidence = [insight.model_dump(mode="json") for insight in insights]

    return f"""
You are the intelligence analyst for Project Lattice.

Create a concise business intelligence report from the
graph-derived insights below.

IMPORTANT RULES:
- Use only the evidence provided.
- Do not invent facts, entities, relationships, or numbers.
- Do not claim causation when the evidence only shows correlation
  or graph connectivity.
- Clearly distinguish graph evidence from interpretation.
- Prioritize the most significant findings.
- Explain why each finding matters.
- Recommendations must be directly connected to the evidence.
- Do not mention that you are an AI.
- Do not mention the internal implementation unless necessary.

GRAPH-DERIVED INSIGHTS:

{json.dumps(evidence, indent=2)}

Return the report using the requested schema.
"""


def narrate_insights(insights: list[Insight]) -> NarratedReport:
    if not insights:
        raise ValueError("No insights were provided.")

    prompt = _build_prompt(insights)

    return call_model(
        prompt,
        NarratedReport,
    )
