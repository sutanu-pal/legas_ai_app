# File: main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.gcp import configure_api_key, analyze_document_from_bytes
import uvicorn

# Create the FastAPI application
app = FastAPI(
    title="Legal Document Analysis API",
    description="An API to analyze legal documents using Gemini AI.",
    version="1.0.0"
)

# --- Add CORS Middleware ---
# This allows our future frontend (on a different address) to talk to this backend
origins = ["*"]  # For development, allow all origins.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Gemini API key when the application starts
@app.on_event("startup")
def startup_event():
    configure_api_key()

@app.get("/")
def read_root():
    """A simple endpoint to check if the server is running."""
    return {"message": "Welcome to the Legal AI Analyzer API!"}

@app.post("/analyze/")
async def analyze_document_endpoint(file: UploadFile = File(...)):
    """
    This endpoint accepts a PDF file, analyzes it, and returns the result.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Read the file content as bytes
        file_bytes = await file.read()
        
        # Get the analysis from our core logic
        analysis_result = analyze_document_from_bytes(file_bytes)
        
        # Return the result
        return {"filename": file.filename, "analysis": analysis_result}
        
    except Exception as e:
        # Handle potential errors during processing
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# This part allows running the server directly for development
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)