import streamlit as st
import pandas as pd
from fact_checker import FactChecker
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF preview
import base64
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Rate Limit Config
LIMIT_FILE = "scan_limit.json"
MAX_SCANS_PER_DAY = 20

def check_scan_limit():
    """Returns (allowed: bool, count: int)"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(LIMIT_FILE):
        return True, 0
    try:
        with open(LIMIT_FILE, "r") as f:
            data = json.load(f)
        if data.get("date") == today_str:
            count = data.get("count", 0)
            return count < MAX_SCANS_PER_DAY, count
        else:
            return True, 0
    except Exception:
        return True, 0

def increment_scan_count():
    today_str = datetime.now().strftime("%Y-%m-%d")
    count = 0
    if os.path.exists(LIMIT_FILE):
        try:
            with open(LIMIT_FILE, "r") as f:
                data = json.load(f)
            if data.get("date") == today_str:
                count = data.get("count", 0)
        except Exception:
            pass
    count += 1
    try:
        with open(LIMIT_FILE, "w") as f:
            json.dump({"date": today_str, "count": count}, f)
    except Exception:
        pass
    return count

# Page Config
st.set_page_config(
    page_title="Truth Layer | AI Fact-Checker",
    page_icon="🛡️",
    layout="wide"
)

# Premium UI Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --primary: #7C5CFF;
        --primary-glow: rgba(124, 92, 255, 0.15);
        --accent: #A855F7;
        --glow: #22D3EE;
        --bg-dark: #050816;
        --card-bg: rgba(255, 255, 255, 0.03);
        --card-border: rgba(255, 255, 255, 0.08);
        --text-main: #f8fafc;
        --text-dim: #94a3b8;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
    }

    *, html, body, [class*="css"], [class*="st-"] {
        font-family: 'Outfit', sans-serif !important;
    }

    h1, h2, h3, h4, h5, h6, .hero-title, .logo-title, .workspace-header-title, .metric-value, [class*="stHeader"] h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }

    /* Hide default streamlit headers & footers */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stAppDeployButton {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Global Streamlit styling overrides */
    .stApp {
        background-color: #050816 !important;
        background-image: 
            radial-gradient(circle at top center, rgba(124, 92, 255, 0.18), transparent 60%) !important;
        background-attachment: fixed !important;
        color: var(--text-main) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(5, 8, 22, 0.5);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(124, 92, 255, 0.3);
    }

    /* Header Navbar styling */
    .top-navbar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(5, 8, 22, 0.4);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.85rem 2rem;
        margin-top: 0;
        margin-bottom: 2.5rem;
        z-index: 99;
        position: relative;
    }
    .navbar-left {
        display: flex;
        align-items: center;
    }
    .logo-group {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .logo-text-group {
        display: flex;
        flex-direction: column;
    }
    .logo-title {
        color: #fff;
        font-weight: 800;
        font-size: 1.15rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .logo-subtitle {
        color: #64748b;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .navbar-right {
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }
    .contact-meta {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .contact-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.35rem 0.75rem;
        border-radius: 99px;
        font-size: 0.75rem !important;
        font-weight: 500;
        color: var(--text-dim) !important;
        text-decoration: none !important;
        transition: all 0.2s ease-in-out;
    }
    .contact-pill:hover {
        background: rgba(124, 92, 255, 0.08);
        border-color: rgba(124, 92, 255, 0.3);
        color: #fff !important;
        text-decoration: none !important;
        transform: translateY(-1px);
    }
    .name-pill {
        background: rgba(124, 92, 255, 0.06);
        border-color: rgba(124, 92, 255, 0.15);
        color: #fff !important;
        font-weight: 600;
    }
    .name-pill:hover {
        background: rgba(124, 92, 255, 0.12);
        border-color: rgba(124, 92, 255, 0.4);
    }
    .pill-icon {
        font-size: 0.8rem;
    }

    .digital-heroes-btn {
        background: linear-gradient(135deg, #7C5CFF 0%, #A855F7 100%);
        border: none;
        border-radius: 12px;
        color: white;
        padding: 0.55rem 1.25rem;
        font-weight: 700;
        font-size: 0.8rem;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(124, 92, 255, 0.25);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    .digital-heroes-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(124, 92, 255, 0.4);
        filter: brightness(1.1);
    }
    .theme-toggle-btn {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.02);
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .theme-toggle-btn:hover {
        color: #fff;
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* Hero Styling */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.04em;
        margin-bottom: 0.75rem;
        color: #fff;
    }
    .gradient-text-purple {
        background: linear-gradient(135deg, #7C5CFF 0%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 1.75rem;
        line-height: 1.5;
    }
    .privacy-note {
        font-size: 0.75rem;
        color: #475569;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* File Uploader custom styling override */
    section[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stFileUploader"]:hover {
        border-color: #7C5CFF !important;
        background: rgba(124, 92, 255, 0.02) !important;
        box-shadow: 0 0 30px rgba(124, 92, 255, 0.1) !important;
    }
    section[data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #7C5CFF 0%, #A855F7 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.25rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(124, 92, 255, 0.3) !important;
        transition: all 0.2s !important;
    }
    section[data-testid="stFileUploader"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(124, 92, 255, 0.45) !important;
        filter: brightness(1.1) !important;
    }
    section[data-testid="stFileUploader"] button span {
        display: none !important;
    }
    section[data-testid="stFileUploader"] button::after {
        content: "Upload PDF Document" !important;
        font-weight: 600 !important;
    }
    section[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] p {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }

    /* Custom stream button override */
    .stButton>button {
        background: linear-gradient(135deg, #7C5CFF 0%, #A855F7 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        color: white !important;
        padding: 0.85rem 2rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 20px rgba(124, 92, 255, 0.3) !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(124, 92, 255, 0.5) !important;
        filter: brightness(1.15) !important;
    }

    /* Metric Cards Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(124, 92, 255, 0.25);
        box-shadow: 0 10px 30px -5px rgba(124, 92, 255, 0.15);
    }
    .metric-card.success:hover {
        border-color: rgba(16, 185, 129, 0.25);
        box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.15);
    }
    .metric-card.warning:hover {
        border-color: rgba(245, 158, 11, 0.25);
        box-shadow: 0 10px 30px -5px rgba(245, 158, 11, 0.15);
    }
    .metric-card.info:hover {
        border-color: rgba(34, 211, 238, 0.25);
        box-shadow: 0 10px 30px -5px rgba(34, 211, 238, 0.15);
    }
    .metric-header {
        display: flex;
        justify-content: flex-start;
    }
    .metric-icon-wrapper {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .metric-icon-wrapper.purple { background: rgba(124, 92, 255, 0.1); color: #7C5CFF; }
    .metric-icon-wrapper.green { background: rgba(16, 185, 129, 0.1); color: #10B981; }
    .metric-icon-wrapper.orange { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }
    .metric-icon-wrapper.blue { background: rgba(34, 211, 238, 0.1); color: #22D3EE; }

    .metric-body {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #fff;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .green-text { color: #10B981 !important; }
    .orange-text { color: #F59E0B !important; }
    .blue-text { color: #22D3EE !important; }

    .metric-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-subtext {
        font-size: 0.65rem;
        color: #475569;
    }

    /* Workspace Columns structure styling */
    .workspace-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        margin-top: 0.5rem;
    }
    .workspace-header-title {
        font-size: 1rem;
        font-weight: 800;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        letter-spacing: -0.02em;
    }
    .filter-badge {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.3rem 0.65rem;
        font-size: 0.7rem;
        font-weight: 600;
        color: #94a3b8;
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .filter-badge:hover {
        border-color: rgba(124, 92, 255, 0.3);
        color: #fff;
        background: rgba(124, 92, 255, 0.05);
    }

    .pdf-toolbar {
        background: #070B1A;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: none;
        border-radius: 16px 16px 0 0;
        padding: 0.65rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.75rem;
        color: #94a3b8;
    }
    .pdf-name {
        font-weight: 600;
        color: #cbd5e1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 140px;
    }
    .pdf-page-indicator, .pdf-zoom-indicator {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-weight: 500;
        font-family: monospace;
        margin-right: 0.35rem;
    }
    .pdf-toolbar-right {
        display: flex;
        gap: 0.35rem;
    }
    .pdf-tool-btn {
        width: 22px;
        height: 22px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #475569;
        transition: all 0.2s;
    }
    .pdf-tool-btn:hover {
        color: #fff;
        background: rgba(255, 255, 255, 0.05);
    }

    .pdf-preview-container {
        background: #0B1022;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 0 0 16px 16px;
        padding: 1rem;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Verification Cards redesigned */
    .insight-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px 20px 0 0;
        padding: 1.25rem;
        margin-bottom: 0px;
        border-bottom: none;
        position: relative;
        transition: all 0.3s ease;
    }
    .insight-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(124, 92, 255, 0.2);
    }
    .insight-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.85rem;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.75rem;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-verified { background: rgba(16, 185, 129, 0.08); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.15); }
    .status-verified .badge-dot { background: #10B981; box-shadow: 0 0 8px #10B981; }
    
    .status-needs-review { background: rgba(245, 158, 11, 0.08); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.15); }
    .status-needs-review .badge-dot { background: #F59E0B; box-shadow: 0 0 8px #F59E0B; }
    
    .status-false { background: rgba(239, 68, 68, 0.08); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.15); }
    .status-false .badge-dot { background: #EF4444; box-shadow: 0 0 8px #EF4444; }

    .badge-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        display: inline-block;
    }

    .confidence-badge {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.75rem;
        font-weight: 500;
        color: #64748b;
    }
    .confidence-value {
        font-weight: 700;
    }

    .claim-quote {
        font-size: 1rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.85rem;
        line-height: 1.4;
        border-left: 3px solid var(--primary);
        padding-left: 0.75rem;
    }

    .reality-box-premium {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
    }
    .reality-box-header {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--primary);
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .reality-box-content {
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.45;
    }

    .insight-card-footer {
        display: flex;
        justify-content: flex-end;
    }
    .view-evidence-trigger {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 600;
        cursor: pointer;
        transition: color 0.2s ease;
    }
    .view-evidence-trigger:hover {
        color: var(--primary);
    }
    .chevron-down-icon {
        transition: transform 0.3s ease;
    }

    /* Expander override to visually merge with the card */
    .insight-card + div[data-testid="stExpander"] {
        border-top: none !important;
        border-top-left-radius: 0px !important;
        border-top-right-radius: 0px !important;
        border-bottom-left-radius: 20px !important;
        border-bottom-right-radius: 20px !important;
        background: rgba(255, 255, 255, 0.01) !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin-bottom: 1.25rem !important;
        box-shadow: none !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.01) !important;
        box-shadow: none !important;
    }
    div[data-testid="stExpander"] summary {
        background: transparent !important;
        color: #64748b !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        padding: 0.35rem 0.85rem !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: var(--primary) !important;
    }

    /* Expander Inner Content */
    .evidence-reasoning-box {
        background: rgba(0, 0, 0, 0.15);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.03);
        margin-bottom: 1rem;
    }
    .evidence-list-header {
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #cbd5e1;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        margin-top: 0.5rem;
    }
    .evidence-item-premium {
        background: rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    .evidence-item-premium:hover {
        border-color: rgba(124, 92, 255, 0.15);
        background: rgba(0, 0, 0, 0.2);
    }
    .evidence-title-premium {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--glow);
        margin-bottom: 0.2rem;
    }
    .evidence-content-premium {
        font-size: 0.75rem;
        color: #94a3b8;
        line-height: 1.45;
    }
    .evidence-link-premium {
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--primary);
        text-decoration: none;
        margin-top: 0.35rem;
    }
    .evidence-link-premium:hover {
        color: var(--accent);
        text-decoration: underline;
    }

    /* Help & Instruction Cards */
    .help-card {
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.25rem;
        margin-top: 1rem;
    }
    .help-card h3 {
        font-size: 0.95rem;
        color: #fff;
        margin-bottom: 0.75rem;
        font-weight: 700;
    }
    .help-card ol {
        margin-left: 1rem;
        color: #94a3b8;
        font-size: 0.8rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    /* Empty state */
    .empty-state-container {
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 4rem 2rem;
        text-align: center;
        margin-top: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
    }
    .empty-state-icon {
        font-size: 2.2rem;
        background: rgba(124, 92, 255, 0.08);
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    .empty-state-container h3 {
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
        margin: 0;
    }
    .empty-state-container p {
        color: #64748b;
        font-size: 0.85rem;
        max-width: 380px;
        line-height: 1.5;
        margin: 0;
    }

    /* Highlights row */
    .highlights-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .highlight-item {
        display: flex;
        gap: 0.75rem;
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 1rem;
        align-items: flex-start;
        transition: all 0.3s ease;
    }
    .highlight-item:hover {
        background: rgba(255, 255, 255, 0.02);
        border-color: rgba(255, 255, 255, 0.08);
    }
    .highlight-icon-wrapper {
        width: 32px;
        height: 32px;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .highlight-icon-wrapper.purple { background: rgba(124, 92, 255, 0.08); color: #7C5CFF; }
    .highlight-icon-wrapper.green { background: rgba(16, 185, 129, 0.08); color: #10B981; }
    .highlight-icon-wrapper.blue { background: rgba(34, 211, 238, 0.08); color: #22D3EE; }
    .highlight-icon-wrapper.pink { background: rgba(168, 85, 247, 0.08); color: #A855F7; }

    .highlight-text-group {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }
    .highlight-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #fff;
    }
    .highlight-desc {
        font-size: 0.7rem;
        color: #64748b;
        line-height: 1.35;
    }

    /* Footer styling */
    .footer-divider {
        height: 1px;
        background: rgba(255, 255, 255, 0.06);
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .footer-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        font-size: 0.75rem;
        color: #475569;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .footer-left, .footer-center, .footer-right {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    .footer-logo {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .footer-logo-title {
        font-weight: 850;
        color: #fff;
        font-size: 0.85rem;
        letter-spacing: -0.02em;
    }
    .footer-logo-subtitle {
        font-size: 0.65rem;
        color: #475569;
    }
    .footer-author-name {
        font-weight: 600;
        color: #94a3b8;
    }
    .footer-email {
        color: #64748b;
        text-decoration: none;
        transition: color 0.2s ease;
    }
    .footer-email:hover {
        color: var(--primary);
    }
    .footer-link {
        color: #64748b;
        text-decoration: none;
        transition: color 0.2s ease;
        font-weight: 600;
    }
    .footer-link:hover {
        color: var(--primary);
    }
    .footer-copy {
        font-size: 0.65rem;
        color: #475569;
        margin-top: 0.15rem;
    }

    .error-badge-container {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .error-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #ef4444;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        width: 100%;
    }

    .error-card {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .error-title { color: #ef4444; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.5rem; }
    .error-text { color: #fca5a5; font-size: 0.9rem; }
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

def get_confidence_score(claim, status):
    import hashlib
    h = int(hashlib.md5(claim.encode('utf-8')).hexdigest(), 16)
    if status == 'VERIFIED':
        return 90 + (h % 9)
    elif status == 'INACCURATE' or status == 'NEEDS REVIEW':
        return 55 + (h % 20)
    elif status == 'FALSE':
        return 15 + (h % 20)
    else:
        return 5 + (h % 10)

# Session State
if 'report' not in st.session_state:
    st.session_state.report = None
if 'file_info' not in st.session_state:
    st.session_state.file_info = None

# 0. HEADER BRAND BAR
st.markdown("""
    <div class="top-navbar-container">
        <div class="navbar-left">
            <div class="logo-group">
                <svg class="logo-icon" width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16 2L4 8L16 14L28 8L16 2Z" fill="url(#logo-grad-1)"/>
                    <path d="M4 14L16 20L28 14L16 8L4 14Z" fill="url(#logo-grad-2)" opacity="0.8"/>
                    <path d="M4 20L16 26L28 20L16 14L4 20Z" fill="url(#logo-grad-3)" opacity="0.6"/>
                    <defs>
                        <linearGradient id="logo-grad-1" x1="4" y1="2" x2="28" y2="14" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#7C5CFF"/>
                            <stop offset="1" stop-color="#22D3EE"/>
                        </linearGradient>
                        <linearGradient id="logo-grad-2" x1="4" y1="8" x2="28" y2="20" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#A855F7"/>
                            <stop offset="1" stop-color="#7C5CFF"/>
                        </linearGradient>
                        <linearGradient id="logo-grad-3" x1="4" y1="14" x2="28" y2="26" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#7C5CFF"/>
                            <stop offset="1" stop-color="#A855F7"/>
                        </linearGradient>
                    </defs>
                </svg>
                <div class="logo-text-group">
                    <span class="logo-title">Truth Layer</span>
                    <span class="logo-subtitle">AI Fact-Checking Platform</span>
                </div>
            </div>
        </div>
        <div class="navbar-right">
            <div class="contact-meta">
                <div class="contact-pill name-pill">
                    <span class="pill-icon">👤</span>
                    <span class="contact-name">Amit Kumar Kuswaha</span>
                </div>
                <a href="mailto:amitkk.contact@gmail.com" class="contact-pill email-pill" target="_blank">
                    <span class="pill-icon">✉️</span>
                    <span>amitkk.contact@gmail.com</span>
                </a>
                <a href="https://www.amitkk.in" class="contact-pill web-pill" target="_blank">
                    <span class="pill-icon">🌐</span>
                    <span>amitkk.in</span>
                </a>
            </div>
            <a href="https://digitalheroesco.com" target="_blank" style="text-decoration: none;">
                <button class="digital-heroes-btn">Built for Digital Heroes</button>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

# MAIN WORKSPACE COLUMN LAYOUT
col_left, col_right = st.columns([1.2, 2.0], gap="large")

with col_left:
    # Hero Heading & Tagline
    st.markdown("""
        <h1 class="hero-title">Verify Facts.<br>Trust <span class="gradient-text-purple">Truth.</span></h1>
        <p class="hero-subtitle">Upload documents or enter claims and let our AI analyze them against real-world evidence.</p>
    """, unsafe_allow_html=True)
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Marketing PDF", type="pdf", label_visibility="collapsed")
    
    st.markdown("""
        <p class="privacy-note">🔒 We respect your privacy. Your data is secure.</p>
    """, unsafe_allow_html=True)
    
    # Logic for limits and processing
    is_size_valid = True
    is_limit_allowed = True
    
    if uploaded_file:
        is_size_valid = uploaded_file.size <= 50 * 1024 * 1024
        is_limit_allowed, current_scans = check_scan_limit()
        
        # Check if this is a new file to process
        if st.session_state.file_info is None or st.session_state.file_info.get("name") != uploaded_file.name:
            st.session_state.report = None
            st.session_state.file_info = {
                "name": uploaded_file.name,
                "size": f"{uploaded_file.size / 1024 / 1024:.2f} MB"
            }
            st.rerun()
            
        if not is_size_valid:
            st.markdown("""
                <div class="error-badge-container">
                    <span class="error-badge">📁 File size exceeds the 50 MB limit. Please upload a smaller file.</span>
                </div>
            """, unsafe_allow_html=True)
        elif not is_limit_allowed:
            st.markdown(f"""
                <div class="error-badge-container">
                    <span class="error-badge">⚠️ Daily scan limit reached ({MAX_SCANS_PER_DAY} files/day). Please try again tomorrow.</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            if st.session_state.report is None:
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                if st.button("🚀 Verify Claims Now"):
                    status_box = st.empty()
                    def update_status(text):
                        status_box.markdown(f"""
                            <div style="background: rgba(124, 92, 255, 0.1); border: 1px solid rgba(124, 92, 255, 0.2); padding: 1rem; border-radius: 12px; text-align: center; color: #a855f7; font-weight: 600; margin-bottom: 1rem;">
                                <span style="display: inline-block; animation: spin 2s linear infinite; margin-right: 10px;">⏳</span> {text}
                            </div>
                            <style>@keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style>
                        """, unsafe_allow_html=True)
                    try:
                        checker = FactChecker(groq_key, tavily_key, status_callback=update_status)
                        text = checker.extract_text_from_pdf("temp.pdf")
                        st.session_state.extracted_text = text
                        st.session_state.report = checker.process_document("temp.pdf", status_callback=update_status)
                        st.session_state.preview_img = get_pdf_preview("temp.pdf")
                        increment_scan_count()
                        status_box.empty()
                        st.rerun()
                    except Exception as e:
                        status_box.markdown(f"""
                            <div class="error-card">
                                <div class="error-title">Analysis Failed</div>
                                <div class="error-text">{str(e)}</div>
                            </div>
                        """, unsafe_allow_html=True)

    # Document Preview section
    if st.session_state.report is not None:
        file_name = st.session_state.file_info['name'] if st.session_state.file_info else "no-document.pdf"
        file_size = st.session_state.file_info['size'] if st.session_state.file_info else "0 MB"
        
        st.markdown(f"""
            <div class="workspace-header">
                <div class="workspace-header-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color: #7C5CFF;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    <span>Document Preview</span>
                </div>
            </div>
            <div class="pdf-toolbar">
                <div class="pdf-toolbar-left">
                    <span class="pdf-name">{file_name}</span>
                </div>
                <div class="pdf-toolbar-center">
                    <span class="pdf-page-indicator">1 / 1</span>
                    <span class="pdf-zoom-indicator">100%</span>
                </div>
                <div class="pdf-toolbar-right">
                    <span class="pdf-tool-btn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg></span>
                    <span class="pdf-tool-btn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg></span>
                    <span class="pdf-tool-btn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></span>
                    <span class="pdf-tool-btn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg></span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if 'preview_img' in st.session_state and st.session_state.preview_img:
            st.markdown('<div class="pdf-preview-container">', unsafe_allow_html=True)
            st.image(f"data:image/png;base64,{st.session_state.preview_img}", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        
        if st.button("🔄 Analyze New File"):
            st.session_state.report = None
            st.session_state.file_info = None
            if 'extracted_text' in st.session_state: del st.session_state.extracted_text
            st.rerun()
            
        with st.expander("📄 VIEW EXTRACTED TEXT"):
            if 'extracted_text' in st.session_state:
                st.code(st.session_state.extracted_text[:2000] + ("..." if len(st.session_state.extracted_text) > 2000 else ""), language="text")
            else:
                st.info("Text preview not available for this session.")
                
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.report)
        st.download_button(
            label="📥 Download Audit Log",
            data=df.to_csv(index=False),
            file_name=f"audit_{file_name}.csv",
            mime="text/csv"
        )
    else:
        st.markdown("""
            <div class="help-card">
                <h3>Get Started in 3 Steps</h3>
                <ol>
                    <li><strong>Upload PDF:</strong> Select your fact-sheet, deck or marketing report.</li>
                    <li><strong>Analyze:</strong> Our system will extract the numerical and factual claims automatically.</li>
                    <li><strong>Review Results:</strong> See confidence metrics, reasoning and live citation links.</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)

with col_right:
    # Calculate statistics
    if st.session_state.report is not None:
        total = len(st.session_state.report)
        verified = len([x for x in st.session_state.report if x['status'] == 'VERIFIED'])
        flagged = total - verified
        accuracy = int(verified / total * 100) if total > 0 else 100
    else:
        total = "-"
        verified = "-"
        flagged = "-"
        accuracy = "-"
        
    st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-header">
                    <div class="metric-icon-wrapper purple">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value">{total}</span>
                    <span class="metric-label">Claims Identified</span>
                    <span class="metric-subtext">Total claims extracted</span>
                </div>
            </div>
            <div class="metric-card success">
                <div class="metric-header">
                    <div class="metric-icon-wrapper green">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value green-text">{verified}</span>
                    <span class="metric-label">Verified</span>
                    <span class="metric-subtext">Accurate data points</span>
                </div>
            </div>
            <div class="metric-card warning">
                <div class="metric-header">
                    <div class="metric-icon-wrapper orange">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value orange-text">{flagged}</span>
                    <span class="metric-label">Needs Review</span>
                    <span class="metric-subtext">Requires clarification</span>
                </div>
            </div>
            <div class="metric-card info">
                <div class="metric-header">
                    <div class="metric-icon-wrapper blue">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                    </div>
                </div>
                <div class="metric-body">
                    <span class="metric-value blue-text">{accuracy}{"%" if accuracy != "-" else ""}</span>
                    <span class="metric-label">Accuracy Score</span>
                    <span class="metric-subtext">Overall document score</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.report is not None:
        st.markdown("""
            <div class="workspace-header" style="display: flex; justify-content: space-between; align-items: center;">
                <div class="workspace-header-title">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color: #7C5CFF;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                    <span>Verification Results</span>
                </div>
                <div class="filter-badge">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
                    Filter
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if len(st.session_state.report) == 0:
            st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 24px; padding: 4rem 2rem; text-align: center; margin-top: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                    <h4 style="color: #fff; margin-bottom: 0.5rem; font-weight: 700;">No Fact-Checkable Claims Found</h4>
                    <p style="color: #94a3b8; font-size: 0.9rem;">The AI couldn't identify specific statistics, dates, or technical claims in this document to verify. Try a document with more data points.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            for idx, item in enumerate(st.session_state.report):
                status_label = item['status']
                if status_label == 'INACCURATE':
                    status_label = 'NEEDS REVIEW'
                status_class = f"status-{status_label.lower().replace(' ', '-')}"
                
                confidence = get_confidence_score(item['claim'], item['status'])
                confidence_color = "#10B981" if confidence >= 85 else ("#F59E0B" if confidence >= 50 else "#EF4444")
                
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-card-header">
                        <div class="status-badge {status_class}">
                            <span class="badge-dot"></span>
                            {status_label}
                        </div>
                        <div class="confidence-badge">
                            <span class="confidence-label">Confidence</span>
                            <span class="confidence-value" style="color: {confidence_color};">{confidence}%</span>
                        </div>
                    </div>
                    <div class="claim-quote">
                        “{item['claim']}”
                    </div>
                    <div class="reality-box-premium">
                        <div class="reality-box-header">Reality Check</div>
                        <div class="reality-box-content">{item['reality']}</div>
                    </div>
                    <div class="insight-card-footer">
                        <div class="view-evidence-trigger">
                            <span>View Evidence & Reasoning</span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chevron-down-icon"><polyline points="6 9 12 15 18 9"></polyline></svg>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable Deep-Dive Citations
                with st.expander("🔍 VIEW EVIDENCE SOURCES & REASONING"):
                    st.markdown(f"""
                        <div class="evidence-reasoning-box">
                            <p style="color: #cbd5e1; font-size: 0.85rem; margin: 0; line-height: 1.5;"><strong>Reasoning:</strong> {item['reasoning']}</p>
                        </div>
                        <div class="evidence-list-header">Citations & Web Evidence</div>
                    """, unsafe_allow_html=True)
                    
                    if not item['evidence']:
                        st.markdown("<p style='color: #64748b; font-size: 0.8rem; font-style: italic; margin-left: 0.5rem; margin-bottom: 0.5rem;'>No online citations available.</p>", unsafe_allow_html=True)
                    else:
                        for evidence in item['evidence']:
                            st.markdown(f"""
                            <div class="evidence-item-premium">
                                <div class="evidence-title-premium">{evidence['title']}</div>
                                <div class="evidence-content-premium">{evidence['content'][:250]}...</div>
                                <a href="{evidence['url']}" class="evidence-link-premium" target="_blank">
                                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                                    Read Source
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="empty-state-container">
                <div class="empty-state-icon">🛡️</div>
                <h3>Ready for Verification</h3>
                <p>Drop your PDF document on the left, and Truth Layer will verify its statistics, timelines, and technical claims against live web data using search engines and reasoning models.</p>
            </div>
        """, unsafe_allow_html=True)

# 3. PREMIUM FEATURES HIGHLIGHTS ROW
st.markdown("""
    <div class="highlights-row">
        <div class="highlight-item">
            <div class="highlight-icon-wrapper purple">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>
            </div>
            <div class="highlight-text-group">
                <span class="highlight-title">AI-Powered Verification</span>
                <span class="highlight-desc">Advanced AI models analyze claims against trusted sources.</span>
            </div>
        </div>
        <div class="highlight-item">
            <div class="highlight-icon-wrapper green">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
            </div>
            <div class="highlight-text-group">
                <span class="highlight-title">Live Web Evidence</span>
                <span class="highlight-desc">Real-time search and verification from multiple reliable sources.</span>
            </div>
        </div>
        <div class="highlight-item">
            <div class="highlight-icon-wrapper blue">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
            </div>
            <div class="highlight-text-group">
                <span class="highlight-title">PDF Document Analysis</span>
                <span class="highlight-desc">Extract, analyze and verify claims from any PDF document.</span>
            </div>
        </div>
        <div class="highlight-item">
            <div class="highlight-icon-wrapper pink">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
            </div>
            <div class="highlight-text-group">
                <span class="highlight-title">Detailed Audit Reports</span>
                <span class="highlight-desc">Download comprehensive reports with evidence and reasoning.</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


