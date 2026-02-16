from fastapi import FastAPI, Body, Response
import pandas as pd
import os
import json

app = FastAPI()

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# 1. The OPTIONS handler for the pre-flight check
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

# 2. The POST handler for the actual logic
@app.post("/api/latency")
async def calculate_metrics(regions: list = Body(...), threshold_ms: int = Body(...)):
    if not os.path.exists(FILE_PATH):
        return Response(content=json.dumps({"error": "file not found"}), status_code=404)

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
    
    # Returning Response directly with headers to ensure CORS compliance
    return Response(
        content=json.dumps(results),
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
