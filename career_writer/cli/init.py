from career_writer.models.store import StoreManager
from career_writer.models.loader import DataLoader
from career_writer.processing.baseline_extractor import BaselineExtractor
from career_writer.models.config import Config
from career_writer.llm.base import LLMProvider
import sys

def init_baseline(config: Config, llm: LLMProvider):
    """
    Ensures that 'baseline.json' exists.
    If not, it reads resume from data/ and extracts it using LLM.
    """
    # Fix path: running from root so we point to internal data dir
    data_dir = "career_writer/data"
    store = StoreManager(data_dir)
    
    if store.baseline_exists():
        print("[Init] Baseline data found (Frozen). Skipping extraction.")
        return store.load_baseline()

    print("[Init] No baseline found. Starting Baseline Extraction...")
    
    # Load raw resume
    loader = DataLoader(data_dir)
    data = loader.load_all()
    
    resume_text = data.resume_text
    if not resume_text:
        print("[Error] Resume is empty or not found (resume.md/txt).")
        sys.exit(1)
    if not resume_text:
        print("[Error] Resume is empty.")
        sys.exit(1)
        
    print(f"[Init] Read resume ({len(resume_text)} chars). Extracting structure via LLM...")
    
    extractor = BaselineExtractor(llm)
    baseline = extractor.extract(resume_text)
    
    if not baseline:
        print("[Error] Baseline extraction failed.")
        sys.exit(1)
        
    store.save_baseline(baseline)
    print("[Init] Baseline extracted and saved to 'data/baseline.json'.")
    return baseline
