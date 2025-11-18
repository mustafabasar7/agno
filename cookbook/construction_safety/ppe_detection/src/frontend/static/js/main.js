// ===========================
// Configuration
// ===========================
const API_BASE_URL = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws';

// ===========================
// State Management
// ===========================
const state = {
    cameras: [],
    violations: [],
    alerts: [],
    currentPage: 1,
    itemsPerPage: 10,
    filters: {
        startDate: null,
        endDate: null,
        cameraId: null,
        violationType: null
    },
    stats: {
        totalViolations: 0,
        complianceRate: 0,
        activeCameras: 0,
        totalCameras: 0,
        detectedWorkers: 0
    }
};

// ===========================
// Utility Functions
// ===========================
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('tr-TR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function getViolationTypeLabel(type) {
    const labels = {
        'helmet': 'Baret Eksikliği',
        'vest': 'Yelek Eksikliği',
        'gloves': 'Eldiven Eksikliği',
        'boots': 'Bot Eksikliği',
        'glasses': 'Gözlük Eksikliği'
    };
    return labels[type] || type;
}

function getConfidenceClass(confidence) {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
}

// ===========================
// Toast Notifications
// ===========================
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<strong>${message}</strong>`;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===========================
// Statistics Update
// ===========================
function updateStatistics() {
    // Update total violations
    document.getElementById('totalViolations').textContent = state.stats.totalViolations;
    document.getElementById('violationsChange').textContent =
        `+${state.stats.todayViolations || 0} bugün`;

    // Update compliance rate
    document.getElementById('complianceRate').textContent =
        `${state.stats.complianceRate}%`;

    // Update active cameras
    document.getElementById('activeCameras').textContent =
        `${state.stats.activeCameras}/${state.stats.totalCameras}`;

    const cameraStatus = state.stats.activeCameras === state.stats.totalCameras
        ? 'Tümü çalışıyor'
        : `${state.stats.totalCameras - state.stats.activeCameras} çevrimdışı`;
    document.getElementById('camerasChange').textContent = cameraStatus;

    // Update detected workers
    document.getElementById('detectedWorkers').textContent = state.stats.detectedWorkers;

    // Update last update time
    document.getElementById('lastUpdate').textContent =
        `Son güncelleme: ${formatTime(new Date())}`;
}

// ===========================
// Camera Grid Management
// ===========================
function renderCameraGrid() {
    const cameraGrid = document.getElementById('cameraGrid');

    if (state.cameras.length === 0) {
        cameraGrid.innerHTML = `
            <div class="camera-placeholder">
                <p>Henüz kamera eklenmemiş</p>
            </div>
        `;
        return;
    }

    cameraGrid.innerHTML = state.cameras.map(camera => `
        <div class="camera-feed" data-camera-id="${camera.id}">
            <img src="${camera.snapshotUrl || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%23333" width="300" height="200"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EYükleniyor...%3C/text%3E%3C/svg%3E'}"
                 alt="${camera.name}"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'300\\' height=\\'200\\'%3E%3Crect fill=\\'%23333\\' width=\\'300\\' height=\\'200\\'/%3E%3Ctext fill=\\'%23fff\\' x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\'%3EÇevrimdışı%3C/text%3E%3C/svg%3E'">
            <div class="camera-overlay">
                <div class="camera-name">${camera.name}</div>
                <div class="camera-status-badge ${camera.status}">
                    ${camera.status === 'active' ? 'Aktif' : 'Çevrimdışı'}
                </div>
            </div>
            ${camera.hasViolation ? '<div class="camera-violation-indicator">⚠️ İhlal Tespit Edildi</div>' : ''}
        </div>
    `).join('');
}

// ===========================
// Alerts Management
// ===========================
function addAlert(alert) {
    state.alerts.unshift(alert);
    if (state.alerts.length > 50) {
        state.alerts = state.alerts.slice(0, 50);
    }
    renderAlerts();
}

function renderAlerts() {
    const alertsContainer = document.getElementById('alertsContainer');

    if (state.alerts.length === 0) {
        alertsContainer.innerHTML = `
            <div class="alert-placeholder">
                <p>Henüz ihlal bildirimi yok</p>
            </div>
        `;
        return;
    }

    alertsContainer.innerHTML = state.alerts.map(alert => `
        <div class="alert-item ${alert.severity || 'danger'}">
            <div class="alert-header">
                <div class="alert-title">⚠️ ${alert.title}</div>
                <div class="alert-time">${formatTime(alert.timestamp)}</div>
            </div>
            <div class="alert-message">${alert.message}</div>
            <div class="alert-meta">
                <span>📹 ${alert.cameraName}</span>
                <span>🎯 ${(alert.confidence * 100).toFixed(0)}%</span>
            </div>
        </div>
    `).join('');
}

// ===========================
// Violations Table
// ===========================
function filterViolations() {
    let filtered = [...state.violations];

    if (state.filters.startDate) {
        filtered = filtered.filter(v =>
            new Date(v.timestamp) >= new Date(state.filters.startDate));
    }

    if (state.filters.endDate) {
        const endDate = new Date(state.filters.endDate);
        endDate.setHours(23, 59, 59);
        filtered = filtered.filter(v =>
            new Date(v.timestamp) <= endDate);
    }

    if (state.filters.cameraId) {
        filtered = filtered.filter(v => v.cameraId === state.filters.cameraId);
    }

    if (state.filters.violationType) {
        filtered = filtered.filter(v => v.type === state.filters.violationType);
    }

    return filtered;
}

function renderViolationsTable() {
    const filtered = filterViolations();
    const start = (state.currentPage - 1) * state.itemsPerPage;
    const end = start + state.itemsPerPage;
    const pageData = filtered.slice(start, end);

    const tableBody = document.getElementById('violationsTableBody');

    if (pageData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="no-data">Gösterilecek veri bulunamadı</td>
            </tr>
        `;
    } else {
        tableBody.innerHTML = pageData.map(violation => `
            <tr>
                <td>${formatDateTime(violation.timestamp)}</td>
                <td>${violation.cameraName}</td>
                <td>${getViolationTypeLabel(violation.type)}</td>
                <td>
                    <span class="confidence-score ${getConfidenceClass(violation.confidence)}">
                        ${(violation.confidence * 100).toFixed(0)}%
                    </span>
                </td>
                <td>
                    <span class="violation-status ${violation.status}">
                        ${violation.status === 'active' ? 'Aktif' :
                          violation.status === 'resolved' ? 'Çözüldü' : 'İnceleniyor'}
                    </span>
                </td>
                <td>
                    <img src="${violation.thumbnailUrl}"
                         alt="İhlal Görüntüsü"
                         class="violation-thumbnail"
                         onclick="openImageModal('${violation.imageUrl}', ${JSON.stringify(violation).replace(/"/g, '&quot;')})">
                </td>
            </tr>
        `).join('');
    }

    // Update pagination
    const totalPages = Math.ceil(filtered.length / state.itemsPerPage);
    document.getElementById('pageInfo').textContent =
        `Sayfa ${state.currentPage} / ${totalPages || 1}`;

    document.getElementById('prevPage').disabled = state.currentPage === 1;
    document.getElementById('nextPage').disabled = state.currentPage >= totalPages;
}

