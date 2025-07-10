// Add this function to admin.js after the markContacted function

async function markContacted(contactId) {
    fetch(`/api/contacts/${contactId}/mark-contacted`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const contact = contactsData.find(c => c.id === contactId);
            if (contact) {
                contact.contacted = true;
                displayContacts();
                updateContactBadge(contactsData);
            }
        } else {
            alert('Error marking contact as contacted');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Network error');
    });
}

// Replace the exportToCSV function with this enhanced version that supports date filtering

function exportToCSV() {
    // Optional: Add date filter UI
    const dateFrom = prompt('Export from date (YYYY-MM-DD) or leave empty for all:');
    const dateTo = prompt('Export to date (YYYY-MM-DD) or leave empty for all:');
    
    let dataToExport = submissionsData;
    
    // Filter by date if provided
    if (dateFrom || dateTo) {
        dataToExport = submissionsData.filter(submission => {
            const submittedAt = new Date(submission.submitted_at);
            if (dateFrom && submittedAt < new Date(dateFrom)) return false;
            if (dateTo && submittedAt > new Date(dateTo + 'T23:59:59')) return false;
            return true;
        });
    }
    
    const csvContent = convertToCSV(dataToExport);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    const dateRange = (dateFrom || dateTo) 
        ? `_${dateFrom || 'start'}_to_${dateTo || 'end'}`
        : '';
    
    a.download = `st_edward_ministry_data${dateRange}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
