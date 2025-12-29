// API Configuration
const API_BASE_URL = 'http://13.53.169.204:8000/api';

// Global State
let allRecommendations = [];
let currentFilter = 'all';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadRecommendations();
    setupFilters();
});

// Load Recommendations from API
async function loadRecommendations() {
    try {
        const response = await fetch(`${API_BASE_URL}/recommendations`);
        
        if (!response.ok) {
            throw new Error('فشل في جلب البيانات');
        }
        
        const data = await response.json();
        allRecommendations = data.recommendations || [];
        
        updateStats();
        renderRecommendations();
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('recommendationsList').innerHTML = `
            <div class="loading" style="color: #ef4444;">
                ❌ خطأ في الاتصال بالسيرفر<br>
                <small>${error.message}</small>
            </div>
        `;
    }
}

// Update Statistics
function updateStats() {
    const total = allRecommendations.length;
    const buyCount = allRecommendations.filter(r => r.type === 'buy').length;
    const sellCount = allRecommendations.filter(r => r.type === 'sell').length;
    const avgConfidence = total > 0 
        ? (allRecommendations.reduce((sum, r) => sum + r.confidence, 0) / total).toFixed(1)
        : 0;
    
    document.getElementById('totalRecommendations').textContent = total;
    document.getElementById('buyCount').textContent = buyCount;
    document.getElementById('sellCount').textContent = sellCount;
    document.getElementById('avgConfidence').textContent = avgConfidence + '%';
}

// Render Recommendations
function renderRecommendations() {
    const container = document.getElementById('recommendationsList');
    
    // Filter recommendations
    const filtered = currentFilter === 'all' 
        ? allRecommendations 
        : allRecommendations.filter(r => r.type === currentFilter);
    
    if (filtered.length === 0) {
        container.innerHTML = '<div class="loading">لا توجد توصيات</div>';
        return;
    }
    
    // Sort by confidence (highest first)
    filtered.sort((a, b) => b.confidence - a.confidence);
    
    container.innerHTML = filtered.map(rec => `
        <div class="recommendation-card ${rec.type}">
            <div class="rec-badge ${rec.type}">
                ${rec.type === 'buy' ? 'شراء' : 'بيع'}
            </div>
            
            <div class="rec-info">
                <div class="rec-header">
                    <span class="rec-symbol">${rec.symbol}</span>
                    <span class="rec-confidence">ثقة: ${rec.confidence.toFixed(1)}%</span>
                </div>
                
                <div class="rec-prices">
                    <div class="price-item">
                        <div class="price-label">نقطة الدخول</div>
                        <div class="price-value">${rec.entryPrice.toFixed(2)} ريال</div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">الهدف</div>
                        <div class="price-value" style="color: var(--success);">
                            ${rec.targetPrice.toFixed(2)} ريال
                        </div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">وقف الخسارة</div>
                        <div class="price-value" style="color: var(--danger);">
                            ${rec.stopLoss.toFixed(2)} ريال
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="rec-actions">
                <button class="btn-primary" onclick="viewDetails('${rec.symbol}')">
                    التفاصيل
                </button>
            </div>
        </div>
    `).join('');
}

// Setup Filters
function setupFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update filter
            currentFilter = btn.dataset.filter;
            renderRecommendations();
        });
    });
}

// View Details (placeholder)
function viewDetails(symbol) {
    alert(`عرض تفاصيل السهم: ${symbol}\n\nسيتم إضافة صفحة التفاصيل قريباً...`);
}

// Auto Refresh every 5 minutes
setInterval(loadRecommendations, 5 * 60 * 1000);
