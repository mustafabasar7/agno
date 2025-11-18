#!/usr/bin/env python3
"""
Simple HTTP server for PPE Detection Dashboard
Usage: python3 server.py [port]
Default port: 8080
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Default port
DEFAULT_PORT = 8080

# Get port from command line or use default
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

# Change to the frontend directory
frontend_dir = Path(__file__).parent
os.chdir(frontend_dir)

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the HTTP server"""
    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            print("=" * 60)
            print("🏗️  İnşaat Güvenliği - KKD Tespit Sistemi Dashboard")
            print("=" * 60)
            print(f"\n✅ Server başlatıldı!")
            print(f"📍 Adres: http://localhost:{PORT}")
            print(f"📂 Dizin: {frontend_dir}")
            print(f"\n🌐 Tarayıcınızda açın: http://localhost:{PORT}")
            print("\n⚠️  Sunucuyu durdurmak için: Ctrl+C\n")
            print("=" * 60)
            print("\n💡 Not: Backend API ve WebSocket servislerinin")
            print("   çalıştığından emin olun!\n")

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n👋 Sunucu kapatılıyor...")
        print("=" * 60)
        sys.exit(0)

    except OSError as e:
        if e.errno == 98:
            print(f"\n❌ Hata: Port {PORT} zaten kullanımda!")
            print(f"💡 Başka bir port deneyin: python3 server.py 8081\n")
        else:
            print(f"\n❌ Hata: {e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
