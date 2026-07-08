from backend.llm import chat
from backend.prompts.planner import build_planner_messages
from backend.prompts.teacher import build_teacher_messages
from backend.prompts.verifier import build_verifier_messages
from backend.services.tree import TreeService
import json

tree_svc = TreeService()

TEACHING_COMPLETE_MARKER = "[TEACHING_COMPLETE]"
VERIFIED_MARKER = "[VERIFIED]"


def plan_tree(goal_id: str, goal_title: str) -> list:
    messages = build_planner_messages(goal_title)
    raw = chat(messages, temperature=0.4)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]
    data = json.loads(raw)
    tree_svc.set_tree(goal_id, data["nodes"], [tuple(d) for d in data["deps"]])
    return data["nodes"]


def teach(goal_id: str, goal_title: str, node_id: str, node_title: str, sort_order: int, history: list) -> dict:
    if not history:
        history = [{"role": "user", "content": "请开始教我这个知识点吧。"}]

    messages = build_teacher_messages(goal_title, node_title, sort_order, history)
    reply = chat(messages)
    teaching_done = TEACHING_COMPLETE_MARKER in reply
    clean_reply = reply.replace(TEACHING_COMPLETE_MARKER, "").strip()
    if teaching_done:
        tree_svc.mark_learned(node_id)
    return {"reply": clean_reply, "teaching_complete": teaching_done}


def verify(node_id: str, node_title: str, node_summary: str, history: list) -> dict:
    if not history:
        history = [{"role": "user", "content": "我准备好验证了，请出题。"}]
    messages = build_verifier_messages(node_title, node_summary, history)
    reply = chat(messages)
    verified = VERIFIED_MARKER in reply
    clean_reply = reply.replace(VERIFIED_MARKER, "").strip()
    if verified:
        tree_svc.mark_verified(node_id)
    return {"reply": clean_reply, "verified": verified}
