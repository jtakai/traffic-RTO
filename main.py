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
    # 1. Validation (No 'try' block here - keeps the parser happy)
    target_days = min(max(days, 1), 14)
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key Missing")

    gmaps = googlemaps.Client(key=api_key)
    forecast_list = []
    
    # Base arrival time: Tomorrow at 9:00 AM
    start_point = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # 2. Processing Loop
    for i in range(target_days):
        current_dt = start_point + timedelta(days=i)
        ts_unix = int(current_dt.timestamp())
        
        try:
            # We only wrap the external network call
            res = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts_unix,
                traffic_model="best_guess"
            )
            
            element = res['rows'][0]['elements'][0]
            if element['status'] != 'OK':
                continue

            traffic_secs = element['duration_in_traffic']['value']
            
            # Simple Color Mapping
            route_color = "#4CAF50" # Green
            if 1800 < traffic_secs <= 2700:
                route_color = "#FFC107" # Yellow
            elif traffic_secs > 2700:
                route_color = "#F44336" # Red

            forecast_list.append({
                "day": current_dt.strftime('%A'),
                "date": current_dt.strftime('%m-%d'),
                "duration": element['duration_in_traffic']['text'],
                "seconds": traffic_secs,
                "hex_color": route_color
            })
        except:
            continue
            
    # 3. Final Response
    if not forecast_list:
        raise HTTPException(status_code=404, detail="No route data found")

    winner = min(forecast_list, key=lambda x: x['seconds'])

    return {
        "status": "success",
        "best_day": {
            "day": winner['day'],
            "duration": winner['duration']
        },
        "forecast": forecast_list
    }
