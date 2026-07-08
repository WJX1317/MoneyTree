import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.db import init_db, get_connection
from backend.services.journal import JournalService

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
        cur.execute("DELETE FROM journal")
    conn.commit()
    conn.close()

def setup_function():
    init_db(TEST_DB_CONFIG)
    _cleanup()

def test_add_and_list_entries():
    svc = JournalService()
    svc.add_entry(
        date="2026-07-07",
        action="buy",
        asset="华安黄金ETF (518880)",
        amount="1000份",
        cost="6000元",
        reason="看好金价"
    )
    entries = svc.list_entries()
    assert len(entries) == 1
    assert entries[0]["asset"] == "华安黄金ETF (518880)"
    assert entries[0]["reason"] == "看好金价"

def test_list_entries_ordered_by_date_desc():
    svc = JournalService()
    svc.add_entry(date="2026-07-01", action="buy", asset="A", amount="1", cost="1", reason="r1")
    svc.add_entry(date="2026-07-05", action="sell", asset="B", amount="2", cost="2", reason="r2")
    entries = svc.list_entries()
    assert entries[0]["date"] == "2026-07-05"
    assert entries[1]["date"] == "2026-07-01"
