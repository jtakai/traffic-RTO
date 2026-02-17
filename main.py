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
    # --- STEP 1: VALIDATION (MUST BE ABOVE THE TRY BLOCK) ---
    v_days = days
    if v_days > 14:
        v_days = 14
    if v_days < 1:
        v_days = 1
    
    forecast_data = []
    # Using UTC-friendly timestamps for Vercel
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # --- STEP 2: THE TRY BLOCK (NO INTERRUPTIONS ALLOWED) ---
    try:
        gmaps = get_gmaps_client()
        
        for i in range(v_days):
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
            
            # Nested Color Logic
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
        # --- STEP 3: THE MANDATORY EXCEPT BLOCK ---
        raise HTTPException(status_code=500, detail=str(e))
