# Recommendation Engine

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/recs/main.py`](src/recs/main.py) | HTTP handlers: `GET /healthz`, `GET /catalog`, `POST /recommend`, `GET /users/{user}/recommendations`, `POST /ratings` |
| [`src/recs/recommend.py`](src/recs/recommend.py) | Functions: `reset`, `cosine`, `recommend`, `item_vector`, `item_similarity`, `rate`, `popular` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/recs/__init__.py`](src/recs/__init__.py) | Implementation or supporting configuration |
| [`tests/test_recommend.py`](tests/test_recommend.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn recs.main:app --reload
```

<!-- project-guide:end -->

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
