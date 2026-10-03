CATALOG = {
    "notebook": (1, 1, 0),
    "pipeline": (1, 1, 1),
    "cluster": (0, 0, 1),
    "invoice": (0, 1, 0),
}

def cosine(left, right):
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    return dot / (left_norm * right_norm)

def recommend(item):
    chosen = CATALOG[item]
    ranked = []
    for name, vector in CATALOG.items():
        if name == item:
            continue
        ranked.append({"item": name, "score": round(cosine(chosen, vector), 4)})
    ranked.sort(key=lambda row: row["score"], reverse=True)
    return {"item": item, "recommendations": ranked}
