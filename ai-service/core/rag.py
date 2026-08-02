import os
import torch
from sentence_transformers import CrossEncoder
from .vector_store import VectorStoreManager
from .llm.factory import get_llm_provider

# Security Guardrail: Explicit instructions to prevent hallucination and prompt injection
SYSTEM_PROMPT = """
You are Docent, an expert AI documentation assistant. 
Your goal is to answer user questions accurately based ONLY on the provided RETRIEVED CONTEXT.
If the answer is not contained in the context, say "I'm sorry, but I don't have enough information in the documentation to answer that."
Do NOT make up answers or use outside knowledge.
Always cite your sources based on the document hierarchy provided in the context.
"""

class RAGPipeline:
    def __init__(self):
        # 1. Initialize the LLM via our Factory (Strategy Pattern)
        self.llm = get_llm_provider()
        
        # 2. Initialize the Hybrid Vector Store
        self.vsm = VectorStoreManager()
        
        # 3. Initialize the Cross-Encoder Reranker
        # We use a sigmoid activation to squash raw logits into 0.0 - 1.0 probability scores
        print("Loading BGE Reranker (this may take a moment on first boot)...")
        self.reranker = CrossEncoder(
            "BAAI/bge-reranker-base", 
            max_length=512, 
            default_activation_function=torch.nn.Sigmoid()
        )
        
        # Confidence threshold to trigger a fallback (Quality/Security Guardrail)
        # Note: BGE-reranker is very strict. A score of 0.02 after Sigmoid still means 
        # it found related keywords, but isn't a "perfect fact match". 
        self.confidence_threshold = 0.01

    def process_query(self, query: str) -> dict:
        """
        Executes the full RAG pipeline: Hybrid Retrieval -> Reranking -> Fallback Check -> Generation
        Returns a dictionary with the answer and metadata for the API Gateway to log.
        """
        print(f"Retrieving candidates for query: '{query}'")
        candidates = self.vsm.search(query, limit=15)
        
        if not candidates:
            return {"answer": "I couldn't find any relevant documentation to address your query.", "metadata": {}}
            
        pairs = [[query, chunk] for chunk in candidates]
        scores = self.reranker.predict(pairs)
        
        scored_candidates = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        
        top_score, best_chunk = scored_candidates[0]
        
        if top_score < self.confidence_threshold:
            print("Confidence too low. Triggering fallback.")
            return {"answer": "I found some related documents, but my confidence is too low to provide a safe, accurate answer. Could you clarify your question?", "metadata": {"top_score": float(top_score)}}
            
        top_chunks = [chunk for score, chunk in scored_candidates[:5]]
        
        # Extract sources for structured logging
        sources = [chunk.split("DOCUMENT HIERARCHY: ")[1].split("\n")[0] for chunk in top_chunks if "DOCUMENT HIERARCHY: " in chunk]
        
        print("Generating response via LLM...")
        response = self.llm.generate_response(SYSTEM_PROMPT, query, top_chunks)
        
        return {
            "answer": response,
            "metadata": {
                "top_score": float(top_score),
                "sources": sources
            }
        }
