#!/usr/bin/env python3
"""
Remote Desktop Client (Run on LAPTOP)
This connects TO your PC and sends screenshots
"""
import socket
import ssl
import json
import threading
import base64
import time
from datetime import datetime
from PIL import Image

# Configuration - UPDATE THESE!
PC_IP = "10.0.0.177"  # Your PC's IP address
PC_PORT = 5000
AUTH_TOKEN = "your_secure_password_here"  # Must match PC's token
LAPTOP_ID = "MyLaptop"  # Name to identify this laptop
SCREEN_UPDATE_INTERVAL = 2  # Seconds between screenshots

class RemoteClient:
    """Client that connects to PC and sends screenshots"""
    def __init__(self):
        self.socket = None
        self.connected = False
        self.running = False
        
    def connect(self):
        """Connect to PC"""
        try:
            print(f"Connecting to PC at {PC_IP}:{PC_PORT}...")
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Connect
            self.socket.connect((PC_IP, PC_PORT))
            
            # Authenticate
            auth_msg = {
                'token': AUTH_TOKEN,
                'laptop_id': LAPTOP_ID
            }
            self.socket.send(json.dumps(auth_msg).encode('utf-8'))
            
            # Check response
            response = json.loads(self.socket.recv(1024).decode('utf-8'))
            if response.get('status') != 'success':
                raise Exception("Authentication failed")
            
            self.connected = True
            print(f"✓ Connected to PC! Authenticated as: {LAPTOP_ID}")
            return True
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PC"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            print("Disconnected from PC")
    
    def capture_and_send_screen(self):
        """Capture screen and send to PC"""
        if not self.connected:
            return
        
        try:
            from PIL import ImageGrab
            import io
            
            # Capture screen
            screenshot = ImageGrab.grab()
            
            # Resize to reduce data size
            max_width = 1280
            max_height = 720
            width, height = screenshot.size
            
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_size = (int(width * ratio), int(height * ratio))
                screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=50, optimize=True)
            screenshot_bytes = buffer.getvalue()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # Send to PC
            message = {
                'type': 'screenshot',
                'laptop_id': LAPTOP_ID,
                'data': screenshot_b64,
                'timestamp': datetime.now().isoformat()
            }
            
            self.socket.send(json.dumps(message).encode('utf-8'))
            print(f"📸 Screenshot sent ({len(screenshot_b64)} bytes)")
            
        except Exception as e:
            print(f"Error capturing/sending screen: {e}")
            self.connected = False
    
    def run(self):
        """Main loop - connect and send screenshots"""
        self.running = True
        
        while self.running:
            if not self.connected:
                if self.connect():
                    # Connected! Start sending screenshots
                    pass
                else:
                    # Failed to connect, wait and retry
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
            
            # Send screenshot
            self.capture_and_send_screen()
            
            # Wait before next screenshot
            time.sleep(SCREEN_UPDATE_INTERVAL)
        
        self.disconnect()
    
    def stop(self):
        """Stop the client"""
        self.running = False
        self.disconnect()

if __name__ == "__main__":
    print("="*50)
    print("🖥️ Remote Desktop - Laptop Client")
    print("="*50)
    print(f"Laptop ID: {LAPTOP_ID}")
    print(f"PC Address: {PC_IP}:{PC_PORT}")
    print(f"Update interval: {SCREEN_UPDATE_INTERVAL}s")
    print("="*50)
    print("\nStarting... Press Ctrl+C to stop\n")
    
    client = RemoteClient()
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        client.stop()
