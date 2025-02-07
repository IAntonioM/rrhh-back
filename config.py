import pyodbc

DB_CONFIG = {
    'server': 'DESKTOP-VLON2SB\\SQLEXPRESS',
    'database': 'BASE2',
    'username': 'cuzco',
    'password': '123456'
}

CONN_STRING = (f"DRIVER={{SQL Server}};SERVER={DB_CONFIG['server']};"
               f"DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};"
               f"PWD={DB_CONFIG['password']}")

def get_db_connection():
    return pyodbc.connect(CONN_STRING)
