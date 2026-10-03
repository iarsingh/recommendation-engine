from fastapi import FastAPI, HTTPException
from recs.recommend import CATALOG, recommend

app = FastAPI()

@app.post("/recommend")
def post_recommend(body: dict):
    if body["item"] not in CATALOG:
        raise HTTPException(status_code=422, detail="Unknown catalog item.")
    return recommend(body["item"])
