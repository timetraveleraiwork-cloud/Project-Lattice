# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_graph_traversal():
    response = client.post(
        "/ask_hybrid",
        json={"question": "What has Priya Nair approved?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] != "INSUFFICIENT_EVIDENCE"

    assert len(data["citations"]) > 0

    assert len(data["graph_paths"]) > 0


def test_vector_retrieval():
    response = client.post(
        "/ask_hybrid",
        json={"question": "Were there any concerns about supplier reliability?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] != "INSUFFICIENT_EVIDENCE"

    assert len(data["citations"]) > 0


def test_honest_refusal():
    response = client.post(
        "/ask_hybrid",
        json={"question": "What is Meridian Group's stock price?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "INSUFFICIENT_EVIDENCE"

    assert data["citations"] == []

    assert data["graph_paths"] == []

    assert data["anchors_used"] == []
