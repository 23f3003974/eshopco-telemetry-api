from fastapi import FastAPI, Body, Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Standard Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

@app.get("/api")
def health():
    return {"status": "online"}

@app.post("/api")
async def calculate_metrics(response: Response, regions: list = Body(...), threshold_ms: int = Body(...)):
    # Manual Header Injection (This fixes the "Enable CORS" error for good)
    response.headers["Access-Control-Allow-Origin"] = "*"
    
    if not os.path.exists(FILE_PATH):
        return {"error": "Data file not found"}

    df = pd.read_json(FILE_PATH)
    results = {}
    
    for region in regions:
        region_df = df[df['region'] == region]
        if region_df.empty:
            continue
            
        results[region] = {
            "avg_latency": float(region_df['latency_ms'].mean()),
            "p95_latency": float(region_df['latency_ms'].quantile(0.95)),
            "avg_uptime": float(region_df['uptime_pct'].mean()),
            "breaches": int((region_df['latency_ms'] > threshold_ms).sum())
        }
        
    return results
