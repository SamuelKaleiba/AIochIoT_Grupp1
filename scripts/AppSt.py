import streamlit as st
import pyodbc
import requests
import pandas as pd
import boto3
from datetime import datetime
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
from Mock_data import get_mock_sensor_data  
from db_init import ensure_weather_table_exists, ensure_irrigation_table_exists, ensure_leaf_table_exists
from db_connection import get_connection

# --- Appinställningar & CSS-styling ---
st.set_page_config(page_title="Vinodling i Nowhere", page_icon="🌿", layout="centered")
st.markdown("""
    <style>
        .stApp { background-color: #eaf5e5; }  /* Ljusgrön bakgrund */
        section[data-testid="stSidebar"] { background-color: #c2e0c2; }  /* Mörkare grön sidopanel */
        section[data-testid="stSidebar"] .css-1d391kg { color: #003300; }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Smart Farming - Grupp1:s Vinodling i Nowhere")
st.markdown("Här kan du se sensordata, väder, bladanalys och chatta med VäderBot!")

# --- Databasinit ---
conn = get_connection()
cursor = conn.cursor()
ensure_weather_table_exists(cursor)
ensure_irrigation_table_exists(cursor)
ensure_leaf_table_exists(cursor)
conn.commit()
cursor.close()
conn.close()

# --- Funktion för att starta modell ---
def start_model(project_arn, model_arn, version_name, min_inference_units):
    try:
        session = boto3.Session(profile_name='Jagne') # <-- Byt till din AWS-profil
        client = session.client('rekognition', config=Config(region_name='eu-central-1'))
    except NoCredentialsError:
        st.error("❌ AWS SSO-autentisering misslyckades. Kontrollera att du är inloggad.")
        st.stop()

    try:
        st.info('⏳ Startar modellen...')
        response = client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        waiter = client.get_waiter('project_version_running')
        waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])
        st.success("✅ Modell är igång!")
    except Exception as e:
        st.error(f"🚨 Kunde inte starta modellen: {str(e)}")
        st.stop()

# --- Lex funktion ---
def call_lex_bot(user_input):
    try:
        lex_client = boto3.client('lex-runtime', region_name='eu-west-1')
        response = lex_client.post_text(
            botName="VäderBot",      # Anpassa till din väderbots namn, vad den nu heter
            botAlias="Prod",         # Eller "TestBotAlias"
            userId="streamlit-user",
            inputText=user_input
        )
        return response.get("message", "❓ Inget svar från boten.")
    except Exception as e:
        return f"❌ Fel: {str(e)}"

# --- Väderdata till DB ---
def store_weather_data(timestamp, temp, humidity, rain, light_intensity):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO Väderdata (timestamp, temperatur, luftfuktighet, nederbord, ljusintensitet)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (timestamp, temp, humidity, rain, light_intensity))
    conn.commit()
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

# --- Meny ---
menu = st.sidebar.radio("Välj funktion", [
    "📈 Sensoranalys", 
    "🌦️ Väder", 
    "🖼️ Bladanalys (demo)", 
    "🤖 VäderBot (chat)"
])

# --- SENSOR ---
if menu == "📈 Sensoranalys":
    st.header("📈 Sensorvärden & Bevattningsrekommendation")
    location = st.text_input("📍 Ange plats (för väderdata)", "Stockholm")
    if st.button("🔍 Hämta sensordata"):
        try:
            data = get_mock_sensor_data(location)
            store_weather_data(data["timestamp"], data["temperature"], data["humidity"], 0, data["light_intensity"])
            st.subheader(f"📍 Sensorvärden i {location}")
            st.write(f"🌡️ **Temperatur:** {data['temperature']}°C")
            st.write(f"💧 **Luftfuktighet:** {data['humidity']}%")
            st.write(f"💡 **Ljusintensitet:** {data['light_intensity']} W/m²")
            st.write(f"🌱 **Jordfuktighet (simulerad):** {data['soil_moisture']}%")
            if data['soil_moisture'] < 30 and data['temperature'] > 20:
                st.warning("💧 Bevattning rekommenderas!")
            else:
                st.success("✅ Ingen bevattning krävs.")
            st.subheader("📊 Sensorgrafik")
            st.line_chart(pd.DataFrame({"°C": [data['temperature']]}, index=["Nu"]))
            st.line_chart(pd.DataFrame({"% Luftfuktighet": [data['humidity']]}, index=["Nu"]))
            st.line_chart(pd.DataFrame({"W/m² Ljus": [data['light_intensity']]}, index=["Nu"]))
            st.line_chart(pd.DataFrame({"% Jordfuktighet": [data['soil_moisture']]}, index=["Nu"]))
            st.subheader("📊 Historik från sensordata")
            df = fetch_weather_history(limit=20)
            st.line_chart(df.set_index("timestamp")["temperature"])
            st.line_chart(df.set_index("timestamp")["humidity"])
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

            def weather_emoji(code): return {
                1: "☀️", 2: "🌤️", 3: "⛅", 4: "☁️", 5: "🌧️", 6: "🌧️",
                7: "🌦️", 8: "⛈️", 9: "❄️", 10: "🌨️", 11: "🌫️"
            }.get(code, "❓")
            def weather_desc(code): return {
                1: "Klart", 2: "Lätt molnighet", 3: "Växlande molnighet",
                4: "Mulet", 5: "Lätt regn", 6: "Regn", 7: "Regnskurar",
                8: "Åska", 9: "Snö", 10: "Snöbyar", 11: "Dimma"
            }.get(code, "Okänt väder")

            st.subheader("🕒 Prognos kommande timmar")
            for entry in weather_data["timeSeries"][:6]:
                time = entry["validTime"][11:16]
                params = {p["name"]: p["values"][0] for p in entry["parameters"]}
                sym = params.get("Wsymb2", 0)
                st.markdown(f"- {weather_emoji(sym)} {time} – {weather_desc(sym)}, {params.get('t', '?')}°C, 💧 {params.get('r', '?')}%, 🌧️ {params.get('pmean', '?')} mm, 💡 {params.get('swr', '?')} W/m²")
        except Exception as e:
            st.error(f"😵 Något gick fel: {str(e)}")

# --- BLADANALYS ---
if menu == "🖼️ Bladanalys (demo)":
    st.header("🖼️ Bladanalys via AWS Rekognition")

    st.subheader("🚀 Starta analysmodell (Custom Labels)")
    if st.button("🟢 Starta modell"):
        project_arn = 'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/1744621659141' #'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/1744621659141'
        model_arn = 'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/version/DiseaseDetection1.2025-04-14T11.21.49/1744622509764' #'arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/version/DiseaseDetection1.2025-04-14T11.21.49/1744622509764'
        version_name = 'DiseaseDetection1.2025-04-14T11.21.49'
        min_inference_units = 1
        start_model(project_arn, model_arn, version_name, min_inference_units)

    uploaded_file = st.file_uploader("📷 Ladda upp ett bladfoto (.jpg eller .png)", type=["jpg", "png"])
    bucket_name = st.text_input("🪣 Ange S3-bucket där bilden finns", "agnesbucket.1")
    image_name = st.text_input("🖼️ Ange bildens namn i bucketen")

    if st.button("🔍 Analysera bild"):
        if uploaded_file and bucket_name and image_name:
            try:
                lambda_url = "https://bb2lvspm0g.execute-api.eu-central-1.amazonaws.com/sc"
                payload = {"bucket": bucket_name, "image": image_name}
                res = requests.post(lambda_url, json=payload)
                st.write("🔍 Rått svar från Lambda (text):", res.text)
                try:
                    json_res = res.json()
                    st.write("🧪 JSON-dekodat svar:", json_res)
                    st.success(json_res.get("body", "❌ 'body' saknas i JSON"))
                except Exception as json_error:
                    st.error(f"❌ Kunde inte tolka svaret som JSON: {str(json_error)}")
            except Exception as e:
                st.error(f"❌ Kunde inte anropa Lambda: {str(e)}")
        else:
            st.warning("⚠️ Vänligen fyll i alla fält och ladda upp en bild.")

# --- VÄDERBOT CHAT ---
if menu == "🤖 VäderBot (chat)":
    st.header("🤖 Chatta med VäderBot")
    user_input = st.text_input("Ställ en väderrelaterad fråga:")
    if user_input:
        lex_response = call_lex_bot(user_input)
        st.success(f"VäderBot: {lex_response}")
