import os
import fitz  # PyMuPDF
from groq import Groq
from tavily import TavilyClient
import json
import re

class FactChecker:
    def __init__(self, groq_api_key, tavily_api_key):
        self.tavily = TavilyClient(api_key=tavily_api_key)
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"

    def extract_text_from_pdf(self, pdf_path):
        """Extracts all text from a PDF file."""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def _get_completion(self, prompt, is_json=True):
        """Helper to get completion from Groq."""
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            response_format={"type": "json_object"} if is_json else None
        )
        return response.choices[0].message.content

    def extract_claims(self, text):
        """Identifies fact-checkable claims from the text."""
        prompt = f"""
        Extract a list of specific, fact-checkable claims from the following text. 
        Focus on statistics, dates, financial figures, technical specifications, and company milestones.
        
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
            print(f"Error parsing claims: {e}")
            return []

    def verify_claim(self, claim):
        """Verifies a single claim using Tavily search and Groq reasoning."""
        # 1. Search the web
        snippets = []
        try:
            search_result = self.tavily.search(query=claim, search_depth="advanced")
            snippets = [{"url": res['url'], "content": res['content'], "title": res.get('title', 'Source')} for res in search_result['results'][:3]]
            context = "\n".join([f"Source: {s['url']}\nContent: {s['content']}" for s in snippets])
        except Exception as e:
            context = "Search failed."

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
                "reasoning": "Internal error during verification.",
                "evidence": []
            }

    def process_document(self, pdf_path):
        """Main pipeline to process PDF and return a report."""
        text = self.extract_text_from_pdf(pdf_path)
        claims = self.extract_claims(text)
        
        report = []
        for claim in claims[:8]:  # Limit for quality
            verification = self.verify_claim(claim)
            report.append({
                "claim": claim,
                **verification
            })
        return report
