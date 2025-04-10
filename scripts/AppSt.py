import streamlit as st
import pyodbc
import requests
import pandas as pd
from Mock_data import get_mock_sensor_data  

from db_connection import get_connection

conn = get_connection()

# Funktion för att lagra väderdata i databasen
def store_weather_data(timestamp, temp, humidity, rain, light_intensity):
    conn = get_connection()
    cursor = conn.cursor()

    # SQL-fråga för att sätta in väderdata i databasen
    query = """
    INSERT INTO Väderdata (timestamp, temperatur, luftfuktighet, nederbord, ljusintensitet)
    VALUES (?, ?, ?, ?, ?)
"""
    cursor.execute(query, (timestamp, temp, humidity, rain, light_intensity))
    conn.commit()  # Spara ändringarna
    cursor.close()
    conn.close()

# --- Apputv ---
# --- SIDHUVUD ---

st.set_page_config(page_title="Vinodling i Nowhere", page_icon="🌿", layout="centered")
st.title("🌿 Smart Farming - Grupp1:s Vinodling i Nowhere")
st.markdown("Här kan du se sensordata, väder och bladanalys")

# --- MENY ---
menu = st.sidebar.radio("Välj funktion", ["📈 Sensoranalys", "🌦️ Väder", "🖼️ Bladanalys (demo)"])

# --- SENSORANALYS ---
if menu == "📈 Sensoranalys":
        st.header("📈 Sensorvärden & Bevattningsrekommendation")
location = st.text_input("📍 Ange plats (för väderdata)", "Stockholm")

if st.button("🔍 Hämta sensordata"):
        try:
            data = get_mock_sensor_data(location)

            # Visa sensorvärden med emojis och tydlig presentation
            st.subheader(f"📍 Sensorvärden i {location}")
            st.write(f"🌡️ **Temperatur:** {data['temperature']}°C")
            st.write(f"💧 **Luftfuktighet:** {data['humidity']}%")
            st.write(f"💡 **Ljusintensitet:** {data['light_intensity']} W/m²")
            st.write(f"🌱 **Jordfuktighet (simulerad):** {data['soil_moisture']}%")

            # Bevattningslogik
            if data['soil_moisture'] < 30 and data['temperature'] > 20:
                st.warning("💧 Bevattning rekommenderas!")
            else:
                st.success("✅ Ingen bevattning krävs.")

            # --- Grafer baserat på sensordata ---
            st.subheader("📊 Sensorgrafik")
            # Graf för temperatur
            st.subheader("📈 Temperatur")
            st.line_chart(pd.DataFrame({"°C": [data['temperature']]}, index=["Aktuell"]))

            # Graf för luftfuktighet
            st.subheader("💧 Luftfuktighet")
            st.line_chart(pd.DataFrame({"%": [data['humidity']]}, index=["Aktuell"]))

            # Graf för ljusintensitet
            st.subheader("💡 Ljusintensitet")
            st.line_chart(pd.DataFrame({"W/m²": [data['light_intensity']]}, index=["Aktuell"]))

            # Graf för jordfuktighet
            st.subheader("🌱 Jordfuktighet")
            st.line_chart(pd.DataFrame({"%": [data['soil_moisture']]}, index=["Aktuell"]))

        except Exception as e:
            st.error(f"🚨 Fel vid hämtning av sensordata: {str(e)}")

# --- VÄDER ---
if menu == "🌦️ Väder":
        st.header("🌦️ Väderdata från SMHI")
location = st.text_input("📍 Skriv en plats", "Stockholm")

