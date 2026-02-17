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
@app.get("/")
async def root():
    return {"message": "Traffic API is Live", "usage": "/traffic-forecast?origin=...&destination=..."}

@app.get("/favicon.ico")
async def favicon():
    return {"status": "no-favicon"}

@app.get("/traffic-forecast")
async def get_forecast(origin: str, destination: str, days: int = 7):
    # 1. FLAT VALIDATION (No blocks that can cause syntax errors)
    safe_days = days
    if safe_days > 14: safe_days = 14
    if safe_days < 1: safe_days = 1
    
#    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    api_key = "AIzaSyBHKTnE_f1rTRanA5tR4ATO2crPuwachU4"
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key Missing")

    gmaps = googlemaps.Client(key=api_key)
    forecast_list = []
    
    # Start time: Tomorrow at 9:00 AM
    start_point = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # 2. PROCESSING LOOP
    for i in range(safe_days):
        current_dt = start_point + timedelta(days=i)
        ts_unix = int(current_dt.timestamp())
        
        # We only wrap the ACTUAL network call, keeping the logic flat
        try:
            res = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts_unix,
                traffic_model="best_guess"
            )
            
            element = res['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                traffic_secs = element['duration_in_traffic']['value']
                
                # Simple Color Mapping
                route_color = "#4CAF50" # Green
                if 1800 < traffic_secs <= 2700: route_color = "#FFC107" # Yellow
                elif traffic_secs > 2700: route_color = "#F44336" # Red

                forecast_list.append({
                    "day": current_dt.strftime('%A'),
                    "date": current_dt.strftime('%m-%d'),
                    "duration": element['duration_in_traffic']['text'],
                    "seconds": traffic_secs,
                    "hex_color": route_color
                })
        except:
            continue
            
    # 3. FINAL RESPONSE
    if not forecast_list:
        raise HTTPException(status_code=404, detail="No route data found")

    winner = min(forecast_list, key=lambda x: x['seconds'])

    return {
        "status": "success",
        "best_day": { "day": winner['day'], "duration": winner['duration'] },
        "forecast": forecast_list
    }
