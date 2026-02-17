import os
import googlemaps
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 1. Do NOT initialize the client here at the top level.
# Line 13 was causing the crash because GOOGLE_API_KEY was None at runtime.

@app.get("/traffic-forecast")
async def get_forecast(origin: str, destination: str, days: int = 7):
    # 2. Fetch the key inside the request handler
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="Deployment Error: GOOGLE_MAPS_API_KEY is not set in Vercel Environment Variables."
        )

    try:
        # 3. Initialize the client safely here
        gmaps = googlemaps.Client(key=api_key)
        
    # Limit days to prevent API abuse (Google charges per request)
    if days > 14: days = 14
    
    forecast_data = []
    start_date = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=1)

    try:
        for i in range(days):
            current_day = start_date + timedelta(days=i)
            ts = int(time.mktime(current_day.timetuple()))
            
            result = gmaps.distance_matrix(
                origins=origin,
                destinations=destination,
                departure_time=ts,
                traffic_model="best_guess"
            )
            
            element = result['rows'][0]['elements'][0]
            secs = element['duration_in_traffic']['value']
            
            # --- COLOR LOGIC (Backend Calculated) ---
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
            
        return {"origin": origin, "destination": destination, "forecast": forecast_data}

except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google API Error: {str(e)}")
