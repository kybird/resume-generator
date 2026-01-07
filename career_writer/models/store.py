import json
import os
from typing import List, Optional
from .schema import Baseline, Fact

class StoreManager:
    """
    Manages persistence for Baseline (Metadata) and Facts (Details).
    Separate from the legacy 'memory.json'.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.baseline_path = os.path.join(data_dir, "baseline.json")
        self.facts_path = os.path.join(data_dir, "facts.json")
        
        # Ensure dir exists
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def save_baseline(self, baseline: Baseline):
        with open(self.baseline_path, "w", encoding="utf-8") as f:
            json.dump(baseline.to_dict(), f, indent=2, ensure_ascii=False)

    def load_baseline(self) -> Optional[Baseline]:
        if not os.path.exists(self.baseline_path):
            return None
        try:
            with open(self.baseline_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Baseline.from_dict(data)
        except Exception as e:
            print(f"[Store] Error loading baseline: {e}")
            return None

    def baseline_exists(self) -> bool:
        return os.path.exists(self.baseline_path)

    def save_facts(self, facts: List[Fact]):
        data = [f.to_dict() for f in facts]
        with open(self.facts_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_facts(self) -> List[Fact]:
        if not os.path.exists(self.facts_path):
            return []
        try:
            with open(self.facts_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Fact.from_dict(item) for item in data]
        except Exception as e:
            print(f"[Store] Error loading facts: {e}")
            return []

    def add_fact(self, fact: Fact):
        facts = self.load_facts()
        facts.append(fact)
        self.save_facts(facts)

    def get_facts_for_experience(self, experience_id: str) -> List[Fact]:
        all_facts = self.load_facts()
        return [f for f in all_facts if f.experience_id == experience_id]
