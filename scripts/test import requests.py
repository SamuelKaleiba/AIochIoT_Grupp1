import requests
import json

def test_lambda_api_gateway():
    # 🔁 Ersätt denna URL med din faktiska API Gateway endpoint (från "Stages")
    url = "https://bb2lvspm0g.execute-api.eu-central-1.amazonaws.com/dev/Lambdaanalyze"

    # 📦 Payload – vad din Lambda förväntar sig
    payload = {
        "bucket": "agnesbucket.1",
        "key": "sjuk/frisk/frisk1.jpg"
    }

    # 🧾 Headers (vanligtvis räcker detta)
    headers = {
        "Content-Type": "application/json"
    }

    # 🚀 Skicka POST-request
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("✅ Statuskod:", response.status_code)
        print("📨 Svar från API:")
        print(response.text)
    except Exception as e:
        print("❌ Fel vid API-anrop:", str(e))

if __name__ == "__main__":
    test_lambda_api_gateway()
