import streamlit as st
import pyodbc
import requests
import pandas as pd
from Mock_data import get_mock_sensor_data  
from db_init import ensure_weather_table_exists, ensure_irrigation_table_exists, ensure_leaf_table_exists

from db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()
ensure_weather_table_exists(cursor)
ensure_irrigation_table_exists(cursor)
ensure_leaf_table_exists(cursor)
conn.commit()
cursor.close()
conn.close()


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

def fetch_weather_history(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = f"""
    SELECT TOP {limit} timestamp, temperatur, luftfuktighet, ljusintensitet 
    FROM Väderdata
    ORDER BY timestamp DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows, columns=["timestamp", "temperature", "humidity", "light_intensity"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df.sort_values("timestamp")


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

            store_weather_data(
            timestamp=data["timestamp"],
            temp=data["temperature"],
            humidity=data["humidity"],
             rain=0,  # placeholder eftersom mockdata inte har regn
            light_intensity=data["light_intensity"]
            )

            # Visa sensorvärden med emojis 
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

            # --- Grafer baserat på aktuell sensordata ---
            st.subheader("📊 Sensorgrafik")
            st.subheader("📈 Temperatur (°C)")
            st.line_chart(pd.DataFrame({"°C": [data['temperature']]}, index=["Nu"]))
            st.subheader("💧 Luftfuktighet (%)")
            st.line_chart(pd.DataFrame({"% Luftfuktighet": [data['humidity']]}, index=["Nu"]))
            st.subheader("💡 Ljusintensitet (W/m²)")
            st.line_chart(pd.DataFrame({"W/m² Ljus": [data['light_intensity']]}, index=["Nu"]))
            st.subheader("🌱 Jordfuktighet (%)")
            st.line_chart(pd.DataFrame({"% Jordfuktighet": [data['soil_moisture']]}, index=["Nu"]))

            # --- Historiska grafer från databasen ---
            st.subheader("📊 Historik från sensordata")

            # Hämta historik från databasen
            df = fetch_weather_history(limit=20)

            # Temperaturhistorik
            st.subheader("📈 Temperatur – senaste 20 mätningar")
            st.line_chart(df.set_index("timestamp")["temperature"])

            # Luftfuktighetshistorik
            st.subheader("💧 Luftfuktighet – senaste 20 mätningar")
            st.line_chart(df.set_index("timestamp")["humidity"])

            # Ljusintensitetshistorik
            st.subheader("💡 Ljusintensitet – senaste 20 mätningar")
            st.line_chart(df.set_index("timestamp")["light_intensity"])
            
        except Exception as e:
            st.error(f"🚨 Fel vid hämtning av sensordata: {str(e)}")

# --- VÄDER ---
if menu == "🌦️ Väder":
    st.header("🌦️ Väderdata från SMHI")
    location = st.text_input("📍 Skriv en plats", "Stockholm")

    if st.button("Hämta väder"):
        try:
            GEOCODE_URL = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={st.secrets['OPENCAGE_KEY']}"
            geo_res = requests.get(GEOCODE_URL)
            coords = geo_res.json()['results'][0]['geometry']
            lat = round(coords['lat'], 6)
            lon = round(coords['lng'], 6)

            WEATHER_URL = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
            weather_data = requests.get(WEATHER_URL).json()

            def weather_emoji(symbol_code):
                return {
                    1: "☀️", 2: "🌤️", 3: "⛅", 4: "☁️", 5: "🌧️",
                    6: "🌧️", 7: "🌦️", 8: "⛈️", 9: "❄️", 10: "🌨️", 11: "🌫️"
                }.get(symbol_code, "❓")

            def weather_description(symbol_code):
                return {
                    1: "Klart", 2: "Lätt molnighet", 3: "Växlande molnighet",
                    4: "Mulet", 5: "Lätt regn", 6: "Regn", 7: "Regnskurar",
                    8: "Åska", 9: "Snö", 10: "Snöbyar", 11: "Dimma"
                }.get(symbol_code, "Okänt väder")

            if 'timeSeries' in weather_data:
                st.subheader("🕒 Prognos kommande timmar")
                for entry in weather_data["timeSeries"][:6]:
                    time = entry["validTime"][11:16]
                    params = {p["name"]: p["values"][0] for p in entry["parameters"]}
                    symbol = params.get("Wsymb2", 0)
                    emoji = weather_emoji(symbol)
                    desc = weather_description(symbol)
                    st.markdown(f"- {emoji} {time} – {desc}, {params.get('t', '?')}°C, 💧 {params.get('r', '?')}%, 🌧️ {params.get('pmean', '?')} mm, 💡 {params.get('swr', '?')} W/m²")

        except Exception as e:
            st.error(f"😵 Något gick fel: {str(e)}")

# --- BLADANALYS ---
if menu == "🖼️ Bladanalys (demo)":
    st.header("🖼️ Bladanalys via AWS Rekognition")

    uploaded_file = st.file_uploader("📷 Ladda upp ett bladfoto (.jpg eller .png)", type=["jpg", "png"])
    bucket_name = st.text_input("🪣 Ange S3-bucket där bilden finns", "agnesbucket.1")
    image_name = st.text_input("🖼️ Ange bildens namn i bucketen")

    if st.button("🔍 Analysera bild"):
        if uploaded_file and bucket_name and image_name:
            try:
                lambda_url = "https://bb2lvspm0g.execute-api.eu-central-1.amazonaws.com/sc"  # Ange din riktiga URL
                payload = {"bucket": bucket_name, "image": image_name}
                res = requests.post(lambda_url, json=payload).json()
                st.write("🩺 Resultat:")
                st.success(res["body"])
            except Exception as e:
                st.error(f"❌ Kunde inte anropa Lambda: {str(e)}")
        else:
            st.warning("⚠️ Vänligen fyll i alla fält och ladda upp en bild.")
