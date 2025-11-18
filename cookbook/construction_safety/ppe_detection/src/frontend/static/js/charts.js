// ===========================
// Chart.js Configuration and Management
// ===========================

let violationsChart = null;
let violationTypesChart = null;

// ===========================
// Chart Initialization
// ===========================
function initCharts() {
    initViolationsChart();
    initViolationTypesChart();

    // Initial data load
    updateCharts('today');
}

// ===========================
// Violations Over Time Chart (Line Chart)
// ===========================
function initViolationsChart() {
    const ctx = document.getElementById('violationsChart');
    if (!ctx) return;

    violationsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'İhlal Sayısı',
                data: [],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                title: {
                    display: true,
                    text: 'İhlal Trendleri',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return `İhlal: ${context.parsed.y} adet`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12
                        },
                        maxRotation: 45,
                        minRotation: 0
                    },
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// ===========================
// Violation Types Chart (Doughnut Chart)
// ===========================
function initViolationTypesChart() {
    const ctx = document.getElementById('violationTypesChart');
    if (!ctx) return;

    violationTypesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Baret', 'Yelek', 'Eldiven', 'Bot', 'Gözlük'],
            datasets: [{
                label: 'İhlal Türleri',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#ef4444',  // Red - Helmet
                    '#f59e0b',  // Orange - Vest
                    '#3b82f6',  // Blue - Gloves
                    '#8b5cf6',  // Purple - Boots
                    '#10b981'   // Green - Glasses
                ],
                borderColor: '#fff',
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                title: {
                    display: true,
                    text: 'İhlal Türlerine Göre Dağılım',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} adet (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// ===========================
// Update Charts with Data
// ===========================
function updateCharts(period = 'today') {
    if (typeof state === 'undefined' || !state.violations) {
        return;
    }

    const data = getChartData(period);
    updateViolationsChart(data.timeline);
    updateViolationTypesChart(data.types);
}

function getChartData(period) {
    const now = new Date();
    let startDate;
    let timeFormat;
    let labels = [];

    // Determine the time period
    switch (period) {
        case 'today':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            timeFormat = 'hour';
            // Create hourly labels
            for (let i = 0; i < 24; i++) {
                labels.push(`${i.toString().padStart(2, '0')}:00`);
            }
            break;

        case 'week':
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            timeFormat = 'day';
            // Create daily labels for last 7 days
            for (let i = 6; i >= 0; i--) {
                const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
                labels.push(date.toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' }));
            }
            break;

        case 'month':
            startDate = new Date(now.getFullYear(), now.getMonth(), 1);
            timeFormat = 'day';
            // Create daily labels for current month
            const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
            for (let i = 1; i <= daysInMonth; i++) {
                labels.push(i.toString());
            }
            break;

        default:
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            timeFormat = 'hour';
            for (let i = 0; i < 24; i++) {
                labels.push(`${i.toString().padStart(2, '0')}:00`);
            }
    }

    // Filter violations by period
    const filteredViolations = state.violations.filter(v =>
        new Date(v.timestamp) >= startDate
    );

    // Count violations per time slot
    const timelineCounts = new Array(labels.length).fill(0);

    filteredViolations.forEach(violation => {
        const vDate = new Date(violation.timestamp);
        let index;

        switch (timeFormat) {
            case 'hour':
                index = vDate.getHours();
                break;
            case 'day':
                if (period === 'week') {
                    const diffDays = Math.floor((now - vDate) / (1000 * 60 * 60 * 24));
                    index = 6 - diffDays;
                } else {
                    index = vDate.getDate() - 1;
                }
                break;
        }

        if (index >= 0 && index < timelineCounts.length) {
            timelineCounts[index]++;
        }
    });

    // Count violations by type
    const typeCounts = {
        helmet: 0,
        vest: 0,
        gloves: 0,
        boots: 0,
        glasses: 0
    };

    filteredViolations.forEach(violation => {
        if (typeCounts.hasOwnProperty(violation.type)) {
            typeCounts[violation.type]++;
        }
    });

    return {
        timeline: {
            labels: labels,
            data: timelineCounts
        },
        types: typeCounts
    };
}

function updateViolationsChart(data) {
    if (!violationsChart) return;

    violationsChart.data.labels = data.labels;
    violationsChart.data.datasets[0].data = data.data;
    violationsChart.update('none'); // Update without animation for smoother updates
}

function updateViolationTypesChart(typeCounts) {
    if (!violationTypesChart) return;

    violationTypesChart.data.datasets[0].data = [
        typeCounts.helmet || 0,
        typeCounts.vest || 0,
        typeCounts.gloves || 0,
        typeCounts.boots || 0,
        typeCounts.glasses || 0
    ];
    violationTypesChart.update('none');
}

// ===========================
// Real-time Chart Updates
// ===========================
function addViolationToChart(violation) {
    if (!violationsChart || !violationTypesChart) return;

    // Get current period from dropdown
    const period = document.getElementById('chartPeriod')?.value || 'today';

    // Check if violation is in current period
    const now = new Date();
    const vDate = new Date(violation.timestamp);
    let inPeriod = false;

    switch (period) {
        case 'today':
            inPeriod = vDate.toDateString() === now.toDateString();
            break;
        case 'week':
            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            inPeriod = vDate >= weekAgo;
            break;
        case 'month':
            inPeriod = vDate.getMonth() === now.getMonth() &&
                      vDate.getFullYear() === now.getFullYear();
            break;
    }

    if (inPeriod) {
        updateCharts(period);
    }
}

// ===========================
// Export Chart as Image
// ===========================
function exportChartAsImage(chartId, filename) {
    const chart = chartId === 'violationsChart' ? violationsChart : violationTypesChart;
    if (!chart) return;

    const url = chart.toBase64Image();
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'chart.png';
    link.click();
}

// ===========================
// Chart Animation Options
// ===========================
const chartAnimationConfig = {
    duration: 750,
    easing: 'easeInOutQuart',
    onComplete: function() {
        // Animation complete callback
    }
};

// ===========================
// Responsive Chart Updates
// ===========================
window.addEventListener('resize', () => {
    if (violationsChart) {
        violationsChart.resize();
    }
    if (violationTypesChart) {
        violationTypesChart.resize();
    }
});

// ===========================
// Auto-refresh Charts
// ===========================
function startChartAutoRefresh(intervalMs = 60000) {
    setInterval(() => {
        const period = document.getElementById('chartPeriod')?.value || 'today';
        updateCharts(period);
    }, intervalMs);
}

// ===========================
// Initialize on Load
// ===========================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            initCharts();
            startChartAutoRefresh();
        }, 500);
    });
} else {
    setTimeout(() => {
        initCharts();
        startChartAutoRefresh();
    }, 500);
}

// Make functions available globally
window.initCharts = initCharts;
window.updateCharts = updateCharts;
window.addViolationToChart = addViolationToChart;
window.exportChartAsImage = exportChartAsImage;
