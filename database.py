import sqlite3

DB_FILE = "air_quality.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            dev_eui     TEXT,
            received_at TEXT,
            rssi        INTEGER,
            snr         REAL,
            pm1         INTEGER,
            pm25        INTEGER,
            pm10        INTEGER,
            temp        INTEGER,
            hum         INTEGER
        );
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS raw_packets (id INTEGER PRIMARY KEY AUTOINCREMENT, dev_eui TEXT, received_at TEXT, payload_hex TEXT);")
    conn.commit()
    conn.close()

def save_reading(dev_eui, received_at, rssi, snr, pm1, pm25, pm10, temp, hum):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sensor_readings (dev_eui, received_at, rssi, snr, pm1, pm25, pm10, temp, hum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dev_eui, received_at, rssi, snr, pm1, pm25, pm10, temp, hum))
    conn.commit()
    conn.close()

def save_packet(dev_eui, received_at, payload_hex):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO raw_packets (dev_eui, received_at, payload_hex) VALUES (?, ?, ?)", (dev_eui, received_at, payload_hex))
    conn.commit()
    conn.close()

def get_latest(limit=5):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, dev_eui, pm25, temp, hum, received_at FROM sensor_readings ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows