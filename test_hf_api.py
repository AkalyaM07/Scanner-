import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

url = "https://api-inference.huggingface.co/models/google/flan-t5-small"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    url,
    headers=headers,
    json={"inputs": "Hello"}
)

print("STATUS CODE:", response.status_code)
print("RESPONSE:")
print(response.text)