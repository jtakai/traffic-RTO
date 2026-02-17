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
    # 1. SIMPLE VALIDATION - No complex blocks
    max_days = 14
    target_days = days if days <= max_days else max_days
    if target_days < 1:
        target_days = 1

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key Missing")

    gmaps = googlemaps.Client(key=api_key)
    forecast_results = []
    
    # Arrival time: Tomorrow at 9:00 AM
    base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # 2. THE PROCESSING LOOP
    for i in range(target_days):
        current_dt = base_time + timedelta(days=i)
        ts_val = int(current_dt.timestamp())
        
        try:
            # Wrap ONLY the specific API call
            result = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts_val,
                traffic_model="best_guess"
            )
            
            element = result['rows'][0]['elements'][0]
            if element['status'] != 'OK':
                continue

            traffic_secs = element['duration_in_traffic']['value']
            
            # Simple Color Mapping
            day_color = "#4CAF50" # Green
            if 1800 < traffic_secs <= 2700:
                day_color = "#FFC107" # Yellow
            elif traffic_secs > 2700:
                day_color = "#F44336" # Red

            forecast_results.append({
                "day": current_dt.strftime('%A'),
                "date": current_dt.strftime('%m-%d'),
                "duration": element['duration_in_traffic']['text'],
                "seconds": traffic_secs,
                "hex_color": day_color
            })
        except:
            continue
            
    # 3. FINAL RESPONSE
    if not forecast_results:
        raise HTTPException(status_code=404, detail="No route data available")

    best_commute = min(forecast_results, key=lambda x: x['seconds'])

    return {
        "status": "success",
        "best_day": {
            "day": best_commute['day'],
            "duration": best_commute['duration']
        },
        "forecast": forecast_results
    }
