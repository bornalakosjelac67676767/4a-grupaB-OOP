import sqlite3

DB = "aegis.db"

def init_users():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin')")

    conn.commit()
    conn.close()


def login(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (username, password))

    user = cur.fetchone()
    conn.close()
    return user