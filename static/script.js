// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const chartInput = document.getElementById('chartInput');
const previewImage = document.getElementById('previewImage');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');

let selectedFile = null;

// Upload box click handler
uploadBox.addEventListener('click', () => {
    chartInput.click();
});

// File input change handler
chartInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

// Drag and drop handlers
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
});

// Handle file selection
function handleFileSelect(file) {
    if (!file) return;
    
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload an image file (PNG, JPG, GIF, or WEBP).');
        return;
    }
    
    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size exceeds 10MB. Please upload a smaller image.');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        document.querySelector('.upload-content').style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    // Enable analyze button
    analyzeBtn.disabled = false;
    
    // Hide any previous errors
    hideError();
}

// Analyze button click handler
analyzeBtn.addEventListener('click', analyzeChart);

// Analyze another button click handler
analyzeAnotherBtn.addEventListener('click', resetForm);

// Analyze chart function
async function analyzeChart() {
    if (!selectedFile) return;
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    hideError();
    
    // Show loading indicator
    loadingIndicator.style.display = 'block';
    analyzeBtn.disabled = true;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('chart', selectedFile);
    
    try {
        // Send request to backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Hide loading indicator
        loadingIndicator.style.display = 'none';
        
        if (data.success) {
            displayResults(data.analysis);
        } else {
            showError(data.error || 'An error occurred during analysis. Please try again.');
            analyzeBtn.disabled = false;
        }
        
    } catch (error) {
        loadingIndicator.style.display = 'none';
        showError('Failed to connect to the server. Please check your connection and try again.');
        analyzeBtn.disabled = false;
        console.error('Error:', error);
    }
}

// Display results function
function displayResults(analysis) {
    // Market type and confidence
    document.getElementById('marketType').textContent = analysis.market_type || 'Unknown';
    
    const confidenceScore = analysis.confidence_score || 0;
    const confidenceBadge = document.getElementById('confidenceScore');
    confidenceBadge.textContent = `${confidenceScore}%`;
    
    // Color code confidence
    if (confidenceScore >= 70) {
        confidenceBadge.style.backgroundColor = 'var(--success-color)';
    } else if (confidenceScore >= 50) {
        confidenceBadge.style.backgroundColor = 'var(--warning-color)';
    } else {
        confidenceBadge.style.backgroundColor = 'var(--danger-color)';
    }
    
    // Patterns
    const patternsList = document.getElementById('patternsList');
    patternsList.innerHTML = '';
    if (analysis.patterns && analysis.patterns.length > 0) {
        analysis.patterns.forEach(pattern => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = pattern;
            patternsList.appendChild(tag);
        });
    } else {
        patternsList.innerHTML = '<p>No specific patterns identified</p>';
    }
    
    // Indicators
    const indicatorsList = document.getElementById('indicatorsList');
    indicatorsList.innerHTML = '';
    if (analysis.indicators && analysis.indicators.length > 0) {
        analysis.indicators.forEach(indicator => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = indicator;
            indicatorsList.appendChild(tag);
        });
    } else {
        indicatorsList.innerHTML = '<p>No specific indicators identified</p>';
    }
    
    // Trade setup
    if (analysis.trade_setup) {
        const direction = analysis.trade_setup.direction || 'Unknown';
        const tradeDirection = document.getElementById('tradeDirection');
        tradeDirection.textContent = `${direction.toUpperCase()} Position`;
        tradeDirection.className = `trade-direction ${direction.toLowerCase()}`;
        
        document.getElementById('entryLevel').textContent = analysis.trade_setup.entry || 'N/A';
        document.getElementById('stopLoss').textContent = analysis.trade_setup.stop_loss || 'N/A';
        
        const takeProfitLevels = document.getElementById('takeProfitLevels');
        takeProfitLevels.innerHTML = '';
        if (analysis.trade_setup.take_profit) {
            if (Array.isArray(analysis.trade_setup.take_profit)) {
                analysis.trade_setup.take_profit.forEach((tp, index) => {
                    const tpDiv = document.createElement('div');
                    tpDiv.textContent = `TP${index + 1}: ${tp}`;
                    takeProfitLevels.appendChild(tpDiv);
                });
            } else {
                takeProfitLevels.textContent = analysis.trade_setup.take_profit;
            }
        } else {
            takeProfitLevels.textContent = 'N/A';
        }
    }
    
    // Pattern explanation
    document.getElementById('patternExplanation').textContent = 
        analysis.pattern_explanation || 'No explanation available.';
    
    // Reasoning
    document.getElementById('reasoning').textContent = 
        analysis.reasoning || 'No reasoning provided.';
    
    // Risk factors
    const riskFactorsList = document.getElementById('riskFactorsList');
    riskFactorsList.innerHTML = '';
    if (analysis.risk_factors && analysis.risk_factors.length > 0) {
        analysis.risk_factors.forEach(risk => {
            const li = document.createElement('li');
            li.textContent = risk;
            riskFactorsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'General market risk applies to all trading activities.';
        riskFactorsList.appendChild(li);
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Reset form function
function resetForm() {
    selectedFile = null;
    chartInput.value = '';
    previewImage.src = '';
    previewImage.style.display = 'none';
    document.querySelector('.upload-content').style.display = 'block';
    analyzeBtn.disabled = true;
    resultsSection.style.display = 'none';
    hideError();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Show error function
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto-hide after 10 seconds
    setTimeout(hideError, 10000);
}

// Hide error function
function hideError() {
    errorMessage.style.display = 'none';
}
