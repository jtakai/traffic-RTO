from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import googlemaps
from datetime import datetime, timedelta
import time

app = FastAPI()

# Enable CORS so your iPhone app can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

gmaps = googlemaps.Client(key=API_KEY)
gmaps = googlemaps.Client(key='AIzaSyBHKTnE_f1rTRanA5tR4ATO2crPuwachU4')

@app.get("/traffic-forecast")
async def get_forecast():
    origin = "3 Blu Harbor Blvd Apt #146, Redwood City, CA 94063"
    destination = "One Apple Park Way, Cupertino, CA 95014"
    forecast = []
    
    # Predict for 9:00 AM arrivals
    start_date = datetime.now().replace(hour=9, minute=0) + timedelta(days=1)

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        ts = int(time.mktime(current_date.timetuple()))
        
        result = gmaps.distance_matrix(
            origins=origin,
            destinations=destination,
            departure_time=ts,
            traffic_model="best_guess"
        )
        
        element = result['rows'][0]['elements'][0]
        forecast.append({
            "day": current_date.strftime('%A'),
            "duration": element['duration_in_traffic']['text'],
            "seconds": element['duration_in_traffic']['value']
        })
        
    return {"forecast": forecast}
