from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_graph_question():
    response = client.post(
        "/ask_hybrid",
        json={"question": "What is the reporting chain above Priya Nair?"},
    )

    assert response.status_code == 200

    assert response.json()["answer"] != "INSUFFICIENT_EVIDENCE"
