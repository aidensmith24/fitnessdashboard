from dotenv import load_dotenv
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import IntegrityError
import secrets
import os
import bcrypt
import requests

load_dotenv()

api_key = os.getenv('USDA_API_KEY')
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def query_usda_info(query):
    params = {"query": query, "api_key": api_key, "pageSize": 5}
    resp = requests.get(BASE_URL, params=params)
    return resp