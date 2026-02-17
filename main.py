import os
import time
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

def get_gmaps_client():
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key Missing")
    return googlemaps.Client(key=api_key)

@app.get("/traffic-forecast")
async def get_forecast(origin: str, destination: str, days: int = 7):
    # --- FIX: Validation MUST be at the very top, before 'try' starts ---
    # This prevents the 'expected except or finally block' SyntaxError
    validated_days = days
    if validated_days > 14:
        validated_days = 14
    if validated_days < 1:
        validated_days = 1
    
    forecast_data = []
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    try:
        gmaps = get_gmaps_client()
        
        for i in range(validated_days):
            current_day = start_date + timedelta(days=i)
            ts = int(current_day.timestamp())
            
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
            
            # Nested Color Logic (Properly Indented)
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
            
        if not forecast_data:
            raise HTTPException(status_code=404, detail="No route data found")

        best_entry = min(forecast_data, key=lambda x: x['seconds'])

        return {
            "status": "success",
            "best_day": {
                "day": best_entry['day'],
                "duration": best_entry['duration']
            },
            "forecast": forecast_data
        }

    except Exception as e:
        # This block now correctly 'closes' the try block
        raise HTTPException(status_code=500, detail=str(e))
