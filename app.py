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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #0ea5e9;
        --primary-glow: rgba(14, 165, 233, 0.3);
        --accent: #8b5cf6;
        --bg-dark: #020617;
        --card-bg: rgba(30, 41, 59, 0.4);
        --text-main: #f8fafc;
        --text-dim: #94a3b8;
    }

    * {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%);
        background-attachment: fixed;
        color: var(--text-main);
    }

    /* Floating Blobs Background */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(14, 165, 233, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.1) 0%, transparent 60%);
        z-index: -1;
        filter: blur(80px);
        animation: floatingBlobs 20s infinite alternate-reverse linear;
    }

    @keyframes floatingBlobs {
        0% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(5%, 10%) scale(1.1); }
        66% { transform: translate(-5%, 5%) scale(0.9); }
        100% { transform: translate(0, 0) scale(1); }
    }

    /* Hide Sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem;
        font-weight: 800;
        text-align: center;
        padding: 3rem 0 0.5rem 0;
        letter-spacing: -0.04em;
        animation: fadeInDown 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    .sub-header {
        text-align: center;
        color: var(--text-dim);
        font-size: 1.35rem;
        margin-bottom: 4rem;
        font-weight: 300;
        letter-spacing: 0.02em;
        animation: fadeInUp 1s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Card Styling */
    .card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 28px;
        margin-bottom: 1.5rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
    }

    .card:hover {
        transform: translateY(-6px) scale(1.01);
        border-color: rgba(14, 165, 233, 0.4);
        background: rgba(30, 41, 59, 0.5);
    }

    /* Metric Cards */
    .metric-container {
        display: flex;
        gap: 1.25rem;
        margin-bottom: 2.5rem;
    }
    .metric-card {
        flex: 1;
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(255, 255, 255, 0.15);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.8rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    /* Status Badges */
    .status-badge {
        padding: 0.5rem 1.25rem;
        border-radius: 14px;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 1.25rem;
    }
    .status-verified { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); box-shadow: 0 0 20px rgba(16, 185, 129, 0.1); }
    .status-inaccurate { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
    .status-false { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); box-shadow: 0 0 20px rgba(239, 68, 68, 0.1); }

    .claim-text { 
        font-size: 1.4rem; 
        font-weight: 600; 
        color: #fff; 
        margin: 1.25rem 0; 
        line-height: 1.5;
        border-left: 5px solid var(--primary);
        padding-left: 1.5rem;
        letter-spacing: -0.01em;
    }
    
    .reality-box { 
        background: rgba(15, 23, 42, 0.8); 
        padding: 1.5rem; 
        border-radius: 20px; 
        margin-top: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
    }

    /* File Uploader Customization */
    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.4);
        border: 2px dashed rgba(56, 189, 248, 0.3);
        border-radius: 32px;
        padding: 3rem;
        transition: all 0.4s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary);
        background: rgba(15, 23, 42, 0.6);
        box-shadow: 0 0 40px rgba(14, 165, 233, 0.1);
    }

    /* Custom Button */
    .stButton>button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        border: none;
        border-radius: 16px;
        color: white;
        padding: 1rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(37, 99, 235, 0.5);
        filter: brightness(1.1);
    }

    /* Evidence Items */
    .evidence-item {
        background: rgba(15, 23, 42, 0.5);
        padding: 1.25rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        transition: all 0.2s ease;
    }
    .evidence-item:hover {
        border-color: rgba(56, 189, 248, 0.4);
        background: rgba(15, 23, 42, 0.7);
    }
    .evidence-title { color: var(--primary); font-size: 0.95rem; font-weight: 800; margin-bottom: 0.5rem; }
    .evidence-content { color: var(--text-dim); font-size: 0.85rem; line-height: 1.7; }
    
    /* Expander Styling */
    .stExpander {
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        background: rgba(30, 41, 59, 0.2) !important;
    }
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

