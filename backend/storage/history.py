
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "netpulse.db"


def initialize_database():

    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            checked_at TEXT NOT NULL,
            status TEXT NOT NULL,
            latency_ms REAL,
            packet_loss REAL
        )
    """)

    connection.commit()
    connection.close()


def save_results(results):

    connection = sqlite3.connect(DB_PATH)

    timestamp = datetime.now(timezone.utc).isoformat()

    for device in results:

        connection.execute("""
            INSERT INTO monitoring_history
            (ip_address, checked_at, status, latency_ms, packet_loss)
            VALUES (?, ?, ?, ?, ?)
        """, (
            device["ip"],
            timestamp,
            device["status"],
            device["latency_ms"],
            device["packet_loss"]
        ))

    connection.commit()
    connection.close()


def get_monitoring_history():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.execute("""
        SELECT *
        FROM monitoring_history
        ORDER BY id DESC
    """)

    records = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return records
