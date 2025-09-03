document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const uploadArea = document.getElementById('upload-area');
    const browseBtn = document.getElementById('browseBtn');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileInfoDiv = document.getElementById('file-info');
    const fileNameSpan = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const loadingDiv = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const errorDiv = document.getElementById('error');

    let currentFile = null;

    // --- Event Listeners ---
    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => handleFileSelect(fileInput.files[0]));
    removeFileBtn.addEventListener('click', resetFileState);
    analyzeBtn.addEventListener('click', handleAnalysis);

    // --- Drag and Drop ---
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('drag-over'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            handleFileSelect(file);
        } else {
            showError('Please drop a PDF file.');
        }
    });

    function handleFileSelect(file) {
        if (!file) return;
        currentFile = file;
        
        uploadArea.classList.add('hidden');
        fileInfoDiv.classList.remove('hidden');
        fileNameSpan.textContent = currentFile.name;
        analyzeBtn.disabled = false;
        errorDiv.classList.add('hidden');
    }

    function resetFileState() {
        currentFile = null;
        fileInput.value = ''; // Reset file input
        uploadArea.classList.remove('hidden');
        fileInfoDiv.classList.add('hidden');
        analyzeBtn.disabled = true;
        resultsContainer.classList.add('hidden');
        errorDiv.classList.add('hidden');
    }

    async function handleAnalysis() {
        if (!currentFile) return;

        // Reset UI for new analysis
        loadingDiv.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        resultsContainer.innerHTML = ''; // Clear previous results
        errorDiv.classList.add('hidden');
        analyzeBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const response = await fetch('http://127.0.0.1:8000/analyze/', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'An unknown error occurred during analysis.');
            }
            
            displayResults(result.analysis);
            resultsContainer.classList.remove('hidden');

        } catch (error) {
            showError(error.message);
        } finally {
            loadingDiv.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    // --- Result Parsing and Display ---
    function displayResults(analysisText) {
        // These keys map to the titles in your Gemini prompt
        const sections = {
            'Document Summary': { icon: 'fas fa-file-alt', theme: 'summary' },
            'Key Parties Involved': { icon: 'fas fa-users', theme: 'parties' },
            'Potential Risks & Red Flags': { icon: 'fas fa-exclamation-triangle', theme: 'risks' },
            'Major Obligations & Responsibilities': { icon: 'fas fa-tasks', theme: 'obligations' },
            'Critical Dates & Deadlines': { icon: 'fas fa-calendar-alt', theme: 'dates' },
            'Glossary of Jargon': { icon: 'fas fa-book', theme: 'glossary' }
        };

        let remainingText = analysisText;

        for (const title in sections) {
            // Regex to find the section by title, e.g., "1. **Document Summary:**"
            const regex = new RegExp(`\\*\\*${title}:\\*\\*`, 'i');
            const match = remainingText.search(regex);
            
            if (match !== -1) {
                // Find the start of the next section to delimit the current one
                let nextMatch = -1;
                let nextTitleIndex = Object.keys(sections).indexOf(title) + 1;
                if(nextTitleIndex < Object.keys(sections).length) {
                    const nextTitle = Object.keys(sections)[nextTitleIndex];
                    const nextRegex = new RegExp(`\\*\\*${nextTitle}:\\*\\*`, 'i');
                    nextMatch = remainingText.substring(match + 1).search(nextRegex);
                }

                let content = (nextMatch !== -1)
                    ? remainingText.substring(match, match + 1 + nextMatch)
                    : remainingText.substring(match);
                
                // Remove the title from the content itself
                content = content.replace(regex, '').trim();

                const card = createAnalysisCard(title, content, sections[title]);
                resultsContainer.appendChild(card);
            }
        }
    }

    function createAnalysisCard(title, markdownContent, section) {
        const card = document.createElement('div');
        card.className = `analysis-card card-${section.theme}`;

        const renderedHtml = marked.parse(markdownContent);

        card.innerHTML = `
            <h3><i class="${section.icon}"></i> ${title}</h3>
            <div class="content">
                ${renderedHtml}
            </div>
        `;
        return card;
    }
});
