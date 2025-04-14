from Mock_data import get_mock_sensor_data
from db_connection import get_connection
from db_init import ensure_irrigation_table_exists
import time
import json

def should_irrigate(data):
    if data['soil_moisture'] < 30 and data['temperature'] > 20:
        return "Bevattning rekommenderas"
    else:
        return "Ingen bevattning krävs"

def lambda_handler(event, context):
    data = get_mock_sensor_data()
    decision = should_irrigate(data)

    try:
        conn = get_connection()
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
