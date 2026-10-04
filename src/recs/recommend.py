import copy

CATALOG = {
    "notebook": (1, 1, 0),
    "pipeline": (1, 1, 1),
    "cluster": (0, 0, 1),
    "invoice": (0, 1, 0),
    "dashboard": (0, 1, 1),
}

SEED_RATINGS = {
    "ada": {"notebook": 5, "pipeline": 4, "cluster": 1},
    "bob": {"notebook": 4, "pipeline": 5, "dashboard": 4},
    "cy": {"cluster": 5, "invoice": 4, "dashboard": 2},
    "dee": {"invoice": 5, "cluster": 4, "notebook": 1},
    "eve": {"pipeline": 4, "dashboard": 5, "notebook": 4},
}
RATINGS = copy.deepcopy(SEED_RATINGS)
LIKED = 4


class RecError(ValueError):
    pass


def reset():
    RATINGS.clear()
    RATINGS.update(copy.deepcopy(SEED_RATINGS))


def cosine(left, right):
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def recommend(item):
    if item not in CATALOG:
        raise RecError(f"unknown catalog item: {item}")
    chosen = CATALOG[item]
    ranked = []
    for name, vector in CATALOG.items():
        if name == item:
            continue
        ranked.append({"item": name, "score": round(cosine(chosen, vector), 4)})
    ranked.sort(key=lambda row: (-row["score"], row["item"]))
    return {"item": item, "recommendations": ranked}


def item_vector(item):
    return [RATINGS[user].get(item, 0) for user in sorted(RATINGS)]


def item_similarity(left, right):
    return cosine(item_vector(left), item_vector(right))


def rate(user, item, rating):
    if not isinstance(user, str) or not user.isidentifier() or len(user) > 40:
        raise RecError("user must be a short identifier")
    if item not in CATALOG:
        raise RecError(f"unknown catalog item: {item}")
    if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
        raise RecError("rating must be an integer from 1 to 5")
    RATINGS.setdefault(user, {})[item] = rating
    return {"user": user, "ratings": dict(RATINGS[user])}


def popular(exclude=(), k=3):
    stats = []
    for item in CATALOG:
        if item in exclude:
            continue
        scores = [ratings[item] for ratings in RATINGS.values() if item in ratings]
        mean = sum(scores) / len(scores) if scores else 0.0
        stats.append({"item": item, "ratings": len(scores), "mean": round(mean, 4)})
    stats.sort(key=lambda row: (-row["ratings"], -row["mean"], row["item"]))
    return stats[:k]


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
    if not ranked:
        return {"user": user, "strategy": "popular", "recommendations": popular(exclude=rated, k=k)}
    return {"user": user, "strategy": "item_based", "recommendations": ranked[:k]}
