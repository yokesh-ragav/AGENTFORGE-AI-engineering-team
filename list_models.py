import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

url = "https://generativelanguage.googleapis.com/v1beta/models"

response = requests.get(
    url,
    params={"key": api_key},
    timeout=15
)

print("Status:", response.status_code)
print()

if response.status_code == 200:
    models = response.json().get("models", [])

    for model in models:
        methods = model.get("supportedGenerationMethods", [])

        if "generateContent" in methods:
            print(model["name"])
else:
    print(response.text)