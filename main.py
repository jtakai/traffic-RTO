import os
import time
from datetime import datetime, timedelta
import googlemaps
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your iPhone app to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the API key from the environment (Vercel Dashboard)
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GOOGLE_API_KEY:
    # This helps you debug if you forgot to add the key to Vercel
    print("WARNING: GOOGLE_MAPS_API_KEY is not set!")

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

@app.get("/traffic-forecast")
async def get_forecast():
    origin = "3 Blu Harbor Blvd Apt #146, Redwood City, CA 94063"
    destination = "One Apple Park Way, Cupertino, CA 95014"
    forecast_data = []
    
    # Target 9:00 AM arrival for the next 7 days
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    try:
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
            
        return {"status": "success", "forecast": forecast_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
