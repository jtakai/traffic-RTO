import os
import time
from datetime import datetime, timedelta
import googlemaps
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gmaps_client():
    """Safely retrieves the API key and initializes the client."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="Deployment Error: GOOGLE_MAPS_API_KEY is not set in Vercel."
        )
    return googlemaps.Client(key=api_key)

@app.get("/traffic-forecast")
async def get_forecast(origin: str, destination: str, days: int = 7):
    # 1. Validation and Date Constraint
    if days > 14: days = 14
    if days < 1: days = 1
    
    gmaps = get_gmaps_client()
    forecast_data = []
    
    # Start predicting from tomorrow at 9:00 AM
    # Using .timestamp() is more robust for Vercel/UTC environments
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    try:
        for i in range(days):
            current_day = start_date + timedelta(days=i)
            ts = int(current_day.timestamp())
            
            result = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts,
                traffic_model="best_guess"
            )
            
            element = result['rows'][0]['elements'][0]
            
            # Check if the specific route exists
            if element['status'] != 'OK':
                continue

            secs = element['duration_in_traffic']['value']
            
            # 2. Heat Map Color Logic
            # Green: < 30m | Yellow: 30-45m | Red: > 45m
            color = "#4CAF50" # Green
            if 1800 < secs <= 2700: color = "#FFC107" # Yellow
            elif secs > 2700: color = "#F44336" # Red

            forecast_data.append({
                "day": current_day.strftime('%A'),
                "date": current_day.strftime('%m-%d'),
                "duration": element['duration_in_traffic']['text'],
                "seconds": secs,
                "hex_color": color
            })
            
        if not forecast_data:
            raise HTTPException(status_code=404, detail="No traffic data found for this route.")

        # 3. Best Day Summary Logic
        best_entry = min(forecast_data, key=lambda x: x['seconds'])

        return {
            "status": "success",
            "origin": origin,
            "destination": destination,
            "best_day": {
                "day": best_entry['day'],
                "duration": best_entry['duration'],
                "date": best_entry['date']
            },
            "forecast": forecast_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google API Error: {str(e)}")
