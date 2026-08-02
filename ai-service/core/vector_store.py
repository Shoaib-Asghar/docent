import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

class VectorStoreManager:
    """
    Manages the Qdrant Vector Database connection and operations.
    Implements Hybrid Search (Dense + Sparse/BM25),
    utilizing local FastEmbed models to eliminate embedding API costs and latency.
    """
    
    def __init__(self, collection_name: str = "docent_knowledge_base"):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        
        # We use an in-memory database if no URL is provided, but in production, this points to the Docker container
        if qdrant_url == "memory":
            self.client = QdrantClient(":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
            
        self.collection_name = collection_name
        
        # Configure FastEmbed models (runs locally on CPU, incredibly fast)
        # Dense vectors capture semantic meaning
        self.client.set_model("BAAI/bge-small-en-v1.5") 
        # Sparse vectors (SPLADE) capture exact keyword matches better than BM25
        self.client.set_sparse_model("prithivida/Splade_PP_en_v1")
        
    def setup_collection(self):
        """
        Creates the collection with hybrid search configured.
        """
        if not self.client.collection_exists(self.collection_name):
            # Using Qdrant's FastEmbed integration, create_collection automatically configures 
            # the necessary dense and sparse vectors based on the models set in __init__
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.client.get_fastembed_vector_params(),
                sparse_vectors_config=self.client.get_fastembed_sparse_vector_params()
            )
            print(f"Collection '{self.collection_name}' created successfully with Hybrid Search capabilities.")

    def ingest_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Embeds and ingests raw text chunks into the vector store.
        """
        if metadata is None:
            metadata = [{} for _ in documents]
            
        self.client.add(
            collection_name=self.collection_name,
            documents=documents,
            metadata=metadata
        )
        print(f"Successfully ingested {len(documents)} chunks.")

    def search(self, query: str, limit: int = 5) -> List[str]:
        """
        Performs a hybrid search (Dense + Sparse) fused via Reciprocal Rank Fusion (RRF).
        """
        # Qdrant's query() method automatically uses both dense and sparse models 
        # if both are configured, and natively fuses the results.
        results = self.client.query(
            collection_name=self.collection_name,
            query_text=query,
            limit=limit
        )
        
        return [hit.document for hit in results]
