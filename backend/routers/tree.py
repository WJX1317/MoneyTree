from fastapi import APIRouter
from backend.services.tree import TreeService

router = APIRouter(prefix="/api/tree", tags=["tree"])
tree_svc = TreeService()


@router.get("/{goal_id}")
def get_tree(goal_id: str):
    nodes = tree_svc.get_tree(goal_id)
    return {"nodes": nodes}


@router.get("/{goal_id}/current")
def get_current_node(goal_id: str):
    node = tree_svc.get_current_node(goal_id)
    if not node:
        return {"node": None, "all_done": True}
    return {"node": node, "all_done": False}
