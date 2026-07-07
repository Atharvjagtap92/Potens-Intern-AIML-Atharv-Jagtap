import sys
import json
import time
import requests
from pathlib import Path

# Add project root to path for local imports
EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import logger, get_gemini_client
from src.vector_store import SimpleVectorStore
from src.rag_engine import RAGEngine

BACKEND_URL = "http://127.0.0.1:8000"

def evaluate_answer_keywords(case_id: int, answer: str) -> dict:
    """Offline deterministic evaluation checking if key compliance facts exist in the answer."""
    answer_lower = answer.lower()
    
    # Define mapping of case_id to validation rules (list of keywords to match, expected description)
    rules = {
        1: (["75", "seventy-five"], "Per diem is $75 for Potens Labs in Mumbai (Tier 1 city)."),
        2: (["15", "collaborator", "शराब", "$15"], "Allows $15 daily alcohol with collaborator."),
        3: (["no", "economy", "reimbursable"], "Domestic flights must be economy under Core policy."),
        4: (["6", "six", "seis"], "Business class allowed for international > 6 hours in Labs."),
        5: (["do not contain", "not found", "sorry", "क्षम", "माफ़", "सूचना उपलब्ध नहीं"], "Correctly refused out-of-scope question."),
        6: (["do not contain", "not found", "sorry", "क्षम", "माफ़", "सूचना उपलब्ध नहीं"], "Correctly refused general knowledge question."),
        7: (["0.40", "0.4", "kilometer", "kilómetro"], "European operations mileage rate is €0.40/km."),
        8: (["14", "fourteen", "client billing"], "Consulting expenses must be submitted within 14 days."),
        9: (["180", "geneva"], "Hotel cap in Geneva is €180/night."),
        10: (["no", "economy", "prohibited", "economy-only"], "Foundation flights must be economy-only.")
    }
    
    keywords, explanation = rules.get(case_id, ([], ""))
    
    # Check if any keyword matches
    is_correct = any(k in answer_lower for k in keywords)
    rating = 5 if is_correct else 0
    
    return {
        "rating": rating,
        "is_correct": is_correct,
        "reason": f"Verified key terms: {keywords} present in response." if is_correct else f"Missing key facts: {explanation}"
    }

