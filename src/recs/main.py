from fastapi import FastAPI, HTTPException

from recs.recommend import CATALOG, RecError, for_user, popular, rate, recommend

app = FastAPI()


def guarded(call, *args):
    try:
        return call(*args)
    except RecError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/catalog")
def catalog():
    return {"items": sorted(CATALOG)}


@app.post("/recommend")
def post_recommend(body: dict):
    return guarded(recommend, body.get("item"))


@app.get("/users/{user}/recommendations")
def user_recommendations(user: str, k: int = 3):
    return guarded(for_user, user, k)


@app.post("/ratings")
def post_rating(body: dict):
    return guarded(rate, body.get("user"), body.get("item"), body.get("rating"))


@app.get("/popular")
def get_popular(k: int = 3):
    return {"recommendations": popular(k=max(1, min(k, len(CATALOG))))}
