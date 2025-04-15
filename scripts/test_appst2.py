import streamlit as st
import boto3
import requests
import json
from io import BytesIO

# S3-konfiguration
BUCKET_NAME = "agnesbucket.1"
REGION = "eu-central-1"
LAMBDA_API_URL = "https://bb2lvspm0g.execute-api.eu-central-1.amazonaws.com/Lambdaanalyze"

# AWS-klient för S3
s3 = boto3.client("s3", region_name=REGION)

st.header("🖼️ Bladanalys via AI-modell (Amazon Rekognition)")

uploaded_file = st.file_uploader("📷 Ladda upp ett bladfoto (.jpg eller .png)", type=["jpg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Förhandsvisning av bladet", use_column_width=True)

    image_name = st.text_input("🖼️ Namnge bilden (t.ex. blad1.jpg)", value=uploaded_file.name)

    if st.button("🚀 Ladda upp & analysera"):
        try:
            # 1. Ladda upp bilden till S3
            s3.upload_fileobj(
                Fileobj=BytesIO(uploaded_file.read()),
                Bucket=BUCKET_NAME,
                Key=image_name,
                ExtraArgs={"ContentType": uploaded_file.type}
            )
            st.success(f"📤 Bilden '{image_name}' laddades upp till '{BUCKET_NAME}'")

            # 2. Anropa Lambda för analys
            payload = {
                "bucket": BUCKET_NAME,
                "image": image_name
            }

            response = requests.post(LAMBDA_API_URL, json=payload)

            if response.status_code == 200:
                response_json = response.json()
                body = json.loads(response_json["body"])
                st.success(f"🩺 Diagnos: {body.get('result', 'Inget resultat angavs.')}")
            else:
                st.error(f"❌ Lambda returnerade felkod {response.status_code}")
                st.code(response.text)

        except Exception as e:
            st.error(f"🚨 Fel vid uppladdning eller analys: {str(e)}")
else:
    st.info("⬆️ Ladda upp en bild för att börja.")
