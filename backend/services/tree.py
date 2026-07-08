import pymysql
import uuid
from datetime import datetime
from backend.db import get_connection


class TreeService:
    def create_goal(self, title: str) -> str:
        goal_id = uuid.uuid4().hex[:8]
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO goals (id, title) VALUES (%s, %s)", (goal_id, title))
            conn.commit()
        finally:
            conn.close()
        return goal_id

    def get_goals(self) -> list:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM goals ORDER BY created_at DESC")
                return cur.fetchall()
        finally:
            conn.close()

    def delete_goal(self, goal_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM conversations WHERE node_id IN (SELECT id FROM nodes WHERE goal_id=%s)", (goal_id,))
                cur.execute("DELETE FROM node_deps WHERE node_id IN (SELECT id FROM nodes WHERE goal_id=%s)", (goal_id,))
                cur.execute("DELETE FROM nodes WHERE goal_id=%s", (goal_id,))
                cur.execute("DELETE FROM goals WHERE id=%s", (goal_id,))
            conn.commit()
        finally:
            conn.close()

    def set_tree(self, goal_id: str, nodes: list, deps: list):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for node in nodes:
                    node_id = f"{goal_id}_{node['id']}"
                    cur.execute(
                        "INSERT INTO nodes (id, goal_id, title, sort_order, status) VALUES (%s, %s, %s, %s, 'locked')",
                        (node_id, goal_id, node["title"], node["sort_order"])
                    )
                for (nid, depends_on) in deps:
                    cur.execute(
                        "INSERT INTO node_deps (node_id, depends_on) VALUES (%s, %s)",
                        (f"{goal_id}_{nid}", f"{goal_id}_{depends_on}")
                    )
            conn.commit()
            self._unlock_ready_nodes(conn, goal_id)
            conn.commit()
        finally:
            conn.close()

    def _unlock_ready_nodes(self, conn, goal_id: str):
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM nodes WHERE goal_id = %s AND status = 'locked'", (goal_id,))
            locked_nodes = cur.fetchall()
            for row in locked_nodes:
                node_id = row["id"]
                cur.execute("""
                    SELECT COUNT(*) as cnt FROM node_deps nd
                    JOIN nodes n ON nd.depends_on = n.id
                    WHERE nd.node_id = %s AND n.status != 'verified'
                """, (node_id,))
                unmet = cur.fetchone()["cnt"]
                if unmet == 0:
                    cur.execute("UPDATE nodes SET status = 'unlocked' WHERE id = %s", (node_id,))

    def get_tree(self, goal_id: str) -> list:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM nodes WHERE goal_id = %s ORDER BY sort_order", (goal_id,))
                return cur.fetchall()
        finally:
            conn.close()

    def get_current_node(self, goal_id: str) -> dict:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM nodes WHERE goal_id = %s AND status IN ('unlocked', 'learned') ORDER BY sort_order LIMIT 1",
                    (goal_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    def mark_learned(self, node_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE nodes SET status = 'learned', learned_at = %s WHERE id = %s",
                    (datetime.now().isoformat(), node_id)
                )
            conn.commit()
        finally:
            conn.close()

    def mark_verified(self, node_id: str):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT goal_id FROM nodes WHERE id = %s", (node_id,))
                node = cur.fetchone()
                cur.execute(
                    "UPDATE nodes SET status = 'verified', verified_at = %s WHERE id = %s",
                    (datetime.now().isoformat(), node_id)
                )
            conn.commit()
            if node:
                self._unlock_ready_nodes(conn, node["goal_id"])
                conn.commit()
        finally:
            conn.close()
