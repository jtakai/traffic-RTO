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

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

@app.get("/traffic-forecast")
async def get_forecast(origin: str, destination: str):
    forecast_data = []
    
    # Predict for 9:00 AM arrivals for the next 7 days
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    try:
        # Initial check to see if both addresses are valid
        test_result = gmaps.distance_matrix(origins=origin, destinations=destination)
        if test_result['rows'][0]['elements'][0]['status'] != 'OK':
            raise HTTPException(status_code=400, detail="One or both addresses are invalid.")

        for i in range(7):
            current_day = start_date + timedelta(days=i)
            ts = int(time.mktime(current_day.timetuple()))
            
            result = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts,
                traffic_model="best_guess"
            )
            
            element = result['rows'][0]['elements'][0]
            forecast_data.append({
                "day": current_day.strftime('%A'),
                "date": current_day.strftime('%m-%d'),
                "duration": element['duration_in_traffic']['text'],
                "seconds": element['duration_in_traffic']['value']
            })
            
        return {
            "status": "success", 
            "origin": origin, 
            "destination": destination, 
            "forecast": forecast_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
