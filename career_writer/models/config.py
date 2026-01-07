from dataclasses import dataclass
import json
import os
from typing import Optional
from dotenv import load_dotenv

@dataclass
class LLMConfig:
    provider: str  # "openai", "local", "groq", "google", "antigravity"
    api_key: Optional[str] = None
    files_url: Optional[str] = None # For local LLM or specific endpoints
    model_name: Optional[str] = None
    base_url: Optional[str] = None # For Antigravity or custom OpenAI-compatible

@dataclass
class Config:
    llm: LLMConfig
    language: str = "ko"
    
    @classmethod
    def load(cls, filepath: str = "data/config.json") -> 'Config':
        # Load .env file
        load_dotenv()

        # Default config
        config_data = {
            "llm": {
                "provider": "openai",
                "model_name": "gpt-4"
            },
            "language": "ko"
        }

        # Load from file if exists
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    
                    # Merge deeply
                    if "llm" in file_data:
                        config_data["llm"].update(file_data["llm"])
                    if "language" in file_data:
                        config_data["language"] = file_data["language"]
        except Exception as e:
            print(f"[WARN] Failed to load config file: {e}")

        # Environment variables override
        env_provider = os.getenv("LLM_PROVIDER")
        if env_provider:
            config_data["llm"]["provider"] = env_provider
        
        # Provider specific overrides
        provider = config_data["llm"]["provider"]
        
        # Generic/OpenAI
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key: config_data["llm"]["api_key"] = api_key
            model = os.getenv("OPENAI_MODEL")
            if model: config_data["llm"]["model_name"] = model

        # Groq
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if api_key: config_data["llm"]["api_key"] = api_key
            model = os.getenv("GROQ_MODEL")
            if model: config_data["llm"]["model_name"] = model

        # Google
        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key: config_data["llm"]["api_key"] = api_key
            model = os.getenv("GOOGLE_MODEL")
            if model: config_data["llm"]["model_name"] = model

        # Antigravity
        elif provider == "antigravity":
            api_key = os.getenv("ANTIGRAVITY_API_KEY")
            if api_key: config_data["llm"]["api_key"] = api_key
            base_url = os.getenv("ANTIGRAVITY_BASE_URL")
            if base_url: config_data["llm"]["base_url"] = base_url
            model = os.getenv("ANTIGRAVITY_MODEL")
            if model: config_data["llm"]["model_name"] = model
        
        # Local LLM
        elif provider == "local":
            files_url = os.getenv("LOCAL_LLM_URL") or os.getenv("LLM_FILES_URL")
            if files_url: config_data["llm"]["files_url"] = files_url

        # Always check for generic override if specific wasn't found or as fallback
        if not config_data["llm"].get("api_key"):
             config_data["llm"]["api_key"] = os.getenv("LLM_API_KEY")

        return cls(
            llm=LLMConfig(**config_data["llm"]),
            language=config_data["language"]
        )
