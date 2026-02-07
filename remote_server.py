#!/usr/bin/env python3
"""
Remote Desktop Server with Web Dashboard
Run this on the laptop you want to control
"""
import socket
import ssl
import json
import threading
import base64
import logging
from io import BytesIO
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Security configuration
CERT_FILE = "server.crt"
KEY_FILE = "server.key"
AUTH_TOKEN = "your_secure_password_here"  # CHANGE THIS!
WEB_PORT = 8080  # Port for the web dashboard

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class DashboardData:
    """Shared data between remote server and web dashboard"""
    def __init__(self):
        self.connected_clients = []
        self.connection_history = []
        self.server_status = "Offline"
        self.last_screenshot = None
        self.lock = threading.Lock()
    
    def add_client(self, addr, connected_time):
        with self.lock:
            self.connected_clients.append({
                'address': str(addr),
                'connected_at': connected_time.isoformat(),
                'status': 'Connected'
            })
            self.connection_history.append({
                'event': 'connected',
                'address': str(addr),
                'time': connected_time.isoformat()
            })
            self.server_status = "Online - Client Connected"
    
    def remove_client(self, addr):
        with self.lock:
            self.connected_clients = [
                c for c in self.connected_clients 
                if c['address'] != str(addr)
            ]
            self.connection_history.append({
                'event': 'disconnected',
                'address': str(addr),
                'time': datetime.now().isoformat()
            })
            if not self.connected_clients:
                self.server_status = "Online - Waiting for connection"
    
    def update_screenshot(self, screenshot_data):
        with self.lock:
            self.last_screenshot = screenshot_data
    
    def set_server_online(self):
        with self.lock:
            self.server_status = "Online - Waiting for connection"
    
    def get_status(self):
        with self.lock:
            return {
                'server_status': self.server_status,
                'connected_clients': self.connected_clients.copy(),
                'connection_history': self.connection_history[-20:],  # Last 20 events
                'has_screenshot': self.last_screenshot is not None
            }

