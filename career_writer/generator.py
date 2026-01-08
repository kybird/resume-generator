from career_writer.models.schema import Baseline, Fact, Experience
from career_writer.models.store import StoreManager
from career_writer.llm.base import LLMProvider
import os

class Generator:
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        # Use absolute paths to avoid issues when running from different CWDs
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.store = StoreManager(os.path.join(base_dir, "data"))
        self.prompts_dir = os.path.join(base_dir, "prompts")
        self.output_dir = os.path.join(os.path.dirname(base_dir), "output")

    def generate_resume(self) -> str:
        """
        Generates the full resume by merging Baseline + Facts.
        """
        baseline = self.store.load_baseline()
        if not baseline:
            return f"[v2.1] Error: No baseline found at {self.store.baseline_path}"
            
        full_markdown = f"# {baseline.person.name}\n**{baseline.person.title}**\n\n---\n"
        
        # Sort experiences (assuming baseline is already sorted or we sort here)
        # We process each experience
        for exp in baseline.experiences:
            section = self._generate_section(exp)
            full_markdown += section + "\n\n"
            
        # Save output
        out_path = os.path.join(self.output_dir, "v2_resume.md")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)
            
        return full_markdown

    def _generate_section(self, exp: Experience) -> str:
        facts = self.store.get_facts_for_experience(exp.id)
        if not facts:
            # If no facts, just print the header
            return f"## {exp.organization} | {exp.role} | {exp.period.start} - {exp.period.end}\n- (No detailed facts recorded)"
            
        # Call LLM to write bullets
        prompt_path = os.path.join(self.prompts_dir, "v2_resume_writer.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system = f.read()
            
        user_content = f"""
        BASELINE:
        Company: {exp.organization}
        Role: {exp.role}
        Period: {exp.period.start} - {exp.period.end}
        
        FACTS:
        {self._format_facts(facts)}
        """
        
        context = {"system_instruction": system}
        # We expect raw markdown output (no json)
        return self.llm.generate(user_content, context=context)

    def _format_facts(self, facts: list[Fact]) -> str:
        out = ""
        for i, f in enumerate(facts):
            out += f"""
            Fact {i+1}:
            - Task: {f.responsibility}
            - Direct: {f.direct_work}
            - Problem: {f.problem}
            - Action: {f.action}
            - Tech: {", ".join(f.tech)}
            - Result: {f.result.description} ({f.result.type})
            """
        return out
