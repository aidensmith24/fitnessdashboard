import sqlite3

# Connect (creates fitness.db if it doesn’t exist)
conn = sqlite3.connect("fitness.db")

# Get a cursor
cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL -- store hashed in production
)
""")

# Create user_data table
cur.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    metric TEXT,
    value REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Save and close
conn.commit()

# Insert users (replace with hashed passwords later)
cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("alice", "password123"))
cur.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("bob", "mypassword"))

conn.commit()

conn.close()

print("✅ Database and tables created successfully!")