// ===========================
// Camera Management
// ===========================
function renderCameraList() {
    const cameraList = document.getElementById('cameraList');

    if (state.cameras.length === 0) {
        cameraList.innerHTML = `
            <div class="camera-placeholder">
                <p>Henüz kamera eklenmemiş</p>
            </div>
        `;
        return;
    }

    cameraList.innerHTML = state.cameras.map(camera => `
        <div class="camera-item">
            <div class="camera-info">
                <div class="camera-item-name">
                    <span class="camera-status-dot ${camera.status}"></span>
                    ${camera.name}
                </div>
                <div class="camera-item-details">
                    <span>📍 ${camera.location || 'Belirtilmemiş'}</span>
                    <span>🔗 ${camera.url}</span>
                </div>
            </div>
            <div class="camera-controls">
                <button class="btn btn-sm" onclick="toggleCamera('${camera.id}')">
                    ${camera.status === 'active' ? '⏸️ Durdur' : '▶️ Başlat'}
                </button>
                <button class="btn btn-sm" onclick="editCamera('${camera.id}')">
                    ✏️ Düzenle
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteCamera('${camera.id}')">
                    🗑️ Sil
                </button>
            </div>
        </div>
    `).join('');
}

// ===========================
// Modal Functions
// ===========================
function openImageModal(imageUrl, violationData) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalInfo = document.getElementById('modalInfo');

    modalImage.src = imageUrl;

    if (typeof violationData === 'string') {
        violationData = JSON.parse(violationData.replace(/&quot;/g, '"'));
    }

    modalInfo.innerHTML = `
        <h3>İhlal Detayları</h3>
        <p><strong>Tarih:</strong> ${formatDateTime(violationData.timestamp)}</p>
        <p><strong>Kamera:</strong> ${violationData.cameraName}</p>
        <p><strong>İhlal Türü:</strong> ${getViolationTypeLabel(violationData.type)}</p>
        <p><strong>Güven Skoru:</strong> ${(violationData.confidence * 100).toFixed(0)}%</p>
        <p><strong>Durum:</strong> ${violationData.status === 'active' ? 'Aktif' :
                                      violationData.status === 'resolved' ? 'Çözüldü' : 'İnceleniyor'}</p>
    `;

    modal.classList.add('active');
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('active');
}

