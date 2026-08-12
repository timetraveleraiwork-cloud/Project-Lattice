# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pprint import pprint

from app.insights.centrality import get_centrality_insights
from app.insights.communities import get_community_insights
from app.insights.narrator import narrate_insights
from app.insights.risk import get_vendor_risk_insights


insights = []

insights.extend(get_centrality_insights())
insights.extend(get_community_insights())
insights.extend(get_vendor_risk_insights())

report = narrate_insights(insights)

pprint(report.model_dump())
