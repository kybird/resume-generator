import os
from typing import Dict, Optional
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base import LLMProvider
from .retry import retry_with_backoff

class OpenAIClient(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        if OpenAI is None:
            raise ImportError("OpenAI library not installed. Please install with `pip install openai`.")
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    @retry_with_backoff(retries=3, backoff_in_seconds=2)
    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        messages = []
        
        # Add system context if provided
        if context and "system_instruction" in context:
            messages.append({"role": "system", "content": context["system_instruction"]})
        else:
             messages.append({"role": "system", "content": "You are a helpful career assistant."})

        # Add main prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # In a real app, use a proper logger
            print(f"[ERROR] OpenAI generation failed: {e}")
            return ""
