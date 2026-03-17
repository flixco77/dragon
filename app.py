from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "air_quality.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    # Это позволяет обращаться к полям по именам: row['pm25'] вместо row[3]
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/archive')
def archive():
    conn = get_db_connection()
    # Получаем все данные для таблицы, включая pm1
    readings = conn.execute(
        "SELECT id, received_at, dev_eui, pm1, pm25, pm10, temp, hum FROM sensor_readings ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('archive.html', readings=readings)


@app.route('/api/latest')
def api_latest():
    conn = get_db_connection()
    # Явно выбираем pm1, pm25, pm10 для графиков
    rows = conn.execute(
        "SELECT pm1, pm25, pm10, temp, hum, received_at FROM sensor_readings ORDER BY id DESC LIMIT 30").fetchall()
    conn.close()

    # Преобразуем Row в обычный список словарей для JSON
    data = [dict(row) for row in rows]
    return jsonify(data)


if __name__ == '__main__':
    # Используем порт 5002, так как 5001 часто занят AirPlay на Mac
    app.run(debug=True, host='0.0.0.0', port=5002)