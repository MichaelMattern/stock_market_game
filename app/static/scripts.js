// Base URL for API calls
const BASE_URL = "http://localhost:8000";

// Helper function to format dates from timestamps
function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Helper function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Helper to format large numbers
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Generic function to make API calls
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.detail || 
                `API request failed with status ${response.status}`
            );
        }
        
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}

// Set active link in navigation
function setActiveLink() {
    const currentPath = window.location.pathname;
    const fileName = currentPath.split('/').pop();
    
    document.querySelectorAll('nav a').forEach(link => {
        const linkPath = link.getAttribute('href').split('/').pop();
        if (linkPath === fileName) {
            link.classList.add('active');
        }
    });
}

// Show an error message
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = `Error: ${message}`;
        element.style.color = '#ff6b6b';
    }
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    setActiveLink();
}); 