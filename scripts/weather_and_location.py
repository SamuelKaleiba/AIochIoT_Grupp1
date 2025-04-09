import requests
import os

# Lägg till din nyckel som miljövariabel i Lambda
OPENCAGE_KEY = os.environ['OPENCAGE_KEY']

def get_coordinates(location_name):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={OPENCAGE_KEY}"
    response = requests.get(url)
    data = response.json()
    coords = data['results'][0]['geometry']
    return coords['lat'], coords['lng']

def get_weather(lat, lon):
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    res = requests.get(url).json()
    forecast = res['timeSeries'][0]['parameters']
    return {param['name']: param['values'][0] for param in forecast}

def lambda_handler(event, context):
    location = event.get("location", "Stockholm")
    lat, lon = get_coordinates(location)
    weather = get_weather(lat, lon)
    return {
        'statusCode': 200,
        'body': {
            'location': location,
            'lat': lat,
            'lon': lon,
            'weather': weather
        }
    }
