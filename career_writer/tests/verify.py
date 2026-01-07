import sys
import os
import json
import unittest
from unittest.mock import MagicMock

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.memory import CareerMemory, Project, FactItem, CompanyMemory
from llm.base import LLMProvider
from generator import Generator

class MockLLM(LLMProvider):
    def generate(self, prompt: str, context: dict = None) -> str:
        return "Mock Response"

class TestCareerSystem(unittest.TestCase):
    def test_memory_serialization(self):
        print("\nTesting Memory data structures...")
        mem = CareerMemory()
        company = CompanyMemory(period="2020-2021")
        proj = Project(
            name="TestProject",
            problem=FactItem("Prob", "fact"),
            action=FactItem("Act", "fact"),
            tech=FactItem(["Python"], "fact"),
            result=FactItem("Res", "fact"),
            difficulty=FactItem("Diff", "fact")
        )
        company.projects.append(proj)
        mem.companies["TestCorp"] = company
        
        # Determine strict path
        test_file = "test_memory.json"
        mem.save(test_file)
        
        loaded = CareerMemory.load(test_file)
        self.assertEqual(len(loaded.companies), 1)
        self.assertEqual(loaded.companies["TestCorp"].projects[0].name, "TestProject")
        self.assertEqual(loaded.companies["TestCorp"].projects[0].tech.text, ["Python"])
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        print("Memory test passed.")

    def test_generator(self):
        print("\nTesting Generator logic...")
        mem = CareerMemory()
        company = CompanyMemory(period="2020-2021")
        proj = Project(
            name="GenProject",
            problem=FactItem("Hard Problem", "fact"),
            action=FactItem("Solved it", "fact"),
            tech=FactItem(["AI"], "fact"),
            result=FactItem("Good results", "fact"),
            difficulty=FactItem("Medium", "fact")
        )
        company.projects.append(proj)
        mem.companies["GenCorp"] = company
        
        llm = MockLLM()
        gen = Generator(llm, mem)
        
        draft_file = "test_draft.md"
        final_file = "test_final.md"
        
        # Test Draft
        gen.generate_draft(draft_file)
        self.assertTrue(os.path.exists(draft_file))
        
        # Test Final
        gen.generate_final(draft_file, final_file)
        self.assertTrue(os.path.exists(final_file))
        
        # Cleanup
        if os.path.exists(draft_file):
            os.remove(draft_file)
        if os.path.exists(final_file):
            os.remove(final_file)
        print("Generator test passed.")

if __name__ == '__main__':
    unittest.main()
