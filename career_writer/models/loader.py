import os
import glob
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class InputData:
    resume_text: str = ""
    references: Dict[str, str] = field(default_factory=dict)

    def get_full_context_text(self) -> str:
        """Combines resume and references into a single context string."""
        text = f"=== RESUME ===\n{self.resume_text}\n\n"
        if self.references:
            text += "=== REFERENCES ===\n"
            for filename, content in self.references.items():
                text += f"--- {filename} ---\n{content}\n\n"
        return text

class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def load_all(self) -> InputData:
        resume_text = self._load_resume()
        references = self._load_references()
        return InputData(resume_text=resume_text, references=references)

    def _load_resume(self) -> str:
        # Check priority: resume.md > resume.txt
        candidates = ["resume.md", "resume.txt"]
        
        for candidate in candidates:
            path = os.path.join(self.data_dir, candidate)
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        print(f"[INFO] Loaded resume from {candidate}")
                        return f.read().strip()
            except Exception as e:
                print(f"[WARN] Failed to load {candidate}: {e}")
        
        return ""

    def _load_references(self) -> Dict[str, str]:
        ref_dir = os.path.join(self.data_dir, "references")
        refs = {}
        if not os.path.exists(ref_dir):
            return refs
        
        # Load .txt and .md files
        patterns = ["*.txt", "*.md"]
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(ref_dir, pattern)))
            
        for filepath in files:
            filename = os.path.basename(filepath)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    refs[filename] = f.read().strip()
            except Exception as e:
                print(f"[WARN] Failed to load reference {filename}: {e}")
        
        return refs
