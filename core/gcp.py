import os
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from typing import List, Dict

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

async def get_copilot_response_async(doc_bytes: bytes, doc_mime_type: str, user_message: str, chat_history: List[Dict]) -> str:
    """
    Asynchronously generates a response from Gemini's chat model.
    This version passes the document bytes directly with the prompt, which is the correct method.
    """
    print("🧠 Initializing AI chat model...")
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # --- THE FIX ---
    # Instead of trying to upload the file separately, we create a 'Part'
    # that contains the document data. This is the modern and correct way.
    document_part = {
        "mime_type": doc_mime_type,
        "data": doc_bytes
    }

    system_instruction = """
    You are an expert AI legal assistant acting as a copilot. The user has provided a legal document.
    Your task is to answer the user's questions based *exclusively* on the content of the provided document.
    Do not use any external knowledge or make assumptions. If the answer is not in the document, state that clearly.
    """

    # --- CHAT HISTORY INTEGRATION ---
    history_for_model = []
    for message in chat_history:
        # The role for the model's messages is 'model'
        role = 'user' if message['role'] == 'user' else 'model'
        history_for_model.append({'role': role, 'parts': [{'text': message['content']}]})

    chat_session = model.start_chat(history=history_for_model)

    # The full prompt now includes the system instruction, the document part, and the user's message
    full_prompt = [system_instruction, document_part, user_message]

    print("🚀 Sending chat message and document to Gemini AI...")

    try:
        response = await chat_session.send_message_async(full_prompt)
        print("✅ Chat response received successfully.")
        return response.text
    except Exception as e:
        print(f"❌ An unexpected error occurred during Gemini API call: {e}")
        return f"Error: Failed to get analysis from AI. Details: {e}"

