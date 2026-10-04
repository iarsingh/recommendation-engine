import pytest
from fastapi.testclient import TestClient

from recs.main import app
from recs.recommend import item_similarity, reset

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_ratings():
    reset()
    yield
    reset()


def test_nearest_item():
    payload = client.post("/recommend", json={"item": "notebook"}).json()
    assert payload["recommendations"][0]["item"] == "pipeline"


def test_unknown_item_is_refused():
    assert client.post("/recommend", json={"item": "spaceship"}).status_code == 422


def test_user_gets_unrated_items_only():
    payload = client.get("/users/ada/recommendations").json()
    items = [row["item"] for row in payload["recommendations"]]
    assert payload["strategy"] == "item_based"
    assert not {"notebook", "pipeline", "cluster"} & set(items)
    assert items[0] == "dashboard"


def test_explanation_names_the_closest_liked_item():
    top = client.get("/users/ada/recommendations").json()["recommendations"][0]
    assert top["because"] == "pipeline"
    assert top["predicted"] == pytest.approx(4.0, abs=0.05)


def test_item_similarity_is_symmetric():
    assert item_similarity("invoice", "cluster") == pytest.approx(item_similarity("cluster", "invoice"))
    assert item_similarity("invoice", "cluster") > item_similarity("invoice", "notebook")


def test_new_user_gets_popular_items():
    payload = client.get("/users/zed/recommendations?k=2").json()
    assert payload["strategy"] == "popular"
    assert payload["recommendations"][0]["item"] == "notebook"
    assert len(payload["recommendations"]) == 2


def test_rating_moves_a_user_out_of_cold_start():
    assert client.post("/ratings", json={"user": "zed", "item": "cluster", "rating": 5}).status_code == 200
    payload = client.get("/users/zed/recommendations").json()
    assert payload["strategy"] == "item_based"
    assert payload["recommendations"][0]["item"] == "invoice"


def test_bad_ratings_are_refused():
    assert client.post("/ratings", json={"user": "zed", "item": "cluster", "rating": 6}).status_code == 422
    assert client.post("/ratings", json={"user": "zed", "item": "spaceship", "rating": 3}).status_code == 422
    assert client.post("/ratings", json={"user": "bad user!", "item": "cluster", "rating": 3}).status_code == 422
    assert client.get("/users/ada/recommendations?k=0").status_code == 422
