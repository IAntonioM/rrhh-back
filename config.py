import pyodbc
from dotenv import load_dotenv
import os
load_dotenv()

DB_CONFIG = {
    'server': os.getenv('DB_SERVER'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

CONN_STRING = (f"DRIVER={{SQL Server}};SERVER={DB_CONFIG['server']};"
               f"DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};"
               f"PWD={DB_CONFIG['password']}")

def get_db_connection():
    return pyodbc.connect(CONN_STRING)
