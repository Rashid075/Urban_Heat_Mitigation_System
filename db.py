import sqlite3

DB_NAME = "urban_heat.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Zones table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS zones (
        name TEXT PRIMARY KEY,
        latitude REAL,
        longitude REAL
    )
    """)

    # Weather history
    cur.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zone TEXT,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_zone(name, lat, lon):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO zones VALUES (?, ?, ?)", (name, lat, lon))
        conn.commit()
    except:
        pass
    conn.close()


def get_zones():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM zones")
    rows = cur.fetchall()
    conn.close()
    return {r[0]: (r[1], r[2]) for r in rows}


def insert_weather(row):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO weather_data (zone, temperature, humidity, wind_speed)
    VALUES (?, ?, ?, ?)
    """, (row["zone"], row["temperature"], row["humidity"], row["wind_speed"]))

    conn.commit()
    conn.close()


def get_history(zone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT temperature, humidity, wind_speed, timestamp
    FROM weather_data WHERE zone=? ORDER BY timestamp DESC LIMIT 50
    """, (zone,))
    data = cur.fetchall()
    conn.close()
    return data

def get_complete_history():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT zone,temperature, humidity, wind_speed, timestamp FROM weather_data""")
    data = cur.fetchall()
    conn.close()
    return data