#!/usr/bin/env python3
"""
Connection Listener + Dashboard (Run on PC)
This waits for the laptop to connect and shows it on the dashboard
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
LISTEN_PORT = 5000  # Port to listen for laptop connections
WEB_PORT = 8080     # Port for the web dashboard
AUTH_TOKEN = "your_secure_password_here"  # Must match laptop's token

class DashboardData:
    """Shared data for dashboard"""
    def __init__(self):
        self.connected_laptops = []
        self.connection_history = []
        self.last_screenshots = {}  # laptop_id -> screenshot
        self.lock = threading.Lock()
        self.server_status = "Waiting for connections"
    
    def add_laptop(self, laptop_id, addr):
        with self.lock:
            self.connected_laptops.append({
                'id': laptop_id,
                'address': str(addr),
                'connected_at': datetime.now().isoformat(),
                'status': 'Connected'
            })
            self.connection_history.append({
                'event': 'connected',
                'laptop': laptop_id,
                'address': str(addr),
                'time': datetime.now().isoformat()
            })
            self.server_status = f"Laptop Connected: {laptop_id}"
    
    def remove_laptop(self, laptop_id):
        with self.lock:
            self.connected_laptops = [
                l for l in self.connected_laptops 
                if l['id'] != laptop_id
            ]
            self.connection_history.append({
                'event': 'disconnected',
                'laptop': laptop_id,
                'time': datetime.now().isoformat()
            })
            if not self.connected_laptops:
                self.server_status = "Waiting for connections"
    
    def update_screenshot(self, laptop_id, screenshot_data):
        with self.lock:
            self.last_screenshots[laptop_id] = screenshot_data
    
    def get_status(self):
        with self.lock:
            return {
                'server_status': self.server_status,
                'connected_laptops': self.connected_laptops.copy(),
                'connection_history': self.connection_history[-20:],
                'screenshot_ids': list(self.last_screenshots.keys())
            }

# Global dashboard data
dashboard = DashboardData()

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the web dashboard"""
    
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
            laptop_id = path.split('/')[-1]
            self.serve_screenshot(laptop_id)
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the HTML dashboard"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Remote Desktop Dashboard - PC</title>
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
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                }
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 10px;
                }
                .status-online { background: #00ff88; }
                .status-offline { background: #ff4444; }
                .status-waiting { background: #ffaa00; }
                .laptop-card {
                    background: #0f3460;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #00d4ff;
                }
                .history-item {
                    padding: 8px;
                    margin: 5px 0;
                    background: #1a1a2e;
                    border-radius: 4px;
                    font-family: monospace;
                }
                .connected { border-left: 4px solid #00ff88; }
                .disconnected { border-left: 4px solid #ff4444; }
                .screenshot-preview {
                    max-width: 100%;
                    max-height: 500px;
                    border-radius: 8px;
                    margin-top: 20px;
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
                    margin: 10px 5px;
                }
                .refresh-btn:hover {
                    background: #00a8cc;
                }
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }
                .control-btn {
                    background: #e94560;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 5px;
                }
                .control-btn:hover {
                    background: #c73e54;
                }
            </style>
        </head>
        <body>
            <h1>🖥️ Remote Desktop Dashboard</h1>
            
            <div class="status-box">
                <h2>Server Status</h2>
                <div id="server-status">
                    <span class="status-indicator status-waiting"></span>
                    <span>Loading...</span>
                </div>
            </div>
            
            <div class="info-grid">
                <div class="status-box">
                    <h2>Connected Laptops</h2>
                    <div id="laptops-list">
                        <p>No laptops connected</p>
                    </div>
                </div>
                
                <div class="status-box">
                    <h2>Connection History</h2>
                    <div id="history-list" style="max-height: 300px; overflow-y: auto;">
                        <p>No history</p>
                    </div>
                </div>
            </div>
            
            <div class="status-box">
                <h2>Laptop Screens</h2>
                <button class="refresh-btn" onclick="refreshData()">Refresh Now</button>
                <button class="refresh-btn" onclick="toggleAutoRefresh()" id="auto-refresh-btn">Auto Refresh: ON</button>
                <div id="screenshots-container">
                    <p>No screenshots available</p>
                </div>
            </div>
            
            <script>
                let autoRefresh = true;
                let refreshInterval;
                
                function getStatusClass(status) {
                    if (status.includes('Connected')) return 'status-online';
                    if (status.includes('Waiting')) return 'status-waiting';
                    return 'status-offline';
                }
                
                async function refreshData() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        
                        // Update server status
                        const statusEl = document.getElementById('server-status');
                        const statusClass = getStatusClass(data.server_status);
                        statusEl.innerHTML = `
                            <span class="status-indicator ${statusClass}"></span>
                            <span>${data.server_status}</span>
                        `;
                        
                        // Update laptops list
                        const laptopsEl = document.getElementById('laptops-list');
                        if (data.connected_laptops.length === 0) {
                            laptopsEl.innerHTML = '<p>No laptops connected</p>';
                        } else {
                            laptopsEl.innerHTML = data.connected_laptops.map(laptop => `
                                <div class="laptop-card">
                                    <strong>Laptop:</strong> ${laptop.id}<br>
                                    <strong>IP:</strong> ${laptop.address}<br>
                                    <strong>Connected:</strong> ${new Date(laptop.connected_at).toLocaleString()}<br>
                                    <strong>Status:</strong> ${laptop.status}
                                </div>
                            `).join('');
                        }
                        
                        // Update history
                        const historyEl = document.getElementById('history-list');
                        if (data.connection_history.length === 0) {
                            historyEl.innerHTML = '<p>No history</p>';
                        } else {
                            historyEl.innerHTML = data.connection_history.slice().reverse().map(item => `
                                <div class="history-item ${item.event}">
                                    [${new Date(item.time).toLocaleTimeString()}] 
                                    ${item.event.toUpperCase()}: ${item.laptop || 'Unknown'}
                                </div>
                            `).join('');
                        }
                        
                        // Update screenshots
                        const screenshotsEl = document.getElementById('screenshots-container');
                        if (data.screenshot_ids.length === 0) {
                            screenshotsEl.innerHTML = '<p>No screenshots available</p>';
                        } else {
                            screenshotsEl.innerHTML = data.screenshot_ids.map(id => `
                                <div style="margin: 20px 0;">
                                    <h3>Laptop: ${id}</h3>
                                    <img src="/api/screenshot/${id}" class="screenshot-preview" id="screenshot-${id}">
                                </div>
                            `).join('');
                        }
                        
                    } catch (error) {
                        console.error('Error fetching status:', error);
                        document.getElementById('server-status').innerHTML = `
                            <span class="status-indicator status-offline"></span>
                            <span>Error connecting to dashboard</span>
                        `;
                    }
                }
                
                function toggleAutoRefresh() {
                    autoRefresh = !autoRefresh;
                    const btn = document.getElementById('auto-refresh-btn');
                    btn.textContent = `Auto Refresh: ${autoRefresh ? 'ON' : 'OFF'}`;
                    
                    if (autoRefresh) {
                        refreshInterval = setInterval(refreshData, 2000);
                    } else {
                        clearInterval(refreshInterval);
                    }
                }
                
                // Initial load
                refreshData();
                
                // Auto refresh every 2 seconds
                if (autoRefresh) {
                    refreshInterval = setInterval(refreshData, 2000);
                }
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_status(self):
        """Serve status as JSON"""
        status = dashboard.get_status()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def serve_screenshot(self, laptop_id):
        """Serve screenshot for a laptop"""
        if laptop_id in dashboard.last_screenshots:
            screenshot_data = dashboard.last_screenshots[laptop_id]
            try:
                screenshot_bytes = base64.b64decode(screenshot_data)
                
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

def recv_all(sock, n):
    """Helper function to receive n bytes or return None if EOF"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def recv_message(sock):
    """Receive a length-prefixed message"""
    # First receive the length (4 bytes)
    raw_length = recv_all(sock, 4)
    if not raw_length:
        return None
    message_length = int.from_bytes(raw_length, byteorder='big')
    
    # Then receive the message
    message_data = recv_all(sock, message_length)
    if not message_data:
        return None
    
    return json.loads(message_data.decode('utf-8'))

def send_message(sock, message):
    """Send a length-prefixed message"""
    message_bytes = json.dumps(message).encode('utf-8')
    message_length = len(message_bytes)
    sock.sendall(message_length.to_bytes(4, byteorder='big'))
    sock.sendall(message_bytes)

class ConnectionListener:
    """Listens for laptop connections"""
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.running = False
        self.laptop_sockets = {}
        
    def authenticate_laptop(self, laptop_socket):
        """Authenticate laptop connection"""
        try:
            auth_msg = recv_message(laptop_socket)
            if not auth_msg:
                return None
            
            if auth_msg.get('token') != AUTH_TOKEN:
                send_message(laptop_socket, {'status': 'error', 'message': 'Authentication failed'})
                return None
            
            laptop_id = auth_msg.get('laptop_id', 'unknown')
            send_message(laptop_socket, {'status': 'success', 'message': 'Authenticated'})
            return laptop_id
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def handle_laptop(self, laptop_socket, addr):
        """Handle connected laptop"""
        print(f"Connection from {addr}")
        
        laptop_id = self.authenticate_laptop(laptop_socket)
        if not laptop_id:
            print(f"Authentication failed for {addr}")
            laptop_socket.close()
            return
        
        print(f"✓ Laptop connected: {laptop_id} from {addr}")
        self.laptop_sockets[laptop_id] = laptop_socket
        dashboard.add_laptop(laptop_id, addr)
        
        try:
            while self.running:
                # Receive message from laptop
                message = recv_message(laptop_socket)
                if not message:
                    break
                
                self.process_laptop_message(laptop_id, message)
                    
        except Exception as e:
            print(f"Error with laptop {laptop_id}: {e}")
        finally:
            print(f"✗ Laptop disconnected: {laptop_id}")
            if laptop_id in self.laptop_sockets:
                del self.laptop_sockets[laptop_id]
            dashboard.remove_laptop(laptop_id)
            try:
                laptop_socket.close()
            except:
                pass
    
    def process_laptop_message(self, laptop_id, message):
        """Process messages from laptop"""
        msg_type = message.get('type')
        
        if msg_type == 'screenshot':
            # Received screenshot from laptop
            screenshot_data = message.get('data')
            dashboard.update_screenshot(laptop_id, screenshot_data)
            print(f"Received screenshot from {laptop_id}")
        elif msg_type == 'status':
            # Received status update
            print(f"Status from {laptop_id}: {message.get('status')}")
    
    def start(self):
        """Start listening for connections"""
        self.running = True
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"="*50)
        print(f"🖥️ Connection Listener Started")
        print(f"="*50)
        print(f"Listening on: {self.host}:{self.port}")
        print(f"Dashboard: http://localhost:{WEB_PORT}")
        print(f"Waiting for laptops to connect...")
        print(f"="*50)
        
        while self.running:
            try:
                laptop_socket, addr = server_socket.accept()
                
                laptop_thread = threading.Thread(
                    target=self.handle_laptop,
                    args=(laptop_socket, addr)
                )
                laptop_thread.daemon = True
                laptop_thread.start()
                
            except Exception as e:
                print(f"Error accepting connection: {e}")
        
        server_socket.close()
    
    def stop(self):
        """Stop the listener"""
        self.running = False
        for socket in self.laptop_sockets.values():
            socket.close()

def start_web_dashboard():
    """Start the web dashboard server"""
    server = HTTPServer(('0.0.0.0', WEB_PORT), DashboardHandler)
    print(f"🌐 Web dashboard started on http://0.0.0.0:{WEB_PORT}")
    
    dashboard_thread = threading.Thread(target=server.serve_forever)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    return server

if __name__ == "__main__":
    # Start web dashboard first
    web_server = start_web_dashboard()
    
    # Start connection listener
    listener = ConnectionListener()
    
    try:
        listener.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.stop()
        web_server.shutdown()
