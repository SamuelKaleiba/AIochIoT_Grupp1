import pyodbc
import os

def get_connection():
    rds_host = os.environ['RDS_HOST']
    rds_user = os.environ['RDS_USER']
    rds_password = os.environ['RDS_PASSWORD']
    rds_db_name = os.environ['RDS_DB_NAME']
    rds_port = os.environ.get('RDS_PORT', '1433')

    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={rds_host},{rds_port};'
        f'DATABASE={rds_db_name};'
        f'UID={rds_user};'
        f'PWD={rds_password};'
    )

    return pyodbc.connect(conn_str, timeout=5)
