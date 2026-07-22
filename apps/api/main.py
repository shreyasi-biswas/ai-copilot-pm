import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "ai-pipeline"))

from fastapi import FastAPI
from pydantic import BaseModel
from extract_themes import extract_themes_from_documents

app = FastAPI(title="AI Copilot for PMs — API")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-copilot-pm-api"}


class Document(BaseModel):
    id: str
    text: str

class ExtractRequest(BaseModel):
    documents: list[Document]


@app.post("/extract")
def extract(request: ExtractRequest):
    documents = [{"id": doc.id, "text": doc.text} for doc in request.documents]
    themes = extract_themes_from_documents(documents)
    return {"themes": themes}