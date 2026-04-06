from typing import List, Optional, Literal
from pydantic import BaseModel


class SupportAction(BaseModel):
    action_type: Literal[
        "search_order",
        "search_policy",
        "add_tag",
        "approve_replacement",
        "deny_refund",
        "refund_payment",
        "draft_reply",
        "submit_resolution",
    ]
    order_id: Optional[str] = None
    query: Optional[str] = None
    tag: Optional[str] = None
    message: Optional[str] = None


class TicketView(BaseModel):
    ticket_id: str
    subject: str
    message: str
    customer_id: str
    known_order_ids: List[str]


class OrderView(BaseModel):
    order_id: str
    status: str
    delivered: bool
    days_since_delivery: int
    total_amount: float
    items: List[str]
    issue_flags: List[str]


class PolicySnippet(BaseModel):
    title: str
    content: str


class SupportObservation(BaseModel):
    task_name: str
    step_count: int
    max_steps: int
    ticket: TicketView
    retrieved_orders: List[OrderView]
    retrieved_policies: List[PolicySnippet]
    current_tags: List[str]
    drafted_reply: Optional[str] = None
    last_action: Optional[str] = None
    last_action_error: Optional[str] = None


class EnvState(BaseModel):
    step: int
    done: bool
    success: bool
    task_name: str
    max_steps: int
    ticket: dict
    orders: dict
    policies: dict
    retrieved_orders: List[str]
    retrieved_policies: List[str]
    tags: List[str]
    reply: Optional[str] = None
    resolution: Optional[str] = None
    last_action: Optional[str] = None
    last_action_error: Optional[str] = None