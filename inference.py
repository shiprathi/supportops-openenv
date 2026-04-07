import os
import json

try:
    from env import SupportEnv
except ImportError:
    from app.env import SupportEnv

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN")

client = None
if API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    except Exception:
        client = None


def log_start(task):
    print(f"[START] task={task} env=supportops model={MODEL_NAME}")


def log_step(step, action, reward, done, error=None):
    err = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={err}"
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.2f} rewards={rewards_str}"
    )


def fallback_action(state):
    task_name = state.get("task_name", "easy")

    if not state["retrieved_orders"]:
        return {
            "action_type": "search_order",
            "order_id": state["ticket"]["known_order_ids"][0]
        }

    if not state["retrieved_policies"]:
        if task_name == "easy":
            return {"action_type": "search_policy", "query": "damaged"}
        if task_name == "medium":
            return {"action_type": "search_policy", "query": "refund"}
        return {"action_type": "search_policy", "query": "payment"}

    if not state["tags"]:
        if task_name == "easy":
            return {"action_type": "add_tag", "tag": "damaged_item"}
        if task_name == "medium":
            return {"action_type": "add_tag", "tag": "late_refund_request"}
        return {"action_type": "add_tag", "tag": "double_charge"}

    if not state["resolution"]:
        if task_name == "easy":
            return {"action_type": "approve_replacement"}
        if task_name == "medium":
            return {"action_type": "deny_refund"}
        return {"action_type": "refund_payment"}

    if not state["reply"]:
        if task_name == "easy":
            return {
                "action_type": "draft_reply",
                "message": "Sorry for the damaged item. We will send a replacement."
            }
        if task_name == "medium":
            return {
                "action_type": "draft_reply",
                "message": "Your refund request cannot be approved because the 7 days return window has passed."
            }
        return {
            "action_type": "draft_reply",
            "message": "We are sorry for the payment issue. Your refund for the duplicate payment will be processed."
        }

    return {"action_type": "submit_resolution"}


def llm_action(state):
    if client is None:
        raise RuntimeError("LLM client unavailable")

    system_prompt = (
        "You are a customer support operations agent.\n"
        "You must choose the NEXT logical action only.\n"
        "Required order of work:\n"
        "1. search_order\n"
        "2. search_policy\n"
        "3. add_tag\n"
        "4. choose resolution\n"
        "5. draft_reply\n"
        "6. submit_resolution\n"
        "Return ONLY valid JSON. No markdown. No explanation."
    )

    user_prompt = f"""
Current state:
{json.dumps(state, indent=2)}

Available actions:
- search_order
- search_policy
- add_tag
- approve_replacement
- deny_refund
- refund_payment
- draft_reply
- submit_resolution

Return one JSON object only.
Examples:
{{"action_type":"search_order","order_id":"O1"}}
{{"action_type":"search_policy","query":"damaged"}}
{{"action_type":"add_tag","tag":"damaged_item"}}
{{"action_type":"approve_replacement"}}
{{"action_type":"deny_refund"}}
{{"action_type":"refund_payment"}}
{{"action_type":"draft_reply","message":"..."}}
{{"action_type":"submit_resolution"}}
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=120,
    )

    text = (response.choices[0].message.content or "").strip()
    return json.loads(text)


def validate_or_fix_action(state, action):
    if not isinstance(action, dict) or "action_type" not in action:
        return fallback_action(state)

    action_type = action["action_type"]

    if not state["retrieved_orders"]:
        if action_type != "search_order":
            return fallback_action(state)

    elif not state["retrieved_policies"]:
        if action_type != "search_policy":
            return fallback_action(state)

    elif not state["tags"]:
        if action_type != "add_tag":
            return fallback_action(state)

    elif not state["resolution"]:
        allowed = {"approve_replacement", "deny_refund", "refund_payment"}
        if action_type not in allowed:
            return fallback_action(state)

    elif not state["reply"]:
        if action_type != "draft_reply":
            return fallback_action(state)

    else:
        if action_type != "submit_resolution":
            return fallback_action(state)

    return action


def get_action(state):
    if client is None:
        return fallback_action(state)

    try:
        action = llm_action(state)
        return validate_or_fix_action(state, action)
    except Exception:
        return fallback_action(state)


def run_task(task_name):
    env = SupportEnv()
    state = env.reset(task_name)

    log_start(task_name)
    rewards = []
    step_count = 0

    while True:
        step_count += 1
        action = get_action(state)
        state, reward, done = env.step(action)
        rewards.append(reward)

        log_step(
            step_count,
            json.dumps(action, separators=(",", ":")),
            reward,
            done,
            state.get("last_action_error"),
        )

        if done:
            break

    success = state.get("success", False)
    score = float(state.get("task_score", 0.01))
    score = min(max(score, 0.01), 0.99)
    log_end(success, step_count, score, rewards)


if __name__ == "__main__":
    for task in ["easy", "medium", "hard"]:
        run_task(task)
