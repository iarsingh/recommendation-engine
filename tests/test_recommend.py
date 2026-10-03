from fastapi.testclient import TestClient
from recs.main import app

def test_nearest_item():
    payload = TestClient(app).post("/recommend", json={"item": "notebook"}).json()
    assert payload["recommendations"][0]["item"] == "pipeline"
