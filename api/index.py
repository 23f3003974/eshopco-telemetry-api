from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Permissive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE_PATH = os.path.join(os.path.dirname(__file__), "telemetry_pings.json")

# This will catch BOTH /api and /api/latency if you use the catch-all rewrite
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
    return results

@app.get("/api/health")
def health():
    return {"status": "online"}
