import requests
from typing import Dict, Optional
from .base import LLMProvider

class LocalClient(LLMProvider):
    def __init__(self, endpoint_url: str = "http://localhost:5000/v1/completions"):
        self.endpoint_url = endpoint_url

    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        # This is a simplified example assuming a specific local API format.
        # Adjust payload based on the actual local LLM server (e.g., Oobabooga, vLLM).
        
        payload = {
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        if context:
            # Inject context into prompt if the API doesn't support system messages directly
            # or simply ignore if not needed.
            pass

        try:
            response = requests.post(self.endpoint_url, json=payload)
            response.raise_for_status()
            data = response.json()
            # Adjust response parsing based on actual API
            return data.get("choices", [{}])[0].get("text", "").strip()
        except Exception as e:
            print(f"[ERROR] Local LLM generation failed: {e}")
            return ""
