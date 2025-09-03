# File: core/gcp.py

import os
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import io
import asyncio  

# Load environment variables from the .env file
load_dotenv()

def configure_api_key():
    """Configures the Gemini API key from environment variables."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=api_key)
        print("✅ Gemini API Key configured successfully!")
    except Exception as e:
        print(f"❌ Error configuring API Key: {e}")
        raise

async def analyze_document_from_bytes(file_bytes: bytes) -> str:
    """
    Asynchronously takes PDF bytes, extracts text, and gets an analysis from Gemini
    with robust retry logic for rate limiting.
    """
    print("📄 Reading content from PDF bytes...")
    pdf_text = ""
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text + "\n"
        
        if not pdf_text.strip():
            return "Error: Could not extract any text from the PDF. The file may be empty or contain only images."
            
        print("✅ PDF read successfully.")
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return f"Error: Could not read the PDF file. It might be corrupted or in an unsupported format. Details: {e}"

    print("🧠 Initializing AI model...")
    # --- IMPROVEMENT 1: Use the 'flash' model for more generous free-tier limits ---
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    You are an expert AI legal assistant. Your task is to analyze the following legal document and provide a clear, easy-to-understand summary for a non-lawyer.

    **Document Text:**
    ---
    {pdf_text}
    ---

    **Analysis Required:**
    Please structure your response using Markdown with the following format. If a section is not applicable, state "Not found in document."

    1.  **Document Summary:** In 2-3 sentences, what is the main purpose of this document?
    
    2.  **Key Parties Involved:**
        *   List all individuals or entities and their roles (e.g., Landlord, Tenant, Lender, Borrower).

    3.  **Potential Risks & Red Flags:**
        *   Highlight any clauses that are one-sided, unusual, or could pose a financial or legal risk to a layperson. Explain *why* it's a risk in simple terms.

    4.  **Major Obligations & Responsibilities:**
        *   **For Party A (e.g., Tenant):** What are their main duties?
        *   **For Party B (e.g., Landlord):** What are their main duties?
        *   (Continue for all parties)

    5.  **Critical Dates & Deadlines:**
        *   List any important dates (e.g., Effective Date, Termination Date, Notice Periods, Payment Due Dates).

    6.  **Glossary of Jargon:**
        *   Define 3-5 of the most confusing legal terms found in the document in plain English.
        
    **Disclaimer:** Always conclude your response with: "This is an AI-generated analysis and not a substitute for professional legal advice. Consult with a qualified attorney for any legal concerns."
    """

    print("🚀 Sending request to Gemini AI...")
    
    # --- IMPROVEMENT 2: Implement retry logic with exponential backoff ---
    retries = 3
    delay = 5  # Initial delay in seconds
    for i in range(retries):
        try:
            # Use the asynchronous method to generate content
            response = await model.generate_content_async(prompt)
            print("✅ Analysis received successfully.")
            return response.text
        except Exception as e:
            # Specifically check for the 429 rate limit error
            if "429" in str(e):
                print(f"⏳ Rate limit hit. Retrying in {delay} seconds... (Attempt {i + 1}/{retries})")
                await asyncio.sleep(delay)  # Use asyncio.sleep for non-blocking delay
                delay *= 2  # Double the delay for the next attempt
            else:
                # For any other error, fail immediately
                print(f"❌ An unexpected error occurred during Gemini API call: {e}")
                return f"Error: Failed to get analysis from AI. Details: {e}"
    
    # This message is returned if all retries fail
    return "Error: The AI service is currently overloaded or unavailable after multiple retries. Please try again later."

