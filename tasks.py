def get_task(task_name="easy"):
    tasks = {
        "easy": {
            "task_name": "easy",
            "max_steps": 6,
            "ticket": {
                "ticket_id": "T1",
                "subject": "Broken item",
                "message": "My mug arrived broken, please help.",
                "customer_id": "C1",
                "known_order_ids": ["O1"],
            },
            "orders_db": {
                "O1": {
                    "order_id": "O1",
                    "status": "delivered",
                    "delivered": True,
                    "days_since_delivery": 2,
                    "total_amount": 500.0,
                    "items": ["Mug"],
                    "issue_flags": [],
                }
            },
            "policy_db": {
                "damaged": {
                    "title": "Damaged Policy",
                    "content": "Damaged items within 7 days are eligible for replacement.",
                }
            },
            "expected": {
                "correct_order": "O1",
                "correct_policy": "damaged",
                "correct_tag": "damaged_item",
                "correct_resolution": "approve_replacement",
                "reply_keywords": ["sorry", "replacement"],
            },
        },
        "medium": {
            "task_name": "medium",
            "max_steps": 7,
            "ticket": {
                "ticket_id": "T2",
                "subject": "Late refund request",
                "message": "I want a refund after 10 days of delivery.",
                "customer_id": "C2",
                "known_order_ids": ["O2"],
            },
            "orders_db": {
                "O2": {
                    "order_id": "O2",
                    "status": "delivered",
                    "delivered": True,
                    "days_since_delivery": 10,
                    "total_amount": 1000.0,
                    "items": ["Shoes"],
                    "issue_flags": [],
                }
            },
            "policy_db": {
                "refund": {
                    "title": "Refund Policy",
                    "content": "Refund allowed within 7 days only.",
                }
            },
            "expected": {
                "correct_order": "O2",
                "correct_policy": "refund",
                "correct_tag": "refund_denied",
                "correct_resolution": "deny_refund",
                "reply_keywords": ["refund", "7 days"],
            },
        },
        "hard": {
            "task_name": "hard",
            "max_steps": 8,
            "ticket": {
                "ticket_id": "T3",
                "subject": "Double charged",
                "message": "I was charged twice for my order.",
                "customer_id": "C3",
                "known_order_ids": ["O3"],
            },
            "orders_db": {
                "O3": {
                    "order_id": "O3",
                    "status": "delivered",
                    "delivered": True,
                    "days_since_delivery": 1,
                    "total_amount": 1500.0,
                    "items": ["Headphones"],
                    "issue_flags": ["double_charge"],
                }
            },
            "policy_db": {
                "payment": {
                    "title": "Payment Issue Policy",
                    "content": "Double charges are refunded immediately.",
                }
            },
            "expected": {
    "correct_order": "O3",
    "correct_policy": "payment",
    "correct_tag": "double_charge",
    "correct_resolution": "refund_payment",
    "reply_keywords": ["refund", "charged twice"]
},
        },
    }

    if task_name not in tasks:
        raise ValueError(f"Unknown task: {task_name}")

    return tasks[task_name]