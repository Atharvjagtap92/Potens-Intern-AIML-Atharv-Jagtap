import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import logger, get_gemini_client, VECTOR_STORE_PATH

class SimpleVectorStore:
    """A lightweight, in-memory vector store using NumPy for cosine similarity.
    
    Avoids binary compilation issues on Windows and is ideal for parsing and 
    searching small-to-medium datasets (e.g. hundreds of policy documents).
    """
    
    def __init__(self, storage_path: Path = VECTOR_STORE_PATH):
        self.storage_path = storage_path
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None # numpy array of shape (num_chunks, embedding_dim)
        self.dim: int = 768 # text-embedding-004 size
        
    def is_empty(self) -> bool:
        """Returns True if the vector store has no indexed chunks."""
        return len(self.chunks) == 0

    def _get_embeddings_batch(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """Calls the Gemini API to get embeddings for a batch of text."""
        client = get_gemini_client()
        if not client:
            raise ValueError("Gemini API client not configured. Set GEMINI_API_KEY in .env.")
            
        task_type = "retrieval_query" if is_query else "retrieval_document"
        
        # Split into batches of 100 to avoid payload size limit
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            try:
                response = client.embed_content(
                    model="models/gemini-embedding-001",
                    content=batch_texts,
                    task_type=task_type
                )
                # response['embedding'] is list of floats for single, or list of list of floats for batch
                embeddings = response.get("embedding", [])
                if not embeddings:
                    # In some older SDK versions, embedding is in another property
                    embeddings = [item for item in response.embeddings]
                all_embeddings.extend(embeddings)
            except Exception as e:
                logger.error(f"Error fetching embeddings: {e}")
                raise e
                
        return all_embeddings

    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Generates embeddings for the provided chunks and adds them to the store."""
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings_list = self._get_embeddings_batch(texts, is_query=False)
        
        new_embeddings = np.array(embeddings_list)
        
        if self.embeddings is None or self.embeddings.size == 0:
            self.embeddings = new_embeddings
            self.chunks = chunks
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
            self.chunks.extend(chunks)
            
        self.save()
        logger.info(f"Successfully added {len(chunks)} chunks and saved vector store.")

    def search(self, query: str, top_k: int = 3, doc_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Searches the vector store using cosine similarity with optional document filters."""
        if self.is_empty() or self.embeddings is None:
            logger.warning("Search called on an empty vector store.")
            return []
            
        # Get query embedding
        query_emb_list = self._get_embeddings_batch([query], is_query=True)
        query_emb = np.array(query_emb_list[0])
        
        # Compute cosine similarity
        # embeddings: (N, D), query_emb: (D,)
        norm_embeddings = np.linalg.norm(self.embeddings, axis=1)
        norm_query = np.linalg.norm(query_emb)
        
        # Avoid division by zero
        norm_embeddings[norm_embeddings == 0] = 1e-10
        norm_query = 1e-10 if norm_query == 0 else norm_query
        
        similarities = np.dot(self.embeddings, query_emb) / (norm_embeddings * norm_query)
        
        # Prepare results
        results = []
        for idx, score in enumerate(similarities):
            chunk = self.chunks[idx]
            
            # Apply filter if provided
            if doc_ids and chunk["doc_id"] not in doc_ids:
                continue
                
            results.append({
                **chunk,
                "score": float(score)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def save(self):
        """Serializes and saves the index to a JSON file."""
        if self.embeddings is None:
            return
            
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings.tolist()
        }
        
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Vector store saved to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def load(self) -> bool:
        """Loads the index from a JSON file. Returns True if successful."""
        if not self.storage_path.exists():
            logger.info(f"No vector store file found at {self.storage_path}")
            return False
            
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self.chunks = data.get("chunks", [])
            embeddings_list = data.get("embeddings", [])
            
            if embeddings_list:
                self.embeddings = np.array(embeddings_list)
                logger.info(f"Loaded vector store with {len(self.chunks)} chunks from {self.storage_path}")
                return True
            else:
                self.embeddings = None
                self.chunks = []
                return False
        except Exception as e:
            logger.error(f"Failed to load vector store from {self.storage_path}: {e}")
            return False
            
    def clear(self):
        """Clears all data and deletes the local file."""
        self.chunks = []
        self.embeddings = None
        if self.storage_path.exists():
            try:
                self.storage_path.unlink()
                logger.info(f"Deleted vector store file at {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to delete vector store file: {e}")
