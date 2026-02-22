from fastapi import FastAPI, Body, Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json

app = FastAPI()

# Optional: Add Middleware as a second layer of defense
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

@app.post("/api/latency")
async def calculate_metrics(regions: list = Body(...), threshold_ms: int = Body(...)):
    try:
        # Check if file exists to prevent crash
        if not os.path.exists(FILE_PATH):
             return Response(content=json.dumps({"error": f"File not found at {FILE_PATH}"}), status_code=404)
        
        df = pd.read_json(FILE_PATH)
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500)

    results = {}
    for region in regions:
        region_df = df[df['region'] == region.lower()]
        if not region_df.empty:
            results[region] = {
                "avg_latency": float(region_df['latency_ms'].mean()),
                "p95_latency": float(region_df['latency_ms'].quantile(0.95)),
                "avg_uptime": float(region_df['uptime_pct'].mean()),
                "breaches": int((region_df['latency_ms'] > threshold_ms).sum())
            }
    
    return results # FastAPI automatically handles JSON conversion and status 200
