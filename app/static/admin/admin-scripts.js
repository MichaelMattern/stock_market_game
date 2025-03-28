// Admin Panel Scripts

// API Base URL - use dynamic hostname for Docker compatibility
const API_BASE_URL = window.location.protocol + '//' + window.location.host;

// API Key Storage
let adminApiKey = localStorage.getItem('adminApiKey') || '';

// Check if user is authenticated
function checkAuth() {
    if (!adminApiKey) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Set active navigation link
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const filename = currentPath.split('/').pop();
    
    document.querySelectorAll('.admin-sidebar-nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === filename) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Display notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `admin-alert admin-alert-${type}`;
    notification.textContent = message;
    
    // Add to notification area or create one if it doesn't exist
    let notificationArea = document.getElementById('notification-area');
    if (!notificationArea) {
        notificationArea = document.createElement('div');
        notificationArea.id = 'notification-area';
        notificationArea.style.position = 'fixed';
        notificationArea.style.top = '20px';
        notificationArea.style.right = '20px';
        notificationArea.style.width = '300px';
        notificationArea.style.zIndex = '1000';
        document.body.appendChild(notificationArea);
    }
    
    notificationArea.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
        if (notificationArea.children.length === 0) {
            notificationArea.remove();
        }
    }, 5000);
}

// Format date
function formatDate(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Format currency
function formatCurrency(amount) {
    if (amount === undefined || amount === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

// Format number with commas
function formatNumber(num) {
    if (num === undefined || num === null) return 'N/A';
    return new Intl.NumberFormat('en-US').format(num);
}

// API helper function for authenticated requests
async function fetchWithAuth(endpoint, options = {}) {
    if (!adminApiKey) {
        throw new Error('Admin API key not found. Please log in again.');
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'x-admin-api-key': adminApiKey,
        ...(options.headers || {})
    };
    
    // Ensure endpoint starts with a slash
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    // Build the full URL - ensure we're not hitting a static route
    let fullUrl = `${API_BASE_URL}${normalizedEndpoint}`;
    
    // Log detailed debugging information
    console.log('API request details:', {
        originalEndpoint: endpoint,
        normalizedEndpoint,
        baseUrl: API_BASE_URL,
        fullUrl,
        headers: {...headers, 'x-admin-api-key': '[REDACTED]'}
    });
    
    try {
        console.log(`Sending API request to: ${fullUrl}`);
        
        const response = await fetch(fullUrl, {
            ...options,
            headers
        });
        
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                console.error('Authentication failed:', await response.text());
                // Only redirect to login if we're not already on the login page
                if (!window.location.pathname.includes('login.html')) {
                    // Clear invalid API key and redirect to login
                    localStorage.removeItem('adminApiKey');
                    window.location.href = 'login.html';
                }
                throw new Error('Authentication failed. Please log in again.');
            }
            
            let errorData;
            try {
                errorData = await response.json();
                console.error('Error response:', errorData);
            } catch (e) {
                const errorText = await response.text();
                console.error('Error text:', errorText);
                throw new Error(`Request failed with status ${response.status}: ${errorText}`);
            }
            
            throw new Error(errorData.detail || `Request failed with status ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// Handle form submission with error handling
async function handleFormSubmit(form, submitFn) {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        
        try {
            await submitFn(form);
        } catch (error) {
            console.error('Form submission error:', error);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
}

// Create table with data
function createDataTable(tableId, data, columns, actions = []) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    // Clear existing table content
    table.innerHTML = '';
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column.label;
        headerRow.appendChild(th);
    });
    
    // Add actions column if actions are provided
    if (actions.length > 0) {
        const actionsHeader = document.createElement('th');
        actionsHeader.textContent = 'Actions';
        headerRow.appendChild(actionsHeader);
    }
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    if (data.length === 0) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = columns.length + (actions.length > 0 ? 1 : 0);
        emptyCell.textContent = 'No data available';
        emptyCell.style.textAlign = 'center';
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
    } else {
        data.forEach(item => {
            const row = document.createElement('tr');
            
            columns.forEach(column => {
                const cell = document.createElement('td');
                let value = item[column.field];
                
                // Apply formatter if provided
                if (column.formatter) {
                    value = column.formatter(value, item);
                }
                
                cell.innerHTML = value !== undefined && value !== null ? value : 'N/A';
                row.appendChild(cell);
            });
            
            // Add action buttons if actions are provided
            if (actions.length > 0) {
                const actionsCell = document.createElement('td');
                actionsCell.className = 'admin-table-actions';
                
                actions.forEach(action => {
                    const button = document.createElement('button');
                    button.className = `admin-button admin-button-${action.type || 'primary'}`;
                    button.textContent = action.label;
                    
                    if (action.icon) {
                        const icon = document.createElement('i');
                        icon.className = action.icon;
                        button.prepend(icon);
                    }
                    
                    button.addEventListener('click', () => action.handler(item));
                    actionsCell.appendChild(button);
                });
                
                row.appendChild(actionsCell);
            }
            
            tbody.appendChild(row);
        });
    }
    
    table.appendChild(tbody);
}

// Create pagination controls
function createPagination(containerId, currentPage, totalPages, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    container.className = 'admin-pagination';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevButton = document.createElement('button');
    prevButton.className = 'admin-pagination-button';
    prevButton.textContent = 'Previous';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            onPageChange(currentPage - 1);
        }
    });
    container.appendChild(prevButton);
    
    // Page buttons
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = 'admin-pagination-button';
        if (i === currentPage) {
            pageButton.classList.add('active');
        }
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            onPageChange(i);
        });
        container.appendChild(pageButton);
    }
    
    // Next button
    const nextButton = document.createElement('button');
    nextButton.className = 'admin-pagination-button';
    nextButton.textContent = 'Next';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            onPageChange(currentPage + 1);
        }
    });
    container.appendChild(nextButton);
}

// Initialize page on load
document.addEventListener('DOMContentLoaded', () => {
    setActiveNavLink();
    
    // Check authentication on admin pages (except login)
    if (!window.location.pathname.includes('login.html')) {
        checkAuth();
    }
    
    // Handle logout
    document.getElementById('logout-button')?.addEventListener('click', () => {
        localStorage.removeItem('adminApiKey');
        window.location.href = 'login.html';
    });
}); 