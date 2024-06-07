import requests

url = "https://api.vapi.ai/call/phone"

payload = {
    "maxDurationSeconds": 360,
    "assistantId": "5ea1c6b4-fe29-4751-b4e0-d1e9ac72103c",
    "type": "outboundPhoneCall",
    "phoneNumberId": "5ecbe56c-6b4f-44a3-942b-ede5bc9f0507",
    "customer": {
        "number": "+998993691864",
        "name": "Islom",
        "extension": ""
    },
}
headers = {
    "Authorization": "Bearer 59f3aafd-4c5d-46eb-b777-13585b4099f7",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)