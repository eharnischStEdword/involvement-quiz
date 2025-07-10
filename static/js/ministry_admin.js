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

// Render category badges
function renderBadges(ministry) {
    let badges = '';
    
    if (ministry.age_groups?.length) {
        badges += ministry.age_groups.slice(0, 2).map(age => 
            `<span class="badge badge-age">${formatLabel(age)}</span>`
        ).join('');
        if (ministry.age_groups.length > 2) {
            badges += `<span class="badge badge-age">+${ministry.age_groups.length - 2}</span>`;
        }
    }
    
    if (ministry.interests?.length) {
        badges += ministry.interests.slice(0, 2).map(interest => 
            `<span class="badge badge-interest">${formatLabel(interest)}</span>`
        ).join('');
    }
    
    if (ministry.genders?.length) {
        badges += ministry.genders.map(gender => 
            `<span class="badge badge-gender">${formatLabel(gender)}</span>`
        ).join('');
    }
    
    return badges || '<span style="color: #999;">No categories</span>';
}

// Show add ministry modal
function showAddModal() {
    editingMinistryId = null;
    document.getElementById('modalTitle').textContent = 'Add Ministry';
    document.getElementById('ministryForm').reset();
    document.getElementById('ministryActive').checked = true;
    document.getElementById('ministryModal').style.display = 'block';
}

// Edit ministry
async function editMinistry(id) {
    try {
        const response = await fetch(`/api/ministries/${id}`);
        const data = await response.json();
        
        if (data.success) {
            editingMinistryId = id;
            document.getElementById('modalTitle').textContent = 'Edit Ministry';
            populateForm(data.ministry);
            document.getElementById('ministryModal').style.display = 'block';
        } else {
            showError('Failed to load ministry details');
        }
    } catch (error) {
        console.error('Error loading ministry:', error);
        showError('Network error');
    }
}

// Populate form with ministry data
function populateForm(ministry) {
    document.getElementById('ministryId').value = ministry.id;
    document.getElementById('ministryKey').value = ministry.ministry_key;
    document.getElementById('ministryName').value = ministry.name;
    document.getElementById('ministryDescription').value = ministry.description || '';
    document.getElementById('ministryDetails').value = ministry.details || '';
    document.getElementById('ministryActive').checked = ministry.active;
    
    // Clear all checkboxes first
    document.querySelectorAll('#ministryForm input[type="checkbox"]').forEach(cb => {
        if (cb.id !== 'ministryActive') cb.checked = false;
    });
    
    // Set age groups
    if (ministry.age_groups) {
        ministry.age_groups.forEach(age => {
            const checkbox = document.getElementById(`age-${age}`);
            if (checkbox) checkbox.checked = true;
        });
    }
    
    // Set genders
    if (ministry.genders) {
        ministry.genders.forEach(gender => {
            const checkbox = document.getElementById(`gender-${gender}`);
            if (checkbox) checkbox.checked = true;
        });
    }
    
    // Set states
    if (ministry.states) {
        ministry.states.forEach(state => {
            const checkbox = document.getElementById(`state-${state}`);
            if (checkbox) checkbox.checked = true;
        });
    }
    
    // Set interests
    if (ministry.interests) {
        ministry.interests.forEach(interest => {
            const checkbox = document.getElementById(`interest-${interest}`);
            if (checkbox) checkbox.checked = true;
        });
    }
    
    // Set situations
    if (ministry.situations) {
        ministry.situations.forEach(situation => {
            const checkbox = document.getElementById(`situation-${situation}`);
            if (checkbox) checkbox.checked = true;
        });
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = collectFormData();
    const url = editingMinistryId 
        ? `/api/ministries/${editingMinistryId}` 
        : '/api/ministries';
    const method = editingMinistryId ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            closeModal();
            loadMinistries();
        } else {
            showError(data.error || 'Failed to save ministry');
        }
    } catch (error) {
        console.error('Error saving ministry:', error);
        showError('Network error saving ministry');
    }
}

// Collect form data
function collectFormData() {
    const getCheckedValues = (prefix) => {
        return Array.from(document.querySelectorAll(`input[id^="${prefix}-"]:checked`))
            .map(cb => cb.value);
    };
    
    return {
        ministry_key: document.getElementById('ministryKey').value,
        name: document.getElementById('ministryName').value,
        description: document.getElementById('ministryDescription').value,
        details: document.getElementById('ministryDetails').value,
        age_groups: getCheckedValues('age'),
        genders: getCheckedValues('gender'),
        states: getCheckedValues('state'),
        interests: getCheckedValues('interest'),
        situations: getCheckedValues('situation'),
        active: document.getElementById('ministryActive').checked
    };
}

// Toggle active status
async function toggleActive(id) {
    if (!confirm('Toggle this ministry\'s active status?')) return;
    
    try {
        const response = await fetch(`/api/ministries/${id}/toggle-active`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadMinistries();
        } else {
            showError(data.error || 'Failed to toggle status');
        }
    } catch (error) {
        console.error('Error toggling status:', error);
        showError('Network error');
    }
}

// Delete ministry
async function deleteMinistry(id) {
    const ministry = allMinistries.find(m => m.id === id);
    if (!confirm(`Are you sure you want to deactivate "${ministry.name}"?\n\nThis will hide it from the quiz but preserve the data.`)) return;
    
    try {
        const response = await fetch(`/api/ministries/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadMinistries();
        } else {
            showError(data.error || 'Failed to delete ministry');
        }
    } catch (error) {
        console.error('Error deleting ministry:', error);
        showError('Network error');
    }
}

// Import ministries
async function importMinistries() {
    const importData = document.getElementById('importData').value;
    
    try {
        const ministries = JSON.parse(importData);
        
        if (!Array.isArray(ministries)) {
            showError('Import data must be an array of ministry objects');
            return;
        }
        
        const response = await fetch('/api/ministries/bulk-import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ministries })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            if (data.errors?.length) {
                console.error('Import errors:', data.errors);
                alert(`Import completed with ${data.errors.length} errors. Check console for details.`);
            }
            closeImportModal();
            loadMinistries();
        } else {
            showError(data.error || 'Import failed');
        }
    } catch (error) {
        console.error('Import error:', error);
        showError('Invalid JSON format or network error');
    }
}

// Modal functions
function closeModal() {
    document.getElementById('ministryModal').style.display = 'none';
    document.getElementById('ministryForm').reset();
    editingMinistryId = null;
}

function showImportModal() {
    document.getElementById('importModal').style.display = 'block';
}

function closeImportModal() {
    document.getElementById('importModal').style.display = 'none';
    document.getElementById('importData').value = '';
}

// Utility functions
function truncate(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function formatLabel(text) {
    return text.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showSuccess(message) {
    // Simple alert for now - could be replaced with toast notification
    alert('✅ ' + message);
}

function showError(message) {
    alert('❌ ' + message);
}

// Export utility for debugging/backup
function exportAllMinistries() {
    const dataStr = JSON.stringify(allMinistries, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `ministries_backup_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// Add to window for console access
window.ministryAdmin = {
    exportAllMinistries,
    allMinistries: () => allMinistries
};
