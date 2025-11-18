#!/usr/bin/env python3
"""
PPE Detection Demo Dashboard

Standalone demo dashboard with simulated data for sales presentations.
Can run without cameras or real detection system.
"""

import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import threading

try:
    from flask import Flask, render_template, jsonify
    from flask_cors import CORS
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    print("Flask not installed. Install with: pip install flask flask-cors")


class DemoDashboardData:
    """Generate fake data for demo dashboard"""

    def __init__(self):
        self.start_time = datetime.now()
        self.violations = []
        self.workers = self._generate_workers()
        self.cameras = self._generate_cameras()

        # Start background data generator
        self.running = True
        self.generator_thread = threading.Thread(target=self._generate_violations_loop)
        self.generator_thread.daemon = True
        self.generator_thread.start()

    def _generate_workers(self) -> List[Dict]:
        """Generate fake worker data"""
        names = [
            "Mehmet Y.", "Ali K.", "Ahmet D.", "Mustafa Ö.", "Hasan A.",
            "İbrahim S.", "Hüseyin T.", "Osman B.", "İsmail C.", "Yusuf E.",
            "Emre K.", "Burak M.", "Cem Ş.", "Deniz A.", "Eren G."
        ]

        workers = []
        for i, name in enumerate(names, 1):
            worker = {
                "id": i,
                "name": name,
                "badge_number": f"W{1000+i}",
                "status": random.choice(["compliant", "compliant", "compliant", "non-compliant"]),
                "last_seen": datetime.now() - timedelta(minutes=random.randint(0, 60)),
                "violations_today": random.randint(0, 3),
                "compliance_rate": random.uniform(75, 100)
            }
            workers.append(worker)

        return workers

    def _generate_cameras(self) -> List[Dict]:
        """Generate fake camera data"""
        locations = [
            "Ana Giriş", "İnşaat Sahası A", "İnşaat Sahası B",
            "Depo Alanı", "Ofis Girişi", "Malzeme Deposu"
        ]

        cameras = []
        for i, location in enumerate(locations, 1):
            camera = {
                "id": i,
                "name": f"Kamera {i}",
                "location": location,
                "status": "active" if random.random() > 0.1 else "inactive",
                "fps": random.randint(20, 30),
                "violations_today": random.randint(0, 15),
                "workers_detected": random.randint(5, 25)
            }
            cameras.append(camera)

        return cameras

    def _generate_violation(self):
        """Generate a random violation event"""
        violation_types = [
            {"type": "missing_helmet", "severity": "high", "name": "Baret Eksik"},
            {"type": "missing_vest", "severity": "medium", "name": "Yelek Eksik"},
            {"type": "missing_both", "severity": "critical", "name": "Baret ve Yelek Eksik"},
        ]

        violation_type = random.choice(violation_types)
        worker = random.choice(self.workers)
        camera = random.choice([c for c in self.cameras if c["status"] == "active"])

        violation = {
            "id": len(self.violations) + 1,
            "timestamp": datetime.now(),
            "worker_id": worker["id"],
            "worker_name": worker["name"],
            "camera_id": camera["id"],
            "camera_location": camera["location"],
            "violation_type": violation_type["type"],
            "violation_name": violation_type["name"],
            "severity": violation_type["severity"],
            "confidence": random.uniform(0.85, 0.99),
            "status": "active",
            "image_url": f"/static/violations/violation_{random.randint(1, 10)}.jpg"
        }

        return violation

    def _generate_violations_loop(self):
        """Background thread to generate violations periodically"""
        while self.running:
            # Generate violation with some probability
            if random.random() < 0.3:  # 30% chance every cycle
                violation = self._generate_violation()
                self.violations.append(violation)

                # Keep only last 50 violations
                if len(self.violations) > 50:
                    self.violations = self.violations[-50:]

            time.sleep(5)  # Generate every 5 seconds

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        total_workers = len(self.workers)
        compliant_workers = len([w for w in self.workers if w["status"] == "compliant"])
        active_cameras = len([c for c in self.cameras if c["status"] == "active"])
        total_violations_today = sum(w["violations_today"] for w in self.workers)

        recent_violations = [v for v in self.violations
                           if (datetime.now() - v["timestamp"]).seconds < 300]  # Last 5 mins

        return {
            "total_workers": total_workers,
            "compliant_workers": compliant_workers,
            "non_compliant_workers": total_workers - compliant_workers,
            "compliance_rate": (compliant_workers / total_workers * 100) if total_workers > 0 else 0,
            "active_cameras": active_cameras,
            "total_cameras": len(self.cameras),
            "total_violations_today": total_violations_today,
            "recent_violations": len(recent_violations),
            "uptime": str(datetime.now() - self.start_time).split('.')[0],
            "frames_processed": random.randint(50000, 100000),
            "average_fps": random.randint(25, 30)
        }

    def get_violations(self, limit: int = 20) -> List[Dict]:
        """Get recent violations"""
        return sorted(self.violations, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_hourly_stats(self) -> List[Dict]:
        """Get hourly statistics for charts"""
        hours = []
        now = datetime.now()

        for i in range(24, 0, -1):
            hour_time = now - timedelta(hours=i)
            hours.append({
                "hour": hour_time.strftime("%H:%M"),
                "workers": random.randint(15, 30),
                "violations": random.randint(0, 8),
                "compliance_rate": random.uniform(85, 98)
            })

        return hours

    def stop(self):
        """Stop background threads"""
        self.running = False


# Flask App
if HAS_FLASK:
    app = Flask(__name__)
    CORS(app)

    # Create demo data instance
    demo_data = DemoDashboardData()

    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('dashboard.html')

    @app.route('/api/stats')
    def api_stats():
        """Get current statistics"""
        return jsonify(demo_data.get_statistics())

    @app.route('/api/violations')
    def api_violations():
        """Get recent violations"""
        limit = int(request.args.get('limit', 20))
        violations = demo_data.get_violations(limit)

        # Convert datetime to string for JSON
        violations_json = []
        for v in violations:
            v_copy = v.copy()
            v_copy['timestamp'] = v['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            violations_json.append(v_copy)

        return jsonify(violations_json)

    @app.route('/api/workers')
    def api_workers():
        """Get worker list"""
        workers = demo_data.workers.copy()
        for w in workers:
            w['last_seen'] = w['last_seen'].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify(workers)

    @app.route('/api/cameras')
    def api_cameras():
        """Get camera list"""
        return jsonify(demo_data.cameras)

    @app.route('/api/hourly')
    def api_hourly():
        """Get hourly statistics"""
        return jsonify(demo_data.get_hourly_stats())


def create_dashboard_html():
    """Create standalone HTML dashboard"""
    html_template = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KKD Tespit Sistemi - Demo Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            color: #667eea;
            font-size: 28px;
        }

        .header .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-card h3 {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .stat-card .value {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }

        .stat-card .label {
            color: #999;
            font-size: 12px;
        }

        .stat-card.success .value {
            color: #10b981;
        }

        .stat-card.warning .value {
            color: #f59e0b;
        }

        .stat-card.danger .value {
            color: #ef4444;
        }

        .violations-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .violations-section h2 {
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .violation-badge {
            background: #ef4444;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }

        .violations-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .violation-item {
            border-left: 4px solid #ef4444;
            background: #fef2f2;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: slideIn 0.5s;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .violation-item.critical {
            border-left-color: #dc2626;
            background: #fee2e2;
        }

        .violation-item.medium {
            border-left-color: #f59e0b;
            background: #fef3c7;
        }

        .violation-info {
            flex: 1;
        }

        .violation-info .time {
            color: #666;
            font-size: 12px;
            margin-bottom: 5px;
        }

        .violation-info .details {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }

        .violation-info .location {
            color: #999;
            font-size: 13px;
        }

        .severity-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }

        .severity-badge.critical {
            background: #dc2626;
            color: white;
        }

        .severity-badge.high {
            background: #ef4444;
            color: white;
        }

        .severity-badge.medium {
            background: #f59e0b;
            color: white;
        }

        .demo-notice {
            background: #fef3c7;
            border: 2px solid #f59e0b;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
            color: #92400e;
        }

        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="demo-notice">
            🎭 DEMO MODU - Simüle Edilmiş Veriler / DEMO MODE - Simulated Data
        </div>

        <div class="header">
            <div>
                <h1>🔍 KKD Tespit Sistemi</h1>
                <p style="color: #666;">PPE Detection System - Real-time Monitoring</p>
            </div>
            <div class="status">
                <div class="status-indicator"></div>
                <span>Sistem Aktif / System Active</span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Toplam İşçi / Total Workers</h3>
                <div class="value" id="total-workers">15</div>
                <div class="label">Şu anda sahada / Currently on site</div>
            </div>

            <div class="stat-card success">
                <h3>Uyumlu / Compliant</h3>
                <div class="value" id="compliant-workers">12</div>
                <div class="label">KKD eksiksiz / Full PPE</div>
            </div>

            <div class="stat-card danger">
                <h3>Uyumsuz / Non-Compliant</h3>
                <div class="value" id="non-compliant-workers">3</div>
                <div class="label">KKD eksik / Missing PPE</div>
            </div>

            <div class="stat-card">
                <h3>Uyumluluk Oranı / Compliance Rate</h3>
                <div class="value" id="compliance-rate">80%</div>
                <div class="label">Genel ortalama / Overall average</div>
            </div>

            <div class="stat-card">
                <h3>Aktif Kameralar / Active Cameras</h3>
                <div class="value" id="active-cameras">6</div>
                <div class="label">Toplam kamera / Total cameras</div>
            </div>

            <div class="stat-card warning">
                <h3>Bugünkü İhlaller / Today's Violations</h3>
                <div class="value" id="violations-today">8</div>
                <div class="label">İhlal tespit edildi / Violations detected</div>
            </div>
        </div>

        <div class="violations-section">
            <h2>
                🚨 Son İhlaller / Recent Violations
                <span class="violation-badge" id="violation-count">0</span>
            </h2>
            <div class="violations-list" id="violations-list">
                <!-- Violations will be added here dynamically -->
            </div>
        </div>

        <div class="footer">
            <p>KKD Tespit Sistemi © 2024 | Yapay Zeka Destekli İş Güvenliği Çözümü</p>
            <p>PPE Detection System | AI-Powered Construction Safety Solution</p>
        </div>
    </div>

    <script>
        // Simulated data updates
        let violationId = 0;

        const violationTypes = [
            { type: 'missing_helmet', name: 'Baret Eksik / Missing Helmet', severity: 'high' },
            { type: 'missing_vest', name: 'Yelek Eksik / Missing Vest', severity: 'medium' },
            { type: 'missing_both', name: 'Baret ve Yelek Eksik / Missing Both', severity: 'critical' }
        ];

        const workers = ['Mehmet Y.', 'Ali K.', 'Ahmet D.', 'Mustafa Ö.', 'Hasan A.'];
        const locations = ['Ana Giriş', 'İnşaat Sahası A', 'İnşaat Sahası B', 'Depo Alanı'];

        function addViolation() {
            const violation = violationTypes[Math.floor(Math.random() * violationTypes.length)];
            const worker = workers[Math.floor(Math.random() * workers.length)];
            const location = locations[Math.floor(Math.random() * locations.length)];

            const violationElement = document.createElement('div');
            violationElement.className = `violation-item ${violation.severity}`;
            violationElement.innerHTML = `
                <div class="violation-info">
                    <div class="time">${new Date().toLocaleString('tr-TR')}</div>
                    <div class="details">${worker} - ${violation.name}</div>
                    <div class="location">📍 ${location}</div>
                </div>
                <span class="severity-badge ${violation.severity}">${violation.severity}</span>
            `;

            const violationsList = document.getElementById('violations-list');
            violationsList.insertBefore(violationElement, violationsList.firstChild);

            // Keep only last 10 violations visible
            while (violationsList.children.length > 10) {
                violationsList.removeChild(violationsList.lastChild);
            }

            // Update violation count
            violationId++;
            document.getElementById('violation-count').textContent = violationId;

            // Update violations today
            const currentCount = parseInt(document.getElementById('violations-today').textContent);
            document.getElementById('violations-today').textContent = currentCount + 1;

            // Update non-compliant count occasionally
            if (Math.random() > 0.7) {
                const nonCompliant = parseInt(document.getElementById('non-compliant-workers').textContent);
                document.getElementById('non-compliant-workers').textContent = Math.min(nonCompliant + 1, 6);
                updateComplianceRate();
            }
        }

        function updateComplianceRate() {
            const total = parseInt(document.getElementById('total-workers').textContent);
            const compliant = parseInt(document.getElementById('compliant-workers').textContent);
            const rate = Math.round((compliant / total) * 100);
            document.getElementById('compliance-rate').textContent = rate + '%';
        }

        function updateStats() {
            // Randomly update worker counts
            const totalWorkers = 12 + Math.floor(Math.random() * 8);
            const compliantWorkers = Math.floor(totalWorkers * (0.75 + Math.random() * 0.2));

            document.getElementById('total-workers').textContent = totalWorkers;
            document.getElementById('compliant-workers').textContent = compliantWorkers;
            document.getElementById('non-compliant-workers').textContent = totalWorkers - compliantWorkers;
            updateComplianceRate();
        }

        // Add violations periodically
        setInterval(() => {
            if (Math.random() > 0.6) {  // 40% chance
                addViolation();
            }
        }, 3000);

        // Update stats periodically
        setInterval(updateStats, 10000);

        // Initialize with some violations
        setTimeout(() => addViolation(), 1000);
        setTimeout(() => addViolation(), 2000);
    </script>
</body>
</html>
    """

    # Save HTML file
    output_path = Path(__file__).parent / "demo_dashboard.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✓ Standalone dashboard created: {output_path}")
    print(f"  Open in browser: file://{output_path.absolute()}")

    return output_path


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="KKD Tespit Sistemi Demo Dashboard")
    parser.add_argument('--mode', choices=['server', 'html'], default='html',
                       help='Dashboard modu / Dashboard mode')
    parser.add_argument('--port', type=int, default=5000,
                       help='Server port (sadece server modunda / server mode only)')

    args = parser.parse_args()

    if args.mode == 'html':
        # Create standalone HTML
        create_dashboard_html()

    elif args.mode == 'server':
        if not HAS_FLASK:
            print("❌ Flask yüklü değil / Flask not installed")
            print("   Yüklemek için / To install: pip install flask flask-cors")
            sys.exit(1)

        print("=" * 80)
        print("KKD TESPİT SİSTEMİ - DEMO DASHBOARD")
        print("PPE Detection System - Demo Dashboard")
        print("=" * 80)
        print(f"\nDashboard başlatılıyor / Starting dashboard...")
        print(f"Port: {args.port}")
        print(f"\nBrowser'da açın / Open in browser:")
        print(f"  http://localhost:{args.port}")
        print("\nÇıkmak için CTRL+C / Press CTRL+C to quit")
        print()

        try:
            app.run(host='0.0.0.0', port=args.port, debug=False)
        except KeyboardInterrupt:
            print("\n\nDashboard kapatılıyor / Shutting down dashboard...")
            demo_data.stop()


if __name__ == "__main__":
    main()
