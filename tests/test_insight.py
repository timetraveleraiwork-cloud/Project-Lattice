# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pprint import pprint
from app.insights.centrality import get_centrality_insights

for insight in get_centrality_insights():
    pprint(insight.model_dump())

    print("-" * 80)
