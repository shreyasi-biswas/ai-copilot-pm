import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path="../../apps/api/.env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-lite-latest")

EXTRACTION_PROMPT = """You are analyzing a piece of customer feedback or an interview excerpt for a product manager.

Extract every distinct feature request, pain point, or complaint mentioned in the text below.

Return ONLY valid JSON (no markdown, no explanation) in this exact structure:
{{
  "themes": [
    {{
      "theme": "short name for the feature request or pain point",
      "evidence_quote": "the exact sentence or phrase from the text that supports this",
      "sentiment": "positive | negative | neutral",
      "type": "explicit_ask | implicit_pain_point"
    }}
  ]
}}

If there is nothing relevant in the text, return {{"themes": []}}.

TEXT TO ANALYZE:
{text}
"""


def normalize(s: str) -> str:
    return " ".join(s.split())


def extract_themes(text: str) -> dict:
    """Extract themes from a SINGLE document. Same as before."""
    prompt = EXTRACTION_PROMPT.format(text=text)
    response = model.generate_content(prompt)

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1) if raw.startswith("json") else raw

    result = json.loads(raw)
    normalized_source = normalize(text)

    verified_themes = []
    for theme in result.get("themes", []):
        quote = theme.get("evidence_quote", "")
        if quote and normalize(quote) in normalized_source:
            verified_themes.append(theme)
        else:
            print(f"Discarded unverifiable theme: {theme.get('theme')}")

    return {"themes": verified_themes}


def extract_themes_from_documents(documents: list[dict]) -> list[dict]:
    """
    Process MULTIPLE documents and tag every extracted theme with which
    document it came from. This is the real ingestion entry point.

    documents: a list like [{"id": "doc1", "text": "..."}, {"id": "doc2", "text": "..."}]

    Returns a flat list of themes, each with a "source_id" field added,
    so we can later trace every theme back to its origin document.
    """
    all_themes = []

    for doc in documents:
        doc_id = doc["id"]
        text = doc["text"]

        print(f"Processing document: {doc_id}...")
        result = extract_themes(text)

        for theme in result["themes"]:
            theme["source_id"] = doc_id
            all_themes.append(theme)

    return all_themes


if __name__ == "__main__":
    # Simulating multiple feedback sources — replace with real data later
    sample_documents = [
        {
            "id": "interview_01",
            "text": """
            I really wish the app had dark mode. Also, every time I try to export my data
            to CSV, it takes forever and sometimes just fails silently. The onboarding
            flow was actually pretty smooth though, no complaints there.
            """
        },
        {
            "id": "feedback_ticket_045",
            "text": """
            Please add dark mode!! My eyes hurt using this app at night.
            Also the search feature is way too slow when I have a lot of items.
            """
        },
    ]

    themes = extract_themes_from_documents(sample_documents)
    print("\n--- ALL EXTRACTED THEMES ---")
    print(json.dumps(themes, indent=2))