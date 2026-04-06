from fastapi import FastAPI
from pydantic import BaseModel

from app.env import SupportEnv

app = FastAPI(title="SupportOps OpenEnv")
env = SupportEnv()


class ResetRequest(BaseModel):
    task_name: str = "easy"


class StepRequest(BaseModel):
    action_type: str
    order_id: str | None = None
    query: str | None = None
    tag: str | None = None
    message: str | None = None


@app.get("/")
def home():
    return {
        "message": "SupportOps OpenEnv is running",
        "available_tasks": ["easy", "medium", "hard"],
    }


@app.post("/reset")
def reset_env(req: ResetRequest = ResetRequest()):
    state = env.reset(req.task_name)
    return {
        "observation": state,
        "reward": 0.0,
        "done": False,
        "info": {
            "message": "reset successful",
            "task_name": req.task_name,
            "success": False,
            "last_action_error": None,
        },
    }


@app.post("/step")
def step_env(req: StepRequest):
    state, reward, done = env.step(req.model_dump())

    return {
        "observation": state,
        "reward": reward,
        "done": done,
        "info": {
            "task_name": state.get("task_name"),
            "success": state.get("success", False),
            "last_action_error": state.get("last_action_error"),
        },
    }


@app.get("/state")
def get_state():
    if env.state is None:
        return {
            "message": "env not initialized",
            "hint": "Call POST /reset first"
        }

    return env.state