def run_evaluation():
    print("Potens Group RAG Compliance Evaluation Suite Starting...")
    print("==========================================================")
    
    # 1. Load Ground Truth
    gt_file = EVAL_DIR / "ground_truth.json"
    if not gt_file.exists():
        print(f"[ERROR] Ground truth file not found at {gt_file}")
        sys.exit(1)
        
    with open(gt_file, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    print(f"Loaded {len(cases)} test cases from ground_truth.json.")
    
    # 2. Check if Backend is running, otherwise fall back to local direct execution
    use_api = False
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            use_api = True
            print("FastAPI Server detected on port 8000. Running tests via REST API.")
    except requests.exceptions.ConnectionError:
        print("[WARNING] FastAPI server not running. Falling back to local in-process engines.")
        
    local_rag = None
    if not use_api:
        vs = SimpleVectorStore()
        if not vs.load() or vs.is_empty():
            print("[ERROR] Vector Store is empty. You must index the files first. Run 'python run.py' or check configs.")
            sys.exit(1)
        local_rag = RAGEngine(vs)
        
    # 3. Execute cases
    results = []
    retrieval_successes = 0
    hallucination_refusals = 0
    out_of_scope_cases = 0
    total_judge_rating = 0
    
    for idx, case in enumerate(cases):
        qid = case["id"]
        query = case["query"]
        expected_doc = case["expected_doc"]
        case_type = case["type"]
        ground_truth = case["ground_truth"]
        
        print(f"\n[{idx+1}/10] Testing Case ID {qid} ({case_type.upper()})...")
        print(f"Query: '{query}'")
        
        # Get Answer & Searched Chunks
        ans_data = None
        if use_api:
            try:
                api_response = requests.post(f"{BACKEND_URL}/ask", json={"query": query}, timeout=15)
                if api_response.status_code == 200:
                    ans_data = api_response.json()
            except Exception as e:
                print(f"[ERROR] API call failed: {e}")
        else:
            ans_data = local_rag.answer_question(query)
            
        if not ans_data:
            print("[ERROR] Failed to get answer.")
            continue
            
        generated_answer = ans_data["answer"]
        searched_chunks = ans_data.get("source_chunks_searched", [])
        
        # Evaluate Retrieval Success
        # Check if the expected_doc ID is among the retrieved source chunk doc_ids
        retrieval_success = False
        if expected_doc == "none":
            # For out-of-scope, retrieval success is defined as having no high-similarity chunks (handled by threshold)
            retrieval_success = True
            if searched_chunks:
                max_score = max([c.get("score", 0.0) for c in searched_chunks])
                if max_score > 0.35:
                    retrieval_success = False
        else:
            # Check if expected document was found in top chunks
            retrieved_doc_ids = [c["doc_id"] for c in searched_chunks]
            retrieval_success = expected_doc in retrieved_doc_ids
            
        if retrieval_success:
            retrieval_successes += 1
            print("Retrieval: SUCCESS")
        else:
            print(f"Retrieval: FAILED (Expected document {expected_doc} not in top search results: {[c['doc_id'] for c in searched_chunks]})")
            
        # Evaluate Generation with Local Deterministic Evaluator
        print("Running local deterministic evaluation...")
        judge_res = evaluate_answer_keywords(qid, generated_answer)
            
        rating = judge_res.get("rating", 3)
        is_correct = judge_res.get("is_correct", True)
        reason = judge_res.get("reason", "N/A")
        
        total_judge_rating += rating
        
        # Tracking hallucination defense
        refusal_indicators = ["do not contain", "not found", "sorry", "क्षम", "माफ़", "सूचना उपलब्ध नहीं"]
        is_refused = any(ind in generated_answer.lower() for ind in refusal_indicators)
        
        if case_type == "out_of_scope":
            out_of_scope_cases += 1
            if is_refused:
                hallucination_refusals += 1
                print("Hallucination Defense: SUCCESS (Refused answer correctly)")
            else:
                print("Hallucination Defense: FAILED (Attempted to answer out-of-scope question!)")
                
        print(f"Grade: {rating}/5 | Correct: {is_correct} | Judge Reason: {reason}")
        
        results.append({
            "id": qid,
            "query": query,
            "language": ans_data.get("language", "English"),
            "expected_doc": expected_doc,
            "type": case_type,
            "retrieval_success": retrieval_success,
            "generated_answer": generated_answer,
            "ground_truth": ground_truth,
            "generation_correctness": f"{rating}/5 - {'Correct' if is_correct else 'Incorrect'}",
            "judge_rating": rating,
            "judge_reason": reason,
            "verdict": "Pass" if is_correct and (retrieval_success or expected_doc == "none") else "Fail"
        })
        time.sleep(0.1)
        
    # 4. Summarize & Save
    total = len(cases)
    retrieval_precision = retrieval_successes / total
    hall_defense = hallucination_refusals / out_of_scope_cases if out_of_scope_cases > 0 else 1.0
    avg_score = total_judge_rating / total
    
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_cases": total,
        "retrieval_precision": retrieval_precision,
        "hallucination_defense_success": hall_defense,
        "average_judge_rating": avg_score,
        "cases": results
    }
    
    out_file = EVAL_DIR / "eval_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("\n==========================================================")
    print("EVALUATION SUMMARY REPORT")
    print("==========================================================")
    print(f"Total Cases:                 {total}")
    print(f"Retrieval Precision (Top-3):  {retrieval_precision * 100:.1f}%")
    print(f"Hallucination Defense:       {hall_defense * 100:.1f}%")
    print(f"Average Judge Grade:         {avg_score:.2f} / 5.0")
    print("==========================================================")
    print(f"Saved detailed results to {out_file.relative_to(PROJECT_ROOT)}")
    print("==========================================================")

if __name__ == "__main__":
    run_evaluation()
