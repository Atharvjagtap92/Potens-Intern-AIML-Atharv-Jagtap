import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Set paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.vector_store import SimpleVectorStore
from src.rag_engine import RAGEngine

def run_direct_test():
    print("==============================================")
    print("Starting Direct RAG Diagnostic Test...")
    print("==============================================")
    
    # 1. Load Vector Store
    print("Step 1: Loading vector store...")
    vs = SimpleVectorStore()
    if not vs.load():
        print("[ERROR] Failed to load vector store from disk. Database is empty.")
        return
    print(f"Vector store loaded successfully with {len(vs.chunks)} chunks.")
    
    # 2. Initialize RAG
    print("\nStep 2: Initializing RAG Engine...")
    rag = RAGEngine(vs)
    
    query = "What is the per diem meal allowance in Mumbai for Potens Labs?"
    
    print(f"\nStep 3: Querying the engine with: '{query}'")
    
    # Track steps in detail
    print("\n--- Starting answer_question logic manually ---")
    
    # 3.1 Lang detect
    print("[3.1] Detecting language and translating query...")
    start = time.time()
    detected_lang, translated_query = rag._detect_and_translate_query(query)
    print(f"      Completed in {time.time() - start:.2f}s | Lang: {detected_lang} | Query: '{translated_query}'")
    
    # 3.2 Search
    print("[3.2] Generating query embedding and searching local vector index...")
    start = time.time()
    retrieved_chunks = vs.search(translated_query, top_k=4)
    print(f"      Completed in {time.time() - start:.2f}s | Retrieved: {len(retrieved_chunks)} chunks.")
    for idx, c in enumerate(retrieved_chunks):
        print(f"      - [{idx+1}] Doc: {c['doc_id']} | Score: {c['score']:.4f} | Path: {c['section']}")
        
    if not retrieved_chunks:
        print("[WARNING] Retrieved chunks list is empty! Search failed.")
        return
        
    # 3.3 LLM Call
    print("[3.3] Formulating prompt and calling Gemini-2.5-flash for response...")
    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks):
        context_str += f"--- SOURCE [{idx + 1}] ---\n"
        context_str += f"Document: {chunk['doc_name']} ({chunk['doc_id']})\n"
        context_str += f"Section: {chunk['section']}\n"
        context_str += f"Content: {chunk['text']}\n\n"
        
    system_instruction = f"""
    You are a highly precise Potens Group compliance assistant. Your task is to answer the user's query based ONLY on the provided context sources.
    You MUST write your response in the language: {detected_lang}.
    """
    
    prompt = f"User Query: \"{translated_query}\"\n\nProvided Context Sources:\n{context_str}"
    
    start = time.time()
    client = rag.vector_store._get_embeddings_batch # helper to check get_gemini_client
    import src.config as config
    gen_client = config.get_gemini_client()
    
    try:
        model = gen_client.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_instruction
        )
        # Timeout at 8 seconds to prevent lock
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": 8.0}
        )
        print(f"      Completed in {time.time() - start:.2f}s")
        print("\n[SUCCESS] Response generated:")
        print(response.text)
    except Exception as e:
        print(f"\n[FAILED] Generation failed: {type(e).__name__} - {e}")

if __name__ == "__main__":
    run_direct_test()
