import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

headers = {
    "Content-Type": "application/json"
}

params = {
    "key": api_key
}

data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with exactly: AI Engineering Team is online."
                }
            ]
        }
    ]
}

print("Sending request...")

response = requests.post(
    url,
    headers=headers,
    params=params,
    json=data,
    timeout=15
)

print("Status:", response.status_code)
print("Response:")
print(response.text)