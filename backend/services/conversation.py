from backend.db import get_connection


def save_message(node_id: str, role: str, content: str, phase: str = "teach"):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO conversations (node_id, role, content, phase) VALUES (%s, %s, %s, %s)",
                (node_id, role, content, phase),
            )
        conn.commit()
    finally:
        conn.close()


def get_history(node_id: str, phase: str = None) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if phase:
                cur.execute(
                    "SELECT role, content, phase, created_at FROM conversations WHERE node_id = %s AND phase = %s ORDER BY id ASC",
                    (node_id, phase),
                )
            else:
                cur.execute(
                    "SELECT role, content, phase, created_at FROM conversations WHERE node_id = %s ORDER BY id ASC",
                    (node_id,),
                )
            return [{"role": r["role"], "content": r["content"], "phase": r["phase"], "time": str(r["created_at"])} for r in cur.fetchall()]
    finally:
        conn.close()


def clear_history(node_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM conversations WHERE node_id = %s", (node_id,))
        conn.commit()
    finally:
        conn.close()


def delete_last_n(node_id: str, n: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM conversations WHERE node_id = %s ORDER BY id DESC LIMIT %s",
                (node_id, n),
            )
            ids = [r["id"] for r in cur.fetchall()]
            if ids:
                placeholders = ",".join(["%s"] * len(ids))
                cur.execute(f"DELETE FROM conversations WHERE id IN ({placeholders})", ids)
        conn.commit()
    finally:
        conn.close()
