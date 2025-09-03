// Get references to the HTML elements
const fileInput = document.getElementById('fileInput');
const analyzeButton = document.getElementById('analyzeButton');
const statusDiv = document.getElementById('status');
const resultPre = document.getElementById('analysisResult');

// Add an event listener to the button
analyzeButton.addEventListener('click', async () => {
    const file = fileInput.files[0];

    // Check if a file is selected
    if (!file) {
        statusDiv.textContent = 'Please select a PDF file first.';
        return;
    }

    // Prepare the file for sending to the backend
    const formData = new FormData();
    formData.append('file', file);

    // Update status and disable the button
    statusDiv.textContent = 'Uploading and analyzing... Please wait.';
    resultPre.textContent = '';
    analyzeButton.disabled = true;

    try {
        // Send the request to our FastAPI backend
        const response = await fetch('http://127.0.0.1:8000/analyze/', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }

        const data = await response.json();
        
        // Display the result
        statusDiv.textContent = 'Analysis complete!';
        resultPre.textContent = data.analysis;

    } catch (error) {
        console.error('Error:', error);
        statusDiv.textContent = 'An error occurred. Please check the console and make sure the backend server is running.';
        resultPre.textContent = `Error details: ${error.message}`;
    } finally {
        // Re-enable the button
        analyzeButton.disabled = false;
    }
});