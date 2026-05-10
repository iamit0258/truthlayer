import fitz
from fact_checker import FactChecker
import os
from dotenv import load_dotenv

load_dotenv()

def test_extraction():
    pdf_path = "temp.pdf"
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found.")
        return

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    print(f"Extracted {len(text)} characters.")
    print("First 500 characters:")
    print(text[:500])

    # Try extracting claims
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if groq_key and tavily_key:
        checker = FactChecker(groq_key, tavily_key)
        claims = checker.extract_claims(text)
        print(f"Extracted {len(claims)} claims:")
        for c in claims:
            print(f"- {c}")
    else:
        print("API keys missing.")

if __name__ == "__main__":
    test_extraction()
