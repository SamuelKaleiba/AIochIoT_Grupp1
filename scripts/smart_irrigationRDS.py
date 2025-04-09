from Mock_data import get_mock_sensor_data
import pyodbc
import os
import time
import json

# Miljövariabler konfigurerade i AWS Lambda
rds_host = os.environ['RDS_HOST']
rds_user = os.environ['RDS_USER']
rds_password = os.environ['RDS_PASSWORD']
rds_db_name = os.environ['RDS_DB_NAME']
rds_port = os.environ.get('RDS_PORT', '1433')

# ODBC-anslutningssträng
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={rds_host},{rds_port};'
    f'DATABASE={rds_db_name};'
    f'UID={rds_user};'
    f'PWD={rds_password};'
)

def should_irrigate(data):
    if data['soil_moisture'] < 30 and data['temperature'] > 20:
        return "Bevattning rekommenderas"
    else:
        return "Ingen bevattning krävs"

def lambda_handler(event, context):
    data = get_mock_sensor_data()
    decision = should_irrigate(data)

    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO IrrigationLogs (
                timestamp, temperature, soil_moisture, humidity, light, decision
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, (
            int(time.time()),
            data['temperature'],
            data['soil_moisture'],
            data['humidity'],
            data['light_intensity'],
            decision
        ))

        conn.commit()

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Fel vid databasanslutning eller SQL: {str(e)}"
        }

    finally:
        conn.close()

    return {
        'statusCode': 200,
        'body': decision
    }
