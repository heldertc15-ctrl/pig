#!/usr/bin/env python3
"""
PC Dashboard - Waits for Computer 2 to connect
"""
import socket
import json
import threading
import base64
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from PIL import Image
import io

# Configuration
LISTEN_PORT = 5000
WEB_PORT = 8080
AUTH_TOKEN = "your_secure_password_here"  # Must match Computer 2's token

class DashboardData:
    def __init__(self):
        self.connected_computers = {}
        self.connection_history = []
        self.last_screenshots = {}
        self.lock = threading.Lock()
    
    def add_computer(self, computer_id, addr):
        with self.lock:
            self.connected_computers[computer_id] = {
                'id': computer_id,
                'address': str(addr),
                'connected_at': datetime.now().isoformat()
            }
            self.connection_history.append({
                'event': 'connected',
                'computer': computer_id,
                'time': datetime.now().isoformat()
            })
            print(f"✓ {computer_id} CONNECTED from {addr}")
    
    def remove_computer(self, computer_id):
        with self.lock:
            if computer_id in self.connected_computers:
                del self.connected_computers[computer_id]
            self.connection_history.append({
                'event': 'disconnected',
                'computer': computer_id,
                'time': datetime.now().isoformat()
            })
            print(f"✗ {computer_id} DISCONNECTED")
    
    def update_screenshot(self, computer_id, screenshot_data):
        with self.lock:
            self.last_screenshots[computer_id] = screenshot_data
    
    def get_status(self):
        with self.lock:
            return {
                'connected_computers': list(self.connected_computers.values()),
                'connection_history': self.connection_history[-10:],
                'screenshot_ids': list(self.last_screenshots.keys())
            }

dashboard = DashboardData()

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/status':
            self.serve_status()
        elif path.startswith('/api/screenshot/'):
            computer_id = path.split('/')[-1]
            self.serve_screenshot(computer_id)
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PC Dashboard - Remote Computers</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #1a1a2e;
                    color: #eee;
                }
                h1 {
                    color: #00d4ff;
                    text-align: center;
                }
                .status-box {
                    background: #16213e;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                }
                .computer-card {
                    background: #0f3460;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #00ff88;
                }
                .history-item {
                    padding: 8px;
                    margin: 5px 0;
                    background: #1a1a2e;
                    border-radius: 4px;
                    font-family: monospace;
                    border-left: 4px solid #00d4ff;
                }
                .screenshot-preview {
                    max-width: 100%;
                    max-height: 600px;
                    border-radius: 8px;
                    border: 2px solid #00d4ff;
                }
                .refresh-btn {
                    background: #00d4ff;
                    color: #1a1a2e;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>🖥️ PC Dashboard</h1>
            
            <div class="status-box">
                <h2>Connected Computers</h2>
                <div id="computers-list">
                    <p>No computers connected</p>
                </div>
            </div>
            
            <div class="status-box">
                <h2>Connection History</h2>
                <div id="history-list">
                    <p>No history</p>
                </div>
            </div>
            
            <div class="status-box">
                <h2>Live Screens</h2>
                <button class="refresh-btn" onclick="refreshData()">Refresh</button>
                <button class="refresh-btn" onclick="toggleAutoRefresh()" id="auto-btn">Auto: ON</button>
                <div id="screenshots-container">
                    <p>No screenshots</p>
                </div>
            </div>
            
            <script>
                let autoRefresh = true;
                let refreshInterval = setInterval(refreshData, 1000);
                
                async function refreshData() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        
                        // Update computers
                        const compEl = document.getElementById('computers-list');
                        if (data.connected_computers.length === 0) {
                            compEl.innerHTML = '<p style="color: #ff4444;">Waiting for connections...</p>';
                        } else {
                            compEl.innerHTML = data.connected_computers.map(c => `
                                <div class="computer-card">
                                    <strong>✓ ${c.id} CONNECTED!</strong><br>
                                    IP: ${c.address}<br>
                                    Connected: ${new Date(c.connected_at).toLocaleString()}
                                </div>
                            `).join('');
                        }
                        
                        // Update history
                        const histEl = document.getElementById('history-list');
                        if (data.connection_history.length > 0) {
                            histEl.innerHTML = data.connection_history.slice().reverse().map(h => `
                                <div class="history-item">
                                    [${new Date(h.time).toLocaleTimeString()}] 
                                    ${h.event.toUpperCase()}: ${h.computer}
                                </div>
                            `).join('');
                        }
                        
                        // Update screenshots
                        const ssEl = document.getElementById('screenshots-container');
                        if (data.screenshot_ids.length > 0) {
                            ssEl.innerHTML = data.screenshot_ids.map(id => `
                                <div style="margin: 20px 0;">
                                    <h3>${id}</h3>
                                    <img src="/api/screenshot/${id}?t=${Date.now()}" class="screenshot-preview">
                                </div>
                            `).join('');
                        }
                    } catch (e) {
                        console.error('Error:', e);
                    }
                }
                
                function toggleAutoRefresh() {
                    autoRefresh = !autoRefresh;
                    document.getElementById('auto-btn').textContent = `Auto: ${autoRefresh ? 'ON' : 'OFF'}`;
                    if (autoRefresh) {
                        refreshInterval = setInterval(refreshData, 1000);
                    } else {
                        clearInterval(refreshInterval);
                    }
                }
                
                refreshData();
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_status(self):
        status = dashboard.get_status()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def serve_screenshot(self, computer_id):
        if computer_id in dashboard.last_screenshots:
            try:
                screenshot_bytes = base64.b64decode(dashboard.last_screenshots[computer_id])
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(screenshot_bytes)
            except:
                self.send_error(500)
        else:
            self.send_error(404)

