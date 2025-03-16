// RAG Writing Assistant - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const statusBar = document.getElementById('status-message');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const uploadForm = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    const reprocessButton = document.getElementById('reprocess-button');
    const reprocessStatus = document.getElementById('reprocess-status');
    const queryInput = document.getElementById('query-input');
    const styleDropdown = document.getElementById('style-dropdown');
    const generateButton = document.getElementById('generate-button');
    const outputContent = document.getElementById('output-content');
    const loadingIndicator = document.getElementById('loading-indicator');
    const copyButton = document.getElementById('copy-button');

    // Check initialization status
    function checkStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'complete') {
                    statusBar.innerHTML = `<span class="status-complete">✓</span> ${data.message}`;
                    enableInterface();
                } else if (data.status === 'error') {
                    statusBar.innerHTML = `<span class="status-error">✗</span> ${data.message}`;
                } else {
                    statusBar.innerHTML = `<span class="status-loading">⟳</span> ${data.message}`;
                    // Continue checking status
                    setTimeout(checkStatus, 2000);
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
                statusBar.innerHTML = `<span class="status-error">✗</span> Error checking status`;
            });
    }

    // Enable interface elements once system is initialized
    function enableInterface() {
        if (generateButton.disabled) {
            generateButton.disabled = false;
            reprocessButton.disabled = false;
            // Update corpus stats
            updateCorpusStats();
        }
    }

    // Update corpus statistics
    function updateCorpusStats() {
        fetch('/corpus')
            .then(response => response.json())
            .then(data => {
                if (data.stats) {
                    const statsElement = document.getElementById('corpus-stats');
                    let html = `<p><strong>Files:</strong> ${data.stats.corpus_files}</p>
                               <p><strong>Text Chunks:</strong> ${data.stats.vector_documents}</p>`;
                    
                    if (data.stats.content_types && Object.keys(data.stats.content_types).length > 0) {
                        html += `<div class="content-types">
                                    <p><strong>Content Types:</strong></p>
                                    <ul>`;
                        
                        for (const [type, count] of Object.entries(data.stats.content_types)) {
                            html += `<li>${type}: ${count}</li>`;
                        }
                        
                        html += `</ul></div>`;
                    }
                    
                    statsElement.innerHTML = html;
                }
            })
            .catch(error => {
                console.error('Error updating corpus stats:', error);
            });
    }

    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileName.textContent = this.files[0].name;
            } else {
                fileName.textContent = 'No file chosen';
            }
        });
    }

    // File upload handler
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!fileInput.files || fileInput.files.length === 0) {
                uploadStatus.textContent = 'Please select a file to upload';
                uploadStatus.style.color = 'var(--danger-color)';
                return;
            }
            
            const file = fileInput.files[0];
            if (!file.name.endsWith('.txt')) {
                uploadStatus.textContent = 'Only .txt files are allowed';
                uploadStatus.style.color = 'var(--danger-color)';
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            uploadStatus.textContent = 'Uploading...';
            uploadStatus.style.color = 'var(--gray-700)';
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    uploadStatus.textContent = data.message;
                    uploadStatus.style.color = 'var(--success-color)';
                    fileInput.value = '';
                    fileName.textContent = 'No file chosen';
                    
                    // Update corpus stats
                    updateCorpusStats();
                } else {
                    uploadStatus.textContent = data.error || 'Error uploading file';
                    uploadStatus.style.color = 'var(--danger-color)';
                }
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                uploadStatus.textContent = 'Error uploading file';
                uploadStatus.style.color = 'var(--danger-color)';
            });
        });
    }

    // Reprocess corpus handler
    if (reprocessButton) {
        reprocessButton.addEventListener('click', function() {
            reprocessStatus.textContent = 'Reprocessing corpus...';
            reprocessStatus.style.color = 'var(--gray-700)';
            
            fetch('/reprocess', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    reprocessStatus.textContent = data.message;
                    reprocessStatus.style.color = 'var(--success-color)';
                    
                    // Update corpus stats
                    updateCorpusStats();
                } else {
                    reprocessStatus.textContent = data.error || 'Error reprocessing corpus';
                    reprocessStatus.style.color = 'var(--danger-color)';
                }
            })
            .catch(error => {
                console.error('Error reprocessing corpus:', error);
                reprocessStatus.textContent = 'Error reprocessing corpus';
                reprocessStatus.style.color = 'var(--danger-color)';
            });
        });
    }

    // Style dropdown handler
    if (styleDropdown) {
        styleDropdown.addEventListener('change', function() {
            if (this.value) {
                const currentQuery = queryInput.value.trim();
                
                // Check if query already has style instructions
                const styleRegex = /\[(make this .*?)\]|\((make this .*?)\)|make this (more|less) (\w+)/i;
                if (styleRegex.test(currentQuery)) {
                    // Replace existing style instruction
                    queryInput.value = currentQuery.replace(styleRegex, `[${this.value}]`);
                } else {
                    // Add style instruction at the end
                    queryInput.value = currentQuery + ` [${this.value}]`;
                }
            }
        });
    }

    // Generate content handler
    if (generateButton) {
        generateButton.addEventListener('click', function() {
            const query = queryInput.value.trim();
            
            if (!query) {
                outputContent.innerHTML = '<p class="placeholder" style="color: var(--danger-color);">Please enter a query</p>';
                return;
            }
            
            // Extract style adjustments from query
            let styleAdjustments = '';
            const styleRegex = /\[(make this .*?)\]|\((make this .*?)\)|make this (more|less) (\w+)/i;
            const styleMatch = query.match(styleRegex);
            
            if (styleMatch) {
                styleAdjustments = styleMatch[1] || styleMatch[2] || `${styleMatch[3]} ${styleMatch[4]}`;
            }
            
            // Show loading indicator
            loadingIndicator.classList.remove('hidden');
            outputContent.classList.add('hidden');
            copyButton.disabled = true;
            
            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    style_adjustments: styleAdjustments
                })
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                loadingIndicator.classList.add('hidden');
                outputContent.classList.remove('hidden');
                
                if (data.content) {
                    outputContent.textContent = data.content;
                    copyButton.disabled = false;
                } else if (data.error) {
                    outputContent.innerHTML = `<p class="placeholder" style="color: var(--danger-color);">${data.error}</p>`;
                }
            })
            .catch(error => {
                console.error('Error generating content:', error);
                loadingIndicator.classList.add('hidden');
                outputContent.classList.remove('hidden');
                outputContent.innerHTML = '<p class="placeholder" style="color: var(--danger-color);">Error generating content</p>';
            });
        });
    }

    // Copy button handler
    if (copyButton) {
        copyButton.addEventListener('click', function() {
            const content = outputContent.textContent;
            
            navigator.clipboard.writeText(content)
                .then(() => {
                    const originalText = copyButton.textContent;
                    copyButton.textContent = 'Copied!';
                    
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                    }, 2000);
                })
                .catch(error => {
                    console.error('Error copying text:', error);
                });
        });
    }

    // Initialize
    if (statusBar) {
        // Check if system is already initialized
        const statusText = statusBar.textContent.trim();
        if (statusText.includes('System initialized') || statusText.includes('✓')) {
            enableInterface();
        } else {
            // Start checking status
            checkStatus();
            
            // Disable buttons initially
            if (generateButton) generateButton.disabled = true;
            if (reprocessButton) reprocessButton.disabled = true;
        }
    }
});
