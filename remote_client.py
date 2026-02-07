#!/usr/bin/env python3
"""
Remote Desktop Client
Run this on the PC you want to control from
"""
import socket
import ssl
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import io
import base64
import threading
import time

# Configuration
SERVER_HOST = 'localhost'  # Change to your server's IP or ngrok URL
SERVER_PORT = 5000
AUTH_TOKEN = "your_secure_password_here"  # Must match server's token

class RemoteClient:
    def __init__(self):
        self.socket = None
        self.ssl_context = None
        self.connected = False
        self.screen_label = None
        self.root = None
        
    def connect(self, host, port):
        """Connect to remote server"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Try SSL first
            try:
                # Create SSL context (accept self-signed certs for now)
                self.ssl_context = ssl.create_default_context()
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
                
                # Connect with SSL
                self.socket.connect((host, port))
                self.socket = self.ssl_context.wrap_socket(self.socket, server_hostname=host)
                print("Connected with SSL encryption")
            except Exception as ssl_error:
                # SSL failed, try without SSL (for testing without certificates)
                print(f"SSL connection failed, trying without encryption...")
                self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((host, port))
                print("Connected without SSL (testing mode)")
            
            # Authenticate
            auth_msg = {'token': AUTH_TOKEN}
            self.socket.send(json.dumps(auth_msg).encode('utf-8'))
            
            # Check response
            response = json.loads(self.socket.recv(1024).decode('utf-8'))
            if response.get('status') != 'success':
                raise Exception("Authentication failed")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def request_screen(self):
        """Request screen capture from server"""
        if not self.connected:
            return None
        
        try:
            command = {'type': 'get_screen'}
            self.socket.send(json.dumps(command).encode('utf-8'))
            
            # Receive response - handle large data
            data = b''
            while True:
                chunk = self.socket.recv(65536)
                if not chunk:
                    break
                data += chunk
                # Try to parse - if it works, we have complete data
                try:
                    response = json.loads(data.decode('utf-8'))
                    return response.get('data')
                except json.JSONDecodeError:
                    # Data incomplete, continue receiving
                    continue
                    
        except Exception as e:
            print(f"Error requesting screen: {e}")
            return None
    
    def send_mouse_move(self, x, y):
        """Send mouse move command"""
        if self.connected:
            command = {'type': 'mouse_move', 'x': x, 'y': y}
            try:
                self.socket.send(json.dumps(command).encode('utf-8'))
            except:
                pass
    
    def send_mouse_click(self, x, y, button='left'):
        """Send mouse click command"""
        if self.connected:
            command = {'type': 'mouse_click', 'x': x, 'y': y, 'button': button}
            try:
                self.socket.send(json.dumps(command).encode('utf-8'))
            except:
                pass
    
    def send_key_press(self, key):
        """Send key press command"""
        if self.connected:
            command = {'type': 'key_press', 'key': key}
            try:
                self.socket.send(json.dumps(command).encode('utf-8'))
            except:
                pass

class RemoteDesktopGUI:
    def __init__(self):
        self.client = RemoteClient()
        self.root = tk.Tk()
        self.root.title("Remote Desktop Client")
        self.root.geometry("800x600")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        connection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Connection", menu=connection_menu)
        connection_menu.add_command(label="Connect", command=self.show_connect_dialog)
        connection_menu.add_command(label="Disconnect", command=self.disconnect)
        connection_menu.add_separator()
        connection_menu.add_command(label="Exit", command=self.root.quit)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Screen display
        self.screen_frame = tk.Frame(self.root, bg='black')
        self.screen_frame.pack(fill=tk.BOTH, expand=True)
        
        self.screen_label = tk.Label(self.screen_frame, bg='black')
        self.screen_label.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.screen_label.bind("<Motion>", self.on_mouse_move)
        self.screen_label.bind("<Button-1>", self.on_mouse_click)
        self.screen_label.bind("<Key>", self.on_key_press)
        self.screen_label.focus_set()
        
    def show_connect_dialog(self):
        """Show connection dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connect to Server")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Server IP/Hostname:").pack(pady=5)
        host_entry = tk.Entry(dialog, width=30)
        host_entry.insert(0, SERVER_HOST)
        host_entry.pack()
        
        def do_connect():
            host = host_entry.get()
            if self.client.connect(host, SERVER_PORT):
                self.status_var.set(f"Connected to {host}")
                dialog.destroy()
                self.start_screen_updates()
            else:
                messagebox.showerror("Error", "Failed to connect to server")
        
        tk.Button(dialog, text="Connect", command=do_connect).pack(pady=20)
        
    def disconnect(self):
        """Disconnect from server"""
        self.client.disconnect()
        self.status_var.set("Not connected")
        
    def start_screen_updates(self):
        """Start receiving screen updates"""
        def update_loop():
            while self.client.connected:
                screenshot_data = self.client.request_screen()
                if screenshot_data:
                    self.update_screen(screenshot_data)
                time.sleep(0.1)  # 10 FPS
        
        thread = threading.Thread(target=update_loop)
        thread.daemon = True
        thread.start()
    
    def update_screen(self, screenshot_data):
        """Update the screen display"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(screenshot_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Resize to fit window
            window_width = self.screen_frame.winfo_width()
            window_height = self.screen_frame.winfo_height()
            
            if window_width > 1 and window_height > 1:
                image = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.screen_label.config(image=photo)
            self.screen_label.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Error updating screen: {e}")
    
    def on_mouse_move(self, event):
        """Handle mouse move"""
        if self.client.connected:
            self.client.send_mouse_move(event.x, event.y)
    
    def on_mouse_click(self, event):
        """Handle mouse click"""
        if self.client.connected:
            self.client.send_mouse_click(event.x, event.y)
    
    def on_key_press(self, event):
        """Handle key press"""
        if self.client.connected:
            self.client.send_key_press(event.keysym)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RemoteDesktopGUI()
    app.run()