class ConnectionListener:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.running = False
        self.computer_sockets = {}
    
    def recv_message(self, sock):
        try:
            raw_length = sock.recv(4)
            if not raw_length:
                return None
            message_length = int.from_bytes(raw_length, byteorder='big')
            data = b''
            while len(data) < message_length:
                chunk = sock.recv(message_length - len(data))
                if not chunk:
                    return None
                data += chunk
            return json.loads(data.decode('utf-8'))
        except:
            return None
    
    def send_message(self, sock, message):
        try:
            message_bytes = json.dumps(message).encode('utf-8')
            message_length = len(message_bytes)
            sock.sendall(message_length.to_bytes(4, byteorder='big'))
            sock.sendall(message_bytes)
            return True
        except:
            return False
    
    def handle_computer(self, sock, addr):
        print(f"Connection from {addr}")
        
        # Authenticate
        auth_msg = self.recv_message(sock)
        if not auth_msg or auth_msg.get('token') != AUTH_TOKEN:
            self.send_message(sock, {'status': 'error'})
            sock.close()
            return
        
        computer_id = auth_msg.get('computer_id', 'unknown')
        self.send_message(sock, {'status': 'success'})
        
        self.computer_sockets[computer_id] = sock
        dashboard.add_computer(computer_id, addr)
        
        try:
            while self.running:
                message = self.recv_message(sock)
                if not message:
                    break
                
                if message.get('type') == 'screenshot':
                    dashboard.update_screenshot(computer_id, message.get('data'))
        except Exception as e:
            print(f"Error with {computer_id}: {e}")
        finally:
            if computer_id in self.computer_sockets:
                del self.computer_sockets[computer_id]
            dashboard.remove_computer(computer_id)
            try:
                sock.close()
            except:
                pass
    
    def start(self):
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print("="*50)
        print("🖥️ PC Dashboard Server")
        print("="*50)
        print(f"Listening on port: {self.port}")
        print(f"Dashboard: http://localhost:{WEB_PORT}")
        print("="*50)
        print("\nWaiting for Computer 2 to connect...")
        print("(Run computer2_client.exe on the other computer)\n")
        
        while self.running:
            try:
                sock, addr = server_socket.accept()
                thread = threading.Thread(target=self.handle_computer, args=(sock, addr))
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Error: {e}")
        
        server_socket.close()

def start_web_dashboard():
    server = HTTPServer(('0.0.0.0', WEB_PORT), DashboardHandler)
    print(f"🌐 Dashboard started at http://localhost:{WEB_PORT}")
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

if __name__ == "__main__":
    web_server = start_web_dashboard()
    listener = ConnectionListener()
    
    try:
        listener.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.running = False
        web_server.shutdown()