# 1. INITIAL STATE: HERO SECTION
if st.session_state.report is None:
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
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
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Verify Claims Now"):
                with st.spinner("🕵️ Analyzing claims and fetching deep-dive evidence..."):
                    try:
                        checker = FactChecker(groq_key, tavily_key)
                        st.session_state.report = checker.process_document("temp.pdf")
                        st.session_state.preview_img = get_pdf_preview("temp.pdf")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.markdown("""
                <div style="text-align: center; color: #64748b; margin-top: 1.5rem;">
                    <p>Drop your marketing PDF here to verify its claims against live web data.</p>
                </div>
            """, unsafe_allow_html=True)

# 2. REPORT STATE: SPLIT SCREEN DASHBOARD
else:
    col_info, col_report = st.columns([1, 2.2], gap="large")
    
    with col_info:
        # Fixed Content on the left
        st.markdown(f"""
        <div class="card">
            <h3 style="margin-top:0; font-size: 1.2rem; color: #fff;">📄 Source Document</h3>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.5rem;"><strong>File:</strong> {st.session_state.file_info['name']}</p>
            <p style="font-size: 0.9rem; color: #94a3b8;"><strong>Size:</strong> {st.session_state.file_info['size']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'preview_img' in st.session_state and st.session_state.preview_img:
            st.markdown('<div class="card" style="padding: 0.5rem; overflow: hidden;">', unsafe_allow_html=True)
            st.image(f"data:image/png;base64,{st.session_state.preview_img}", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Actions
        if st.button("🔄 Analyze New File"):
            st.session_state.report = None
            st.session_state.file_info = None
            st.rerun()
            
        df = pd.DataFrame(st.session_state.report)
        st.download_button(
            label="📥 Download Audit Log",
            data=df.to_csv(index=False),
            file_name=f"audit_{st.session_state.file_info['name']}.csv",
            mime="text/csv"
        )

    with col_report:
        # Dashboard Summary
        total = len(st.session_state.report)
        verified = len([x for x in st.session_state.report if x['status'] == 'VERIFIED'])
        flagged = total - verified
        
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card">
                    <div class="metric-value">{total}</div>
                    <div class="metric-label">Total Claims</div>
                </div>
                <div class="metric-card" style="border-bottom: 3px solid #10b981;">
                    <div class="metric-value" style="color: #10b981;">{verified}</div>
                    <div class="metric-label">Verified</div>
                </div>
                <div class="metric-card" style="border-bottom: 3px solid #f43f5e;">
                    <div class="metric-value" style="color: #f43f5e;">{flagged}</div>
                    <div class="metric-label">Flagged</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### 🛡️ Verification Feed")
        
        for idx, item in enumerate(st.session_state.report):
            status_class = f"status-{item['status'].lower()}"
            
            with st.container():
                # Card Main Body
                st.markdown(f"""
                <div class="card" style="margin-bottom: 0;">
                    <span class="status-badge {status_class}">{item['status']}</span>
                    <div class="claim-text">"{item['claim']}"</div>
                    <div class="reality-box">
                        <div style="color: var(--primary); text-transform: uppercase; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                            Reality Check
                        </div>
                        <div style="line-height: 1.6; font-size: 1rem; color: #e2e8f0;">{item['reality']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable Deep-Dive Citations
                with st.expander("🔍 VIEW EVIDENCE SOURCES & REASONING"):
                    st.markdown(f"""
                        <div style="padding: 1rem; background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 1rem;">
                            <p style="color: #94a3b8; font-size: 0.9rem;"><strong>Reasoning:</strong> {item['reasoning']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<p style='font-weight: 700; font-size: 0.8rem; color: #fff; margin-bottom: 0.5rem;'>CITATIONS</p>", unsafe_allow_html=True)
                    for evidence in item['evidence']:
                        st.markdown(f"""
                        <div class="evidence-item">
                            <div class="evidence-title">{evidence['title']}</div>
                            <div class="evidence-content">{evidence['content'][:250]}...</div>
                            <div style="margin-top: 0.5rem;">
                                <a href="{evidence['url']}" style="color: var(--primary); font-size: 0.8rem; text-decoration: none; font-weight: 600;" target="_blank">
                                    🔗 Read Source
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
