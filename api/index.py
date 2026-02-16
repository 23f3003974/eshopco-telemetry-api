from fastapi import FastAPI, Body, Response
import pandas as pd
import os
import json

app = FastAPI()

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# This is the "Everything Allowed" header set
FINAL_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
    "Access-Control-Allow-Headers": "*",  # This is the key change
    "Access-Control-Max-Age": "86400",
}

@app.options("/{path:path}")
async def options_handler():
    return Response(status_code=200, headers=FINAL_CORS)

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
    
    return Response(
        content=json.dumps(results),
        media_type="application/json",
        headers=FINAL_CORS
    )
