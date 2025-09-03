# File: main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.gcp import configure_api_key, analyze_document_from_bytes
import uvicorn

app = FastAPI(
    title="Legal Document Analysis API",
    description="An API to analyze legal documents using Gemini AI.",
    version="1.0.0"
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    configure_api_key()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Legal AI Analyzer API!"}

@app.post("/analyze/")
async def analyze_document_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        file_bytes = await file.read()
        
        # --- KEY CHANGE: Await the async function ---
        analysis_result = await analyze_document_from_bytes(file_bytes)
        
        return {"filename": file.filename, "analysis": analysis_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    # Ensure you have 'python-multipart' installed: pip install python-multipart
    uvicorn.run(app, host="127.0.0.1", port=8000)
