import sqlite3

DB = "aegis.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS senzori (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT,
        lokacija TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mjerenja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id INTEGER,
        vrijeme TEXT,
        tip TEXT,
        vrijednost REAL
    )
    """)

    conn.commit()
    conn.close()


def dodaj_senzor(naziv, lokacija):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO senzori VALUES (NULL, ?, ?)", (naziv, lokacija))
    conn.commit()
    conn.close()


def dodaj_mjerenje(sensor_id, vrijeme, tip, vrijednost):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mjerenja VALUES (NULL, ?, ?, ?, ?)
    """, (sensor_id, vrijeme, tip, vrijednost))
    conn.commit()
    conn.close()


def dohvati_podatke():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT senzori.naziv, senzori.lokacija, mjerenja.vrijeme,
           mjerenja.tip, mjerenja.vrijednost
    FROM mjerenja
    JOIN senzori ON senzori.id = mjerenja.sensor_id
    """)

    data = cur.fetchall()
    conn.close()
    return data