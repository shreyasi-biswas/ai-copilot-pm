from fastapi import FastAPI

app = FastAPI(title="AI Copilot for PMs — API")

@app.get("/health")
def health_check():
    """Simple endpoint to confirm the API is alive and responding."""
    return {"status": "ok", "service": "ai-copilot-pm-api"}