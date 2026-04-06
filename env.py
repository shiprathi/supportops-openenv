from app.tasks import get_task
from app.graders import grade_task


class SupportEnv:
    def __init__(self):
        self.state = None
        self.task = None

    def reset(self, task_name="easy"):
        self.task = get_task(task_name)

        self.state = {
            "step": 0,
            "done": False,
            "success": False,
            "task_name": self.task["task_name"],
            "max_steps": self.task["max_steps"],
            "ticket": self.task["ticket"],
            "orders": self.task["orders_db"],
            "policies": self.task["policy_db"],
            "retrieved_orders": [],
            "retrieved_policies": [],
            "tags": [],
            "reply": None,
            "resolution": None,
            "last_action": None,
            "last_action_error": None,
        }

        return self.state

    def step(self, action: dict):
        if self.state is None:
            raise ValueError("Environment not reset. Call reset() first.")

        if self.state["done"]:
            return self.state, 0.0, True

        self.state["step"] += 1
        reward = 0.0
        error = None
        action_type = action.get("action_type")
        previous_action = self.state.get("last_action")

        # repeated resolution action penalty
        if previous_action == action_type and action_type in [
            "approve_replacement",
            "deny_refund",
            "refund_payment",
        ]:
            self.state["last_action"] = action_type
            self.state["last_action_error"] = "repeated action penalty"
            return self.state, -0.5, self.state["done"]

        if action_type == "search_order":
            order_id = action.get("order_id")
            if order_id in self.state["orders"]:
                if order_id not in self.state["retrieved_orders"]:
                    self.state["retrieved_orders"].append(order_id)
                    reward = 1.0
                else:
                    reward = -0.1
                    error = "order already retrieved"
            else:
                reward = -0.2
                error = "order not found"

        elif action_type == "search_policy":
            query = (action.get("query") or "").lower()
            found = False

            for key, value in self.state["policies"].items():
                hay = f"{key} {value['title']} {value['content']}".lower()
                if query in hay:
                    if key not in self.state["retrieved_policies"]:
                        self.state["retrieved_policies"].append(key)
                        reward = 1.0
                    else:
                        reward = -0.1
                        error = "policy already retrieved"
                    found = True
                    break

            if not found:
                reward = -0.2
                error = "policy not found"

        elif action_type == "add_tag":
            tag = action.get("tag")
            if tag:
                if tag not in self.state["tags"]:
                    self.state["tags"].append(tag)
                    reward = 1.0
                else:
                    reward = -0.1
                    error = "tag already added"
            else:
                reward = -0.2
                error = "tag missing"

        elif action_type in ["approve_replacement", "deny_refund", "refund_payment"]:
            self.state["resolution"] = action_type
            reward = 2.0

        elif action_type == "draft_reply":
            message = action.get("message")
            if message:
                self.state["reply"] = message
                reward = 1.0
            else:
                reward = -0.2
                error = "message missing"

        elif action_type == "submit_resolution":
            self.state["done"] = True
            score = grade_task(self.state, self.task)
            reward = score * 10.0

            if score >= 0.8:
                self.state["success"] = True
            else:
                self.state["success"] = False

        else:
            reward = -0.2
            error = f"unsupported action: {action_type}"

        self.state["last_action"] = action_type
        self.state["last_action_error"] = error

        if self.state["step"] >= self.state["max_steps"] and not self.state["done"]:
            self.state["done"] = True
            score = grade_task(self.state, self.task)
            reward = max(reward, score * 5.0)

            if score >= 0.8:
                self.state["success"] = True
            else:
                self.state["success"] = False

        done = self.state["done"]
        return self.state, reward, done