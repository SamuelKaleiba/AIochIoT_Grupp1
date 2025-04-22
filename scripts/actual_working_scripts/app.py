import streamlit as st
from PIL import Image
import uuid

from iot_simulation import generate_sensor_data
from aws_setup import rekognition, lex_v2, LEX_BOT_ID, LEX_BOT_ALIAS_ID, LEX_LOCALE_ID, analyze_image, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

def get_s3_object_key(image_name):
    if "/" in image_name:
        return image_name
    else:
        return image_name

# Sidomeny och bakgrund - Lägg till anpassad CSS för att ändra bakgrundsfärg och sidomeny
st.set_page_config(page_title="Smart Vinodling", layout="centered")

# Lägg till CSS för sidomenyn och bakgrund
st.markdown("""
    <style>
        /* Bakgrundsfärg för hela appen */
        body {
            background-color: #f0f8ff;
            font-family: Arial, sans-serif;
        }
        
        /* Sidomeny färg */
        .sidebar .sidebar-content {
            background-color: #e0f7fa;
        }
        
        /* Titeln på sidan */
        .css-18e3th9 {
            color: #2f4f4f;
        }
        
        /* Stil för text i sidan */
        .css-1r6j3c7 {
            color: #2f4f4f;
        }

        /* Försök att få texten i sidomenyn att synas bättre */
        .sidebar .sidebar-header {
            color: #2f4f4f;
        }
        
        /* Anpassad färg på knappar */
        .css-1v0mbdj {
            background-color: #4caf50;
            color: white;
        }
        
        /* Ändra färg på input text */
        .stTextInput>div>div>input {
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
        }
    </style>
    """, unsafe_allow_html=True)

# Titel och beskrivning
st.title("🍇 Smart Vinodling")
st.write("Analysera dina druvor, kontrollera miljödata och ställ frågor till AI-assistenten.")

# === Sidomeny ===
st.sidebar.title("Välj analys")
option = st.sidebar.selectbox(
    "Välj en analys",
    ["Bildanalys", "Miljösensorer", "Chatbot"]
)

# === 1. Bildanalys ===
if option == "Bildanalys":
    st.header("📷 Ladda upp bild på druvor")
    uploaded = st.file_uploader("Välj en bildfil", type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="Uppladdad bild", use_container_width=True)

        st.subheader("🔍 AI-analys via Rekognition")

        try:
            img_bytes = uploaded.getvalue()
            if img_bytes:
                image_name = uploaded.name
                bucket_name = "agnesbucket.1"
                project_version_arn = "arn:aws:rekognition:eu-central-1:390402541367:project/DiseaseDetection1/version/DiseaseDetection1.2025-04-14T11.21.49/1744622509764"

                if 'mjoldagg' in image_name.lower():
                    s3_key = f"sjuk/mjoldagg/{image_name}"
                elif 'frisk' in image_name.lower():
                    s3_key = f"sjuk/frisk/{image_name}"
                elif 'svartrota' in image_name.lower():
                    s3_key = f"sjuk/svartrota/{image_name}"
                else:
                    s3_key = image_name

                try:
                    labels = analyze_image(s3_key, bucket_name, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, project_version_arn)
                    if labels:
                        st.success("Analys klar! Här är vad AI:n hittade:")
                        for label in labels:
                            st.write(f"• **{label}**")
                    else:
                        st.warning("Inga sjukdomar identifierades.")
                except Exception as e:
                    st.error(f"Något gick fel med analysen: {e}")
            else:
                st.error("Bildinnehållet kunde inte laddas korrekt.")
        except Exception as e:
            st.error(f"Något gick fel med analysen: {e}")

# === 2. Miljösensorer ===
elif option == "Miljösensorer":
    st.header("🌿 Miljödata från vinodlingen")

    if st.button("🔄 Uppdatera sensordata"):
        st.rerun()

    sensor_data = generate_sensor_data()

    temp_min, temp_max = 15, 30
    humid_min, humid_max = 40, 80
    soil_min, soil_max = 20, 60

    temp = sensor_data["temperature"]
    humid = sensor_data["humidity"]
    soil = sensor_data["soil_moisture"]

    st.markdown(f"🌡️ **Temperatur:** {temp} °C " +
                ("✅" if temp_min <= temp <= temp_max else "⚠️"))

    st.markdown(f"💧 **Luftfuktighet:** {humid} % " +
                ("✅" if humid_min <= humid <= humid_max else "⚠️"))

    st.markdown(f"🌱 **Jordfuktighet:** {soil} % " +
                ("✅" if soil_min <= soil <= soil_max else "⚠️"))

    st.caption("Gränsvärden används för att indikera om klimatet är lämpligt för vinrankor.")

# === 3. Chatbot ===
elif option == "Chatbot":
    st.header("💬 Prata med AI-assistenten")
    
    # Uppdatera med exempel på frågor som matchar intents definierade i Lex
    st.markdown("💡 **Exempel på frågor:**\n\n- Hur mår plantor?\n- Är plantorna friska?\n- Vad är fel med vinranka?\n- Vad säger bildanalysen?\n- Vad är vädret?\n- Hur blir vädret idag?\n- Är det soligt imorgon?")

    user_input = st.text_input("Skriv en fråga till chatboten:")

    if user_input:
        try:
            response = lex_v2.recognize_text(
                botId="VAN9BJTZBH",
                botAliasId="RTHXTBTLOH",
                localeId="en_US",
                sessionId=str(uuid.uuid4()),
                text=user_input
            )

            # Extrahera och visa meddelanden från Lex
            messages = response.get("messages", [])
            if messages:
                for msg in messages:
                    st.markdown(f"**🤖 Chatbot:** {msg['content']}")
            else:
                st.info("Chatboten hade inget svar.")
        except Exception as e:
            st.error(f"Något gick fel med chatboten: {e}")
