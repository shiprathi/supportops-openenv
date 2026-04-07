def grade_task(state, task):
    score = 0.0
    expected = task["expected"]

    if expected["correct_order"] in state["retrieved_orders"]:
        score += 0.2

    if expected["correct_policy"] in state["retrieved_policies"]:
        score += 0.2

    # flexible tag match
    expected_tag = expected["correct_tag"]
    if expected_tag in state["tags"]:
        score += 0.2
    elif expected["correct_resolution"] == "refund_payment" and (
        "double_charge" in state["tags"] or "payment_issue" in state["tags"]
    ):
        score += 0.2

    if state["resolution"] == expected["correct_resolution"]:
        score += 0.2

    if state["reply"]:
        reply = state["reply"].lower()
        matched = 0
        for keyword in expected["reply_keywords"]:
            if keyword.lower() in reply:
                matched += 1

        if matched >= 1:
            score += 0.1
        if matched >= 2:
            score += 0.1

        score = min(max(score, 0.01), 0.99)
        return score
