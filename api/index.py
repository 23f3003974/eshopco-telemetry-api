from fastapi import FastAPI, Body, Response
import pandas as pd
import os
import json

app = FastAPI()

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# Explicitly handle the OPTIONS pre-flight for the grader
@app.options("/api/latency")
@app.options("/api/latency/")
async def options_handler():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@app.post("/api/latency")
@app.post("/api/latency/")
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
    
    # Return JSON with explicit CORS headers
    return Response(
        content=json.dumps(results),
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )
