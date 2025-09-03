

***LexiGuard AI: Legal Document Analyzer***



**LexiGuard is an intelligent tool designed to demystify complex legal documents. By leveraging Google's Gemini generative AI, it transforms dense legal jargon into clear, actionable insights, empowering users to understand contracts, agreements, and terms of service with confidence.**

This project provides a secure, private, and user-friendly platform to analyze legal texts, highlight potential risks, and explain critical clauses in plain English.

 <img width="1804" height="844" alt="image" src="https://github.com/user-attachments/assets/743b43da-2450-4588-9952-5c62cef2d069" />
 <img width="1894" height="858" alt="image" src="https://github.com/user-attachments/assets/8bc29cc0-b473-4c2b-b061-b8e0b789eefc" />



***

## 🚀 Key Features

*   **AI-Powered Analysis**: Utilizes the Google Gemini 1.5 Flash model for fast and accurate document interpretation.
*   **Simple Summaries**: Generates concise summaries of a document's purpose.
*   **Risk & Obligation Highlighting**: Automatically identifies potential risks, one-sided clauses, and key responsibilities for all parties.
*   **Jargon Buster**: Defines confusing legal terms in simple, everyday language.
*   **Secure & Private**: Analyzes documents on the fly without storing them, ensuring user privacy.
*   **Modern Interface**: Features a clean, intuitive drag-and-drop interface for uploading PDF documents.
*   **Asynchronous Backend**: Built with FastAPI for high-performance, non-blocking request handling.
*   **Robust Error Handling**: Includes automatic retries with exponential backoff to manage API rate limits gracefully.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI, Uvicorn
*   **AI**: Google Generative AI (Gemini 1.5 Flash)
*   **PDF Processing**: PyPDF2
*   **Frontend**: HTML5, CSS3, JavaScript
*   **Dependencies**: python-dotenv, python-multipart, google-generativeai

## 📂 Project Structure

```
legal-ai-app/
│
├── core/
│   └── gcp.py              # Core logic for PDF extraction and Gemini API interaction
│
├── frontend/
│   ├── index.html          # Main HTML file for the user interface
│   ├── style.css           # Styling for the frontend
│   └── script.js           # Client-side logic, API calls, and DOM manipulation
│
├── .env                    # Environment variables (contains API key)
├── .gitignore              # Files and directories to be ignored by Git
├── main.py                 # FastAPI application server
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

***




