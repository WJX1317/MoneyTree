from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.tree import TreeService
from backend.services.learning import plan_tree

router = APIRouter(prefix="/api/goals", tags=["goals"])
tree_svc = TreeService()


class GoalCreate(BaseModel):
    title: str


@router.get("")
def list_goals():
    return tree_svc.get_goals()


@router.post("")
def create_goal(body: GoalCreate):
    goal_id = tree_svc.create_goal(body.title)
    try:
        nodes = plan_tree(goal_id, body.title)
    except Exception as e:
        tree_svc.delete_goal(goal_id)
        raise HTTPException(status_code=500, detail=str(e))
    return {"goal_id": goal_id, "nodes": nodes}
