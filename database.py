import sqlite3

conn = sqlite3.connect("insurance.db", check_same_thread=False)
cursor = conn.cursor()

# Users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")

# Claims (single table with status instead of 2 tables → more stable)
cursor.execute("""
CREATE TABLE IF NOT EXISTS claims (
    username TEXT,
    age INT,
    bmi REAL,
    smoker INT,
    result TEXT,
    reason TEXT
)
""")

conn.commit()