if st.button("Hämta väder"):
        try:
            # Hämta lat/lon från OpenCage
            GEOCODE_URL = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={st.secrets['OPENCAGE_KEY']}"
            geo_res = requests.get(GEOCODE_URL)
            geo_res.raise_for_status()
            geo_data = geo_res.json()

            if not geo_data['results']:
                st.error("❌ Kunde inte hitta platsen. Försök med en annan.")
            else:
                coords = geo_data['results'][0]['geometry']
                lat = round(coords['lat'], 6)
                lon = round(coords['lng'], 6)

                WEATHER_URL = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
                weather_res = requests.get(WEATHER_URL)
                weather_res.raise_for_status()
                weather_data = weather_res.json()

                if 'timeSeries' not in weather_data:
                    st.error("⚠️ Kunde inte hämta väderdata för denna plats.")
                else:
                    forecast = weather_data['timeSeries'][0]['parameters']
                    weather_info = {param['name']: param['values'][0] for param in forecast}

                    st.subheader(f"📍 Aktuellt väder i {location}")
                    st.write(f"🌡️ **Temperatur:** {weather_info.get('t', 'N/A')}°C")
                    st.write(f"💧 **Luftfuktighet:** {weather_info.get('r', 'N/A')}%")
                    st.write(f"🌧️ **Nederbörd:** {weather_info.get('pmean', 'N/A')} mm")
                    st.write(f"💡 **Ljusintensitet (Solstrålning):** {weather_info.get('swr', 'N/A')} W/m²")  # Solstrålning

                    # --- Förbered listor för grafer ---
                    temp_list = []  # För temperatur
                    rain_list = []  # För nederbörd
                    humidity_list = []  # För luftfuktighet
                    light_intensity_list = []  # För ljusintensitet (solstrålning)
                    labels = []  # För tidsstämplar

                    text_forecast = []  # För att visa prognosen som text

                    # Loop genom väderprognoser (t.ex. de första 10 timmarna)
                    for entry in weather_data["timeSeries"][:10]:
                        time = entry["validTime"][11:16]  # Extrahera tiden
                        params = {p["name"]: p["values"][0] for p in entry["parameters"]}

                        temp = params.get("t")  # Temperatur
                        rain = params.get("pmean", 0)  # Nederbörd
                        humidity = params.get("r")  # Luftfuktighet
                        solar_radiation = params.get("swr", 0)  # Solstrålning (ljusintensitet)
                        symbol = params.get("Wsymb2", 0)  # Väderikon

                    def weather_emoji(symbol):
                        emoji = weather_emoji(symbol)  # Emoji för väder

                    def weather_description(symbol):
                        weather_descriptions = {
                            1: "Klart väder",
                            2: "Delvis molnigt",
                            3: "Molnigt",
                            4: "Mycket molnigt",
                            5: "Regn",
                            6: "Åska",
                            7: "Snö",
                            8: "Blåsigt",
                            9: "Åska med regn",
                            10: "Snöstorm",
                            11: "Storm",
                        }
                        return weather_descriptions.get(symbol, "Okänt väder")

                        # Lägg till värden i listorna för grafer
                        temp_list.append(temp)
                        rain_list.append(rain)
                        humidity_list.append(humidity)
                        light_intensity_list.append(solar_radiation)
                        labels.append(f"{time} {emoji}")

                        # Lägg till textprognos
                        forecast_text = f"{emoji} {time} – {desc}, {temp}°C, 💧 {humidity}%, 🌧️ {rain} mm, 💡 {solar_radiation} W/m²"
                        text_forecast.append(forecast_text)

                    # --- Visa textprognos ---
                    st.subheader("🕒 Prognos kommande timmar")
                    for row in text_forecast:
                        st.markdown(f"- {row}")

                    # --- Visa grafer ---
                    st.subheader("📊 Temperatur")
                    st.line_chart(pd.DataFrame({"°C": temp_list}, index=labels))

                    st.subheader("🌧️ Nederbörd (mm)")
                    st.line_chart(pd.DataFrame({"mm": rain_list}, index=labels))

                    st.subheader("💧 Luftfuktighet (%)")
                    st.line_chart(pd.DataFrame({"%": humidity_list}, index=labels))

                    st.subheader("💡 Ljusintensitet (W/m²)")
                    st.line_chart(pd.DataFrame({"W/m²": light_intensity_list}, index=labels))

        except requests.exceptions.RequestException as e:
            st.error(f"🚨 Fel vid API-anrop: {str(e)}")
        except Exception as e:
            st.error(f"😵 Något gick fel: {str(e)}")

# --- BLADANALYS ---
if menu == "🖼️ Bladanalys (demo)":
        st.header("🖼️ Bladanalys via AWS Rekognition")

uploaded_file = st.file_uploader("📷 Ladda upp ett bladfoto (.jpg eller .png)", type=["jpg", "png"])
bucket_name = st.text_input("🪣 Ange S3-bucket där bilden finns", "my-smartfarm-bucket")
image_name = st.text_input("🖼️ Ange bildens namn i bucketen")

if st.button("🔍 Analysera bild"):
        if uploaded_file and bucket_name and image_name:
            try:
                lambda_url = "https://<din-api-gateway-url>/blad-analys"  # Ange din riktiga URL
                payload = {"bucket": bucket_name, "image": image_name}
                res = requests.post(lambda_url, json=payload).json()
                st.write("🩺 Resultat:")
                st.success(res["body"])
            except Exception as e:
                st.error(f"❌ Kunde inte anropa Lambda: {str(e)}")
        else:
            st.warning("⚠️ Vänligen fyll i alla fält och ladda upp en bild.")
