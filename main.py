import uvicorn
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from contextlib import asynccontextmanager

# Import your functions from gcp.py
from core.gcp import configure_api_key, get_copilot_response_async

# --- Pydantic Models for API validation ---
class ChatRequest(BaseModel):
    document_id: str
    message: str
    history: List[Dict]

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Legal Document Copilot API",
    description="An API to interact with a legal document using Gemini AI.",
    version="3.0.0" # Final Version
)

# --- CRUCIAL CORS CONFIGURATION ---
# This is the most permissive setting. It tells the browser to allow
# requests from ANY origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lifespan event to configure API key on startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application starting up...")
    configure_api_key()
    print("✅ Application startup complete.")
    yield

app.router.lifespan_context = lifespan

# --- In-memory storage for the MVP ---
document_storage = {}

# --- API Endpoints ---
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Only PDF or TXT files are supported.")
    
    document_id = str(uuid.uuid4())
    content = await file.read()
    
    document_storage[document_id] = {
        "content": content,
        "mime_type": file.content_type
    }
    
    print(f"📄 Document uploaded with ID: {document_id}")
    return {"document_id": document_id, "filename": file.filename}

@app.post("/chat")
async def chat_with_document(request: ChatRequest):
    if request.document_id not in document_storage:
        raise HTTPException(status_code=404, detail="Document not found. Please upload again.")
    
    document_data = document_storage[request.document_id]
    
    response_text = await get_copilot_response_async(
        doc_bytes=document_data["content"],
        doc_mime_type=document_data["mime_type"],
        user_message=request.message,
        chat_history=request.history
    )
    
    return {"reply": response_text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

