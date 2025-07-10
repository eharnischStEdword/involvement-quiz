// Ministry Management JavaScript
let allMinistries = [];
let filteredMinistries = [];
let editingMinistryId = null;
let selectedMinistries = new Set();

// Helper functions for show/hide without inline styles
function show(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.classList.remove('hidden');
    }
}

function hide(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.classList.add('hidden');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadMinistries();
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('ministryForm').addEventListener('submit', handleFormSubmit);
    
    // Search
    document.getElementById('searchInput').addEventListener('input', debounce(applyFilters, 300));
    
    // Filter dropdowns
    document.getElementById('filterAge').addEventListener('change', applyFilters);
    document.getElementById('filterInterest').addEventListener('change', applyFilters);
    document.getElementById('filterStatus').addEventListener('change', applyFilters);
    
    // Header buttons
    document.getElementById('importBtn').addEventListener('click', showImportModal);
    document.getElementById('addBtn').addEventListener('click', showAddModal);
    
    // Select all checkbox
    document.getElementById('selectAll').addEventListener('change', toggleSelectAll);
    
    // Bulk action buttons
    document.getElementById('bulkActivateBtn').addEventListener('click', () => toggleBulkStatus('active'));
    document.getElementById('bulkDeactivateBtn').addEventListener('click', () => toggleBulkStatus('inactive'));
    document.getElementById('bulkEditBtn').addEventListener('click', showBulkEditModal);
    document.getElementById('bulkDeleteBtn').addEventListener('click', bulkDelete);
    document.getElementById('clearSelectionBtn').addEventListener('click', clearSelection);
    
    // Modal close buttons
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('modalCancelBtn').addEventListener('click', closeModal);
    document.getElementById('bulkModalClose').addEventListener('click', closeBulkEditModal);
    document.getElementById('bulkCancelBtn').addEventListener('click', closeBulkEditModal);
    document.getElementById('bulkApplyBtn').addEventListener('click', applyBulkEdit);
    document.getElementById('importModalClose').addEventListener('click', closeImportModal);
    document.getElementById('importCancelBtn').addEventListener('click', closeImportModal);
    document.getElementById('importSubmitBtn').addEventListener('click', importMinistries);
    
    // Modal close on outside click
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            if (event.target.id === 'ministryModal') closeModal();
            else if (event.target.id === 'bulkEditModal') closeBulkEditModal();
            else if (event.target.id === 'importModal') closeImportModal();
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
                <td colspan="6" class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No ministries found</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredMinistries.map(ministry => `
        <tr class="${selectedMinistries.has(ministry.id) ? 'selected-row' : ''}" data-id="${ministry.id}">
            <td>
                <input type="checkbox" 
                       class="ministry-checkbox"
                       value="${ministry.id}" 
                       ${selectedMinistries.has(ministry.id) ? 'checked' : ''}>
            </td>
            <td>
                <div class="ministry-name">${ministry.name}</div>
                <small class="ministry-key">${ministry.ministry_key}</small>
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
                    <button class="btn btn-primary btn-sm edit-btn" data-id="${ministry.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-secondary btn-sm toggle-btn" data-id="${ministry.id}">
                        <i class="fas fa-${ministry.active ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="btn btn-danger btn-sm delete-btn" data-id="${ministry.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners to newly created elements
    document.querySelectorAll('.ministry-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            toggleRowSelection(parseInt(this.value));
        });
    });
    
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            editMinistry(parseInt(this.dataset.id));
        });
    });
    
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            toggleActive(parseInt(this.dataset.id));
        });
    });
    
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            deleteMinistry(parseInt(this.dataset.id));
        });
    });
    
    updateBulkActions();
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
    
    return badges || '<span class="no-categories">No categories</span>';
}

// Selection management
function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('#ministryList input[type="checkbox"]');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
        const ministryId = parseInt(checkbox.value);
        if (selectAll.checked) {
            selectedMinistries.add(ministryId);
        } else {
            selectedMinistries.delete(ministryId);
        }
    });
    
    // Update row highlighting
    document.querySelectorAll('#ministryList tr').forEach(row => {
        const id = parseInt(row.dataset.id);
        if (id) {
            if (selectedMinistries.has(id)) {
                row.classList.add('selected-row');
            } else {
                row.classList.remove('selected-row');
            }
        }
    });
    
    updateBulkActions();
}

function toggleRowSelection(ministryId) {
    if (selectedMinistries.has(ministryId)) {
        selectedMinistries.delete(ministryId);
    } else {
        selectedMinistries.add(ministryId);
    }
    
    // Update row highlighting
    const row = document.querySelector(`tr[data-id="${ministryId}"]`);
    if (row) {
        if (selectedMinistries.has(ministryId)) {
            row.classList.add('selected-row');
        } else {
            row.classList.remove('selected-row');
        }
    }
    
    updateBulkActions();
}

function clearSelection() {
    selectedMinistries.clear();
    document.getElementById('selectAll').checked = false;
    document.querySelectorAll('#ministryList input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    document.querySelectorAll('#ministryList tr').forEach(row => {
        row.classList.remove('selected-row');
    });
    updateBulkActions();
}

function updateBulkActions() {
    const bulkActions = document.getElementById('bulkActions');
    const selectedCount = document.getElementById('selectedCount');
    
    if (selectedMinistries.size > 0) {
        show(bulkActions);
        selectedCount.textContent = `${selectedMinistries.size} selected`;
    } else {
        hide(bulkActions);
    }
}

// Bulk actions
async function toggleBulkStatus(status) {
    const action = status === 'active' ? 'activate' : 'deactivate';
    if (!confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} ${selectedMinistries.size} ministries?`)) return;
    
    try {
        const response = await fetch('/api/ministries/bulk-update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ministry_ids: Array.from(selectedMinistries),
                updates: {
                    set: { active: status === 'active' }
                }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            clearSelection();
            loadMinistries();
        } else {
            showError(data.error || 'Failed to update ministries');
        }
    } catch (error) {
        console.error('Error in bulk status update:', error);
        showError('Network error');
    }
}

