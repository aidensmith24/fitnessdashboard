import sqlite3

def get_db_connection():
    conn = sqlite3.connect("data/fitness.db")
    conn.row_factory = sqlite3.Row  # dictionary-style results
    return conn