from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse
import pandas as pd
import os

app = FastAPI()

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# A global headers dictionary to ensure consistency
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}

@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content="OK", headers=CORS_HEADERS)

@app.post("/api/latency")
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
    
    return JSONResponse(content=results, headers=CORS_HEADERS)
