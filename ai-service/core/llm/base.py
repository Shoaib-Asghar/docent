from abc import ABC, abstractmethod
from typing import List

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers.
    This enforces the Strategy Pattern, ensuring our core RAG logic 
    never depends on a specific provider's API.
    """
    
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, context_chunks: List[str]) -> str:
        """
        Generates a response from the LLM based on the prompt and retrieved context.
        """
        pass
