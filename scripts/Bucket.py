import boto3 
import random
import time
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def list_bucket_objects(bucket_name):
    """List objects in an S3 bucket"""
    s3 = boto3.client('s3')
    keys = []

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' in response:
            for obj in response['Contents']:
                keys.append(obj["Key"])
        else:
            print(f'Bucket {bucket_name} is empty.')

    except NoCredentialsError:
        print('Credentials not available.')
    except PartialCredentialsError:
        print('Incomplete credentials provided.')

    return keys


def get_mock_sensor_data():
    """Generate mock sensor readings"""
    data = {
        'timestamp': int(time.time()),
        'temperature': round(random.uniform(18, 35), 1),
        'soil_moisture': round(random.uniform(10, 60), 1),
        'humidity': round(random.uniform(30, 90), 1),
        'light_intensity': round(random.uniform(100, 1000), 1)
    }
    return data


def combine_images_and_sensordata(bucket_name):
    image_keys = list_bucket_objects(bucket_name)

    if not image_keys:
        return

    print("\nBilder och tillhÃ¶rande mock-sensordata:\n")
    for key in image_keys:
        sensor_data = get_mock_sensor_data()
        print(f'Bild: {key}')
        print(f'SensorData: {json.dumps(sensor_data, indent=2)}\n')


if __name__ == '__main__':
    bucket_name = 'agnesbucket.1'
    combine_images_and_sensordata(bucket_name)