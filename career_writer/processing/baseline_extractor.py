import json
import os
import re
from typing import Optional
from career_writer.models.schema import Baseline
from career_writer.llm.base import LLMProvider
from career_writer.utils import extract_json_from_text

class BaselineExtractor:
    def __init__(self, llm: LLMProvider, prompts_dir: str = "career_writer/prompts"):
        self.llm = llm
        self.prompts_dir = prompts_dir

    def extract(self, resume_text: str) -> Optional[Baseline]:
        """
        Uses LLM to parse resume_text into a Baseline object.
        """
        prompt_path = os.path.join(self.prompts_dir, "extract_baseline.txt")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instruction = f.read()

        prompt = f"RESUME CONTENT:\n\n{resume_text}"
        
        # Call LLM
        # We use a custom context to pass system instruction if supported
        context = {"system_instruction": system_instruction}
        response = self.llm.generate(prompt, context=context)
        
        # Parse JSON
        data = extract_json_from_text(response)
        if not data:
            print("[Error] Failed to parse Baseline JSON from LLM response.")
            return None

        try:
            return Baseline.from_dict(data)
        except Exception as e:
            print(f"[Error] JSON matched schema but validation failed: {e}")
            return None
