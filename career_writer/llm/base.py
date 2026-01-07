from abc import ABC, abstractmethod
from typing import Dict, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Generates text based on the prompt and optional context.
        
        Args:
            prompt: The main user prompt or instruction.
            context: Optional dictionary containing additional context (e.g., resume data).
            
        Returns:
            The generated text string.
        """
        pass
