import random
import time
import json

def get_mock_sensor_data():
    data = {
        'timestamp': int(time.time()),
        'temperature': round(random.uniform(18, 35), 1),
        'soil_moisture': round(random.uniform(10, 60), 1),
        'humidity': round(random.uniform(30, 90), 1),
        'light_intensity': round(random.uniform(100, 1000), 1)
    }
    return data

# För testande:
if __name__ == "__main__":
    print(get_mock_sensor_data())

