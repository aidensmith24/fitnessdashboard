import sqlite3
import os
from dotenv import load_dotenv

import psycopg2
from psycopg2 import IntegrityError

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
