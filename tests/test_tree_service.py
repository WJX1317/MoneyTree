import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.db import init_db, get_connection
from backend.services.tree import TreeService

TEST_DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "moneytree",
}

def _cleanup():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM node_deps")
        cur.execute("DELETE FROM conversations")
        cur.execute("DELETE FROM nodes")
        cur.execute("DELETE FROM goals")
        cur.execute("DELETE FROM journal")
    conn.commit()
    conn.close()

def setup_function():
    init_db(TEST_DB_CONFIG)
    _cleanup()

def test_create_goal_and_nodes():
    svc = TreeService()
    goal_id = svc.create_goal("搞懂黄金ETF")
    assert goal_id is not None

    nodes = [
        {"id": "participants", "title": "市场参与者", "sort_order": 1},
        {"id": "trading-flow", "title": "交易链路", "sort_order": 2},
        {"id": "arbitrage", "title": "套利机制", "sort_order": 3},
    ]
    deps = [
        ("trading-flow", "participants"),
        ("arbitrage", "trading-flow"),
    ]
    svc.set_tree(goal_id, nodes, deps)

    tree = svc.get_tree(goal_id)
    assert len(tree) == 3
    assert tree[0]["status"] == "unlocked"
    assert tree[1]["status"] == "locked"
    assert tree[2]["status"] == "locked"

def test_complete_node_unlocks_next():
    svc = TreeService()
    goal_id = svc.create_goal("测试目标")
    nodes = [
        {"id": "n1", "title": "节点1", "sort_order": 1},
        {"id": "n2", "title": "节点2", "sort_order": 2},
    ]
    deps = [("n2", "n1")]
    svc.set_tree(goal_id, nodes, deps)

    svc.mark_learned("n1")
    svc.mark_verified("n1")

    tree = svc.get_tree(goal_id)
    assert tree[0]["status"] == "verified"
    assert tree[1]["status"] == "unlocked"

def test_get_current_node():
    svc = TreeService()
    goal_id = svc.create_goal("测试目标2")
    nodes = [
        {"id": "m1", "title": "节点1", "sort_order": 1},
        {"id": "m2", "title": "节点2", "sort_order": 2},
    ]
    deps = [("m2", "m1")]
    svc.set_tree(goal_id, nodes, deps)

    current = svc.get_current_node(goal_id)
    assert current["id"] == "m1"
