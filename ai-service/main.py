import os
from dotenv import load_dotenv
# Load environment variables from .env file before anything else initializes
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from core.rag import RAGPipeline

# Initialize FastAPI
app = FastAPI(
    title="Docent AI RAG Service",
    description="Production-grade backend for the AI Docs Assistant."
)

# We initialize the pipeline lazily so that importing main.py (e.g., during tests)
# doesn't immediately load heavy PyTorch models into RAM.
rag_pipeline = None

def get_pipeline() -> RAGPipeline:
    global rag_pipeline
    if rag_pipeline is None:
        print("Booting up RAG Pipeline (Lazy Load)...")
        rag_pipeline = RAGPipeline()
    return rag_pipeline

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    metadata: dict

@app.post("/api/chat", response_model=QueryResponse)
def chat(request: QueryRequest):
    """
    Main endpoint for the frontend gateway to interact with the AI service.
    """
    pipeline = get_pipeline()
    result = pipeline.process_query(request.query)
    return {"answer": result["answer"], "metadata": result["metadata"]}

@app.get("/health")
def health_check():
    """
    Kubernetes/Docker health check endpoint.
    """
    return {"status": "healthy"}
