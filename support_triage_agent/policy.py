POLICY = {
    "queues": {"billing": "accounts", "access": "identity", "product": "product-support"},
    "high_impact_users": 10,
}


def validate(case):
    if not isinstance(case, dict) or set(case) != {
        "ticket_id", "category", "users_affected", "workaround"
    }:
        raise ValueError("Expected ticket_id, category, users_affected, and workaround.")
    for field in ("ticket_id", "category"):
        if not isinstance(case[field], str) or not case[field].strip():
            raise ValueError(f"{field} must be a nonempty string.")
    if type(case["users_affected"]) is not int or case["users_affected"] < 1:
        raise ValueError("users_affected must be a positive integer.")
    if type(case["workaround"]) is not bool:
        raise ValueError("workaround must be a boolean.")
    return case


def assess(case, policy):
    queue = policy["queues"].get(case["category"].strip().lower(), "general")
    priority = "normal"
    if not case["workaround"]:
        priority = "elevated"
        if case["users_affected"] >= policy["high_impact_users"]:
            priority = "urgent"
    return {"ticket_id": case["ticket_id"], "queue": queue, "priority": priority}
