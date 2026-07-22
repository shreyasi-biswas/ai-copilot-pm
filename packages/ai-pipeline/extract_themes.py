import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load GEMINI_API_KEY from apps/api/.env
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

def extract_themes(text: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(text=text)
    response = model.generate_content(prompt)

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1) if raw.startswith("json") else raw

    result = json.loads(raw)

    def normalize(s: str) -> str:
        return " ".join(s.split())

    normalized_source = normalize(text)

    verified_themes = []
    for theme in result.get("themes", []):
        quote = theme.get("evidence_quote", "")
        if quote and normalize(quote) in normalized_source:
            verified_themes.append(theme)
        else:
            print(f"⚠️  Discarded unverifiable theme: {theme.get('theme')}")

    return {"themes": verified_themes}


if __name__ == "__main__":
    sample_text = """
    I really wish the app had dark mode. Also, every time I try to export my data
    to CSV, it takes forever and sometimes just fails silently. The onboarding
    flow was actually pretty smooth though, no complaints there.
    """

    result = extract_themes(sample_text)
    print(json.dumps(result, indent=2))