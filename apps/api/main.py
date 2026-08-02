import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "ai-pipeline"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import run_pipeline

app = FastAPI(title="AI Copilot for PMs — API")

# Allow the Next.js frontend (running on a different port) to call this API.
# Without this, browsers block the request entirely — this isn't optional.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-copilot-pm-api"}


class Document(BaseModel):
    id: str
    text: str

class AnalyzeRequest(BaseModel):
    documents: list[Document]


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    documents = [{"id": doc.id, "text": doc.text} for doc in request.documents]
    ranked_clusters = run_pipeline(documents)
    return {"ranked_features": ranked_clusters}