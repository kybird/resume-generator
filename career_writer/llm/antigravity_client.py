import os
import json
import requests
import logging
from typing import Dict, Optional, List, Any
from .base import LLMProvider
from .auth import GoogleAuth
from .retry import retry_with_backoff

# Configure basic logger for this module
logger = logging.getLogger("Antigravity")
logging.basicConfig(level=logging.INFO)

class AntigravityClient(LLMProvider):
    """
    LLM implementation using the reverse-engineered Antigravity API (Google Internal/Sandbox).
    """
    def __init__(self, api_key: Optional[str] = None):
        # Note: api_key arg kept for signature compatibility
        self.endpoint = "https://daily-cloudcode-pa.sandbox.googleapis.com/v1internal:generateContent"
        
        # 1. Base Model Resolution (Env -> Alias -> Default)
        default_model = "models/antigravity-gemini-3-pro"
        env_model = os.environ.get("LLM_MODEL", default_model)
        
        aliases = {
            "gemini": "models/antigravity-gemini-3-pro",
            "flash": "models/antigravity-gemini-3-flash", 
            "claude": "models/antigravity-claude-sonnet-4-5",
            "opus": "models/antigravity-claude-opus-4-5",
        }
        base_model = aliases.get(env_model.lower(), env_model)
        
        # 2. Apply Mode Suffix (LLM_MODE)
        mode = os.environ.get("LLM_MODE", "").lower()
        
        self.mode = mode 
        self.model_name = base_model
        
        logger.info(f"Antigravity Config: Model={self.model_name}, Mode={self.mode}")
        
        # Initial check for token (this might trigger browser auth if no token exists)
        # We don't force it here to avoid blocking startup excessively if not needed immediately,
        # but the user intent seems to be "auth if needed".
        # Let's simple load it.
        try:
            self.access_token = GoogleAuth.get_valid_token()
        except Exception as e:
            logger.warning(f"Antigravity token init deferred: {e}")
            self.access_token = None

    def authenticate(self):
        """Manual authentication trigger for CLI menu"""
        print("\n[Antigravity Auth]")
        try:
            # Force re-authentication or check
            token = GoogleAuth.get_valid_token()
            if token:
                self.access_token = token
                print("Authentication successful.")
            else:
                print("Authentication failed.")
        except Exception as e:
            print(f"Authentication error: {e}")

    def _call_api(self, messages: list, json_mode: bool = False) -> str:
        # Ensure we have a valid token before call
        if not self.access_token:
             try:
                 self.access_token = GoogleAuth.get_valid_token()
             except Exception:
                 pass
        
        if not self.access_token:
             raise PermissionError("No Access Token available. Run 'Authenticate' menu option.")
             
        # ... Body construction ...
        # (Snippet truncated for replace tool match, logic resumes below)
        
        # Construct Gemini-style body
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            if msg["role"] == "system":
                role = "user"
            
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        # Parse model name
        api_model = self.model_name
        thinking_level = None
        
        if self.mode == "plan":
            thinking_level = "high"
        elif self.mode == "fast":
            thinking_level = "low"
            
        api_model = api_model.replace("models/", "") 
        api_model = api_model.replace("antigravity-", "")
            
        gen_config = {}
        if json_mode:
            gen_config["responseMimeType"] = "application/json"
            
        if thinking_level:
             gen_config["thinkingConfig"] = {
                 "includeThoughts": True,
                 "thinkingLevel": thinking_level
             }
            
        payload = {
            "model": api_model,
            "project": "rising-fact-p41fc", 
            "request": {
                "contents": contents,
                "generationConfig": gen_config
            }
        }
        
        logger.info(f"Antigravity Req: Model={api_model} (Orig: {self.model_name})")
        
        max_retries = 1
        for attempt in range(max_retries + 1):
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "User-Agent": "antigravity/1.11.5 windows/amd64", 
                "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
            }
            
            try:
                response = requests.post(self.endpoint, headers=headers, json=payload, timeout=120)
                
                # Debug logging
                logger.info(f"Antigravity Raw Response Code: {response.status_code}")
                logger.info(f"Antigravity Raw Body: {response.text[:1000]}") # Truncate for sanity
                
                # Auth Retry Logic
                if response.status_code == 401:
                    logger.warning(f"Antigravity API 401 Unauthorized (Attempt {attempt+1}).")
                    if attempt < max_retries:
                        logger.info("Attempting automatic token refresh...")
                        # In new flow, get_valid_token handles refresh if expired, 
                        # but 401 implies it might be expired despite check or revoked.
                        # We force a refresh check.
                        
                        # We need to manually load token data to refresh it properly 
                        # relying on auth.py's internal logic is better.
                        # Ideally auth.py should have force_refresh.
                        # For now, let's just call get_valid_token again, hoping it refreshes? 
                        # Actually get_valid_token only refreshes if time > expiry.
                        # If 401 happens *before* expiry (e.g. revoked), we might need force auth.
                        # But simpler: let's try get_valid_token first.
                        
                        # Correction: user snippet provided explicit refresh_access_token(token_data).
                        # We should re-load data and force refresh?
                        # Or just let the user re-authenticate?
                        # Let's try to be smart: if 401, maybe just re-run get_valid_token?
                        # If that returns same token, then we are stuck.
                        
                        # Let's simplify:
                        # If 401, we consider the token invalid. 
                        # We can try to authenticate_user() again if needed, or just fail.
                        # But wait, the user provided snippet for get_valid_token handles expiry.
                        # 401 means "Invalid".
                        
                        # Let's try to reload it.
                        try:
                            # Re-acquire (might trigger browser if refresh failed)
                            # But we want to avoid popup during loop if possible?
                            # Actually, authenticating via browser is the only fix.
                            self.access_token = GoogleAuth.get_valid_token()
                            if self.access_token:
                                continue # Retry request
                        except Exception:
                            pass
                            
                    raise PermissionError("Antigravity API 401 Unauthorized")
                
                if response.status_code != 200:
                    logger.error(f"Antigravity API Error {response.status_code}: {response.text}")
                    return "{}"
                    
                data = response.json()
                
                # Extract candidates
                candidates = []
                if 'candidates' in data:
                    candidates = data['candidates']
                elif 'response' in data and 'candidates' in data['response']:
                    candidates = data['response']['candidates']
                
                if candidates:
                    try:
                        parts = candidates[0]['content']['parts']
                        final_text = ""
                        for part in parts:
                            final_text += part.get('text', "")
                        
                        if not final_text.strip():
                            logger.warning("Antigravity extracted empty text. Returning empty JSON.")
                            return "{}"
                            
                        return final_text
                    except (KeyError, IndexError, TypeError):
                         return "{}"
                else:
                    return "{}"

            except Exception as e:
                if attempt == max_retries:
                    raise e
                logger.warning(f"Request failed: {e}, retrying...")
                
        return "{}"

    @retry_with_backoff(retries=3, backoff_in_seconds=2)
    def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        messages = []
        
        # Handle system instruction
        system_instruction = "You are a helpful career assistant."
        if context and "system_instruction" in context:
            system_instruction = context["system_instruction"]
            
        messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        # By default we don't force JSON here unless we want to.
        # The user snippet had `_call_api(..., json_mode=True)` default, 
        # but `generate` is generic. Let's assume text output unless caller specifies.
        # Since `LLMProvider.generate` signature is fixed, we infer or config.
        # For now, disable JSON enforcement for general chat.
        return self._call_api(messages, json_mode=False)
