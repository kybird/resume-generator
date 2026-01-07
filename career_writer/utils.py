import json
import re
from typing import List, Dict

def extract_json_from_text(text: str) -> Dict:
    """
    Robustly extracts the first valid JSON object from a string, 
    ignoring markdown code blocks or preambles.
    """
    try:
        # 1. Fast path: try parsing the whole string
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Try to find markdown code blocks
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Fallback: Find the first outer-most curly braces
    # This is a simple regex, might fail on nested unbalanced braces if malformed
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
            
    raise ValueError("Could not find valid JSON in text")

class ContextManager:
    def __init__(self, static_context: str, max_chars: int = 10000):
        self.static_context = static_context
        self.conversation_history: List[str] = []
        self.max_chars = max_chars

    def add_turn(self, speaker: str, text: str):
        self.conversation_history.append(f"{speaker}: {text}")

    def get_context(self) -> str:
        """
        Returns static context + recent conversation history, fitting within max_chars.
        Retains static context first, then truncates history from the beginning (keeping newest).
        """
        history_text = "\n".join(self.conversation_history)
        
        total_len = len(self.static_context) + len(history_text)
        if total_len <= self.max_chars:
            return f"{self.static_context}\n\n=== Recent Conversation ===\n{history_text}"
        
        # Truncate history
        available_chars = self.max_chars - len(self.static_context) - 50 # Buffer
        if available_chars < 0:
            # resume is too huge, just return truncated resume
            return self.static_context[:self.max_chars]
            
        truncated_history = history_text[-available_chars:]
        # Try to cut cleanly at a newline
        first_newline = truncated_history.find('\n')
        if first_newline != -1:
             truncated_history = truncated_history[first_newline+1:]
             
        return f"{self.static_context}\n\n=== Recent Conversation (Truncated) ===\n{truncated_history}"
