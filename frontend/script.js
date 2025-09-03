// frontend/script.js

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileNameSpan = document.getElementById('fileName');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const analysisContentDiv = document.getElementById('analysis-content');
    const errorDiv = document.getElementById('error');

    // Trigger the hidden file input when the custom button is clicked
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Update the file name display and enable the analyze button
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileNameSpan.textContent = fileInput.files[0].name;
            analyzeBtn.disabled = false;
        } else {
            fileNameSpan.textContent = 'No file selected';
            analyzeBtn.disabled = true;
        }
    });

    // Handle the analysis process
    analyzeBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file first.');
            return;
        }

        // Reset UI
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        analyzeBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Call your FastAPI backend
            const response = await fetch('http://127.0.0.1:8000/analyze/', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                // Handle errors from the API (e.g., 400, 500)
                throw new Error(result.detail || 'An unknown error occurred.');
            }
            
            // The prompt asks Gemini for Markdown, so we use a library to render it.
            analysisContentDiv.innerHTML = marked.parse(result.analysis);
            resultsDiv.classList.remove('hidden');

        } catch (error) {
            errorDiv.textContent = `Error: ${error.message}`;
            errorDiv.classList.remove('hidden');
        } finally {
            // Clean up
            loadingDiv.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });
});
