let submissionsData = [];
let charts = {};
let chartJsLoaded = false;

function initializeDashboard() {
    document.getElementById('loading').style.display = 'block';
    
    fetch('/api/submissions')
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            submissionsData = data;
            
            const total = data.length;
            const last24h = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 24*60*60*1000)).length;
            const last7days = data.filter(s => new Date(s.submitted_at) > new Date(Date.now() - 7*24*60*60*1000)).length;
            const avg = total > 0 ? (data.reduce((sum, s) => sum + (Array.isArray(s.recommended_ministries) ? s.recommended_ministries.length : 0), 0) / total).toFixed(1) : 0;
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon submissions"><i class="fas fa-users"></i></div>
                    </div>
                    <div class="stat-number">${total}</div>
                    <div class="stat-label">Total Submissions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon today"><i class="fas fa-calendar-day"></i></div>
                    </div>
                    <div class="stat-number">${last24h}</div>
                    <div class="stat-label">Last 24 Hours</div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon week"><i class="fas fa-calendar-week"></i></div>
                    </div>
                    <div class="stat-number">${last7days}</div>
                    <div class="stat-label">Last 7 Days</div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon avg"><i class="fas fa-chart-bar"></i></div>
                    </div>
                    <div class="stat-number">${avg}</div>
                    <div class="stat-label">Avg Ministries</div>
                </div>
            `;
            
            if (chartJsLoaded && typeof Chart !== 'undefined') {
                createCharts(data);
                document.getElementById('chart-loading').style.display = 'none';
                document.getElementById('charts-content').style.display = 'block';
            }
            
            let html = '<table><tr><th>Date</th><th>Age</th><th>Gender</th><th>States</th><th>Interests</th><th>Situation</th><th>Ministries</th></tr>';
            data.slice(0, 50).forEach(sub => {
                const isRecent = new Date(sub.submitted_at) > new Date(Date.now() - 24*60*60*1000);
                html += `<tr ${isRecent ? 'class="recent"' : ''}>
                    <td>${new Date(sub.submitted_at).toLocaleDateString()}</td>
                    <td>${sub.age_group || ''}</td>
                    <td>${sub.gender || ''}</td>
                    <td>${Array.isArray(sub.state_in_life) ? sub.state_in_life.join(', ') : ''}</td>
                    <td>${Array.isArray(sub.interest) ? sub.interest.join(', ') : sub.interest || ''}</td>
                    <td>${Array.isArray(sub.situation) ? sub.situation.join(', ') : ''}</td>
                    <td>${Array.isArray(sub.recommended_ministries) ? sub.recommended_ministries.slice(0, 3).join(', ') + (sub.recommended_ministries.length > 3 ? '...' : '') : ''}</td>
                </tr>`;
            });
            html += '</table>';
            document.getElementById('submissions').innerHTML = html;
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('submissions').innerHTML = `<div class="error-message">Error loading data: ${error.message}</div>`;
        });
}

function loadChartJS() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.js';
    script.onload = () => {
        chartJsLoaded = true;
        if (submissionsData.length > 0) {
            createCharts(submissionsData);
            document.getElementById('chart-loading').style.display = 'none';
            document.getElementById('charts-content').style.display = 'block';
        } else {
            document.getElementById('chart-loading').style.display = 'none';
        }
    };
    script.onerror = () => {
        document.getElementById('chart-loading').style.display = 'none';
        document.getElementById('chart-error').style.display = 'block';
        console.error('Failed to load Chart.js');
    };
    
    document.head.appendChild(script);
}

function createCharts(data) {
    if (!chartJsLoaded || typeof Chart === 'undefined') return;
    
    try {
        const stEdwardColors = ['#005921', '#00843D', '#DAAA00', '#DDCC71', '#003764', '#2d7a47'];
        
        // FILTER OUT "Come to Mass!" from ministry count
        const ministryCount = {};
        data.forEach(sub => {
            if (Array.isArray(sub.recommended_ministries)) {
                sub.recommended_ministries.forEach(ministry => {
                    // Skip "Come to Mass!" in analytics
                    if (ministry !== 'Come to Mass!') {
                        ministryCount[ministry] = (ministryCount[ministry] || 0) + 1;
                    }
                });
            }
        });
        
        const topMinistries = Object.entries(ministryCount)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 8);
        
        createBarChart('ministriesChart', {
            labels: topMinistries.map(([name]) => {
                // Truncate long ministry names more aggressively
                return name.length > 20 ? name.substring(0, 20) + '...' : name;
            }),
            data: topMinistries.map(([,count]) => count)
        });

        const ageCount = {};
        data.forEach(sub => {
            const age = sub.age_group || 'Unknown';
            ageCount[age] = (ageCount[age] || 0) + 1;
        });
        createPieChart('ageChart', ageCount);

        const genderCount = {};
        data.forEach(sub => {
            const gender = sub.gender || 'Not specified';
            genderCount[gender] = (genderCount[gender] || 0) + 1;
        });
        createPieChart('genderChart', genderCount);

        const interestCount = {};
        data.forEach(sub => {
            if (Array.isArray(sub.interest)) {
                sub.interest.forEach(interest => {
                    interestCount[interest] = (interestCount[interest] || 0) + 1;
                });
            }
        });
        createPieChart('interestChart', interestCount);

        const situationCount = {};
        data.forEach(sub => {
            if (Array.isArray(sub.situation)) {
                sub.situation.forEach(situation => {
                    situationCount[situation] = (situationCount[situation] || 0) + 1;
                });
            }
        });
        createPieChart('situationChart', situationCount);
    } catch (error) {
        console.error('Error creating charts:', error);
        document.getElementById('chart-loading').style.display = 'none';
        document.getElementById('chart-error').style.display = 'block';
    }
}

function createBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (charts[canvasId]) charts[canvasId].destroy();
    
    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: 'rgba(0, 89, 33, 0.8)',
                borderColor: 'rgba(0, 89, 33, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        // Show full ministry name in tooltip
                        title: function(context) {
                            const index = context[0].dataIndex;
                            // You might need to store full names separately if truncated
                            return data.labels[index];
                        }
                    }
                }
            },
            scales: {
                y: { 
                    beginAtZero: true, 
                    ticks: { stepSize: 1 } 
                },
                x: { 
                    ticks: { 
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: false,
                        font: {
                            size: 11
                        }
                    } 
                }
            }
        }
    });
}

function createPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (charts[canvasId]) charts[canvasId].destroy();
    
    const stEdwardColors = ['#005921', '#00843D', '#DAAA00', '#DDCC71', '#003764', '#2d7a47', '#52c41a', '#73d13d', '#95de64', '#b7eb8f'];
    
    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: stEdwardColors.slice(0, Object.keys(data).length),
                borderWidth: 3,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { 
                        padding: 15, 
                        usePointStyle: true,
                        font: {
                            size: 11
                        },
                        boxWidth: 15
                    }
                }
            }
        }
    });
}

function showClearModal() {
    document.getElementById('clearModal').style.display = 'block';
    document.getElementById('confirmClear').checked = false;
    document.getElementById('confirmBtn').disabled = true;
}

function hideClearModal() {
    document.getElementById('clearModal').style.display = 'none';
}

document.getElementById('confirmClear').addEventListener('change', function() {
    document.getElementById('confirmBtn').disabled = !this.checked;
});

function clearAllData() {
    if (!document.getElementById('confirmClear').checked) return;
    
    if (confirm('FINAL CONFIRMATION: Delete all submission data?')) {
        fetch('/api/clear-all-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ All data cleared successfully');
                location.reload();
            } else {
                alert('❌ Error: ' + data.message);
            }
        })
        .catch(error => alert('❌ Error: ' + error.message));
        hideClearModal();
    }
}

function exportToCSV() {
    const csvContent = convertToCSV(submissionsData);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `st_edward_ministry_data_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    // Get headers dynamically from first row
    const headers = Object.keys(data[0]);
    let csv = headers.map(h => `"${h}"`).join(',') + '\n';
    
    data.forEach(row => {
        const csvRow = headers.map(header => {
            let value = row[header];
            
            // Handle different data types
            if (value === null || value === undefined) {
                return '""';
            } else if (value instanceof Date || header.includes('_at')) {
                return `"${new Date(value).toLocaleDateString()}"`;
            } else if (Array.isArray(value)) {
                return `"${value.join('; ')}"`;
            } else if (typeof value === 'object') {
                return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
            } else {
                return `"${String(value).replace(/"/g, '""')}"`;
            }
        });
        csv += csvRow.join(',') + '\n';
    });
    return csv;
}

window.onclick = function(event) {
    if (event.target == document.getElementById('clearModal')) {
        hideClearModal();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setTimeout(loadChartJS, 100);
});
