import sys
from typing import List, Dict
from career_writer.models.schema import Baseline, Fact, Experience
from career_writer.models.store import StoreManager
from career_writer.llm.base import LLMProvider
from career_writer.utils import extract_json_from_text
import os

class Interviewer:
    def __init__(self, llm: LLMProvider, baseline: Baseline):
        self.llm = llm
        self.baseline = baseline
        self.store = StoreManager("career_writer/data")
    
    def start(self):
        print("\n" + "="*50)
        print(" FACTS GATHERING INTERVIEW (v2)")
        print(" Strict Fact Mode: No dates, No title questions.")
        print("="*50 + "\n")
        
        # 1. Select Experience
        exp = self._select_experience()
        if not exp:
            return

        print(f"\n[Selected] {exp.organization} / {exp.role}")
        print("Please answer the following 6 questions to detail this experience.\n")

        # 2. Question Loop
        answers = {}
        
        # Q1
        answers['q1'] = self._ask("1. Core Task: What was the single task you spent the most time on?", "e.g. Refactoring the server loop")
        
        # Q2
        answers['q2'] = self._ask("2. Directness: Did you implement this directly? (Yes/No/Partial)", "e.g. Yes, I wrote the core logic")
        
        # Q3
        answers['q3'] = self._ask("3. Problem Context: What was the problem/situation that led to this?", "e.g. The legacy code was causing 50ms latency")
        
        # Q4
        answers['q4'] = self._ask("4. Structure/Action: How did you change the structure or logic?", "e.g. Separated input processing from state updates")
        
        # Q5
        answers['q5'] = self._ask("5. Tech Stack: List the technologies used.", "e.g. C++, Python, Redis")
        
        # Q6
        answers['q6'] = self._ask("6. Result: What changed compared to before? (Qualitative/Quantitative)", "e.g. Latency dropped to 10ms")

        # 3. Process & Save
        print("\n[Processing] Structuring your answers...")
        fact = self._parse_answers_to_fact(exp.id, answers)
        if fact:
            self.store.add_fact(fact)
            print(f"\n[Success] Fact saved for {exp.organization}!")
        else:
            print("\n[Error] Failed to process answers.")

    def _select_experience(self) -> Experience:
        print("Select an experience to elaborate on:")
        exps = self.baseline.experiences
        for i, exp in enumerate(exps):
            print(f" [{i+1}] {exp.organization} | {exp.role} ({exp.period.start} ~ {exp.period.end})")
        
        while True:
            try:
                choice = input("\nEnter number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    sys.exit(0)
                idx = int(choice) - 1
                if 0 <= idx < len(exps):
                    return exps[idx]
                print("Invalid number.")
            except ValueError:
                print("Invalid input.")

    def _ask(self, question: str, hint: str = "") -> str:
        print(f"\n{question}")
        if hint:
            print(f" > Hint: {hint}")
        while True:
            ans = input("Answer: ").strip()
            if ans:
                return ans
            print("Please enter an answer.")

    def _parse_answers_to_fact(self, exp_id: str, answers: Dict[str, str]) -> Fact:
        prompt_path = "career_writer/prompts/v2_fact_parser.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instruction = f.read()

        user_content = f"""
        Experience ID: {exp_id}
        Q1 (Task): {answers['q1']}
        Q2 (Directness): {answers['q2']}
        Q3 (Problem): {answers['q3']}
        Q4 (Action): {answers['q4']}
        Q5 (Tech): {answers['q5']}
        Q6 (Result): {answers['q6']}
        """
        
        context = {"system_instruction": system_instruction}
        response = self.llm.generate(user_content, context=context)
        
        data = extract_json_from_text(response)
        if not data:
            return None
            
        data['experience_id'] = exp_id
        return Fact.from_dict(data)
