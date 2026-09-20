"""Creates the tables by running schema.sql against the database.
Run this once after starting PostgreSQL (docker compose up -d).
"""
from db import get_connection


def init():
    with open("schema.sql") as f:
        sql = f.read()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Tables created.")


if __name__ == "__main__":
    init()
