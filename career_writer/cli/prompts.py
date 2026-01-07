import os

class PromptManager:
    def __init__(self, prompt_dir: str = "prompts"):
        self.prompt_dir = prompt_dir

    def load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompt_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[WARN] Prompt file not found: {filename}")
            return ""

    def get_fact_interview_prompt(self) -> str:
        return self.load_prompt("interview_fact.txt")
        
    def get_draft_prompt(self) -> str:
        return self.load_prompt("draft.txt")
