import os
from .base import BaseLLMProvider
from .gemini import GeminiProvider

def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function to instantiate the correct LLM provider based on configuration.
    This fulfills the 'swappable' non-negotiable requirement.
    """
    provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_name == "gemini":
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        return GeminiProvider(model_name=model_name)
    elif provider_name == "openai":
        raise NotImplementedError("OpenAI provider is not yet implemented.")
    else:
        raise ValueError(f"Unknown LLM_PROVIDER in config: {provider_name}")
