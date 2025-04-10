import random
import time
import requests

# Funktionshjälp för att hämta väderdata från SMHI via OpenCage API
def get_weather_data(location):
    """Hämtar väderdata från SMHI baserat på platsen."""
    try:
        # Hämta lat/lon från OpenCage
        GEOCODE_URL = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key=din-opencage-nyckel"
        geo_res = requests.get(GEOCODE_URL)
        geo_res.raise_for_status()
        geo_data = geo_res.json()

        if not geo_data['results']:
            raise ValueError("Kunde inte hitta platsen.")
        
        coords = geo_data['results'][0]['geometry']
        lat = round(coords['lat'], 6)
        lon = round(coords['lng'], 6)

        # Hämta väderdata från SMHI API
        WEATHER_URL = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
        weather_res = requests.get(WEATHER_URL)
        weather_res.raise_for_status()
        weather_data = weather_res.json()

        # Extrahera relevant data (t.ex. temperatur, luftfuktighet, och solstrålning)
        if 'timeSeries' not in weather_data:
            raise ValueError("Ingen väderdata tillgänglig.")

        forecast = weather_data['timeSeries'][0]['parameters']
        weather_info = {param['name']: param['values'][0] for param in forecast}

        # Hämta solstrålning (som en uppskattning för ljusintensitet)
        solar_radiation = weather_info.get('swr', 0)  # 'swr' är koden för solstrålning i SMHI:s API

        return {
            'temperature': weather_info.get('t', random.uniform(18, 35)),  # Temperatur
            'humidity': weather_info.get('r', random.uniform(30, 90)),  # Luftfuktighet
            'solar_radiation': solar_radiation  # Solstrålning (W/m²) - använd som ljusintensitet
        }
    
    except requests.exceptions.RequestException as e:
        raise ValueError(f"API-anropet misslyckades: {str(e)}")
    except Exception as e:
        raise ValueError(f"Fel vid hämtning av väderdata: {str(e)}")


# Hämta mocksensorvärden med väderdata från SMHI
def get_mock_sensor_data(location="Stockholm"):
    try:
        # Hämta väderdata för angiven plats (t.ex. Stockholm)
        weather_info = get_weather_data(location)
        
        # Generera mockvärden för andra sensorer
        data = {
            'timestamp': int(time.time()),
            'temperature': round(weather_info['temperature'], 1),  # Temperatur från väderdata
            'soil_moisture': round(random.uniform(10, 60), 1),  # Mockad jordfuktighet
            'humidity': round(weather_info['humidity'], 1),  # Luftfuktighet från väderdata
            'light_intensity': round(weather_info['solar_radiation'], 1)  # Solstrålning som ljusintensitet
        }
        return data
    except ValueError as e:
        # Om väderdata inte kan hämtas, återgå till mockade temperatur- och fuktighetsvärden
        return {
            'timestamp': int(time.time()),
            'temperature': round(random.uniform(18, 35), 1),
            'soil_moisture': round(random.uniform(10, 60), 1),
            'humidity': round(random.uniform(30, 90), 1),
            'light_intensity': round(random.uniform(0, 1000), 1)  # Mockad ljusintensitet
        }

# För testande:
if __name__ == "__main__":
    location = "Stockholm"  # Ändra till önskad plats
    print(get_mock_sensor_data(location))




