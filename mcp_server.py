from fastmcp import FastMCP
import sys
import os
import json
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from career_writer.models.store import StoreManager
from career_writer.models.schema import Fact, FactResult
from career_writer.models.config import Config
from career_writer.llm.antigravity_client import AntigravityClient
from career_writer.llm.google_client import GoogleClient
from career_writer.llm.openai_client import OpenAIClient
from career_writer.generator import Generator

# Initialize Server
mcp = FastMCP("Career Data Server (v2)")
# Determine the absolute data path
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "career_writer", "data")
print(f"Server Initialized. Data Path: {data_path}")
store = StoreManager(data_path)

# === Baseline Tools (Metadata) ===

@mcp.tool
def get_baseline_info() -> Dict:
    """
    Retrieves the FROZEN Baseline Metadata (Person info and List of Experiences).
    Use this to see what 'Experience IDs' are available (e.g., exp_01, exp_02).
    The AI should NEVER try to modify this.
    """
    baseline = store.load_baseline()
    if not baseline:
        return {"error": "No baseline.json found. Please run local CLI init first."}
    return baseline.to_dict()

# === Fact Tools (Details) ===

@mcp.tool
def get_linked_facts(experience_id: str) -> List[Dict]:
    """
    Retrieves all Facts linked to a specific Experience ID.
    Use this to see what details have already been collected for a job.
    """
    facts = store.get_facts_for_experience(experience_id)
    return [f.to_dict() for f in facts]

@mcp.tool
def add_linked_fact(
    experience_id: str, 
    responsibility: str, 
    direct_work: bool, 
    tech: List[str], 
    problem: str = "", 
    action: str = "", 
    result_desc: str = "", 
    result_type: str = "none"
) -> str:
    """
    Adds a strict Fact linked to an Experience.
    
    Args:
        experience_id: Must match an ID from get_baseline_info() (e.g. 'exp_01')
        responsibility: Core task description (What did you do?)
        direct_work: True if hands-on implementation
        tech: List of technologies (e.g. ["Python", "AWS"])
        problem: Context/Situation
        action: Structural change or approach
        result_desc: Outcome description
        result_type: 'qualitative', 'quantitative', or 'none'
    """
    # Verify ID exists
    baseline = store.load_baseline()
    if not baseline:
        return "Error: Baseline not loaded."
    
    valid_ids = [e.id for e in baseline.experiences]
    if experience_id not in valid_ids:
        return f"Error: Invalid experience_id '{experience_id}'. Valid IDs: {valid_ids}"

    fact = Fact(
        experience_id=experience_id,
        responsibility=responsibility,
        direct_work=direct_work,
        tech=tech,
        problem=problem,
        action=action,
        result=FactResult(type=result_type, description=result_desc),
        source="mcp_agent"
    )
    
    store.add_fact(fact)
    return f"Saved fact to {experience_id}."

# === Generator ===

@mcp.tool
def debug_system_info() -> Dict:
    """
    Returns internal path and environment info for debugging.
    """
    import career_writer
    import career_writer.generator
    return {
        "cwd": os.getcwd(),
        "sys_path": sys.path,
        "career_writer_path": career_writer.__file__,
        "generator_path": career_writer.generator.__file__,
        "base_dir": base_dir,
        "data_path": data_path,
        "baseline_exists": os.path.exists(os.path.join(data_path, "baseline.json")),
        "env_vars": {k: "SET" if v else "NOT SET" for k, v in os.environ.items() if "API_KEY" in k or "LLM" in k}
    }

@mcp.tool
def generate_resume_v2() -> str:
    """
    Triggers the v2 Generator to merge Baseline + Facts into a final Resume Markdown.
    Returns the content of the generated file.
    """
    # We need to spin up an LLM for the generator.
    # We'll re-load config here.
    try:
        config = Config.load()
        if config.llm.provider == "antigravity":
            llm = AntigravityClient(config.llm.api_key)
        elif config.llm.provider == "google":
            llm = GoogleClient(config.llm.api_key, config.llm.model_name)
        elif config.llm.provider == "openai":
            llm = OpenAIClient(config.llm.api_key, config.llm.model_name)
        else:
             # Default/Fallback
             return "Error: LLM Provider not supported for server-side generation yet."
             
        gen = Generator(llm)
        return gen.generate_resume()
        
    except Exception as e:
        return f"[v2.1] Error generating resume (Exception): {e}"

if __name__ == "__main__":
    mcp.run()
