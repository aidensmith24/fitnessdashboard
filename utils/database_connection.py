import sqlite3
import os
from dotenv import load_dotenv

import psycopg2


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