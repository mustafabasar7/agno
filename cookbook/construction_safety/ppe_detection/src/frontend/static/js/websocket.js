// ===========================
// WebSocket Connection Manager
// ===========================

let ws = null;
let reconnectInterval = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 3000;

// ===========================
// WebSocket Initialization
// ===========================
function initWebSocket() {
    const wsUrl = typeof WS_URL !== 'undefined' ? WS_URL : 'ws://localhost:8000/ws';

    console.log('Connecting to WebSocket:', wsUrl);

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = handleWebSocketOpen;
        ws.onmessage = handleWebSocketMessage;
        ws.onerror = handleWebSocketError;
        ws.onclose = handleWebSocketClose;

    } catch (error) {
        console.error('WebSocket initialization error:', error);
        scheduleReconnect();
    }
}

// ===========================
// WebSocket Event Handlers
// ===========================
function handleWebSocketOpen(event) {
    console.log('WebSocket connected');
    reconnectAttempts = 0;

    // Clear any existing reconnect interval
    if (reconnectInterval) {
        clearInterval(reconnectInterval);
        reconnectInterval = null;
    }

    // Update UI to show connected status
    updateConnectionStatus(true);

    // Show connection success toast
    if (typeof showToast === 'function') {
        showToast('Canlı bağlantı kuruldu', 'success');
    }

    // Send initial handshake message
    sendWebSocketMessage({
        type: 'handshake',
        clientId: generateClientId(),
        timestamp: new Date().toISOString()
    });
}

function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);

        switch (data.type) {
            case 'violation_detected':
                handleViolationDetected(data);
                break;

            case 'camera_status_changed':
                handleCameraStatusChanged(data);
                break;

            case 'statistics_update':
                handleStatisticsUpdate(data);
                break;

            case 'camera_snapshot':
                handleCameraSnapshot(data);
                break;

            case 'system_alert':
                handleSystemAlert(data);
                break;

            case 'pong':
                // Heartbeat response
                console.log('Heartbeat received');
                break;

            default:
                console.log('Unknown message type:', data.type);
        }

    } catch (error) {
        console.error('Error handling WebSocket message:', error);
    }
}

function handleWebSocketError(event) {
    console.error('WebSocket error:', event);
    updateConnectionStatus(false);
}

function handleWebSocketClose(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    updateConnectionStatus(false);

    if (typeof showToast === 'function') {
        showToast('Canlı bağlantı kesildi', 'warning');
    }

    // Attempt to reconnect
    scheduleReconnect();
}

// ===========================
// Message Handlers
// ===========================
function handleViolationDetected(data) {
    console.log('Violation detected:', data);

    // Create violation object
    const violation = {
        id: data.violationId || `viol_${Date.now()}`,
        timestamp: data.timestamp || new Date().toISOString(),
        cameraId: data.cameraId,
        cameraName: data.cameraName,
        type: data.violationType,
        confidence: data.confidence,
        status: 'active',
        thumbnailUrl: data.thumbnailUrl || data.imageUrl,
        imageUrl: data.imageUrl
    };

    // Add to violations list
    if (typeof state !== 'undefined') {
        state.violations.unshift(violation);

        // Keep only last 100 violations in memory
        if (state.violations.length > 100) {
            state.violations = state.violations.slice(0, 100);
        }

        // Update violations table
        if (typeof renderViolationsTable === 'function') {
            renderViolationsTable();
        }
    }

    // Create alert
    const alert = {
        id: `alert_${Date.now()}`,
        title: `${data.cameraName} - ${getViolationTypeLabel(data.violationType)}`,
        message: `KKD ihlali tespit edildi. Güven skoru: ${(data.confidence * 100).toFixed(0)}%`,
        timestamp: data.timestamp || new Date().toISOString(),
        cameraName: data.cameraName,
        confidence: data.confidence,
        severity: data.confidence >= 0.8 ? 'danger' : 'warning'
    };

    // Add to alerts
    if (typeof addAlert === 'function') {
        addAlert(alert);
    }

    // Show toast notification
    if (typeof showToast === 'function') {
        showToast(`⚠️ ${alert.title}`, 'error');
    }

    // Update camera grid to show violation indicator
    if (typeof state !== 'undefined') {
        const camera = state.cameras.find(c => c.id === data.cameraId);
        if (camera) {
            camera.hasViolation = true;
            if (typeof renderCameraGrid === 'function') {
                renderCameraGrid();
            }

            // Remove violation indicator after 10 seconds
            setTimeout(() => {
                camera.hasViolation = false;
                if (typeof renderCameraGrid === 'function') {
                    renderCameraGrid();
                }
            }, 10000);
        }
    }

    // Update statistics
    if (typeof state !== 'undefined') {
        state.stats.totalViolations++;
        if (typeof updateStatistics === 'function') {
            updateStatistics();
        }
    }

    // Play alert sound (optional)
    playAlertSound();
}

