import boto3
import random
import time
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def list_bucket_objects(bucket_name, s3):
    """Lista objekt i en S3-bucket"""
    keys = []
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                keys.append(obj["Key"])
        else:
            print(f"Bucket {bucket_name} är tom.")
    except ClientError as e:
        print("ClientError:", e)
    return keys

def get_mock_sensor_data():
    """Generera mock-sensoravläsningar"""
    data = {
        'timestamp': int(time.time()),
        'temperature': round(random.uniform(18, 35), 1),
        'soil_moisture': round(random.uniform(10, 60), 1),
        'humidity': round(random.uniform(30, 90), 1),
        'light_intensity': round(random.uniform(100, 1000), 1)
    }
    return data

def detect_image_labels(bucket_name, image_key, rekognition):
    """
    Använder Rekognition för att analysera en bild i S3 och returnera de etiketter (labels) som hittas.
    """
    try:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': image_key
                }
            },
            MaxLabels=10,         # Hämta högst 10 etiketter per bild
            MinConfidence=80       # Endast etiketter med minst 80% säkerhet inkluderas
        )
        return response.get("Labels", [])
    except ClientError as e:
        print(f"Rekognition error för bilden {image_key}: {e}")
        return []

def combine_images_sensordata_and_rekognition(bucket_name, s3, rekognition):
    """
    Kombinerar bilder från S3, mock-sensordata och Rekognition-resultat.
    """
    image_keys = list_bucket_objects(bucket_name, s3)
    if not image_keys:
        return

    print("\nBilder, mock-sensordata och Rekognition-resultat:\n")
    for key in image_keys:
        # Hämta mock-sensordata
        sensor_data = get_mock_sensor_data()

        # Hämta Rekognition-etiketter för bilden
        labels = detect_image_labels(bucket_name, key, rekognition)

        print(f"Bild: {key}")
        print("SensorData:")
        print(json.dumps(sensor_data, indent=2))

        if labels:
            print("Rekognition Labels:")
            for label in labels:
                name = label.get("Name")
                confidence = label.get("Confidence")
                print(f" - {name}: {confidence:.2f}%")
        else:
            print("Inga etiketter hittades med Rekognition.")
        print()

if __name__ == '__main__':
    # Ange ditt specifika AWS-profilnamn här (t.ex. den SSO-konfigurerade profilen)
    session = boto3.Session(profile_name="Daniel")
    
    # Skapa klienter för S3 och Rekognition
    s3 = session.client('s3')
    rekognition = session.client('rekognition')
    
    bucket_name = 'agnesbucket.1'  # Namn på din S3-bucket
    combine_images_sensordata_and_rekognition(bucket_name, s3, rekognition)
