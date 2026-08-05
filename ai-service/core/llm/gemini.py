import os
from typing import List
import google.generativeai as genai
from .base import BaseLLMProvider

from langfuse import observe

class GeminiProvider(BaseLLMProvider):
    def __init__(self, model_name: str = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
        
        # Use env variable if provided, otherwise default to 2.5-flash
        final_model = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(final_model)
        
    @observe(as_type="generation")
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
