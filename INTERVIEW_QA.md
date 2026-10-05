# recommendation-engine — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does recommendation-engine address, and what can you demonstrate?

recommendation engine repository.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/recs/main.py`](src/recs/main.py): Implementation or supporting configuration.
- [`src/recs/recommend.py`](src/recs/recommend.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/recs/__init__.py`](src/recs/__init__.py): Implementation or supporting configuration.
- [`tests/test_recommend.py`](tests/test_recommend.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `for_user` and explain the decision it makes?

The main walkthrough here is `for_user(user, k=3)` in [`src/recs/recommend.py`](src/recs/recommend.py#L84).

```python
def for_user(user, k=3):
    if not isinstance(k, int) or not 1 <= k <= len(CATALOG):
        raise RecError(f"k must be from 1 to {len(CATALOG)}")
    rated = RATINGS.get(user, {})
    if not rated:
        return {"user": user, "strategy": "popular", "recommendations": popular(k=k)}
    ranked = []
    for candidate in CATALOG:
        if candidate in rated:
            continue
        sims = {item: item_similarity(candidate, item) for item in rated}
        positive = {item: sim for item, sim in sims.items() if sim > 0}
        if not positive:
            continue
        support = sum(positive.values())
        predicted = sum(sim * rated[item] for item, sim in positive.items()) / support
        liked = {item: sim for item, sim in positive.items() if rated[item] >= LIKED}
        because = max(liked, key=lambda item: (liked[item], item)) if liked else None
        ranked.append({"item": candidate, "predicted": round(predicted, 4), "support": round(support, 4), "because": because})
    ranked.sort(key=lambda row: (-row["predicted"], -row["support"], row["item"]))
```

This is an excerpt; follow the source link for the rest of the branches.

The implementation calls `RATINGS.get`, `RecError`, `isinstance`, `item_similarity`, `len`, `max`, `popular`, `positive.items`, `positive.values`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `recommend` have?

`recommend(item)` is defined in [`src/recs/recommend.py`](src/recs/recommend.py#L40).

Its return expressions include:

- `{'item': item, 'recommendations': ranked}`

It uses `CATALOG.items`, `RecError`, `cosine`, `ranked.append`, `ranked.sort`, `round`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/recs/main.py`](src/recs/main.py#L12).
- `RecError(f'unknown catalog item: {item}')` in [`src/recs/recommend.py`](src/recs/recommend.py#L42).
- `RecError('user must be a short identifier')` in [`src/recs/recommend.py`](src/recs/recommend.py#L63).
- `RecError(f'unknown catalog item: {item}')` in [`src/recs/recommend.py`](src/recs/recommend.py#L65).
- `RecError('rating must be an integer from 1 to 5')` in [`src/recs/recommend.py`](src/recs/recommend.py#L67).
- `RecError(f'k must be from 1 to {len(CATALOG)}')` in [`src/recs/recommend.py`](src/recs/recommend.py#L86).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_recommend.py`](tests/test_recommend.py#L17) contains `test_nearest_item`:

```python
def test_nearest_item():
    payload = client.post("/recommend", json={"item": "notebook"}).json()
    assert payload["recommendations"][0]["item"] == "pipeline"
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/recs/main.py`](src/recs/main.py#L16).
- `GET /catalog` → `catalog` in [`src/recs/main.py`](src/recs/main.py#L21).
- `POST /recommend` → `post_recommend` in [`src/recs/main.py`](src/recs/main.py#L26).
- `GET /users/{user}/recommendations` → `user_recommendations` in [`src/recs/main.py`](src/recs/main.py#L31).
- `POST /ratings` → `post_rating` in [`src/recs/main.py`](src/recs/main.py#L36).
- `GET /popular` → `get_popular` in [`src/recs/main.py`](src/recs/main.py#L41).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `CATALOG`, `SEED_RATINGS` in [`src/recs/recommend.py`](src/recs/recommend.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `for_user`?

In [`src/recs/recommend.py`](src/recs/recommend.py#L84), `for_user(user, k=3)` receives the inputs. The function computes these intermediate values:

- `rated = RATINGS.get(user, {})`
- `ranked = []`

Its result is defined by:

- `{'user': user, 'strategy': 'item_based', 'recommendations': ranked[:k]}`
- `{'user': user, 'strategy': 'popular', 'recommendations': popular(k=k)}`
- `{'user': user, 'strategy': 'popular', 'recommendations': popular(exclude=rated, k=k)}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/recs/recommend.py`](src/recs/recommend.py#L84) branches on:

- `not isinstance(k, int) or not 1 <= k <= len(CATALOG)`
- `not rated`
- `not ranked`
- `candidate in rated`
- `not positive`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
