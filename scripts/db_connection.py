import pyodbc
import os

def get_connection():
    # Hämta värden från miljövariabler
    rds_host = os.environ.get('RDS_HOST', 'database-2.ch0eo28sely1.eu-central-1.rds.amazonaws.com')
    rds_user = os.environ.get('RDS_USER', 'admin')
    rds_password = os.environ.get('RDS_PASSWORD', 'grupp1ai')
    rds_db_name = os.environ.get('RDS_DB_NAME', 'master')
    rds_port = os.environ.get('RDS_PORT', '1433')  

    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={rds_host},{rds_port};'
        f'DATABASE={rds_db_name};'
        f'UID={rds_user};'
        f'PWD={rds_password};'
    )

    return pyodbc.connect(conn_str, timeout=5)
