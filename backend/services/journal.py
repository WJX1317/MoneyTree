import uuid
from backend.db import get_connection


class JournalService:
    def add_entry(self, date: str, action: str, asset: str, amount: str = "", cost: str = "", reason: str = "") -> str:
        entry_id = f"{date}-{uuid.uuid4().hex[:6]}"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO journal (id, date, action, asset, amount, cost, reason) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (entry_id, date, action, asset, amount, cost, reason)
                )
            conn.commit()
        finally:
            conn.close()
        return entry_id

    def list_entries(self) -> list:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM journal ORDER BY date DESC, created_at DESC")
                return cur.fetchall()
        finally:
            conn.close()
