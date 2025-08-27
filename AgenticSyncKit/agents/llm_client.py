# agents/llm_client.py
import os
from typing import Dict, Any

class LLMClient:
    def __init__(self, model: str|None=None, temperature: float=0.0):
        self.provider = os.getenv("LLM_PROVIDER","MOCK").upper()
        self.model = model or os.getenv("LLM_MODEL","gpt-4o-mini")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", str(temperature)))

    def call(self, system: str, prompt: str, **kwargs) -> str:
        if self.provider == "MOCK":
            return f"[MOCK REPLY]\nSYSTEM:\n{system}\n\nPROMPT:\n{prompt}"
        raise NotImplementedError("LLM provider not configured. Set LLM_PROVIDER=MOCK for dry runs.")

def call_llm(system: str, prompt: str, **kwargs) -> str:
    return LLMClient().call(system, prompt, **kwargs)
