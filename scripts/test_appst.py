# --- BLADANALYS ---
import json
import requests
import streamlit as st

st.header("🖼️ Bladanalys via AWS Rekognition")

# Input från användaren
uploaded_file = st.file_uploader("📷 Ladda upp ett bladfoto (.jpg eller .png)", type=["jpg", "png"])
bucket_name = st.text_input("🪣 Ange S3-bucket där bilden finns", "my-smartfarm-bucket")
image_name = st.text_input("🖼️ Ange bildens namn i bucketen (t.ex. blad1.jpg)")

# Knapp för att trigga analys
if st.button("🔍 Analysera bild"):
    if uploaded_file and bucket_name and image_name:
        try:
            lambda_url = lambda_url = "https://bb2lvspm0g.execute-api.eu-central-1.amazonaws.com/Lambdaanalyze"
  # <-- din API Gateway URL --justerade den här jäveln, kanske måste bytas i rätt script. fick den vid deployment av API i stage "lambdaanalyze"
            payload = {
                "bucket": bucket_name,
                "image": image_name
            }

            # Anropa Lambda via API Gateway
            response = requests.post(lambda_url, json=payload)

            # Kontrollera att svaret är OK
            if response.status_code == 200:
                response_json = response.json()

                # Lambda svarar med body som är en JSON-sträng
                if "body" in response_json:
                    body = json.loads(response_json["body"])
                    st.success(body.get("result", "✅ Bilden analyserades, men inget resultat hittades."))
                else:
                    st.error("❌ 'body' saknas i svaret från Lambda.")

            else:
                st.error(f"🚨 Lambda returnerade statuskod {response.status_code}")

        except Exception as e:
            st.error(f"❌ Fel vid anrop till Lambda: {str(e)}")
    else:
        st.warning("⚠️ Vänligen fyll i alla fält och ladda upp en bild.")
