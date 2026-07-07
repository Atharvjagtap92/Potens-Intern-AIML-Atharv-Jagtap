import streamlit as st
import requests
import json
import os
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Potens Compliance Cockpit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Helper function to query backend API
def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False

# Sidebar Info
with st.sidebar:
    st.markdown("""
    <div class='sidebar-profile-card'>
        <img src='https://img.icons8.com/nolan/96/shield.png' width='55'/>
        <h3 style='margin-top: 10px; margin-bottom: 2px; font-size: 16px; font-weight: 700; color: var(--text-primary) !important;'>Potens Group</h3>
        <span style='font-size: 10px; text-transform: uppercase; color: #3b82f6; font-weight: bold;'>Auditor Cockpit</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme Mode selection
    theme_mode = st.radio("Display Theme Mode:", ["Dark Theme", "Light Theme"], index=0)
    st.markdown("---")
    
    is_healthy = check_backend_health()
    if is_healthy:
        st.markdown("""
        <div style='display: flex; align-items: center; margin-bottom: 12px;'>
            <span class='status-dot-online'></span>
            <strong style='font-size: 14px;'>System API Status: Online</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='display: flex; align-items: center; margin-bottom: 12px;'>
            <span class='status-dot-offline'></span>
            <strong style='font-size: 14px;'>System API Status: Offline</strong>
        </div>
        """, unsafe_allow_html=True)
        st.warning("FastAPI backend is not running at port 8000. Start it using `python run.py` first.")
        
    st.markdown("---")
    st.markdown("#### About AI/ML Q1 RAG")
    st.markdown("""
    This dashboard interacts with the Potens compliance engine, enabling:
    1. **Policy Q&A**: Asks questions across subsidiaries in any language and retrieves cited policies.
    2. **Contradiction Auditor**: Analyzes different travel guides to flag discrepancies.
    """)
    st.markdown("---")
    st.markdown("🧬 *Powered by Gemini 1.5 & NumPy Similarity*")

# Select CSS variables based on theme
if theme_mode == "Light Theme":
    css_theme_vars = """
    :root {
        --bg-color: linear-gradient(135deg, #e0f2fe 0%, #f1f5f9 50%, #faf5ff 100%);
        --text-color: #334155;
        --sidebar-bg: #f8fafc;
        --card-bg: rgba(255, 255, 255, 0.75);
        --card-border: rgba(255, 255, 255, 0.6);
        --card-hover-border: #3b82f6;
        --text-primary: #0f172a;
        --citation-bg: rgba(255, 255, 255, 0.6);
        --citation-border: rgba(226, 232, 240, 0.8);
        --badge-text: #334155;
        --divider-start: rgba(226, 232, 240, 0.5);
        --divider-mid: rgba(148, 163, 184, 0.3);
        --tab-list-bg: rgba(226, 232, 240, 0.8);
        --tab-bg: transparent;
        --tab-text: #64748b;
        --tab-hover-bg: rgba(0, 0, 0, 0.03);
        --tab-active-bg: #ffffff;
        --tab-active-text: #2563eb;
        --title-gradient: linear-gradient(90deg, #1e3a8a 0%, #2563eb 50%, #4f46e5 100%);
        --input-bg: rgba(255, 255, 255, 0.9);
        --input-border: rgba(148, 163, 184, 0.4);
    }
    """
else:
    css_theme_vars = """
    :root {
        --bg-color: radial-gradient(circle at 80% 20%, rgba(37, 99, 235, 0.08) 0%, transparent 45%), radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.08) 0%, transparent 45%), #0b0f19;
        --text-color: #e2e8f0;
        --sidebar-bg: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.4);
        --card-border: #334155;
        --card-hover-border: #475569;
        --text-primary: #ffffff;
        --citation-bg: #111827;
        --citation-border: #1e293b;
        --badge-text: #e2e8f0;
        --divider-start: #1e293b;
        --divider-mid: #334155;
        --tab-list-bg: rgba(15, 23, 42, 0.6);
        --tab-bg: transparent;
        --tab-text: #94a3b8;
        --tab-hover-bg: rgba(255, 255, 255, 0.05);
        --tab-active-bg: rgba(30, 41, 59, 0.8);
        --tab-active-text: #3b82f6;
        --title-gradient: linear-gradient(90deg, #3b82f6 0%, #60a5fa 50%, #818cf8 100%);
        --input-bg: rgba(15, 23, 42, 0.6);
        --input-border: #334155;
    }
    """

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    {css_theme_vars}
    
    /* Animation Keyframes */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(12px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }}
        70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}
    
    @keyframes pulseGlowOffline {{
        0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }}
        70% {{ box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
    }}
    
    /* Apply fadeInUp animation to elements for liquid-smooth load */
    .compliance-card, .citation-card, .main-title, .main-subtitle, .stTabs, div[data-testid="stExpander"], .header-banner, .metric-card {{
        animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    
    .stApp {{
        background: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'Inter', sans-serif;
        transition: background 0.3s ease, color 0.3s ease;
    }}
    
    /* Custom Input and Select Box Skins */
    div[data-baseweb="select"], div[data-baseweb="input"], input[type="text"], .stMultiSelect {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
        color: var(--text-color) !important;
        transition: all 0.2s ease !important;
    }}
    div[data-baseweb="select"]:hover, div[data-baseweb="input"]:hover, input[type="text"]:hover, .stMultiSelect:hover {{
        border-color: var(--card-hover-border) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
    }}
    
    /* Styling Streamlit Labels */
    label[data-testid="stWidgetLabel"] {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #64748b !important;
        margin-bottom: 6px !important;
    }}
    
    /* Header Banner Container */
    .header-banner {{
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px 32px !important;
        margin-bottom: 24px !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06) !important;
    }}
    
    /* Title styling */
    .main-title {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        background: var(--title-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.025em !important;
    }}
    
    .main-subtitle {{
        font-family: 'Inter', sans-serif !important;
        font-size: 1.05rem !important;
        color: var(--text-color) !important;
        opacity: 0.85;
        margin-bottom: 0 !important;
    }}
    
    h1, h2, h3, h4 {{
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--card-border) !important;
        transition: background-color 0.3s ease;
    }}
    
    /* Custom Sidebar Card */
    .sidebar-profile-card {{
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        text-align: center !important;
        margin-bottom: 20px !important;
    }}
    
    /* Status indicator glowing animation */
    .status-dot-online {{
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulseGlow 2s infinite;
    }}
    
    .status-dot-offline {{
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #ef4444;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulseGlowOffline 2s infinite;
    }}
    
    /* Card Container & Streamlit Border Container Wrapper */
    .compliance-card, div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 16px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
    }}
    .compliance-card:hover, div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-2px) scale(1.002) !important;
        border-color: var(--card-hover-border) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12) !important;
    }}
    
    /* Custom styled Streamlit expanders */
    div[data-testid="stExpander"] {{
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stExpander"]:hover {{
        border-color: var(--card-hover-border) !important;
    }}
    
    /* Citation Card */
    .citation-card {{
        background: var(--citation-bg) !important;
        border-left: 4px solid #3b82f6;
        border-radius: 4px 8px 8px 4px;
        padding: 12px 16px;
        margin-top: 12px;
        margin-bottom: 12px;
        font-size: 14px;
        border-top: 1px solid var(--citation-border);
        border-right: 1px solid var(--citation-border);
        border-bottom: 1px solid var(--citation-border);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }}
    .citation-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
    }}
    
    .citation-header {{
        font-weight: 600;
        color: #3b82f6;
        margin-bottom: 4px;
    }}
    .citation-snippet {{
        font-style: italic;
        color: #9ca3af;
        margin-top: 6px;
    }}
    
    /* Alert Status Badges */
    .badge {{
        display: inline-block;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        margin-right: 8px;
    }}
    .badge-contradiction {{
        background-color: #7f1d1d;
        color: #fca5a5;
        border: 1px solid #ef4444;
    }}
    .badge-difference {{
        background-color: #78350f;
        color: #fde047;
        border: 1px solid #eab308;
    }}
    .badge-aligned {{
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #10b981;
    }}
    
    /* Custom divider */
    .divider {{
        height: 1px;
        background: linear-gradient(90deg, var(--divider-start), var(--divider-mid), var(--divider-start));
        margin: 20px 0;
    }}
    
    /* Button custom hover and active states */
    .stButton>button {{
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35) !important;
        background: linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%) !important;
    }}
    .stButton>button:active {{
        transform: translateY(0) scale(0.98) !important;
    }}
    
    /* Segmented Control Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: var(--tab-list-bg) !important;
        padding: 6px !important;
        border-radius: 12px !important;
        border-bottom: none !important;
        display: flex !important;
        width: fit-content !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 24px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: var(--tab-bg) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        color: var(--tab-text) !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: var(--text-primary) !important;
        background-color: var(--tab-hover-bg) !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: var(--tab-active-bg) !important;
        color: var(--tab-active-text) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        font-weight: 600 !important;
    }}
    
    /* Custom HTML Metrics Grid */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
        margin-top: 16px;
    }}
    .metric-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 24px 16px !important;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        min-height: 125px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }}
    .metric-title {{
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #64748b !important;
        margin-bottom: 6px !important;
    }}
    .metric-value {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: var(--title-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)

# Main Header Card Banner
st.markdown("""
<div class='header-banner'>
    <h1 class='main-title'>🛡️ Policy Compliance Cockpit</h1>
    <p class='main-subtitle'>A unified intelligence system to retrieve, translate, and audit compliance guidelines across Potens subsidiaries.</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_qa, tab_compare, tab_docs, tab_eval = st.tabs([
    "🔍 Compliance Q&A Search", 
    "⚖️ Policy Contradiction Auditor", 
    "📂 Document Explorer", 
    "📊 Evaluation Suite"
])

# --- TAB 1: COMPLIANCE Q&A SEARCH ---
with tab_qa:
    st.subheader("Query Compliance Guidelines")
    st.markdown("Search policy documents in English or any Indian language. The engine retrieves English source texts, synthesizes the answer, and translates it back to the query language with strict source citations.")
    
    if not is_healthy:
        st.error("Cannot connect to the FastAPI backend. Please make sure the server is running.")
    else:
        # Load available documents for filter
        docs_list = []
        try:
            doc_response = requests.get(f"{BACKEND_URL}/documents", timeout=2.0)
            if doc_response.status_code == 200:
                docs_list = doc_response.json()
        except Exception:
            pass
            
        doc_options = {d["doc_id"]: d["doc_name"] for d in docs_list}
        
        # User input fields wrapped in glassy card
        with st.container(border=True):
            col_q, col_opt = st.columns([3, 1])
            with col_q:
                query = st.text_input(
                    "Enter your compliance query:",
                    value="Does Potens Labs reimburse alcoholic drinks during dinners?",
                    placeholder="e.g. Can a consultant book Business Class flights?"
                )
                
            with col_opt:
                selected_docs = st.multiselect(
                    "Filter by Document:",
                    options=list(doc_options.keys()),
                    format_func=lambda x: doc_options[x],
                    help="Leave empty to search all documents."
                )
            
        # Action button under the card
        run_search = st.button("Run Compliance Search", key="run_qa")
        
        if run_search:
            with st.spinner("Retrieving facts, translating boundaries, and synthesizing answer..."):
                payload = {
                    "query": query,
                    "doc_ids": selected_docs if selected_docs else None
                }
                
                try:
                    response = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=12.0)
                    
                    if response.status_code == 200:
                        res = response.json()
                        
                        # Display Results
                        st.markdown("<div class='compliance-card'>", unsafe_allow_html=True)
                        st.markdown(f"#### 🤖 Answer (Language: {res['language']})")
                        
                        # Style confidence
                        conf = res['confidence_score']
                        conf_lvl = res['confidence_level']
                        if conf_lvl == "High":
                            conf_badge = f"<span class='badge badge-aligned'>Confidence: {conf:.2f} (High)</span>"
                        elif conf_lvl == "Medium":
                            conf_badge = f"<span class='badge badge-difference'>Confidence: {conf:.2f} (Medium)</span>"
                        else:
                            conf_badge = f"<span class='badge badge-contradiction'>Confidence: {conf:.2f} (Low/None)</span>"
                            
                        st.markdown(f"<div>{conf_badge}</div><br>", unsafe_allow_html=True)
                        
                        # Display output text
                        st.markdown(res['answer'])
                        
                        # Display original translated query if query was not English
                        if res['language'] != "English":
                            st.markdown(f"<p style='font-size: 13px; color: #64748b;'>Translated Query for Retrieval: <i>'{res['translated_query']}'</i></p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Display Citations
                        citations = res.get("citations", [])
                        if citations:
                            st.markdown("#### 📖 Citations & Source Snippets")
                            cols_cit = st.columns(len(citations) if len(citations) < 3 else 3)
                            
                            for i, cit in enumerate(citations):
                                col_idx = i % 3
                                with cols_cit[col_idx]:
                                    st.markdown(f"""
                                    <div class='citation-card'>
                                        <div class='citation-header'>[{cit['source_index']}] {cit['doc_name']}</div>
                                        <div style='font-size:12px; font-weight:bold; color:#64748b;'>{cit['section']}</div>
                                        <div class='citation-snippet'>"{cit['snippet'][:180]}..."</div>
                                        <div style='font-size:11px; margin-top:5px; color:#4b5563;'>Char Offset: {cit['char_offset']}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            if conf_lvl != "None":
                                st.info("No sources explicitly cited in the response.")
                                
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

# --- TAB 2: POLICY CONTRADICTION AUDITOR ---
with tab_compare:
    st.subheader("Cross-Examine Subsidiary Policies")
    st.markdown("Compare policy rules of two entities side-by-side to highlight direct contradictions, rule discrepancies, or alignments.")
    
    if not is_healthy:
        st.error("Cannot connect to the FastAPI backend.")
    else:
        # Load documents for dropdown
        docs_list = []
        try:
            doc_response = requests.get(f"{BACKEND_URL}/documents", timeout=2.0)
            if doc_response.status_code == 200:
                docs_list = doc_response.json()
        except Exception:
            pass
            
        doc_options = {d["doc_id"]: d["doc_name"] for d in docs_list}
        
        # User selections wrapped in glassy card
        with st.container(border=True):
            col_a, col_b = st.columns(2)
            with col_a:
                doc_a = st.selectbox(
                    "Document A (Base Reference):",
                    options=list(doc_options.keys()),
                    format_func=lambda x: doc_options[x],
                    index=0 if len(doc_options) > 0 else 0
                )
            with col_b:
                doc_b = st.selectbox(
                    "Document B (Comparison Subject):",
                    options=list(doc_options.keys()),
                    format_func=lambda x: doc_options[x],
                    index=1 if len(doc_options) > 1 else 0
                )
                
            # Quick-start topic presets
            presets = [
                "Travel flight class restrictions for domestic and international routes",
                "Daily per-diem meal caps in Tier 1 and other cities",
                "Alcohol expense reimbursement guidelines",
                "Lodging / Hotel accommodation price caps per night",
                "Allowed types of ground transportation (Uber Comfort, Black Car, public transit)",
                "Submission deadline for expense claims after return date",
                "Reimbursement rate for personal vehicle mileage per mile/kilometer"
            ]
            
            topic = st.selectbox("Select a comparison topic (or write your own below):", options=["-- Write Custom Topic --"] + presets)
            
            custom_topic = ""
            if topic == "-- Write Custom Topic --":
                custom_topic = st.text_input("Enter custom comparison topic:", value="Hotel accommodation price caps")
                
            selected_topic = custom_topic if topic == "-- Write Custom Topic --" else topic
            
        # Action button under card
        run_audit = st.button("Run Audit", key="run_contradict")
        
        if run_audit:
            if doc_a == doc_b:
                st.warning("Please select two different documents to compare.")
            else:
                with st.spinner("Analyzing text blocks and scanning for regulatory contradictions..."):
                    payload = {
                        "doc_a": doc_a,
                        "doc_b": doc_b,
                        "topic": selected_topic
                    }
                    
                    try:
                        response = requests.post(f"{BACKEND_URL}/contradict", json=payload, timeout=12.0)
                        if response.status_code == 200:
                            res = response.json()
                            
                            # Render Audit Verdict
                            st.markdown("### ⚖️ Audit Verdict")
                            is_contradicts = res.get("contradicts", False)
                            has_diffs = res.get("has_differences", False)
                            
                            if is_contradicts:
                                verdict_html = "<span class='badge badge-contradiction' style='font-size:16px; padding:6px 16px;'>🚨 CONTRADICTION DETECTED</span>"
                            elif has_diffs:
                                verdict_html = "<span class='badge badge-difference' style='font-size:16px; padding:6px 16px;'>⚠️ POLICY DIFFERENCE FLAGS</span>"
                            else:
                                verdict_html = "<span class='badge badge-aligned' style='font-size:16px; padding:6px 16px;'>✅ POLICIES ALIGNED</span>"
                                
                            st.markdown(verdict_html, unsafe_allow_html=True)
                            st.markdown(f"<div class='compliance-card' style='margin-top:12px;'><b>Auditor Reasoning:</b><br>{res.get('reasoning')}</div>", unsafe_allow_html=True)
                            
                            # Render side-by-side columns
                            col_doc_a, col_doc_b = st.columns(2)
                            
                            with col_doc_a:
                                details_a = res.get("details_doc_a", {})
                                st.markdown(f"<div class='compliance-card' style='border-top: 4px solid #3b82f6;'>", unsafe_allow_html=True)
                                st.markdown(f"#### 📄 {details_a.get('doc_name')}")
                                
                                if details_a.get("covers_topic", True):
                                    st.markdown(f"**Stance:** {details_a.get('stance')}")
                                    st.markdown(f"**Key Section:** `{details_a.get('key_citation_section')}`")
                                    if details_a.get("key_snippet"):
                                        st.markdown(f"<div class='citation-card'><div class='citation-snippet'>\"{details_a.get('key_snippet')}\"</div></div>", unsafe_allow_html=True)
                                else:
                                    st.info("Document does not cover this topic.")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            with col_doc_b:
                                details_b = res.get("details_doc_b", {})
                                st.markdown(f"<div class='compliance-card' style='border-top: 4px solid #10b981;'>", unsafe_allow_html=True)
                                st.markdown(f"#### 📄 {details_b.get('doc_name')}")
                                
                                if details_b.get("covers_topic", True):
                                    st.markdown(f"**Stance:** {details_b.get('stance')}")
                                    st.markdown(f"**Key Section:** `{details_b.get('key_citation_section')}`")
                                    if details_b.get("key_snippet"):
                                        st.markdown(f"<div class='citation-card'><div class='citation-snippet'>\"{details_b.get('key_snippet')}\"</div></div>", unsafe_allow_html=True)
                                else:
                                    st.info("Document does not cover this topic.")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                        else:
                            st.error(f"Error {response.status_code}: {response.text}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

# --- TAB 3: DOCUMENT EXPLORER ---
with tab_docs:
    st.subheader("Ingested Compliance Database")
    st.markdown("Below is a catalog of the company compliance policies ingested and stored in the vector database index.")
    
    if not is_healthy:
        st.error("Cannot connect to the FastAPI backend.")
    else:
        try:
            response = requests.get(f"{BACKEND_URL}/documents", timeout=2.0)
            if response.status_code == 200:
                docs = response.json()
                
                if not docs:
                    st.info("No documents are currently ingested in the vector database.")
                else:
                    # Render documents list in cards
                    cols_docs = st.columns(2)
                    for idx, doc in enumerate(docs):
                        col_idx = idx % 2
                        with cols_docs[col_idx]:
                            st.markdown(f"""
                            <div class='compliance-card'>
                                <h3>📂 {doc['doc_name']}</h3>
                                <p style='font-size: 13px; color: #64748b; margin-top:-5px;'>Document ID: <code>{doc['doc_id']}</code></p>
                                <table style='width:100%; border-collapse:collapse; margin-top:10px;'>
                                    <tr>
                                        <td style='padding:5px 0; font-weight:bold;'>Semantic Chunks</td>
                                        <td style='padding:5px 0; text-align:right;'>{doc['chunk_count']} chunks</td>
                                    </tr>
                                    <tr>
                                        <td style='padding:5px 0; font-weight:bold;'>File Size</td>
                                        <td style='padding:5px 0; text-align:right;'>{doc['file_size_bytes'] / 1024:.2f} KB</td>
                                    </tr>
                                    <tr>
                                        <td style='padding:5px 0; font-weight:bold;'>Language</td>
                                        <td style='padding:5px 0; text-align:right;'>English (Source)</td>
                                    </tr>
                                </table>
                            </div>
                            """, unsafe_allow_html=True)
                            
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                st.markdown("### Database Operations")
                st.markdown("Index parsing, embedding computation, and saving can be forced by scanning the `data/` directory again.")
                
                if st.button("Force Re-ingest database", key="reingest"):
                    with st.spinner("Re-parsing data directory and updating embeddings..."):
                        re_response = requests.post(f"{BACKEND_URL}/ingest", timeout=25.0)
                        if re_response.status_code == 200:
                            st.success(re_response.json()["message"])
                            st.rerun()
                        else:
                            st.error("Failed to re-ingest documents.")
            else:
                st.error("Failed to retrieve document metadata from the server.")
        except Exception as e:
            st.error(f"Connection failed: {e}")

# --- TAB 4: EVALUATION SUITE ---
with tab_eval:
    st.subheader("RAG Evaluation Suite")
    st.markdown("""
    To verify compliance database retrieval precision and hallucination prevention, an offline evaluation script runs **10 Q&A ground-truth pairs**.
    This panel displays the evaluation methodology and results.
    """)
    
    # Check if eval results file exists
    eval_results_file = Path("eval/eval_results.json")
    if eval_results_file.exists():
        try:
            with open(eval_results_file, "r", encoding="utf-8") as f:
                eval_data = json.load(f)
                
            st.success("✅ Offline Evaluation Results Loaded!")
            
            # Key statistics (Custom HTML Metrics Grid)
            ret_acc = eval_data.get("retrieval_precision", 0) * 100
            hall_def = eval_data.get("hallucination_defense_success", 0) * 100
            
            st.markdown(f"""
            <div class='metrics-grid'>
                <div class='metric-card'>
                    <div class='metric-title'>Total Evaluation Cases</div>
                    <div class='metric-value'>{eval_data.get("total_cases", 0)}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-title'>Retrieval Precision (Top-3)</div>
                    <div class='metric-value'>{ret_acc:.1f}%</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-title'>Hallucination Defense</div>
                    <div class='metric-value'>{hall_def:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
                
            # Table of cases
            st.markdown("### Ground-Truth Test Run Table")
            
            cases = eval_data.get("cases", [])
            for idx, case in enumerate(cases):
                verdict = case.get("verdict", "Pass")
                badge_style = "badge-aligned" if verdict == "Pass" else "badge-contradiction"
                
                with st.expander(f"Case {idx+1}: {case.get('query')[:70]}... | Verdict: {verdict}"):
                    st.markdown(f"""
                    **Original Query:** `{case.get('query')}`  
                    **Language:** `{case.get('language')}`  
                    **Expected Context Doc:** `{case.get('expected_doc')}`  
                    **Retrieval Success:** {'✅ Yes' if case.get('retrieval_success') else '❌ No'}  
                    **Response Correctness (LLM Judge):** {case.get('generation_correctness')}  
                    
                    **RAG Generated Answer:**
                    > {case.get('generated_answer')}
                    
                    **Ground Truth Expected Info:**
                    > {case.get('ground_truth')}
                    """)
                    
        except Exception as e:
            st.error(f"Failed to parse evaluation results: {e}")
    else:
        st.warning("⚠️ No offline evaluation run found. Run the evaluation script via command line first.")
        st.markdown("""
        To run the evaluation suite and compute correctness, open a terminal in the project directory and run:
        ```bash
        python eval/eval.py
        ```
        This will run all 10 ground-truth compliance scenarios and save the metrics report to `eval/eval_results.json`.
        """)
        
        st.markdown("### Ground Truth Test Scenarios List")
        st.markdown("""
        1. **Meal limits (English)**: "What is the per diem meal allowance in Mumbai for Potens Labs?"
        2. **Meal limits (Hindi)**: "क्या रात के भोजन में शराब का खर्च कंपनी देती है?" (Tests boundary translation & R&D exception)
        3. **Business Class (English)**: "Can I book a business class flight for a 5-hour domestic flight under Core policy?"
        4. **Business Class (Spanish)**: "¿Cuál es el límite de horas de vuelo para clase ejecutiva internacional en Potens Labs?" (Tests Spanish translation)
        5. **Out of Scope (Halucination Test)**: "What is the policy for buying snacks for office birthday parties?" (Tests refusal)
        6. **Out of Scope (General Knowledge)**: "What is the capital of India?" (Tests refusal of general questions)
        7. **Mileage comparison**: "How much does Potens Europe reimburse for personal car mileage?" (Tests EU policy/km conversion)
        8. **Late submissions**: "Can I submit my expenses for a consulting project 20 days after traveling?" (Tests Consulting 14-day limit)
        9. **Lodging limit**: "What is the maximum hotel room rate in Geneva for European operations?" (Tests Western Europe Tier 1 hotel cap)
        10. **Non-Profit Flights**: "Does Potens Foundation allow Premium Economy class flights?" (Tests Foundation strict Economy-only policy)
        """)
