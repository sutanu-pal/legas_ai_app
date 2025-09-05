
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocal
  ? 'http://127.0.0.1:8000' // URL for local testing
  : 'https://legas-ai-app.onrender.com'; 

// --- DOM Element References ---
const fileUploadInput = document.getElementById('file-upload');
const uploadButton = document.getElementById('upload-button');
const uploadStatus = document.getElementById('upload-status');
const uploadSection = document.getElementById('upload-section');
const chatContainer = document.getElementById('chat-container');
const chatHeader = document.getElementById('chat-header');
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

// --- Application State ---
let documentId = null;
let chatHistory = [];
let isWaitingForResponse = false;

// --- Event Listeners ---
uploadButton.addEventListener('click', () => fileUploadInput.click());
fileUploadInput.addEventListener('change', handleFileUpload);
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// --- Core Functions ---
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadButton.disabled = true;
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'File upload failed.');
        }

        const result = await response.json();
        documentId = result.document_id;

        uploadSection.style.display = 'none';
        chatContainer.style.display = 'flex';
        chatHeader.textContent = `Chatting about ${result.filename}`;
        
        addMessage('model', `Hello! I've finished reading the document. How can I help you?`);

    } catch (error) {
        uploadStatus.textContent = `Error: ${error.message}`;
        uploadButton.disabled = false;
        console.error("Upload Error:", error);
    }
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !documentId || isWaitingForResponse) return;

    addMessage('user', message);
    chatInput.value = '';
    setLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_id: documentId,
                message: message,
                history: chatHistory
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get a response.');
        }
        
        const result = await response.json();
        addMessage('model', result.reply);

    } catch (error) {
        addMessage('model', `Sorry, an error occurred: ${error.message}`);
        console.error("Chat Error:", error);
    } finally {
        setLoading(false);
    }
}

// --- UI Helper Functions ---
function addMessage(role, content) {
    // We only add real messages to the chat history, not the loading indicator
    if (role !== 'loading') {
        chatHistory.push({ role: role, content: content });
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${role}-message`);
    
    // Enhanced Markdown-to-HTML formatting
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>');       // Italics

    // Handle bullet points that start with * or -
    if (formattedContent.includes('\n* ') || formattedContent.includes('\n- ')) {
        formattedContent = formattedContent.replace(/^\* (.*$)/gm, '<ul><li>$1</li></ul>')
            .replace(/^- (.*$)/gm, '<ul><li>$1</li></ul>')
            .replace(/<\/ul>\s?<ul>/g, ''); // Join adjacent lists
    }
    
    formattedContent = formattedContent.replace(/\n/g, '<br>'); // Line breaks
    messageElement.innerHTML = formattedContent;
    
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function setLoading(isLoading) {
    const loadingElement = document.getElementById('loading-indicator');
    if (isLoading) {
        isWaitingForResponse = true;
        sendBtn.disabled = true;
        chatInput.disabled = true;
        if (!loadingElement) {
            const el = document.createElement('div');
            el.classList.add('message', 'model-message');
            el.id = 'loading-indicator';
            el.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
            chatBox.appendChild(el);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    } else {
        isWaitingForResponse = false;
        sendBtn.disabled = false;
        chatInput.disabled = false;
        chatInput.focus();
        if (loadingElement) {
            loadingElement.remove();
        }
    }
}

