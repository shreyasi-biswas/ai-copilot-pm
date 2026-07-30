import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "ai-pipeline"))

from fastapi import FastAPI
from pydantic import BaseModel
from pipeline import run_pipeline

app = FastAPI(title="AI Copilot for PMs — API")


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
    """
    The main product endpoint: takes raw documents (interviews, feedback, etc.)
    and returns a ranked, evidence-backed list of feature clusters —
    the actual output a PM would look at.
    """
    documents = [{"id": doc.id, "text": doc.text} for doc in request.documents]
    ranked_clusters = run_pipeline(documents)
    return {"ranked_features": ranked_clusters}