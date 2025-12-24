// Dashboard functionality
let currentFilter = 'all';
let allAnalyses = [];

// Load user data on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserData();
    await loadStats();
    await loadHistory();
    
    // Set up event listeners
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            filterHistory();
        });
    });
});

async function loadUserData() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('userFullName').textContent = data.user.full_name;
        } else {
            // Redirect to login if not authenticated
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        window.location.href = '/login';
    }
}

async function loadStats() {
    try {
        const [statsResponse, userResponse] = await Promise.all([
            fetch('/api/stats'),
            fetch('/api/user')
        ]);
        
        const statsData = await statsResponse.json();
        const userData = await userResponse.json();
        
        if (statsData.success && userData.success) {
            const stats = statsData.stats;
            const user = userData.user;
            
            document.getElementById('totalAnalyses').textContent = stats.total_analyses;
            document.getElementById('winRate').textContent = `${stats.win_rate}%`;
            document.getElementById('avgConfidence').textContent = `${stats.avg_confidence}%`;
            
            // Display analyses left today
            if (user.is_premium) {
                document.getElementById('analysesLeft').textContent = '∞';
                document.querySelector('#analysesLeft').parentElement.querySelector('.stat-label').textContent = 'Premium User';
            } else {
                const remaining = user.daily_limit - user.analyses_today;
                document.getElementById('analysesLeft').textContent = remaining;
                document.querySelector('#analysesLeft').parentElement.querySelector('.stat-label').textContent = 'Analyses Left Today';
            }
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadHistory() {
    const loadingIndicator = document.getElementById('loadingHistory');
    const noHistory = document.getElementById('noHistory');
    const historyContainer = document.getElementById('historyContainer');
    
    loadingIndicator.style.display = 'block';
    noHistory.style.display = 'none';
    historyContainer.innerHTML = '';
    
    try {
        const response = await fetch('/api/history?per_page=20');
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';
        
        if (data.success && data.analyses.length > 0) {
            allAnalyses = data.analyses;
            filterHistory();
        } else {
            noHistory.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        loadingIndicator.style.display = 'none';
        noHistory.style.display = 'block';
    }
}

function filterHistory() {
    const historyContainer = document.getElementById('historyContainer');
    const noHistory = document.getElementById('noHistory');
    
    let filtered = allAnalyses;
    if (currentFilter !== 'all') {
        filtered = allAnalyses.filter(a => a.outcome === currentFilter);
    }
    
    historyContainer.innerHTML = '';
    
    if (filtered.length === 0) {
        noHistory.style.display = 'block';
        document.querySelector('#noHistory h3').textContent = `No ${currentFilter === 'all' ? '' : currentFilter} analyses`;
        return;
    }
    
    noHistory.style.display = 'none';
    
    filtered.forEach(analysis => {
        const card = createHistoryCard(analysis);
        historyContainer.appendChild(card);
    });
}

function createHistoryCard(analysis) {
    const card = document.createElement('div');
    card.className = 'history-card';
    card.onclick = () => viewAnalysisDetail(analysis.id);
    
    const direction = analysis.trade_direction || 'N/A';
    const outcome = analysis.outcome || 'pending';
    const confidence = analysis.confidence_score || 0;
    
    // Determine confidence level
    let confidenceClass = 'high';
    if (confidence < 50) confidenceClass = 'low';
    else if (confidence < 70) confidenceClass = 'medium';
    
    // Format date
    const date = new Date(analysis.created_at);
    const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    // Parse take profit if it's a JSON string
    let takeProfitDisplay = 'N/A';
    if (analysis.take_profit && analysis.take_profit.length > 0) {
        takeProfitDisplay = Array.isArray(analysis.take_profit) 
            ? analysis.take_profit[0] 
            : analysis.take_profit;
    }
    
    card.innerHTML = `
        <div class="history-header">
            <span class="trade-direction-badge ${direction.toLowerCase()}">${direction}</span>
            <span class="outcome-badge ${outcome}">${outcome}</span>
        </div>
        <div class="history-details">
            <div class="detail-row">
                <span class="detail-label">Market</span>
                <span class="detail-value">${analysis.market_type || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Style</span>
                <span class="detail-value">${analysis.trading_style || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Entry</span>
                <span class="detail-value">${analysis.entry_price || 'N/A'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Take Profit</span>
                <span class="detail-value">${takeProfitDisplay}</span>
            </div>
        </div>
        <div class="confidence-score">
            <span class="detail-label">Confidence</span>
            <div class="confidence-bar">
                <div class="confidence-fill ${confidenceClass}" style="width: ${confidence}%"></div>
            </div>
            <span class="detail-value">${confidence}%</span>
        </div>
        <div class="history-date">${formattedDate}</div>
    `;
    
    return card;
}

async function viewAnalysisDetail(analysisId) {
    // For now, just navigate to analyzer with a query parameter
    // In a full implementation, you'd create a detail view
    try {
        const response = await fetch(`/api/analysis/${analysisId}`);
        const data = await response.json();
        
        if (data.success) {
            // Store in sessionStorage and open analyzer
            sessionStorage.setItem('viewAnalysis', JSON.stringify(data.analysis));
            window.location.href = `/analyzer?view=${analysisId}`;
        }
    } catch (error) {
        console.error('Error loading analysis detail:', error);
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error logging out:', error);
        // Force redirect anyway
        window.location.href = '/login';
    }
}
