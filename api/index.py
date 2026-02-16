from fastapi import FastAPI, Body, Response
import pandas as pd
import os
import json

app = FastAPI()

# Make sure the data is saved in the same directory as this file
FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
        "Access-Control-Max-Age": "86400",
    }

@app.options("/{path:path}")
async def handle_options():
    return Response(status_code=200, headers=get_cors_headers())

@app.post("/api/latency")
async def calculate_metrics(regions: list = Body(...), threshold_ms: int = Body(...)):
    # Using the data you just provided
    try:
        df = pd.read_json(FILE_PATH)
    except Exception:
        # Fallback if file reading fails
        return Response(content=json.dumps({"error": "Data file missing"}), status_code=500, headers=get_cors_headers())

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
    
    return Response(
        content=json.dumps(results),
        media_type="application/json",
        headers=get_cors_headers()
    )