# Global dashboard data
dashboard = DashboardData()

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the web dashboard"""
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/status':
            self.serve_status()
        elif path == '/api/screenshot':
            self.serve_screenshot()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the HTML dashboard"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Remote Desktop Dashboard</title>
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
                .client-card {
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
                    border-radius: 8px;
                    margin-top: 20px;
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
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Remote Desktop Dashboard</h1>
            
            <div class="status-box">
                <h2>Server Status</h2>
                <div id="server-status">
                    <span class="status-indicator status-offline"></span>
                    <span>Loading...</span>
                </div>
            </div>
            
            <div class="info-grid">
                <div class="status-box">
                    <h2>Connected Clients</h2>
                    <div id="clients-list">
                        <p>No clients connected</p>
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
                <h2>Live Preview</h2>
                <button class="refresh-btn" onclick="refreshData()">Refresh Now</button>
                <button class="refresh-btn" onclick="toggleAutoRefresh()" id="auto-refresh-btn">Auto Refresh: ON</button>
                <div id="screenshot-container">
                    <p>No screenshot available</p>
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
                        
                        // Update clients list
                        const clientsEl = document.getElementById('clients-list');
                        if (data.connected_clients.length === 0) {
                            clientsEl.innerHTML = '<p>No clients connected</p>';
                        } else {
                            clientsEl.innerHTML = data.connected_clients.map(client => `
                                <div class="client-card">
                                    <strong>Client:</strong> ${client.address}<br>
                                    <strong>Connected:</strong> ${new Date(client.connected_at).toLocaleString()}<br>
                                    <strong>Status:</strong> ${client.status}
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
                                    ${item.event.toUpperCase()}: ${item.address}
                                </div>
                            `).join('');
                        }
                        
                        // Update screenshot if available
                        if (data.has_screenshot) {
                            document.getElementById('screenshot-container').innerHTML = `
                                <img src="/api/screenshot" class="screenshot-preview" id="live-screenshot">
                            `;
                        }
                        
                    } catch (error) {
                        console.error('Error fetching status:', error);
                        document.getElementById('server-status').innerHTML = `
                            <span class="status-indicator status-offline"></span>
                            <span>Error connecting to server</span>
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
    
    def serve_screenshot(self):
        """Serve the latest screenshot"""
        if dashboard.last_screenshot:
            screenshot_bytes = base64.b64decode(dashboard.last_screenshot)
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(screenshot_bytes)
        else:
            self.send_error(404)

class RemoteServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.running = False
        self.clients = []
        
    def create_ssl_context(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        except FileNotFoundError:
            print(f"Warning: SSL certificates not found. Run generate_certs.py first!")
            print("For testing only, continuing without encryption...")
            return None
        return context
    
    def authenticate_client(self, client_socket):
        """Authenticate client before allowing access"""
        try:
            auth_data = client_socket.recv(1024).decode('utf-8')
            auth_msg = json.loads(auth_data)
            
            if auth_msg.get('token') != AUTH_TOKEN:
                response = {'status': 'error', 'message': 'Authentication failed'}
                client_socket.send(json.dumps(response).encode('utf-8'))
                return False
            
            response = {'status': 'success', 'message': 'Authenticated'}
            client_socket.send(json.dumps(response).encode('utf-8'))
            return True
            
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return False
    
    def handle_client(self, client_socket, addr):
        """Handle individual client connection"""
        logging.info(f"Client connected from {addr}")
        
        if not self.authenticate_client(client_socket):
            logging.warning(f"Authentication failed for {addr}")
            client_socket.close()
            return
        
        logging.info(f"Client authenticated: {addr}")
        self.clients.append(client_socket)
        
        # Update dashboard
        dashboard.add_client(addr, datetime.now())
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                command = json.loads(data.decode('utf-8'))
                self.process_command(client_socket, command)
                
        except Exception as e:
            logging.error(f"Error handling client {addr}: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            logging.info(f"Client disconnected: {addr}")
            dashboard.remove_client(addr)
    
    def process_command(self, client_socket, command):
        """Process commands from client"""
        cmd_type = command.get('type')
        
        if cmd_type == 'get_screen':
            screenshot_data = self.capture_screen()
            dashboard.update_screenshot(screenshot_data)
            response = {
                'type': 'screen',
                'data': screenshot_data,
                'timestamp': datetime.now().isoformat()
            }
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        elif cmd_type == 'mouse_move':
            x, y = command.get('x'), command.get('y')
            self.move_mouse(x, y)
            
        elif cmd_type == 'mouse_click':
            x, y = command.get('x'), command.get('y')
            button = command.get('button', 'left')
            self.mouse_click(x, y, button)
            
        elif cmd_type == 'key_press':
            key = command.get('key')
            self.press_key(key)
    
    def capture_screen(self):
        """Capture screen"""
        import windows_impl
        return windows_impl.get_screen_capture()
    
    def move_mouse(self, x, y):
        """Move mouse to position"""
        import windows_impl
        windows_impl.move_mouse(x, y)
    
    def mouse_click(self, x, y, button):
        """Simulate mouse click"""
        import windows_impl
        windows_impl.mouse_click(x, y, button)
    
    def press_key(self, key):
        """Simulate key press"""
        import windows_impl
        windows_impl.press_key(key)
    
    def start(self):
        """Start the server"""
        self.running = True
        dashboard.set_server_online()
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        logging.info(f"Remote server started on {self.host}:{self.port}")
        logging.info(f"Web dashboard available at http://localhost:{WEB_PORT}")
        logging.info(f"Waiting for connections...")
        
        ssl_context = self.create_ssl_context()
        
        while self.running:
            try:
                client_socket, addr = server_socket.accept()
                
                if ssl_context:
                    client_socket = ssl_context.wrap_socket(client_socket, server_side=True)
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                logging.error(f"Error accepting connection: {e}")
        
        server_socket.close()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        for client in self.clients:
            client.close()

def start_web_dashboard():
    """Start the web dashboard server"""
    server = HTTPServer(('0.0.0.0', WEB_PORT), DashboardHandler)
    logging.info(f"Web dashboard started on http://0.0.0.0:{WEB_PORT}")
    
    # Run in a thread so it doesn't block
    dashboard_thread = threading.Thread(target=server.serve_forever)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    return server

if __name__ == "__main__":
    setup_logging()
    
    # Start web dashboard first
    web_server = start_web_dashboard()
    
    # Start remote server
    server = RemoteServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        server.stop()
        web_server.shutdown()
