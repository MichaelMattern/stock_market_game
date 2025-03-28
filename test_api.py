"""
Simple script to test the admin API endpoint
"""
import requests
import json

# Test parameters
API_URL = "http://localhost:8000/admin/accounts/verify"
ADMIN_ID = 1000
API_KEY = "my-secret-admin-key"

# Request headers and body
headers = {
    "Content-Type": "application/json",
    "x-admin-api-key": API_KEY
}
data = {
    "admin_id": ADMIN_ID
}

print(f"Testing admin verification endpoint: {API_URL}")
print(f"Headers: {headers}")
print(f"Data: {data}")

try:
    # Make the request
    response = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=5
    )
    
    # Print response details
    print(f"\nResponse status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    # Try to parse JSON response
    try:
        response_data = response.json()
        print(f"Response JSON: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response text: {response.text}")
    
    # Success or failure
    if response.status_code == 200:
        print("\n✅ Admin verification successful!")
    else:
        print("\n❌ Admin verification failed!")
        
except Exception as e:
    print(f"\nError testing endpoint: {e}")

print("\nIf successful, you should now be able to log in to the admin panel at:")
print("http://localhost:8000/static/admin/login.html")
print("with admin ID 1000 and API key: my-secret-admin-key") 