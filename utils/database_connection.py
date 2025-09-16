import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import IntegrityError
import secrets

import bcrypt

load_dotenv()


def get_db_connection():
    database = os.getenv("DATABASE")
    database_user = os.getenv("DATABASE_USER")
    database_host = os.getenv("DATABASE_HOST")
    database_password = os.getenv("DATABASE_PASSWORD")
    database_port = os.getenv("DATABASE_PORT")

    conn = psycopg2.connect(database = database, 
                        user = database_user, 
                        host= database_host,
                        password = database_password,
                        port = database_port)

    return conn

def save_user_to_db(email, username, password):
    # ✅ Hash the password with bcrypt
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
            (email, username, hashed_pw),
        )
        conn.commit()
        return True, "✅ Registration successful!"

    except IntegrityError as e:
        conn.rollback()
        if "unique" in str(e).lower():
            return False, "⚠️ Email or username already exists."
        return False, f"❌ Integrity error: {e}"

    except Exception as e:
        conn.rollback()
        return False, f"❌ Database error: {e}"

    finally:
        cursor.close()
        conn.close()


def get_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def check_login(username, password):
    user = get_user_by_username(username)
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return user
    return None

def update_password(user_id, new_password):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed, user_id))
    conn.commit()
    cur.close()
    conn.close()

# --- Reset Token Flow ---
def create_reset_token(user_id, expires_minutes=30):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO password_resets (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (user_id, token, expires_at)
    )
    conn.commit()
    cur.close()
    conn.close()

    return token

def verify_token(token):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM password_resets WHERE token = %s AND expires_at > %s",
        (token, datetime.utcnow())
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None