import requests
import json

# The local URL where FastAPI runs (usually port 8000)
BASE_URL = "http://127.0.0.1:8000"

def test_traffic_endpoint():
    print("--- Testing Traffic Forecast Endpoint ---")
    
    # 1. Define test parameters
# In test_api.py, update the params:
    params = {
        "origin": "3 Blu Harbor Blvd, Redwood City CA",
        "destination": "1 Infinite Loop, Cupertino, CA",
        "days": 3
    }

    try:
        # 2. Execute the request
        response = requests.get(f"{BASE_URL}/traffic-forecast", params=params)
        
        # 3. Check for success
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Best day to drive: {data['best_day']['day']}")
            print(f"Sample Forecast: {data['forecast'][0]['day']} - {data['forecast'][0]['duration']}")
            # Pretty print the first day for inspection
            # print(json.dumps(data['forecast'][0], indent=2))
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Error detail: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Is 'fastapi dev main.py' running?")

if __name__ == "__main__":
    test_traffic_endpoint()
