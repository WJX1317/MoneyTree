from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from backend.services.tree import TreeService
from backend.services.learning import teach, verify
from backend.services.conversation import save_message, get_history

router = APIRouter(prefix="/api/chat", tags=["chat"])
tree_svc = TreeService()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    goal_id: str
    node_id: str
    message: str = ""
    phase: str = ""


@router.get("/history/{node_id}")
def get_chat_history(node_id: str):
    history = get_history(node_id)
    return {"history": history}


@router.post("")
def chat_endpoint(body: ChatRequest):
    nodes = tree_svc.get_tree(body.goal_id)
    node = next((n for n in nodes if n["id"] == body.node_id), None)
    if not node:
        return {"error": "node not found"}

    goals = tree_svc.get_goals()
    goal = next((g for g in goals if g["id"] == body.goal_id), None)
    goal_title = goal["title"] if goal else ""

    use_verify = (body.phase == "verify") or (node["status"] == "learned" and body.phase != "teach")

    if use_verify:
        if body.message:
            save_message(body.node_id, "user", body.message, phase="verify")

        verify_history = get_history(body.node_id, phase="verify")
        result = verify(
            node_id=body.node_id,
            node_title=node["title"],
            node_summary=node.get("summary", ""),
            history=[{"role": m["role"], "content": m["content"]} for m in verify_history],
        )
        save_message(body.node_id, "assistant", result["reply"], phase="verify")
        return {
            "reply": result["reply"],
            "verified": result["verified"],
            "teaching_complete": False,
            "phase": "verify",
        }
    else:
        if body.message:
            save_message(body.node_id, "user", body.message, phase="teach")

        teach_history = get_history(body.node_id, phase="teach")
        result = teach(
            goal_id=body.goal_id,
            goal_title=goal_title,
            node_id=body.node_id,
            node_title=node["title"],
            sort_order=node["sort_order"],
            history=[{"role": m["role"], "content": m["content"]} for m in teach_history],
        )

        reply = result["reply"]
        options = []
        import re
        opt_match = re.search(r'\[OPTIONS:\s*(.+?)\]', reply)
        if opt_match:
            options = [o.strip() for o in opt_match.group(1).split('|') if o.strip()]
            reply = reply[:opt_match.start()].rstrip()

        save_message(body.node_id, "assistant", reply, phase="teach")
        return {
            "reply": reply,
            "teaching_complete": result["teaching_complete"],
            "verified": False,
            "phase": "teach",
            "options": options,
        }


@router.post("/undo/{node_id}")
def undo_last_pair(node_id: str):
    from backend.services.conversation import delete_last_n
    delete_last_n(node_id, 2)
    return {"ok": True}


@router.post("/undo-last/{node_id}")
def undo_last_message(node_id: str):
    from backend.services.conversation import delete_last_n
    delete_last_n(node_id, 1)
    return {"ok": True}


@router.delete("/history/{node_id}")
def clear_chat_history(node_id: str):
    from backend.services.conversation import clear_history
    clear_history(node_id)
    return {"ok": True}