async function bulkDelete() {
    if (!confirm(`Deactivate ${selectedMinistries.size} ministries?\n\nThis will hide them from the quiz but preserve the data.`)) return;
    
    const promises = Array.from(selectedMinistries).map(id => 
        fetch(`/api/ministries/${id}`, { method: 'DELETE' })
    );
    
    try {
        await Promise.all(promises);
        showSuccess(`Deactivated ${selectedMinistries.size} ministries`);
        clearSelection();
        loadMinistries();
    } catch (error) {
        console.error('Error in bulk delete:', error);
        showError('Failed to delete some ministries');
    }
}

function showBulkEditModal() {
    document.getElementById('bulkEditCount').textContent = selectedMinistries.size;
    show('bulkEditModal');
}

function closeBulkEditModal() {
    hide('bulkEditModal');
    // Clear all bulk edit checkboxes
    document.querySelectorAll('#bulkEditModal input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
}

async function applyBulkEdit() {
    const getCheckedValues = (prefix) => {
        return Array.from(document.querySelectorAll(`input[id^="${prefix}"]:checked`))
            .map(cb => cb.value);
    };
    
    const toAdd = {
        age_groups: getCheckedValues('bulk-add-age-'),
        interests: getCheckedValues('bulk-add-interest-')
    };
    
    const toRemove = {
        age_groups: getCheckedValues('bulk-remove-age-'),
        interests: getCheckedValues('bulk-remove-interest-')
    };
    
    try {
        const response = await fetch('/api/ministries/bulk-update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ministry_ids: Array.from(selectedMinistries),
                updates: {
                    add: toAdd,
                    remove: toRemove
                }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            closeBulkEditModal();
            clearSelection();
            loadMinistries();
        } else {
            showError(data.error || 'Failed to update ministries');
        }
    } catch (error) {
        showError('Network error');
    }
}

// Show add ministry modal
function showAddModal() {
    editingMinistryId = null;
    document.getElementById('modalTitle').textContent = 'Add Ministry';
    document.getElementById('ministryForm').reset();
    document.getElementById('ministryActive').checked = true;
    show('ministryModal');
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
            show('ministryModal');
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
    hide('ministryModal');
    document.getElementById('ministryForm').reset();
    editingMinistryId = null;
}

function showImportModal() {
    show('importModal');
}

function closeImportModal() {
    hide('importModal');
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

// Notification functions with styled elements instead of alerts
function showSuccess(message) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-success';
    notification.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('notification-show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showError(message) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-error';
    notification.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('notification-show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
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
