# Truth Layer | AI-Powered Fact-Checking Dashboard

This repository contains the submission for the **GEO (Generative Engine Optimization)** Product Assessment. It features a sophisticated "Truth Layer" application designed to automate the verification of marketing content, catching hallucinations and outdated statistics in real-time.

---

## 🛡️ Part 2: The "Truth Layer" Web App

### Key Features
- **Split-Screen Dashboard**: A professional UI with a fixed document preview on the left and a scrollable analysis report on the right.
- **Deep-Dive Citations**: Not just a status, but a full breakdown including:
    - **AI Reasoning**: Explanation of why a claim was flagged.
    - **Multi-Source Evidence**: Up to 3 live web snippets per claim (Title, Content, URL).
- **Advanced Tech Stack**:
    - **Brain**: Llama 3.3 (70B) via **Groq** for high-speed, high-accuracy reasoning.
    - **Search**: **Tavily API** for real-time, RAG-optimized web searching.
    - **Processing**: **PyMuPDF** for document parsing and visual previews.
- **Premium UX**: Glassmorphism design, Outfit typography, and a dark-mode palette.

### Setup & Local Execution
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/iamit0258/truthlayer.git
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

### Configuration
The app reads credentials from a `.env` file in the root directory:
- `GROQ_API_KEY`: Your Groq API Key.
- `TAVILY_API_KEY`: Your Tavily Search API Key.

---

## 📈 Part 1: GEO Product Strategy

The included strategy document (`GEO_Product_Strategy.pptx`) outlines a comprehensive vision for a GEO analytics platform:
- **Core Feature**: "Share of Voice (SOV) Benchmarking" across top LLMs (ChatGPT, Perplexity, etc.).
- **Competitive Edge**: Deep Citation Mapping vs. traditional competitors like Profound.
- **Roadmap**: 
    - **3 Months**: Launching AI Citation Tracking for Google AI Overviews.
    - **1 Year**: Multi-Agent Persona Simulations & Predictive GEO Analytics.
- **Monetization**: Usage-based tiered SaaS model.

---

## 🛠️ Tech Stack Summary
- **Frontend**: Streamlit (Python)
- **LLM Engine**: Groq (Llama 3.3 70B)
- **Web Search**: Tavily API
- **Document Logic**: PyMuPDF
- **Styling**: Vanilla CSS / Glassmorphism

---
**Author**: Amit K.
**Date**: May 2026
