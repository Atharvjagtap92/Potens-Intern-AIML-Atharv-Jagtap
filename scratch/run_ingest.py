import sys
from pathlib import Path
from dotenv import load_dotenv

# Set paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.config import DATA_DIR, get_gemini_client
from src.document_parser import MarkdownParser
from src.vector_store import SimpleVectorStore

def run_debug_ingest():
    print("==============================================")
    print("Running Standalone Ingestion Diagnostic...")
    print("==============================================")
    
    # 1. Check API Key
    client = get_gemini_client()
    if not client:
        print("[ERROR] Gemini API client is not configured. Check your .env file.")
        return
        
    # 2. Check Data files
    print(f"Data directory: {DATA_DIR}")
    files = list(DATA_DIR.glob("*.md"))
    print(f"Found {len(files)} markdown policy files:")
    for f in files:
        print(f" - {f.name} ({f.stat().st_size} bytes)")
        
    if not files:
        print("[ERROR] No policy documents found in data folder!")
        return
        
    # 3. Parse Markdown
    print("\nParsing markdown documents...")
    parser = MarkdownParser()
    chunks = parser.parse_directory(DATA_DIR)
    print(f"Successfully split into {len(chunks)} chunks.")
    
    if not chunks:
        print("[ERROR] Split produced 0 chunks!")
        return
        
    # 4. Generate Embeddings & Save
    vs = SimpleVectorStore()
    vs.clear()
    
    print("\nSending chunks to Gemini to compute embeddings...")
    print("This makes network calls and might take 5-10 seconds. Please wait...")
    
    try:
        # Get first 3 chunks to test quickly
        test_chunks = chunks[:3]
        print(f"Testing first 3 chunks to verify API response...")
        vs.add_documents(test_chunks)
        print("[SUCCESS] API responded and successfully stored 3 test chunks!")
        
        # Now do the rest
        remaining_chunks = chunks[3:]
        print(f"Indexing remaining {len(remaining_chunks)} chunks...")
        vs.add_documents(remaining_chunks)
        print("[SUCCESS] Fully indexed all chunks in the vector store!")
        print(f"Database saved to {vs.storage_path}")
        
    except Exception as e:
        print("\n[ERROR] Embedding generation failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")

if __name__ == "__main__":
    run_debug_ingest()
