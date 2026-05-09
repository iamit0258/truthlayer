import streamlit as st
import pandas as pd
from fact_checker import FactChecker
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF preview
import base64

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Truth Layer | AI Fact-Checker",
    page_icon="🛡️",
    layout="wide"
)

# Premium UI Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top right, #0f172a, #020617);
        color: #f8fafc;
    }

    /* Hide Sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }

    .main-header {
        background: linear-gradient(135deg, #2dd4bf 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        padding-top: 1rem;
    }

    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Card Styling */
    .card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }

    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .status-verified { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
    .status-inaccurate { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
    .status-false { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }

    .claim-text { font-size: 1.15rem; font-weight: 600; color: #f1f5f9; margin: 0.8rem 0; line-height: 1.4; }
    .reality-box { background: rgba(15, 23, 42, 0.5); padding: 1rem; border-radius: 12px; margin: 0.8rem 0; border-left: 4px solid #3b82f6; }

    /* Sticky Left Panel */
    [data-testid="column"]:nth-child(1) {
        position: sticky;
        top: 2rem;
        height: calc(100vh - 4rem);
        overflow-y: hidden;
    }

    /* Scrollable Right Panel */
    [data-testid="column"]:nth-child(2) {
        height: auto;
        overflow-y: visible;
    }

    /* File Uploader Styling */
    .stFileUploader {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 2px dashed rgba(59, 130, 246, 0.3) !important;
        border-radius: 24px !important;
        padding: 1rem !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.8rem;
        font-weight: 600;
    }

    /* Evidence Styling */
    .evidence-item {
        background: rgba(15, 23, 42, 0.3);
        padding: 0.8rem;
        border-radius: 10px;
        margin-top: 0.5rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .evidence-title { color: #38bdf8; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem; }
    .evidence-content { color: #94a3b8; font-size: 0.8rem; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

def get_pdf_preview(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_data = pix.tobytes("png")
        return base64.b64encode(img_data).decode()
    except:
        return None

# Session State
if 'report' not in st.session_state:
    st.session_state.report = None
if 'file_info' not in st.session_state:
    st.session_state.file_info = None

# Header
st.markdown('<h1 class="main-header">Truth Layer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Fact-Checking Platform with Deep-Dive Citations</p>', unsafe_allow_html=True)

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

# 1. INITIAL STATE: CENTERED UPLOAD
if st.session_state.report is None:
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        uploaded_file = st.file_uploader("Upload Marketing PDF", type="pdf", label_visibility="collapsed")
        
        if uploaded_file:
            st.session_state.file_info = {
                "name": uploaded_file.name,
                "size": f"{uploaded_file.size / 1024 / 1024:.2f} MB"
            }
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("🚀 Start Verification"):
                with st.spinner("🕵️ Analyzing claims and fetching deep-dive evidence..."):
                    try:
                        checker = FactChecker(groq_key, tavily_key)
                        st.session_state.report = checker.process_document("temp.pdf")
                        st.session_state.preview_img = get_pdf_preview("temp.pdf")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# 2. REPORT STATE: SPLIT SCREEN
else:
    col_info, col_report = st.columns([1, 1.6], gap="large")
    
    with col_info:
        # Fixed Content on the left
        st.markdown(f"""
        <div class="card">
            <h3 style="margin-top:0;">📄 File Details</h3>
            <p><strong>Name:</strong> {st.session_state.file_info['name']}</p>
            <p><strong>Size:</strong> {st.session_state.file_info['size']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'preview_img' in st.session_state and st.session_state.preview_img:
            st.image(f"data:image/png;base64,{st.session_state.preview_img}", use_container_width=True)
        
        st.markdown("---")
        
        # Actions
        if st.button("🔄 Check Another File"):
            st.session_state.report = None
            st.session_state.file_info = None
            st.rerun()
            
        df = pd.DataFrame(st.session_state.report)
        st.download_button(
            label="📥 Export Analysis (CSV)",
            data=df.to_csv(index=False),
            file_name=f"report_{st.session_state.file_info['name']}.csv",
            mime="text/csv"
        )

    with col_report:
        st.markdown(f"### 📊 Analysis Report ({len(st.session_state.report)} Claims Verified)")
        
        for idx, item in enumerate(st.session_state.report):
            status_class = f"status-{item['status'].lower()}"
            
            with st.container():
                # Card Main Body
                st.markdown(f"""
                <div class="card" style="margin-bottom: 0;">
                    <span class="status-badge {status_class}">{item['status']}</span>
                    <div class="claim-text">"{item['claim']}"</div>
                    <div class="reality-box">
                        <small style="color: #94a3b8; text-transform: uppercase; font-size: 0.7rem; font-weight: 700;">Reality Check</small>
                        <div style="margin-top: 0.5rem; line-height: 1.6; font-size: 0.95rem;">{item['reality']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable Deep-Dive Citations
                with st.expander("🔍 View Deep-Dive Citations & Reasoning"):
                    st.markdown(f"**Reasoning:** {item['reasoning']}")
                    st.markdown("---")
                    st.markdown("**Evidence Sources:**")
                    for evidence in item['evidence']:
                        st.markdown(f"""
                        <div class="evidence-item">
                            <div class="evidence-title">{evidence['title']}</div>
                            <div class="evidence-content">{evidence['content'][:200]}...</div>
                            <a href="{evidence['url']}" style="color: #38bdf8; font-size: 0.75rem;" target="_blank">🔗 Open Full Source</a>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
