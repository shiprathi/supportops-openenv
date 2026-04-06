# 🚀 SupportOps OpenEnv

SupportOps OpenEnv is a real-world customer support simulation environment designed for training and evaluating AI agents.

It models realistic e-commerce workflows including order lookup, policy retrieval, tagging, resolution decisions, and customer response generation.

---

## 🌍 Why this matters

Customer support is a real-world problem where AI agents must:
- Understand user issues
- Retrieve relevant data (orders, policies)
- Take correct decisions
- Generate human-like responses

This environment simulates that workflow step-by-step.

---

## ⚙️ Environment Design

The environment follows the OpenEnv standard:

- `reset(task_name)` → initializes a new support ticket
- `step(action)` → performs an action and returns next state
- `state()` → returns current environment state

---

## 🧠 Action Space

Agents can perform:

- `search_order`
- `search_policy`
- `add_tag`
- `approve_replacement`
- `deny_refund`
- `refund_payment`
- `draft_reply`
- `submit_resolution`

---

## 📊 Tasks

### 🟢 Easy
- Damaged item
- Replacement required

### 🟡 Medium
- Late refund request
- Refund must be denied

### 🔴 Hard
- Double payment issue
- Refund required

Each task increases in complexity.

---

## 🎯 Reward & Grading

- Deterministic grader
- Score range: **0.0 – 1.0**
- Rewards include:
  - partial progress rewards
  - penalties for wrong actions
  - final score-based reward

---

## 🤖 Inference

`inference.py` runs an agent across all tasks.

Features:
- LLM-based decision making
- fallback rule-based logic
- structured logs:
