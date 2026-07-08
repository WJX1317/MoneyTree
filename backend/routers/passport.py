from fastapi import APIRouter
from backend.services.tree import TreeService

router = APIRouter(prefix="/api/passport", tags=["passport"])
tree_svc = TreeService()


@router.get("")
def get_passport():
    goals = tree_svc.get_goals()
    stats = {"total_goals": len(goals), "goals": []}
    for goal in goals:
        nodes = tree_svc.get_tree(goal["id"])
        total = len(nodes)
        verified = sum(1 for n in nodes if n["status"] == "verified")
        stats["goals"].append({
            "id": goal["id"],
            "title": goal["title"],
            "total_nodes": total,
            "verified_nodes": verified,
            "progress": round(verified / total * 100) if total > 0 else 0,
        })
    return stats
