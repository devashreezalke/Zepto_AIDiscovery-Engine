from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zepto AI Discovery Engine API")

# Enable CORS for Vercel dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your specific Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "service": "Zepto AI Discovery Engine API"}

@app.get("/api/insights")
def get_insights():
    """Serves the compiled insights_export.json feed to the dashboard."""
    # Check both data/ and dashboard/public/ locations
    paths = [
        os.path.join("data", "insights_export.json"),
        os.path.join("dashboard", "public", "insights_export.json")
    ]
    for path in paths:
        if os.path.exists(path):
            logger.info(f"Serving insights from {path}")
            return FileResponse(path, media_type="application/json")
            
    return {"error": "Insights data feed is not generated yet. Run pipeline first."}

@app.post("/api/run-pipeline")
def trigger_pipeline():
    """Web-hook to run the ETL ingestion and validation pipeline in the background."""
    import traceback
    try:
        from run_pipeline import run_full_pipeline
        import threading
        
        logger.info("Etl pipeline run requested via Webhook...")
        threading.Thread(target=run_full_pipeline).start()
        return {"status": "Pipeline run triggered in the background."}
    except Exception as e:
        logger.error(f"Failed to trigger pipeline: {e}")
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

if __name__ == '__main__':
    import uvicorn
    # Read port from environment (Railway dynamically assigns PORT)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
