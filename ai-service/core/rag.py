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

    def process_query(self, query: str) -> str:
        """
        Executes the full RAG pipeline: Hybrid Retrieval -> Reranking -> Fallback Check -> Generation
        """
        # Step 1: Broad Hybrid Retrieval (Fast, Cheap, High Recall)
        # We fetch 15 chunks, knowing many will be irrelevant, to ensure we don't miss anything.
        print(f"Retrieving candidates for query: '{query}'")
        candidates = self.vsm.search(query, limit=15)
        
        if not candidates:
            return "I couldn't find any relevant documentation to address your query."
            
        # Step 2: Cross-Encoder Reranking (Slow, Highly Accurate, High Precision)
        # We pair the user's query with every retrieved chunk to score exact relevance.
        pairs = [[query, chunk] for chunk in candidates]
        scores = self.reranker.predict(pairs)
        
        # Zip the scores with the chunks and sort them descending
        scored_candidates = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        
        # Step 3: Confidence Handling
        top_score, best_chunk = scored_candidates[0]
        print(f"Top rerank score: {top_score:.4f}")
        
        if top_score < self.confidence_threshold:
            print("Confidence too low. Triggering fallback.")
            return "I found some related documents, but my confidence is too low to provide a safe, accurate answer. Could you clarify your question?"
            
        # Step 4: Context Truncation
        # Keep only the top 5 highly relevant chunks to fit safely in the LLM's context window.
        # This completely mitigates the "Lost in the Middle" failure mode.
        top_chunks = [chunk for score, chunk in scored_candidates[:5]]
        
        # Step 5: Generation
        print("Generating response via LLM...")
        response = self.llm.generate_response(SYSTEM_PROMPT, query, top_chunks)
        
        return response
