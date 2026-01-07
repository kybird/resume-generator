from typing import Dict, Optional
import os

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from .base import LLMProvider
from .retry import retry_with_backoff

class GoogleClient(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        if genai is None:
            raise ImportError("google-genai library not installed. Please install with `pip install google-genai`.")
        
        # New SDK Initialization
        # If api_key is provided, pass it. Otherwise it might pick up GOOGLE_API_KEY env var automatically.
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    @retry_with_backoff(retries=3, backoff_in_seconds=2)
    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        # Construct contents. New SDK uses specific 'contents' parameter string or list of parts.
        
        system_instruction = None
        if context and "system_instruction" in context:
            system_instruction = context["system_instruction"]
        
        # Configuration for generation
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text.strip() if response.text else ""
            
        except Exception as e:
            print(f"[ERROR] Google generation failed: {e}")
            return ""
