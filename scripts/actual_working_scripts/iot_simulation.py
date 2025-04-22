import random

def generate_sensor_data():
    return {
        "temperature": round(random.uniform(15, 30), 2),
        "humidity": round(random.uniform(40, 90), 2),
        "soil_moisture": round(random.uniform(0.2, 0.8), 2),
        "ph": round(random.uniform(5.5, 7.5), 2)
    }
