from Mock_data import get_mock_sensor_data
import boto3
import time
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IrrigationDecisions')  # Skapa denna tabell i DynamoDB

def should_irrigate(data):
    if data['soil_moisture'] < 30 and data['temperature'] > 20:
        return "Bevattning rekommenderas"
    else:
        return "Ingen bevattning krävs"

def lambda_handler(event, context):
    data = get_mock_sensor_data()
    decision = should_irrigate(data)

    # Spara till DynamoDB
    table.put_item(Item={
        'timestamp': str(int(time.time())),
        'temperature': data['temperature'],
        'soil_moisture': data['soil_moisture'],
        'humidity': data['humidity'],
        'light': data['light_intensity'],
        'decision': decision
    })

    return {
        'statusCode': 200,
        'body': decision
    }
