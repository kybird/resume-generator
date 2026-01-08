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
        print(" Dynamic Mode: Driven by Resume & References context.")
        print("="*50 + "\n")
        
        # 0. Load Context (Resume + References)
        loader = DataLoader(self.store.data_dir)
        input_data = loader.load_all()
        
        # 1. Select Experience
        exp = self._select_experience()
        if not exp:
            return

        print(f"\n[Selected] {exp.organization} / {exp.role}")
        print("The AI interviewer will now ask questions based on your resume and industry references.\n")

        # 2. Dynamic Interview Loop
        history = []
        extracted_fact = Fact(
            experience_id=exp.id,
            responsibility="",
            problem="",
            action="",
            tech=[],
            result={"type": "none", "description": ""}
        )

        prompt_path = "career_writer/prompts/interview_fact.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_template = f.read()

        while True:
            # Prepare status for prompt
            problem_status = extracted_fact.problem or "missing"
            action_status = extracted_fact.action or "missing"
            tech_status = ", ".join(extracted_fact.tech) if extracted_fact.tech else "missing"
            result_status = f"{extracted_fact.result.description} ({extracted_fact.result.type})" if extracted_fact.result.description else "missing"

            # Build Full System Instruction
            system_instruction = system_template.format(
                company=exp.organization,
                role=exp.role,
                period=f"{exp.period.start} ~ {exp.period.end}",
                resume_context=input_data.resume_text,
                reference_context="\n".join([f"{k}: {v[:300]}..." for k, v in input_data.references.items()]), # Truncate references to avoid context overflow
                problem_status=problem_status,
                action_status=action_status,
                tech_status=tech_status,
                result_status=result_status,
                history="\n".join(history[-10:]) # last 10 turns
            )

            # Generate Next Question
            user_input = "Please provide the next question." if not history else history[-1]
            response = self.llm.generate(user_input, context={"system_instruction": system_instruction})
            
            data = extract_json_from_text(response)
            if not data:
                print("\n[Error] Failed to parse AI response.")
                break

            # Update Extracted Data
            if "extracted_data" in data:
                ext = data["extracted_data"]
                if ext.get("responsibility"): extracted_fact.responsibility = ext["responsibility"]
                if ext.get("problem"): extracted_fact.problem = ext["problem"]
                if ext.get("action"): extracted_fact.action = ext["action"]
                if ext.get("tech"): extracted_fact.tech = list(set(extracted_fact.tech + ext["tech"]))
                if ext.get("result"):
                    res = ext["result"]
                    if isinstance(res, dict):
                        extracted_fact.result.type = res.get("type", extracted_fact.result.type)
                        extracted_fact.result.description = res.get("description", extracted_fact.result.description)

            question = data.get("question", "DONE")
            if question.upper() == "DONE":
                print("\n[Complete] All necessary information gathered.")
                break

            # Ask User
            print(f"\nAI: {question}")
            ans = input("Answer: ").strip()
            if not ans:
                print("Conversation ended by user.")
                break
            
            history.append(f"AI: {question}")
            history.append(f"User: {ans}")

        # 3. Save
        if extracted_fact.responsibility or extracted_fact.problem:
            self.store.add_fact(extracted_fact)
            print(f"\n[Success] Fact saved for {exp.organization}!")
        else:
            print("\n[Error] No meaningful data extracted.")

    def _select_experience(self) -> Experience:
        print("Select an experience to elaborate on:")
        exps = self.baseline.experiences
        for i, exp in enumerate(exps):
            print(f" [{i+1}] {exp.organization} | {exp.role} ({exp.period.start} ~ {exp.period.end})")
        
        while True:
            try:
                choice = input("\nEnter number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    return None
                idx = int(choice) - 1
                if 0 <= idx < len(exps):
                    return exps[idx]
                print("Invalid number.")
            except ValueError:
                print("Invalid input.")

    def _ask(self, question: str, hint: str = "") -> str:
        # Deprecated in dynamic mode
        pass

    def _parse_answers_to_fact(self, exp_id: str, answers: Dict[str, str]) -> Fact:
        # Deprecated in dynamic mode
        pass
