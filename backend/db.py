import os
import pymysql
from pymysql.cursors import DictCursor

_config: dict = None

def init_db(config: dict = None):
    global _config
    if config:
        _config = config
    else:
        _config = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", ""),
            "database": os.getenv("MYSQL_DB", "moneytree"),
        }

def get_connection() -> pymysql.Connection:
    return pymysql.connect(
        host=_config["host"],
        port=_config["port"],
        user=_config["user"],
        password=_config["password"],
        database=_config["database"],
        cursorclass=DictCursor,
        autocommit=False,
    )
