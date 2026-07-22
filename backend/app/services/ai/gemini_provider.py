"""
Google Gemini API LLM Provider implementation.
Utilizes Gemini API to extract structured JSON summaries (dates, deadlines, action items, locations).
"""

import json
import httpx
from typing import Dict, Any
from app.config.config import settings
from app.services.ai.base_provider import LLMProvider


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    async def summarize_email(self, subject: str, sender: str, content: str) -> Dict[str, Any]:
        """
        Uses Google Gemini API to produce structured email summary JSON.
        """
        api_key = settings.GEMINI_API_KEY
        
        # If API key is missing or dummy, fallback to structured extraction safely
        if not api_key or api_key == "your-gemini-api-key":
            return self._fallback_summary(subject, sender, content)

        prompt = f"""You are an expert executive email assistant. Analyze the following email and extract structured information in JSON format ONLY.

Email Details:
Sender: {sender}
Subject: {subject}
Content: {content[:3000]}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "summary_headline": "A concise headline describing the email core purpose",
  "bullet_points": ["Key summary point 1", "Key summary point 2"],
  "extracted_dates": ["List of dates mentioned, e.g. 5 August"],
  "extracted_times": ["List of times mentioned, e.g. 11:00 AM"],
  "extracted_deadlines": ["List of deadlines mentioned"],
  "extracted_locations": ["List of physical or virtual locations mentioned"],
  "action_items": ["Action items required from recipient"],
  "important_names": ["Important contact names mentioned"],
  "important_links": ["Important URLs or links mentioned"]
}}
Do NOT include markdown block syntax like ```json. Output raw JSON string.
"""

        try:
            # Using REST API endpoint for Google Gemini 1.5 Flash
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned_text = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
                    parsed = json.loads(cleaned_text)
                    return self._validate_and_normalize(parsed, subject)
                else:
                    print(f"[GeminiProvider] Gemini API HTTP error {response.status_code}: {response.text}")
                    return self._fallback_summary(subject, sender, content)
        except Exception as err:
            print(f"[GeminiProvider] Exception during Gemini summarization: {str(err)}")
            return self._fallback_summary(subject, sender, content)

    def _validate_and_normalize(self, parsed: Dict[str, Any], default_headline: str) -> Dict[str, Any]:
        """Ensures all expected array fields are present and properly typed."""
        return {
            "summary_headline": str(parsed.get("summary_headline", default_headline)),
            "bullet_points": list(parsed.get("bullet_points", [default_headline])),
            "extracted_dates": list(parsed.get("extracted_dates", [])),
            "extracted_times": list(parsed.get("extracted_times", [])),
            "extracted_deadlines": list(parsed.get("extracted_deadlines", [])),
            "extracted_locations": list(parsed.get("extracted_locations", [])),
            "action_items": list(parsed.get("action_items", [])),
            "important_names": list(parsed.get("important_names", [])),
            "important_links": list(parsed.get("important_links", [])),
        }

    def _fallback_summary(self, subject: str, sender: str, content: str) -> Dict[str, Any]:
        """
        Deterministic heuristic summary generator when API key is unconfigured or offline.
        """
        headline = subject if subject and subject != "(No Subject)" else f"Important Email from {sender}"
        snippet_lines = [line.strip() for line in content.split("\n") if line.strip()]
        bullets = snippet_lines[:3] if snippet_lines else ["Important incoming email requiring review."]

        return {
            "summary_headline": headline,
            "bullet_points": bullets,
            "extracted_dates": [],
            "extracted_times": [],
            "extracted_deadlines": [],
            "extracted_locations": [],
            "action_items": ["Review full email content in inbox."],
            "important_names": [sender],
            "important_links": [],
        }