function handleCameraStatusChanged(data) {
    console.log('Camera status changed:', data);

    if (typeof state !== 'undefined') {
        const camera = state.cameras.find(c => c.id === data.cameraId);
        if (camera) {
            camera.status = data.status;

            if (typeof renderCameraGrid === 'function') {
                renderCameraGrid();
            }

            if (typeof renderCameraList === 'function') {
                renderCameraList();
            }

            if (typeof updateStatistics === 'function') {
                updateStatistics();
            }

            if (typeof showToast === 'function') {
                const message = data.status === 'active'
                    ? `${camera.name} aktif`
                    : `${camera.name} çevrimdışı`;
                showToast(message, data.status === 'active' ? 'success' : 'warning');
            }
        }
    }
}

function handleStatisticsUpdate(data) {
    console.log('Statistics update:', data);

    if (typeof state !== 'undefined') {
        // Update statistics
        state.stats = {
            ...state.stats,
            ...data.statistics
        };

        if (typeof updateStatistics === 'function') {
            updateStatistics();
        }

        // Update charts if needed
        if (typeof updateCharts === 'function') {
            updateCharts();
        }
    }
}

function handleCameraSnapshot(data) {
    console.log('Camera snapshot received:', data.cameraId);

    if (typeof state !== 'undefined') {
        const camera = state.cameras.find(c => c.id === data.cameraId);
        if (camera && data.snapshotUrl) {
            camera.snapshotUrl = data.snapshotUrl;

            if (typeof renderCameraGrid === 'function') {
                renderCameraGrid();
            }
        }
    }
}

function handleSystemAlert(data) {
    console.log('System alert:', data);

    const alert = {
        id: `alert_${Date.now()}`,
        title: data.title || 'Sistem Bildirimi',
        message: data.message,
        timestamp: data.timestamp || new Date().toISOString(),
        cameraName: data.cameraName || 'Sistem',
        confidence: 1.0,
        severity: data.severity || 'info'
    };

    if (typeof addAlert === 'function') {
        addAlert(alert);
    }

    if (typeof showToast === 'function') {
        showToast(data.message, data.severity || 'info');
    }
}

// ===========================
// Connection Management
// ===========================
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('systemStatus');
    if (statusIndicator) {
        const statusDot = statusIndicator.querySelector('.status-dot');
        if (connected) {
            statusIndicator.innerHTML = '<span class="status-dot"></span> Sistem Aktif';
            if (statusDot) {
                statusDot.classList.remove('offline');
            }
        } else {
            statusIndicator.innerHTML = '<span class="status-dot offline"></span> Bağlantı Kesildi';
        }
    }
}

function scheduleReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.log('Max reconnect attempts reached');
        if (typeof showToast === 'function') {
            showToast('Bağlantı kurulamadı. Lütfen sayfayı yenileyin.', 'error');
        }
        return;
    }

    if (!reconnectInterval) {
        reconnectInterval = setInterval(() => {
            reconnectAttempts++;
            console.log(`Reconnect attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`);
            initWebSocket();
        }, RECONNECT_DELAY);
    }
}

function sendWebSocketMessage(message) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
        return true;
    } else {
        console.warn('WebSocket is not open. Message not sent:', message);
        return false;
    }
}

// ===========================
// Heartbeat
// ===========================
function startHeartbeat() {
    setInterval(() => {
        sendWebSocketMessage({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }, 30000); // Every 30 seconds
}

// ===========================
// Utility Functions
// ===========================
function generateClientId() {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function getViolationTypeLabel(type) {
    if (typeof window.getViolationTypeLabel === 'function') {
        return window.getViolationTypeLabel(type);
    }

    const labels = {
        'helmet': 'Baret Eksikliği',
        'vest': 'Yelek Eksikliği',
        'gloves': 'Eldiven Eksikliği',
        'boots': 'Bot Eksikliği',
        'glasses': 'Gözlük Eksikliği'
    };
    return labels[type] || type;
}

function playAlertSound() {
    // Create a simple beep sound using Web Audio API
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.log('Audio playback not available:', error);
    }
}

// ===========================
// Cleanup on page unload
// ===========================
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
    if (reconnectInterval) {
        clearInterval(reconnectInterval);
    }
});

// ===========================
// Auto-initialize when loaded
// ===========================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait a bit before connecting to ensure main.js is loaded
        setTimeout(() => {
            initWebSocket();
            startHeartbeat();
        }, 1000);
    });
} else {
    // Document already loaded
    setTimeout(() => {
        initWebSocket();
        startHeartbeat();
    }, 1000);
}

// Make functions available globally
window.initWebSocket = initWebSocket;
window.sendWebSocketMessage = sendWebSocketMessage;
