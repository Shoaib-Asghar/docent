import os
from typing import List
import google.generativeai as genai
from .base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def generate_response(self, system_prompt: str, user_prompt: str, context_chunks: List[str]) -> str:
        # Security Guardrail: Clearly separate instructions from retrieved (untrusted) data
        context_str = "\n\n".join([f"--- Chunk {i+1} ---\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        full_prompt = f"""
{system_prompt}

### RETRIEVED CONTEXT (UNTRUSTED DATA):
{context_str}

### USER QUERY:
{user_prompt}
"""
        response = self.model.generate_content(full_prompt)
        return response.text
