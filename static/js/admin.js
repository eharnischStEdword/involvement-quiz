// © 2024–2025 Harnisch LLC. All Rights Reserved.
// Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
// Unauthorized use, distribution, or modification is prohibited.

// Admin Dashboard JavaScript
let submissionsData = [];

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

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // Button event listeners
    document.getElementById('exportBtn').addEventListener('click', exportToCSV);
    document.getElementById('refreshBtn').addEventListener('click', () => location.reload());
    document.getElementById('clearBtn').addEventListener('click', showClearModal);
    document.getElementById('cancelClearBtn').addEventListener('click', hideClearModal);
    document.getElementById('confirmBtn').addEventListener('click', clearAllData);
    
    // Enable/disable clear button based on checkbox
    document.getElementById('confirmClear').addEventListener('change', function() {
        document.getElementById('confirmBtn').disabled = !this.checked;
    });
    
    // Modal close on outside click
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            hideClearModal();
        }
    };
}

// Load main dashboard data
async function loadDashboardData() {
    try {
        show('loading');
        
        const response = await fetch('/admin/api/submissions');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        submissionsData = await response.json();
        
        // Update stats
        updateStats(submissionsData);
        
        // Render submissions table
        renderSubmissionsTable(submissionsData);
        
        // Initialize charts
        initializeCharts(submissionsData);
        
        hide('loading');
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        hide('loading');
        document.getElementById('submissions').innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading submissions data</p>
            </div>
        `;
    }
}



// Update statistics cards
function updateStats(data) {
    const statsHtml = `
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-icon submissions">
                    <i class="fas fa-users"></i>
                </div>
            </div>
            <div class="stat-number">${data.length}</div>
            <div class="stat-label">Total Submissions</div>
        </div>
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-icon today">
                    <i class="fas fa-calendar-day"></i>
                </div>
            </div>
            <div class="stat-number">${getSubmissionsToday(data)}</div>
            <div class="stat-label">Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-icon week">
                    <i class="fas fa-calendar-week"></i>
                </div>
            </div>
            <div class="stat-number">${getSubmissionsThisWeek(data)}</div>
            <div class="stat-label">This Week</div>
        </div>
        <div class="stat-card">
            <div class="stat-header">
                <div class="stat-icon avg">
                    <i class="fas fa-chart-line"></i>
                </div>
            </div>
            <div class="stat-number">${getAveragePerDay(data)}</div>
            <div class="stat-label">Daily Average</div>
        </div>
    `;
    
    document.getElementById('stats').innerHTML = statsHtml;
}

// Calculate stats
function getSubmissionsToday(data) {
    const today = new Date().toDateString();
    return data.filter(s => new Date(s.submitted_at).toDateString() === today).length;
}

function getSubmissionsThisWeek(data) {
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    return data.filter(s => new Date(s.submitted_at) >= oneWeekAgo).length;
}

function getAveragePerDay(data) {
    if (data.length === 0) return 0;
    
    const dates = data.map(s => new Date(s.submitted_at).toDateString());
    const uniqueDates = [...new Set(dates)];
    return (data.length / uniqueDates.length).toFixed(1);
}

// Render submissions table
function renderSubmissionsTable(data) {
    const tableHtml = `
        <table>
            <thead>
                <tr>
                    <th>Date/Time</th>
                    <th>Age Group</th>
                    <th>Gender</th>
                    <th>State(s)</th>
                    <th>Situation(s)</th>
                    <th>Interest(s)</th>
                    <th>Ministries</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(submission => `
                    <tr class="${isRecent(submission.submitted_at) ? 'recent' : ''}">
                        <td>${formatDate(submission.submitted_at)}</td>
                        <td>${formatAge(submission.age_group)}</td>
                        <td>${submission.gender || '-'}</td>
                        <td>${formatArray(submission.state_in_life)}</td>
                        <td>${formatArray(submission.situation)}</td>
                        <td>${formatArray(submission.interest)}</td>
                        <td>${formatMinistries(submission.recommended_ministries)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('submissions').innerHTML = tableHtml;
}

// Format helpers
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatAge(age) {
    const ageMap = {
        'infant': 'Infant (0-3)',
        'elementary': 'Elementary',
        'junior-high': 'Junior High',
        'high-school': 'High School',
        'college-young-adult': 'College/Young Adult',
        'married-parents': 'Married/Parents',
        'journeying-adults': 'Journeying Adults'
    };
    return ageMap[age] || age;
}

function formatArray(arr) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '-';
    return arr.map(item => {
        return item.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }).join(', ');
}

function formatMinistries(ministries) {
    if (!ministries || !Array.isArray(ministries)) return '-';
    return ministries.length + ' ministries';
}

function isRecent(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const hoursDiff = (now - date) / (1000 * 60 * 60);
    return hoursDiff < 24;
}

// Initialize charts
function initializeCharts(data) {
    const chartLoading = document.getElementById('chart-loading');
    const chartError = document.getElementById('chart-error');
    const chartsContent = document.getElementById('charts-content');
    
    try {
        // Hide loading, show content
        hide(chartLoading);
        hide(chartError);
        show(chartsContent);
        
        // Create charts
        createMinistriesChart(data);
        createAgeChart(data);
        createGenderChart(data);
        createInterestChart(data);
        createSituationChart(data);
        
    } catch (error) {
        console.error('Error creating charts:', error);
        hide(chartLoading);
        show(chartError);
        hide(chartsContent);
    }
}

// Ministry popularity chart
function createMinistriesChart(data) {
    const ministryCount = {};
    
    data.forEach(submission => {
        if (submission.recommended_ministries && Array.isArray(submission.recommended_ministries)) {
            submission.recommended_ministries.forEach(ministry => {
                // Skip "Come to Mass!" as it's always included
                if (ministry !== 'Come to Mass!') {
                    ministryCount[ministry] = (ministryCount[ministry] || 0) + 1;
                }
            });
        }
    });
    
    const sorted = Object.entries(ministryCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const ctx = document.getElementById('ministriesChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(item => truncateLabel(item[0])),
            datasets: [{
                label: 'Recommendations',
                data: sorted.map(item => item[1]),
                backgroundColor: '#005921',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// Age distribution chart
function createAgeChart(data) {
    const ageCount = {};
    const ageLabels = {
        'infant': 'Infant',
        'elementary': 'Elementary',
        'junior-high': 'Junior High',
        'high-school': 'High School',
        'college-young-adult': 'College/YA',
        'married-parents': 'Married/Parents',
        'journeying-adults': 'Adults'
    };
    
    data.forEach(submission => {
        const age = submission.age_group;
        if (age) {
            ageCount[age] = (ageCount[age] || 0) + 1;
        }
    });
    
    const ctx = document.getElementById('ageChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(ageCount).map(age => ageLabels[age] || age),
            datasets: [{
                data: Object.values(ageCount),
                backgroundColor: ['#005921', '#00843D', '#DAAA00', '#003764', '#52c41a', '#722ed1', '#ff6b6b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 10 }
                }
            }
        }
    });
}

// Gender distribution chart
function createGenderChart(data) {
    const genderCount = { male: 0, female: 0, skip: 0 };
    
    data.forEach(submission => {
        if (submission.gender) {
            genderCount[submission.gender] = (genderCount[submission.gender] || 0) + 1;
        }
    });
    
    const ctx = document.getElementById('genderChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Male', 'Female', 'Not Specified'],
            datasets: [{
                data: [genderCount.male, genderCount.female, genderCount.skip],
                backgroundColor: ['#005921', '#DAAA00', '#64748b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Interest chart
function createInterestChart(data) {
    const interestCount = {};
    
    data.forEach(submission => {
        if (submission.interest && Array.isArray(submission.interest)) {
            submission.interest.forEach(interest => {
                if (interest !== 'all') {
                    interestCount[interest] = (interestCount[interest] || 0) + 1;
                }
            });
        }
    });
    
    const sorted = Object.entries(interestCount).sort((a, b) => b[1] - a[1]);
    
    const ctx = document.getElementById('interestChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(item => formatLabel(item[0])),
            datasets: [{
                label: 'Count',
                data: sorted.map(item => item[1]),
                backgroundColor: '#00843D',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// Situation chart
function createSituationChart(data) {
    const situationCount = {};
    
    data.forEach(submission => {
        if (submission.situation && Array.isArray(submission.situation)) {
            submission.situation.forEach(situation => {
                if (situation !== 'situation-none-of-above') {
                    situationCount[situation] = (situationCount[situation] || 0) + 1;
                }
            });
        }
    });
    
    const ctx = document.getElementById('situationChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(situationCount).map(s => formatLabel(s)),
            datasets: [{
                data: Object.values(situationCount),
                backgroundColor: ['#005921', '#DAAA00', '#003764', '#00843D', '#ff6b6b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 10 }
                }
            }
        }
    });
}

// Helper functions
function truncateLabel(label) {
    return label.length > 20 ? label.substring(0, 20) + '...' : label;
}

function formatLabel(text) {
    return text.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Show/hide contacts


// Export to CSV
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

function convertToCSV(data) {
    if (data.length === 0) return '';
    
    // Define headers
    const headers = [
        'Date/Time',
        'Age Group',
        'Gender',
        'State(s)',
        'Situation(s)',
        'Interest(s)',
        'Recommended Ministries',
        'IP Address'
    ];
    
    // Create rows
    const rows = data.map(submission => {
        return [
            formatDate(submission.submitted_at),
            formatAge(submission.age_group),
            submission.gender || '-',
            formatArray(submission.state_in_life),
            formatArray(submission.situation),
            formatArray(submission.interest),
            submission.recommended_ministries?.join('; ') || '-',
            submission.ip_address || '-'
        ].map(cell => `"${cell}"`).join(',');
    });
    
    return [headers.join(','), ...rows].join('\n');
}

// Clear all data modal
function showClearModal() {
    show('clearModal');
}

function hideClearModal() {
    hide('clearModal');
    document.getElementById('confirmClear').checked = false;
    document.getElementById('confirmBtn').disabled = true;
}

// Clear all data
async function clearAllData() {
    try {
        const response = await fetch('/admin/api/clear-all-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            hideClearModal();
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error clearing data:', error);
        alert('Network error. Please try again.');
    }
}
