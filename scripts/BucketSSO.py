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
            print(f'Bucket {bucket_name} är tom.')
    except NoCredentialsError:
        print('Inga autentiseringsuppgifter tillgängliga.')
    except PartialCredentialsError:
        print('Ofullständiga autentiseringsuppgifter angivna.')
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

def combine_images_and_sensordata(bucket_name, s3):
    """Kombinera bilder från en S3-bucket med mock-sensordata"""
    image_keys = list_bucket_objects(bucket_name, s3)
    if not image_keys:
        return
    print("\nBilder och tillhörande mock-sensordata:\n")
    for key in image_keys:
        sensor_data = get_mock_sensor_data()
        print(f'Bild: {key}')
        print(f'SensorData: {json.dumps(sensor_data, indent=2)}\n')

if __name__ == '__main__':
    # Ange ditt specifika AWS-profilnamn här (t.ex. SSO-profilen)
    session = boto3.Session(profile_name="axel")
    s3 = session.client('s3')
    bucket_name = 'agnesbucket.1'  # Namn på S3-bucket
    
    try:
        combine_images_and_sensordata(bucket_name, s3)
    except ClientError as e:
        print("Ett fel inträffade:", e)
