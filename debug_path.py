import os
from career_writer.models.store import StoreManager
from career_writer.generator import Generator

print(f"CWD: {os.getcwd()}")
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Base Dir (debug script): {base_dir}")

data_path = os.path.join(base_dir, "career_writer", "data")
print(f"Expected Data Path: {data_path}")

store = StoreManager(data_path)
baseline = store.load_baseline()
print(f"Baseline loaded by direct store: {baseline is not None}")

# Check generator
from career_writer.llm.base import LLMProvider
class MockLLM(LLMProvider):
    def generate(self, prompt, context=None): return "test"
    
gen = Generator(MockLLM())
print(f"Generator Store Dir: {gen.store.data_dir}")
gen_baseline = gen.store.load_baseline()
print(f"Baseline loaded by generator: {gen_baseline is not None}")
