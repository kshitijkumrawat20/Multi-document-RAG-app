import requests
import json

# Test data
test_data = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is covered for room rent and ICU charges?"
    ]
}

# Headers
headers = {
    "Authorization": "Bearer cc13b8bb7f4bc1570c8a39bda8c9d4c34b2be6b8abe1044c89abf49b28cee3f8",
    "Content-Type": "application/json"
}

# Make the request
response = requests.post(
    "http://127.0.0.1:8000/api/v1/hackrx/run",
    headers=headers,
    data=json.dumps(test_data)
)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")