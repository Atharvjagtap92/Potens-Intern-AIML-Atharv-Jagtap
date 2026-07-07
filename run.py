import os
import sys
import time
import subprocess
import signal

def run_servers():
    """Runs the FastAPI backend and Streamlit frontend concurrently."""
    print("==========================================================")
    print("[INFO] Starting Potens Group Compliance Cockpit Servers...")
    print("==========================================================")
    
    # Check for Gemini API key first
    from dotenv import load_dotenv
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("\n[WARNING] WARNING: GEMINI_API_KEY is not set in your .env file!")
        print("   The RAG engine and embedding generation will fail.")
        print("   Please open .env and add your key: GEMINI_API_KEY=AIzaSy...\n")
        
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "src.backend:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "src/frontend.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ]
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("[INFO] Launching FastAPI Backend on http://127.0.0.1:8000 ...")
        backend_proc = subprocess.Popen(
            backend_cmd
        )
        processes.append(backend_proc)
        
        # Wait a moment for backend to initialize
        time.sleep(2)
        
        # Start Streamlit frontend
        print("[INFO] Launching Streamlit Dashboard on http://127.0.0.1:8501 ...")
        frontend_proc = subprocess.Popen(
            frontend_cmd
        )
        processes.append(frontend_proc)
        
        print("\n[INFO] Both servers are running. Press Ctrl+C to terminate both servers.\n")
        
        # Monitor processes and stream output to terminal
        while True:
            # Check if either process exited
            backend_status = backend_proc.poll()
            frontend_status = frontend_proc.poll()
            
            if backend_status is not None:
                print(f"\n[ERROR] FastAPI backend exited unexpectedly with code {backend_status}.")
                break
            if frontend_status is not None:
                print(f"\n[ERROR] Streamlit frontend exited unexpectedly with code {frontend_status}.")
                break
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down servers gracefully...")
    finally:
        # Terminate all processes
        for proc in processes:
            if proc.poll() is None:
                print(f"Stopping process {proc.pid}...")
                try:
                    # On Windows, we use terminate()
                    proc.terminate()
                    # Wait up to 3 seconds for graceful shutdown
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print(f"Force-killing process {proc.pid}...")
                    proc.kill()
                    
        print("[INFO] Shutdown complete. Goodbye!")

if __name__ == "__main__":
    run_servers()
