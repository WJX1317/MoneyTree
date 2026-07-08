import os
import sys
import pymysql

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.db import init_db, get_connection

TEST_DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "moneytree",
}

def test_connection_works():
    init_db(TEST_DB_CONFIG)
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 as val")
        row = cur.fetchone()
    conn.close()
    assert row["val"] == 1

def test_tables_exist():
    init_db(TEST_DB_CONFIG)
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cur.fetchall()]
    conn.close()
    assert "goals" in tables
    assert "nodes" in tables
    assert "node_deps" in tables
    assert "conversations" in tables
    assert "journal" in tables
