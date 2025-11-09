// Main JavaScript for Amazon Book Trends Analyzer

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatPercentage(num) {
    return (num * 100).toFixed(2) + '%';
}

function formatCurrency(num) {
    return '$' + num.toFixed(2);
}

// API Helper
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p class="mt-2">Loading data...</p>
            </div>
        `;
    }
}

// Show error message
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="empty-state">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Show empty state
function showEmpty(elementId, message = 'No data available') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="empty-state">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
                <h3>${message}</h3>
                <p>Try selecting a different time period or category.</p>
            </div>
        `;
    }
}

// Render trend badge
function getTrendBadge(score) {
    const percentage = (score * 100).toFixed(1);
    if (score > 0.1) {
        return `<span class="badge success">↑ ${percentage}%</span>`;
    } else if (score < -0.1) {
        return `<span class="badge danger">↓ ${Math.abs(percentage)}%</span>`;
    } else {
        return `<span class="badge warning">→ ${percentage}%</span>`;
    }
}

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function() {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });
    }
});

// Export functionality
function exportData(type, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `/api/export/${type}?${queryString}`;
    window.location.href = url;
}

// Format category name for display
function formatCategoryName(category) {
    return category.split('-').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Get rank badge color
function getRankBadgeClass(rank) {
    if (rank <= 10) return 'success';
    if (rank <= 50) return 'primary';
    if (rank <= 100) return 'warning';
    return 'secondary';
}
