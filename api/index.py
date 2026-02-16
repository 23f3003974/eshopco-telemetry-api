from fastapi import FastAPI, Body
import pandas as pd
import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Note: Must be False if allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)


FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

@app.get("/api")
def health():
    return {"status": "online"}

@app.post("/api/latency")
async def calculate_metrics(regions: list = Body(...), threshold_ms: int = Body(...)):
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
