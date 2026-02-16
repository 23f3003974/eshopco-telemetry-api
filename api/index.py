from fastapi import FastAPI, Body, Response, Request
import pandas as pd
import os

app = FastAPI()

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# Explicitly handle OPTIONS for the specific path
@app.options("/api/latency")
async def options_handler():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

@app.post("/api/latency")
async def calculate_metrics(regions: list = Body(...), threshold_ms: int = Body(...)):
    # Calculate metrics
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
    
    # Return with explicit headers to bypass middleware issues
    return Response(
        content=pd.Series(results).to_json(),
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
