// Ministry Management JavaScript
let allMinistries = [];
let filteredMinistries = [];
let editingMinistryId = null;
let selectedMinistries = new Set();

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadMinistries();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('ministryForm').addEventListener('submit', handleFormSubmit);
    
    // Search
    document.getElementById('searchInput').addEventListener('input', debounce(applyFilters, 300));
    
    // Modal close on outside click
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal();
            closeImportModal();
        }
    };
}

// Load all ministries from API
async function loadMinistries() {
    try {
        const response = await fetch('/api/ministries/all');
        const data = await response.json();
        
        if (data.success) {
            allMinistries = data.ministries;
            applyFilters();
            updateStats();
        } else {
            showError('Failed to load ministries');
        }
    } catch (error) {
        console.error('Error loading ministries:', error);
        showError('Network error loading ministries');
    }
}

// Update statistics
function updateStats() {
    const total = allMinistries.length;
    const active = allMinistries.filter(m => m.active).length;
    const inactive = total - active;
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('activeCount').textContent = active;
    document.getElementById('inactiveCount').textContent = inactive;
}

// Apply search and filters
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const ageFilter = document.getElementById('filterAge').value;
    const interestFilter = document.getElementById('filterInterest').value;
    const statusFilter = document.getElementById('filterStatus').value;
    
    filteredMinistries = allMinistries.filter(ministry => {
        // Search filter
        if (searchTerm) {
            const searchableText = `${ministry.name} ${ministry.description} ${ministry.ministry_key}`.toLowerCase();
            if (!searchableText.includes(searchTerm)) return false;
        }
        
        // Age filter
        if (ageFilter && (!ministry.age_groups || !ministry.age_groups.includes(ageFilter))) {
            return false;
        }
        
        // Interest filter
        if (interestFilter && (!ministry.interests || !ministry.interests.includes(interestFilter))) {
            return false;
        }
        
        // Status filter
        if (statusFilter === 'active' && !ministry.active) return false;
        if (statusFilter === 'inactive' && ministry.active) return false;
        
        return true;
    });
    
    renderMinistryTable();
}

// Render ministry table
function renderMinistryTable() {
    const tbody = document.getElementById('ministryList');
    
    if (filteredMinistries.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No ministries found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredMinistries.map(ministry => `
        <tr>
            <td>
                <div class="ministry-name">${ministry.name}</div>
                <small style="color: #64748b;">${ministry.ministry_key}</small>
            </td>
            <td>${truncate(ministry.description, 100)}</td>
            <td>
                ${renderBadges(ministry)}
            </td>
            <td>
                <span class="status-badge ${ministry.active ? 'status-active' : 'status-inactive'}">
                    ${ministry.active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-primary btn-sm" onclick="editMinistry(${ministry.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="toggleActive(${ministry.id})">
                        <i class="fas fa-${ministry.active ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteMinistry(${ministry.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}
