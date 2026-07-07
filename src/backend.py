import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body, Depends, Header
from pydantic import BaseModel, Field
from src.config import logger, DATA_DIR
from src.document_parser import MarkdownParser
from src.vector_store import SimpleVectorStore
from src.rag_engine import RAGEngine
from src.contradict_engine import ContradictEngine

# Define Pydantic models for API Validation
class AskRequest(BaseModel):
    query: str = Field(..., example="What is the meal allowance in Mumbai for Potens Labs?")
    doc_ids: Optional[List[str]] = Field(default=None, example=["potens_labs_travel_2026"])

class Citation(BaseModel):
    source_index: int
    doc_id: str
    doc_name: str
    section: str
    snippet: str
    char_offset: int

class AskResponse(BaseModel):
    query: str
    translated_query: str
    language: str
    answer: str
    confidence_score: float
    confidence_level: str
    citations: List[Citation]
    source_chunks_searched: Optional[List[dict]] = Field(default=None)

class ContradictRequest(BaseModel):
    doc_a: str = Field(..., example="potens_core_travel_2026")
    doc_b: str = Field(..., example="potens_labs_travel_2026")
    topic: str = Field(..., example="Meal per diem caps")

class DocumentInfo(BaseModel):
    doc_id: str
    doc_name: str
    chunk_count: int
    file_size_bytes: int

# Initialize FastAPI App
app = FastAPI(
    title="Potens compliance RAG API",
    description="Backend service for multilingual compliance Q&A and policy contradiction auditing.",
    version="1.0.0"
)

# Global variables for engines
vector_store = SimpleVectorStore()
rag_engine = None
contradict_engine = None

@app.on_event("startup")
def startup_event():
    """Initializes the vector store, processes data if empty, and sets up engines."""
    global rag_engine, contradict_engine
    
    logger.info("Starting up Potens Compliance RAG Backend...")
    
    # 1. Load vector store from disk
    loaded = vector_store.load()
    
    # 2. If no data exists, perform initial parsing and ingestion
    if not loaded or vector_store.is_empty():
        logger.info("Vector store is empty or missing. Starting initial ingestion...")
        parser = MarkdownParser()
        
        try:
            chunks = parser.parse_directory(DATA_DIR)
            if chunks:
                vector_store.add_documents(chunks)
                logger.info(f"Ingested {len(chunks)} chunks from {DATA_DIR}")
            else:
                logger.error(f"No markdown documents found in data folder {DATA_DIR}!")
        except Exception as e:
            logger.error(f"Initial ingestion failed: {e}")
            
    # 3. Instantiate engines
    rag_engine = RAGEngine(vector_store)
    contradict_engine = ContradictEngine(vector_store)
    logger.info("Compliance Engines initialized successfully.")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Potens Group Compliance RAG API",
        "documents_indexed": len(vector_store.chunks) if vector_store else 0
    }

@app.get("/documents", response_model=List[DocumentInfo])
def get_documents():
    """Lists all documents indexed in the vector store with metadata."""
    if vector_store.is_empty():
        return []
        
    doc_stats = {}
    for chunk in vector_store.chunks:
        doc_id = chunk["doc_id"]
        if doc_id not in doc_stats:
            # Calculate file size
            filepath = DATA_DIR / f"{doc_id}.md"
            size = filepath.stat().st_size if filepath.exists() else 0
            doc_stats[doc_id] = {
                "doc_id": doc_id,
                "doc_name": chunk["doc_name"],
                "chunk_count": 0,
                "file_size_bytes": size
            }
        doc_stats[doc_id]["chunk_count"] += 1
        
    return list(doc_stats.values())

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """Processes a question, handles multilingual translation, retrieves context, and returns cited answers."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG Engine is not initialized.")
        
    logger.info(f"API Request: /ask | Query: '{request.query}' | Filters: {request.doc_ids}")
    
    start_time = time.time()
    result = rag_engine.answer_question(request.query, doc_ids=request.doc_ids)
    elapsed = time.time() - start_time
    
    logger.info(f"API Response: /ask | Time elapsed: {elapsed:.2f}s | Confidence: {result.get('confidence_level')}")
    return result

@app.post("/contradict")
def detect_contradictions(request: ContradictRequest):
    """Cross-examines two documents on a topic to find contradictions, differences, or alignments."""
    if not contradict_engine:
        raise HTTPException(status_code=503, detail="Contradiction Engine is not initialized.")
        
    logger.info(f"API Request: /contradict | Doc A: {request.doc_a} | Doc B: {request.doc_b} | Topic: '{request.topic}'")
    
    start_time = time.time()
    result = contradict_engine.compare_policies(request.doc_a, request.doc_b, request.topic)
    elapsed = time.time() - start_time
    
    logger.info(f"API Response: /contradict | Time elapsed: {elapsed:.2f}s")
    return result

@app.post("/ingest")
def force_ingest():
    """Forces scanning and re-indexing of the data directory."""
    logger.info("Forced ingestion API called.")
    parser = MarkdownParser()
    vector_store.clear()
    
    try:
        chunks = parser.parse_directory(DATA_DIR)
        if chunks:
            vector_store.add_documents(chunks)
            return {"status": "success", "message": f"Successfully re-indexed {len(chunks)} chunks."}
        else:
            raise HTTPException(status_code=404, detail="No markdown files found to ingest.")
    except Exception as e:
        logger.error(f"Forced ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
