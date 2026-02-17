import os
from datetime import datetime, timedelta
import googlemaps
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/traffic-forecast")
async def get_forecast(origin: str, destination: str, days: int = 7):
    # 1. Logic and Validation (Top Level - No Try Block)
    v_days = min(max(days, 1), 14)
    forecast_data = []
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key Missing")

    # Initialize client
    gmaps = googlemaps.Client(key=api_key)
    
    # Base arrival time: Tomorrow at 9:00 AM
    start_dt = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # 2. The Loop
    for i in range(v_days):
        current_day = start_dt + timedelta(days=i)
        ts = int(current_day.timestamp())
        
        try:
            # Wrap ONLY the external API call in a try/except
            result = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts,
                traffic_model="best_guess"
            )
            
            element = result['rows'][0]['elements'][0]
            if element['status'] != 'OK':
                continue

            secs = element['duration_in_traffic']['value']
            
            # Color Logic
            color = "#4CAF50" # Green
            if 1800 < secs <= 2700:
                color = "#FFC107" # Yellow
            elif secs > 2700:
                color = "#F44336" # Red

            forecast_data.append({
                "day": current_day.strftime('%A'),
                "date": current_day.strftime('%m-%d'),
                "duration": element['duration_in_traffic']['text'],
                "seconds": secs,
                "hex_color": color
            })
        except Exception as api_err:
            # If one day fails, log it and keep moving
            print(f"Error on day {i}: {api_err}")
            continue
            
    # 3. Final Response Construction
    if not forecast_data:
        raise HTTPException(status_code=404, detail="No route data found")

    best_day_obj = min(forecast_data, key=lambda x: x['seconds'])

    return {
        "status": "success",
        "best_day": {
            "day": best_day_obj['day'],
            "duration": best_day_obj['duration']
        },
        "forecast": forecast_data
    }
