# 🛡️ Truth Layer: AI-Powered Fact-Checking Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://truthlayer.streamlit.app)

Truth Layer is a state-of-the-art verification platform designed for the **Generative Engine Optimization (GEO)** era. It automates the audit of marketing collateral, research papers, and technical specifications, identifying hallucinations and outdated claims in real-time using high-speed AI and RAG-optimized web search.

---

## ✨ Features

### 📊 Modern Analysis Dashboard
- **Split-Screen Workspace**: Fixed document preview on the left with a dynamic analysis stream on the right.
- **Insight Metrics**: Instant summary cards showing Total Claims, Verified claims, and Flagged inaccuracies.
- **Dynamic Atmosphere**: A premium glassmorphism UI with "floating blobs" background animations and smooth micro-interactions.

### 🕵️ Deep-Dive Verification
- **Real-Time Fact-Checking**: Every claim is verified against live web data using the Tavily Search API.
- **Comprehensive Citations**: Each report item includes:
    - **Status Badges**: Visual cues for `VERIFIED`, `INACCURATE`, or `FALSE` claims.
    - **Reality Check**: Direct corrections for identified inaccuracies.
    - **AI Reasoning**: Transparent explanation of why a claim was flagged.
    - **Source Feed**: Direct links to evidence snippets used for verification.

### ⚡ Cutting-Edge Tech Stack
- **Inference**: **Groq (Llama 3.3 70B)** for ultra-low latency, high-accuracy reasoning.
- **Search Engine**: **Tavily API** for RAG-optimized, real-time web intelligence.
- **Processing**: **PyMuPDF (fitz)** for high-fidelity document parsing and visual previews.
- **Styling**: **Vanilla CSS & Glassmorphism** for a bespoke, premium aesthetic.

---

## 🛠️ How It Works

1.  **Ingestion**: The system parses the uploaded PDF, extracting core text and generating a visual preview.
2.  **Claim Extraction**: AI identifies specific, fact-checkable claims (statistics, dates, specs, etc.).
3.  **Autonomous Research**: For each claim, a targeted web search is performed to gather live evidence.
4.  **Verification Engine**: The LLM compares document claims against search results to determine accuracy.
5.  **Audit Generation**: A structured, interactive report is rendered with full citations and reasoning.

---

## 🚀 Setup & Execution

### 1. Local Installation
```bash
# Clone the repository
git clone https://github.com/iamit0258/truthlayer.git

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 3. Launch
```bash
streamlit run app.py
```

---

## 📈 Strategy Context (GEO)

This project was built as part of a **GEO Product Assessment**, demonstrating how companies can protect their brand "Truth" as generative engines (like Perplexity and ChatGPT) become the primary source of information.

The accompanying strategy document (`GEO_Product_Strategy.pptx`) covers:
- **Share of Voice (SOV) Benchmarking** across LLMs.
- **AI Citation Mapping** to ensure brand mentions are accurate and frequent.
- **Predictive Analytics** for future generative trends.

---

**Author**: Amit K.
**Date**: May 2026
