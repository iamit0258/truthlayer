import os
import fitz  # PyMuPDF
from groq import Groq
from tavily import TavilyClient
import json
import re

class FactChecker:
    def __init__(self, groq_api_key, tavily_api_key, status_callback=None):
        self.tavily = TavilyClient(api_key=tavily_api_key)
        self.client = Groq(api_key=groq_api_key)
        self.models = [
            "llama-3.3-70b-versatile", 
            "llama-3.1-8b-instant", 
            "mixtral-8x7b-32768", 
            "gemma2-9b-it"
        ]
        self.current_model_idx = 0
        self.status_callback = status_callback

    def extract_text_from_pdf(self, pdf_path):
        """Extracts all text from a PDF file using a more robust method."""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            # Using "text" with clean layout preservation
            text += page.get_text("text", sort=True) + "\n\n"
        return text.strip()

    def _get_completion(self, prompt, is_json=True):
        """Helper to get completion from Groq with automatic fallback for rate limits."""
        last_error = None
        
        # Try models in order if rate limited
        for i in range(self.current_model_idx, len(self.models)):
            model = self.models[i]
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model,
                    response_format={"type": "json_object"} if is_json else None
                )
                # Success! Stick with this model for now
                self.current_model_idx = i
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                err_msg = str(e).lower()
                # Fallback if rate limited OR if the model is decommissioned/invalid
                if any(x in err_msg for x in ["429", "rate_limit", "400", "decommissioned", "not found"]):
                    if self.status_callback:
                        self.status_callback(f"⚠️ Model {model} unavailable ({'rate limited' if '429' in err_msg else 'deprecated'}). Trying fallback...")
                    continue
                else:
                    # For other errors (like auth or network), raise immediately
                    raise e
                    
        raise Exception(f"All models rate limited or failed. Last error: {last_error}")

    def extract_claims(self, text):
        """Identifies fact-checkable claims from the text."""
        if not text.strip():
            return []
            
        prompt = f"""
        You are an expert fact-checker. I have extracted text from a PDF document (which may include slide content, technical reports, or marketing materials).
        
        TASK:
        Extract a list of specific, fact-checkable claims from the text below. 
        Focus on:
        - Statistics and numerical data
        - Dates and timelines
        - Technical specifications
        - Financial figures
        - Explicit company milestones or achievements
        
        NOTE: The text is extracted from a PDF, so ignore page numbers, headers, footers, or formatting artifacts.
        
        Return the result as a JSON object with a "claims" key containing an array of strings.
        Example: {{"claims": ["The iPhone was launched in 2007", "Company X revenue grew by 20% in 2023"]}}
        
        Text:
        {text[:8000]}
        """
        try:
            response_text = self._get_completion(prompt)
            data = json.loads(response_text)
            return data.get("claims", [])
        except Exception as e:
            raise Exception(f"Failed to extract claims: {str(e)}")

    def verify_claim(self, claim):
        """Verifies a single claim using Tavily search and Groq reasoning."""
        # 1. Search the web
        snippets = []
        try:
            search_result = self.tavily.search(query=claim, search_depth="advanced")
            snippets = [{"url": res['url'], "content": res['content'], "title": res.get('title', 'Source')} for res in search_result['results'][:3]]
            context = "\n".join([f"Source: {s['url']}\nContent: {s['content']}" for s in snippets])
        except Exception as e:
            context = f"Search failed: {e}"

        # 2. Verify with LLM
        prompt = f"""
        Claim: {claim}
        
        Web Evidence:
        {context}
        
        Based on the web evidence, determine if the claim is:
        - VERIFIED: The claim matches the latest data.
        - INACCURATE: The claim is partially correct but outdated or slightly off.
        - FALSE: The claim is fundamentally incorrect or no evidence supports it.
        
        Provide:
        1. status (VERIFIED, INACCURATE, or FALSE)
        2. reality (The actual facts if inaccurate or false)
        3. reasoning (Briefly explain why based on the evidence)
        
        Return as a JSON object with keys "status", "reality", and "reasoning".
        """
        try:
            response_text = self._get_completion(prompt)
            verification = json.loads(response_text)
            return {
                **verification,
                "evidence": snippets
            }
        except Exception as e:
            return {
                "status": "ERROR", 
                "reality": f"Could not verify: {e}", 
                "reasoning": f"Internal error during verification: {str(e)}",
                "evidence": []
            }

    def process_document(self, pdf_path, status_callback=None):
        """Main pipeline to process PDF and return a report."""
        if status_callback: status_callback("📄 Extracting text from PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if status_callback: status_callback("🧠 Identifying fact-checkable claims...")
        claims = self.extract_claims(text)
        
        if not claims:
            return []
            
        report = []
        for i, claim in enumerate(claims[:8]):  # Limit for quality
            if status_callback: status_callback(f"🔎 Verifying claim {i+1} of {len(claims[:8])}...")
            verification = self.verify_claim(claim)
            report.append({
                "claim": claim,
                **verification
            })
        return report
