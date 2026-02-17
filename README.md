🚗 CommuteWise: Smart Traffic Forecast API
A lightweight FastAPI service deployed on Vercel that leverages the Google Maps Distance Matrix API to predict the best commuting days. This project was specifically designed to help optimize travel between Hermosa Beach and surrounding business hubs using real-time "best guess" traffic models.

🌟 Features
* Predictive Analysis: Queries Google’s traffic models for the next $n$ days to find the statistical "sweet spot" for your commute.
* Color-Coded Insights: Returns HEX codes based on traffic density:
    * 🟢 Green: < 30 mins (Smooth sailing)
    * 🟡 Yellow: 30–45 mins (Moderate)
    * 🔴 Red: > 45 mins (Heavy congestion)
* Vercel Optimized: Built for serverless execution with automated UTC/Local time conversions.
* EV Friendly: Minimal footprint, designed to eventually integrate with EV charging schedules (Hyundai Bluelink).

🛠️ Tech Stack
* Language: Python 3.13
* Framework: FastAPI
* Deployment: Vercel (Serverless Functions)
* API: Google Maps (Distance Matrix)
* Testing: Requests & Pytest

🚀 Deployment & Environment Setup
1. Google Cloud Configuration
1. Enable the Distance Matrix API in your Google Cloud Console.
2. Ensure a Billing Account is linked (required for traffic data).
3. Generate an API Key.

2. Vercel Environment Variables
Add the following key to your Vercel project settings:
Key	Value
Maps_API_KEY	your_api_key_here

Note: After updating environment variables, you must trigger a "Redeploy" in Vercel and uncheck "Use existing Build Cache" to inject the new keys.

📡 API Usage
Endpoint: GET /traffic-forecast
Parameters:

origin (string): Your starting point (e.g., "Hermosa Beach, CA").

destination (string): Your workplace (e.g., "Irvine, CA").

days (int): Number of days to forecast (Max: 14).



Example Request:
Bash:
curl "https://your-project.vercel.app/traffic-forecast?origin=Hermosa+Beach&destination=Irvine&days=5"

Example Response:
JSON
{
  "status": "success",
  "best_day": {
    "day": "Wednesday",
    "duration": "38 mins"
  },
  "forecast": [
    {
      "day": "Monday",
      "date": "02-23",
      "duration": "45 mins",
      "seconds": 2700,
      "hex_color": "#FFC107"
    },
    ...
  ]
}

🧪 Local Development
Install Dependencies:

Bash
pip install "fastapi[standard]" googlemaps requests
Set Local Key:

Bash
export GOOGLE_MAPS_API_KEY=your_key_here
Run Dev Server:

Bash
fastapi dev main.py
Run Test Script:

Bash
python test_api.py
🗺️ Roadmap
[ ] Phase 2: Integrate with Hyundai Bluelink API to suggest departure times based on Ioniq 5 battery state.

[ ] Phase 3: Frontend dashboard for a "Commute Calendar" view.

[ ] Phase 4: SMS Alerts for the "Best Day to Drive" sent every Sunday night.

📄 License
MIT License - Created by Joe Takai




