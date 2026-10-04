# Recommendation Engine

Level: 3 — Machine learning

Skills: Python, cosine similarity, item-based collaborative filtering, cold start

Two recommenders over a five-item catalog:

- Content-based: `POST /recommend` with an item returns the other items ranked by cosine similarity on fixed feature vectors.
- Item-based collaborative filtering: `GET /users/{user}/recommendations` predicts a rating for each item the user has not rated. The prediction is a weighted average of the user's own ratings, weighted by how similar each rated item is to the candidate across all users' ratings.

```bash
pip install -r requirements.txt
pytest -q
PYTHONPATH=src uvicorn recs.main:app --reload
```

| Method and path | Returns |
| --- | --- |
| `GET /catalog` | Item names |
| `POST /recommend` | Content-based neighbours of one item |
| `GET /users/{user}/recommendations?k=3` | Unrated items with `predicted`, `support`, and `because` |
| `POST /ratings` | Adds or replaces a rating from 1 to 5 |
| `GET /popular?k=3` | Items with the most ratings, then the highest mean |

## Behaviour worth knowing

- Items the user already rated are never recommended back.
- `because` names the most similar item the user rated 4 or higher, so a recommendation can be explained in one sentence.
- A user with no ratings gets `strategy: popular`. After one rating they move to `item_based`.
- Ties on predicted rating are broken by `support`, the total similarity behind the prediction, so a guess backed by one weak neighbour ranks below one backed by a strong neighbour.
- Ratings live in memory. Restarting the service returns to the seed data.
