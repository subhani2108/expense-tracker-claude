import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "spendly.db"


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users LIMIT 1")
    if cursor.fetchone() is not None:
        conn.close()
        return

    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123"))
    )
    user_id = cursor.lastrowid

    expenses = [
        (user_id, 450.0, "Food", "2026-04-02", "Lunch at corner cafe"),
        (user_id, 150.0, "Transport", "2026-04-05", "Bus pass"),
        (user_id, 2200.0, "Bills", "2026-04-10", "Electricity bill"),
        (user_id, 800.0, "Health", "2026-04-12", "Pharmacy"),
        (user_id, 599.0, "Entertainment", "2026-04-15", "Movie streaming subscription"),
        (user_id, 1500.0, "Shopping", "2026-04-18", "New shirt"),
        (user_id, 250.0, "Food", "2026-04-20", "Groceries"),
        (user_id, 350.0, "Other", "2026-04-22", "Parking fee"),
    ]
    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    conn.commit()
    conn.close()