function openAddCameraModal() {
    const modal = document.getElementById('addCameraModal');
    modal.classList.add('active');
}

function closeAddCameraModal() {
    const modal = document.getElementById('addCameraModal');
    modal.classList.remove('active');
    document.getElementById('addCameraForm').reset();
}

// ===========================
// Camera Actions
// ===========================
async function toggleCamera(cameraId) {
    try {
        const camera = state.cameras.find(c => c.id === cameraId);
        const newStatus = camera.status === 'active' ? 'offline' : 'active';

        const response = await fetch(`${API_BASE_URL}/cameras/${cameraId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            camera.status = newStatus;
            renderCameraList();
            renderCameraGrid();
            showToast(`Kamera ${newStatus === 'active' ? 'başlatıldı' : 'durduruldu'}`, 'success');
        }
    } catch (error) {
        console.error('Camera toggle error:', error);
        showToast('Kamera durumu güncellenemedi', 'error');
    }
}

async function deleteCamera(cameraId) {
    if (!confirm('Bu kamerayı silmek istediğinizden emin misiniz?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/cameras/${cameraId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            state.cameras = state.cameras.filter(c => c.id !== cameraId);
            renderCameraList();
            renderCameraGrid();
            showToast('Kamera silindi', 'success');
        }
    } catch (error) {
        console.error('Camera delete error:', error);
        showToast('Kamera silinemedi', 'error');
    }
}

function editCamera(cameraId) {
    const camera = state.cameras.find(c => c.id === cameraId);
    if (!camera) return;

    // Populate form with camera data
    document.getElementById('cameraName').value = camera.name;
    document.getElementById('cameraUrl').value = camera.url;
    document.getElementById('cameraLocation').value = camera.location || '';

    openAddCameraModal();
}

// ===========================
// Export to CSV
// ===========================
function exportToCSV() {
    const filtered = filterViolations();

    if (filtered.length === 0) {
        showToast('Dışa aktarılacak veri yok', 'warning');
        return;
    }

    const headers = ['Tarih/Saat', 'Kamera', 'İhlal Türü', 'Güven Skoru', 'Durum'];
    const rows = filtered.map(v => [
        formatDateTime(v.timestamp),
        v.cameraName,
        getViolationTypeLabel(v.type),
        `${(v.confidence * 100).toFixed(0)}%`,
        v.status === 'active' ? 'Aktif' : v.status === 'resolved' ? 'Çözüldü' : 'İnceleniyor'
    ]);

    const csv = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `ihlaller_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();

    showToast('CSV dosyası indirildi', 'success');
}

// ===========================
// API Functions
// ===========================
async function fetchInitialData() {
    try {
        // Fetch cameras
        const camerasResponse = await fetch(`${API_BASE_URL}/cameras`);
        if (camerasResponse.ok) {
            state.cameras = await camerasResponse.json();
        }

        // Fetch violations
        const violationsResponse = await fetch(`${API_BASE_URL}/violations?limit=100`);
        if (violationsResponse.ok) {
            state.violations = await violationsResponse.json();
        }

        // Fetch statistics
        const statsResponse = await fetch(`${API_BASE_URL}/statistics`);
        if (statsResponse.ok) {
            state.stats = await statsResponse.json();
        }

        // Render all components
        updateStatistics();
        renderCameraGrid();
        renderCameraList();
        renderViolationsTable();
        renderAlerts();
        updateCameraFilter();

    } catch (error) {
        console.error('Failed to fetch initial data:', error);
        showToast('Veri yüklenirken hata oluştu', 'error');

        // Load mock data for development
        loadMockData();
    }
}

// ===========================
// Mock Data (for development)
// ===========================
function loadMockData() {
    // Mock cameras
    state.cameras = [
        {
            id: 'cam1',
            name: 'Giriş Kapısı',
            location: 'A Blok Giriş',
            url: 'rtsp://192.168.1.100:554/stream',
            status: 'active',
            snapshotUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%234ade80" width="300" height="200"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EGiriş Kapısı%3C/text%3E%3C/svg%3E'
        },
        {
            id: 'cam2',
            name: 'İnşaat Alanı 1',
            location: 'B Blok Zemin Kat',
            url: 'rtsp://192.168.1.101:554/stream',
            status: 'active',
            snapshotUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%23f59e0b" width="300" height="200"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3Eİnşaat Alanı 1%3C/text%3E%3C/svg%3E',
            hasViolation: true
        },
        {
            id: 'cam3',
            name: 'Vinç Bölgesi',
            location: 'C Blok Üst Kat',
            url: 'rtsp://192.168.1.102:554/stream',
            status: 'active',
            snapshotUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%234ade80" width="300" height="200"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EVinç Bölgesi%3C/text%3E%3C/svg%3E'
        },
        {
            id: 'cam4',
            name: 'Depo Alanı',
            location: 'Zemin Kat Depo',
            url: 'rtsp://192.168.1.103:554/stream',
            status: 'offline',
            snapshotUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%236b7280" width="300" height="200"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EÇevrimdışı%3C/text%3E%3C/svg%3E'
        }
    ];

    // Mock violations
    state.violations = [];
    const violationTypes = ['helmet', 'vest', 'gloves', 'boots', 'glasses'];
    const statuses = ['active', 'resolved', 'reviewing'];

    for (let i = 0; i < 25; i++) {
        const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
        const camera = state.cameras[Math.floor(Math.random() * 3)];
        const type = violationTypes[Math.floor(Math.random() * violationTypes.length)];

        state.violations.push({
            id: `viol${i + 1}`,
            timestamp: timestamp.toISOString(),
            cameraId: camera.id,
            cameraName: camera.name,
            type: type,
            confidence: 0.6 + Math.random() * 0.4,
            status: statuses[Math.floor(Math.random() * statuses.length)],
            thumbnailUrl: `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="60"%3E%3Crect fill="%23ef4444" width="80" height="60"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="8"%3E${getViolationTypeLabel(type)}%3C/text%3E%3C/svg%3E`,
            imageUrl: `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%23ef4444" width="800" height="600"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="24"%3E${getViolationTypeLabel(type)}%3C/text%3E%3C/svg%3E`
        });
    }

    // Sort by timestamp
    state.violations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // Mock statistics
    state.stats = {
        totalViolations: state.violations.length,
        todayViolations: state.violations.filter(v =>
            new Date(v.timestamp).toDateString() === new Date().toDateString()).length,
        complianceRate: 87,
        activeCameras: state.cameras.filter(c => c.status === 'active').length,
        totalCameras: state.cameras.length,
        detectedWorkers: 23
    };

    // Render all
    updateStatistics();
    renderCameraGrid();
    renderCameraList();
    renderViolationsTable();
    updateCameraFilter();

    showToast('Mock veri yüklendi (Geliştirme modu)', 'info');
}

// ===========================
// Event Listeners
// ===========================
function setupEventListeners() {
    // Modal close buttons
    document.getElementById('modalClose').addEventListener('click', closeImageModal);
    document.getElementById('addCameraModalClose').addEventListener('click', closeAddCameraModal);
    document.getElementById('cancelAddCamera').addEventListener('click', closeAddCameraModal);

    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
        }
    });

    // Add camera button
    document.getElementById('addCamera').addEventListener('click', openAddCameraModal);

    // Add camera form
    document.getElementById('addCameraForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const newCamera = {
            id: 'cam' + Date.now(),
            name: document.getElementById('cameraName').value,
            url: document.getElementById('cameraUrl').value,
            location: document.getElementById('cameraLocation').value,
            status: 'active',
            snapshotUrl: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect fill="%234ade80" width="300" height="200"/%3E%3Ctext fill="%23fff" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E' +
                document.getElementById('cameraName').value + '%3C/text%3E%3C/svg%3E'
        };

        try {
            const response = await fetch(`${API_BASE_URL}/cameras`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newCamera)
            });

            if (response.ok) {
                state.cameras.push(newCamera);
                renderCameraGrid();
                renderCameraList();
                updateCameraFilter();
                closeAddCameraModal();
                showToast('Kamera başarıyla eklendi', 'success');
            }
        } catch (error) {
            console.error('Add camera error:', error);
            // Add anyway for demo
            state.cameras.push(newCamera);
            renderCameraGrid();
            renderCameraList();
            updateCameraFilter();
            closeAddCameraModal();
            showToast('Kamera eklendi (Demo modu)', 'info');
        }
    });

    // Refresh cameras
    document.getElementById('refreshCameras').addEventListener('click', () => {
        renderCameraGrid();
        showToast('Kameralar yenilendi', 'info');
    });

    // Clear alerts
    document.getElementById('clearAlerts').addEventListener('click', () => {
        state.alerts = [];
        renderAlerts();
        showToast('Bildirimler temizlendi', 'info');
    });

    // Filters
    document.getElementById('filterStartDate').addEventListener('change', (e) => {
        state.filters.startDate = e.target.value;
        state.currentPage = 1;
        renderViolationsTable();
    });

    document.getElementById('filterEndDate').addEventListener('change', (e) => {
        state.filters.endDate = e.target.value;
        state.currentPage = 1;
        renderViolationsTable();
    });

    document.getElementById('filterCamera').addEventListener('change', (e) => {
        state.filters.cameraId = e.target.value;
        state.currentPage = 1;
        renderViolationsTable();
    });

    document.getElementById('filterType').addEventListener('change', (e) => {
        state.filters.violationType = e.target.value;
        state.currentPage = 1;
        renderViolationsTable();
    });

    // Pagination
    document.getElementById('prevPage').addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            renderViolationsTable();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        const totalPages = Math.ceil(filterViolations().length / state.itemsPerPage);
        if (state.currentPage < totalPages) {
            state.currentPage++;
            renderViolationsTable();
        }
    });

    // Export CSV
    document.getElementById('exportCsv').addEventListener('click', exportToCSV);

    // Chart period
    document.getElementById('chartPeriod').addEventListener('change', (e) => {
        updateCharts(e.target.value);
    });
}

function updateCameraFilter() {
    const filterCamera = document.getElementById('filterCamera');
    const currentValue = filterCamera.value;

    filterCamera.innerHTML = '<option value="">Tüm Kameralar</option>' +
        state.cameras.map(camera =>
            `<option value="${camera.id}">${camera.name}</option>`
        ).join('');

    filterCamera.value = currentValue;
}

// ===========================
// Initialization
// ===========================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    fetchInitialData();

    // Initialize WebSocket connection
    if (typeof initWebSocket === 'function') {
        initWebSocket();
    }

    // Initialize charts
    if (typeof initCharts === 'function') {
        initCharts();
    }

    // Update statistics every 30 seconds
    setInterval(updateStatistics, 30000);
});

// Make functions available globally
window.openImageModal = openImageModal;
window.toggleCamera = toggleCamera;
window.editCamera = editCamera;
window.deleteCamera = deleteCamera;
