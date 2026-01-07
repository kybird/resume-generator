from typing import Dict, Optional
try:
    from groq import Groq
except ImportError:
    Groq = None

from .base import LLMProvider
from .retry import retry_with_backoff

class GroqClient(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "llama3-70b-8192"):
        if Groq is None:
            raise ImportError("Groq library not installed. Please install with `pip install groq`.")
        
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    @retry_with_backoff(retries=3, backoff_in_seconds=2)
    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        messages = []
        
        # System Message
        system_content = "You are a helpful career assistant."
        if context and "system_instruction" in context:
            system_content = context["system_instruction"]
        messages.append({"role": "system", "content": system_content})

        # User Message
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] Groq generation failed: {e}")
            return ""
