# File: core/gcp.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import io

# Load the environment variables from the .env file
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

def analyze_document_from_bytes(file_bytes: bytes):
    """
    Takes the raw bytes of a PDF file, extracts text, and gets an analysis from Gemini.
    """
    print("📄 Reading content from PDF bytes...")
    pdf_text = ""
    try:
        # Create a file-like object from the bytes
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            # Add a check for None in case a page has no text
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text
        print("✅ PDF read successfully.")
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return f"Error: Could not read the PDF file. It might be corrupted or in an unsupported format. Details: {e}"

    print("🧠 Loading AI model...")
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    prompt = """
    You are a highly skilled legal analyst. Carefully review the attached document text and provide the following information in a clear, structured format:

    1.  **Document Summary:** What is the main purpose of this document?
    2.  **Key Parties:** List all individuals or companies involved and their roles.
    3.  **Critical Dates:** List any important dates, deadlines, or effective dates.
    4.  **Major Obligations:** Briefly describe the main responsibilities for each party.
    """
    
    contents = [prompt, pdf_text]

    print("🚀 Sending request to Gemini AI... This may take a moment.")
    try:
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        print(f"❌ An error occurred during Gemini API call: {e}")
        return f"Error: Failed to get analysis from AI. Details: {e}"