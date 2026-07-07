import requests

url = "http://127.0.0.1:8000/ask"
payload = {
    "query": "Does Potens Labs reimburse alcoholic drinks during dinners?",
    "doc_ids": ["potens_europe_travel_2026", "potens_consulting_travel_2026"]
}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)
