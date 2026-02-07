#!/usr/bin/env python3
"""
Simple Remote Client for Computer 2
Connects to your PC and sends screenshots
"""
import socket
import json
import base64
import time
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import io
from datetime import datetime

# Configuration - EDIT THESE BEFORE CREATING EXE
PC_IP = "10.0.0.177"  # <-- EDIT THIS: Your PC's IP address
PC_PORT = 5000
AUTH_TOKEN = "MySecretPassword123"  # <-- EDIT THIS: Must match PC's password
COMPUTER_NAME = "Computer2"  # <-- EDIT THIS: Name shown on dashboard
AUTO_CONNECT = True  # Set to True to connect automatically when .exe opens
UPDATE_INTERVAL = 1  # Seconds between screenshots

class ConnectionWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Remote Desktop - {COMPUTER_NAME}")
        self.root.geometry("400x200")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to connect...")
        
        tk.Label(self.root, text=f"Remote Desktop Client", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Computer: {COMPUTER_NAME}", font=("Arial", 12)).pack()
        tk.Label(self.root, text=f"Target PC: {PC_IP}:{PC_PORT}", font=("Arial", 10)).pack(pady=5)
        
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=20)
        
        self.connect_btn = tk.Button(self.root, text="Connect", command=self.start_connection, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.connect_btn.pack(pady=10)
        
        self.disconnect_btn = tk.Button(self.root, text="Disconnect", command=self.stop_connection, bg="red", fg="white", state="disabled")
        self.disconnect_btn.pack()
        
        self.running = False
        self.socket = None
        
    def on_closing(self):
        if self.running:
            self.stop_connection()
        self.root.destroy()
        sys.exit()
    
    def capture_screen(self):
        """Capture and compress screen"""
        try:
            screenshot = ImageGrab.grab()
            
            # Resize for faster transfer
            screenshot = screenshot.resize((960, 540), Image.Resampling.LANCZOS)
            
            # Convert to JPEG
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=40, optimize=True)
            screenshot_bytes = buffer.getvalue()
            
            return base64.b64encode(screenshot_bytes).decode('utf-8')
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
    
    def send_message(self, message):
        """Send length-prefixed message"""
        try:
            message_bytes = json.dumps(message).encode('utf-8')
            message_length = len(message_bytes)
            self.socket.sendall(message_length.to_bytes(4, byteorder='big'))
            self.socket.sendall(message_bytes)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def recv_message(self):
        """Receive length-prefixed message"""
        try:
            # Receive length
            raw_length = self.socket.recv(4)
            if not raw_length:
                return None
            message_length = int.from_bytes(raw_length, byteorder='big')
            
            # Receive message
            data = b''
            while len(data) < message_length:
                chunk = self.socket.recv(message_length - len(data))
                if not chunk:
                    return None
                data += chunk
            
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def connection_loop(self):
        """Main connection loop"""
        while self.running:
            try:
                # Capture and send screenshot
                screenshot_data = self.capture_screen()
                if screenshot_data:
                    message = {
                        'type': 'screenshot',
                        'computer_id': COMPUTER_NAME,
                        'data': screenshot_data,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if not self.send_message(message):
                        break
                
                time.sleep(UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"Connection loop error: {e}")
                break
        
        # Connection lost
        self.root.after(0, self.on_connection_lost)
    
    def start_connection(self):
        """Start connection to PC"""
        try:
            self.status_var.set("Connecting...")
            self.root.update()
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Connect
            self.socket.connect((PC_IP, PC_PORT))
            
            # Authenticate
            auth_msg = {
                'token': AUTH_TOKEN,
                'computer_id': COMPUTER_NAME
            }
            
            if not self.send_message(auth_msg):
                raise Exception("Failed to send auth")
            
            # Check response
            response = self.recv_message()
            if not response or response.get('status') != 'success':
                raise Exception("Authentication failed")
            
            self.running = True
            self.status_var.set("✓ Connected! Streaming screen...")
            self.status_label.config(fg="green")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            # Start connection loop in thread
            import threading
            thread = threading.Thread(target=self.connection_loop)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.status_var.set(f"✗ Connection failed: {e}")
            self.status_label.config(fg="red")
            if self.socket:
                self.socket.close()
                self.socket = None
    
    def stop_connection(self):
        """Stop connection"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.status_var.set("Disconnected")
        self.status_label.config(fg="blue")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
    
    def on_connection_lost(self):
        """Handle connection lost"""
        self.running = False
        self.socket = None
        self.status_var.set("✗ Connection lost")
        self.status_label.config(fg="red")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
    
    def run(self):
        """Run the application"""
        # Auto-connect if enabled
        if AUTO_CONNECT:
            self.root.after(1000, self.start_connection)  # Wait 1 second for window to show
        self.root.mainloop()

if __name__ == "__main__":
    # Check if IP is still set to default
    if "YOUR_PC_IP_HERE" in PC_IP or PC_IP == "":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Configuration Error",
            "Please edit the PC_IP variable in this file before running!\n\n"
            "Change:\nPC_IP = \"YOUR_PC_IP_HERE\"\n\n"
            "To your PC's IP address, e.g.:\nPC_IP = \"192.168.1.100\""
        )
        sys.exit(1)
    
    app = ConnectionWindow()
    app.run()
