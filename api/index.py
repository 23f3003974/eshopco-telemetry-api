from fastapi import FastAPI, Body, Response
import pandas as pd
import os

app = FastAPI()

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# This catches the "pre-flight" request the grader sends
@app.options("/{path:path}")
async def preflight(path: str, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {}

@app.post("/api/latency")
async def calculate_metrics(response: Response, regions: list = Body(...), threshold_ms: int = Body(...)):
    # Attach header to the successful response
    response.headers["Access-Control-Allow-Origin"] = "*"
    
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
