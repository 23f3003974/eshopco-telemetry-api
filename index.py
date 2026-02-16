from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Force the path to be local to the api folder
FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

@app.get("/api")
def health_check():
    return {"status": "alive", "file_exists": os.path.exists(FILE_PATH)}

@app.post("/api")
async def calculate_metrics(regions: list = Body(...), threshold_ms: int = Body(...)):
    df = pd.read_json(FILE_PATH)
    results = {}
    for region in regions:
        region_df = df[df['region'] == region]
        if not region_df.empty:
            results[region] = {
                "avg_latency": float(region_df['latency_ms'].mean()),
                "p95_latency": float(region_df['latency_ms'].quantile(0.95)),
                "avg_uptime": float(region_df['uptime_pct'].mean()),
                "breaches": int((region_df['latency_ms'] > threshold_ms).sum())
            }
    return results
