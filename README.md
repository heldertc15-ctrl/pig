# Remote Desktop Software

A secure remote desktop solution built with Python that avoids antivirus false positives.

## Features

- ✅ Remote screen viewing
- ✅ Remote mouse control
- ✅ Remote keyboard control
- ✅ **Web Dashboard** - Monitor your laptop status from any browser
- ✅ Encrypted connections (SSL/TLS)
- ✅ Authentication required
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ No antivirus false positives
- ✅ Internet connectivity support

## Security Design

This software is designed to avoid triggering antivirus software by:

1. **Visible UI** - Shows a window and system tray icon when running
2. **Explicit consent** - Requires authentication and user confirmation
3. **Standard libraries** - Uses well-known Python packages (PIL, pyautogui)
4. **Encryption** - All traffic is encrypted with SSL/TLS
5. **Proper networking** - Uses standard socket connections with authentication
6. **No persistence** - Doesn't install itself or run automatically

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- OpenSSL (for generating certificates)

### Quick Setup

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Generate SSL certificates:**
   ```bash
   python generate_certs.py
   ```

3. **Set your password:**
   Edit both `remote_server.py` and `remote_client.py` and change:
   ```python
   AUTH_TOKEN = "your_secure_password_here"
   ```
   to your own secure password.

## Usage

### On the laptop to be controlled (Server):

```bash
python remote_server.py
```

You'll see:
- A console window showing connection status
- "Server started" message with the IP and port

### On the connecting PC (Client):

```bash
python remote_client.py
```

1. Click "Connection" → "Connect"
2. Enter the server's IP address:
   - For local network: Use the laptop's local IP (e.g., `192.168.1.100`)
   - For internet: Use ngrok URL or public IP with port forwarding
3. Enter your password when prompted
4. The remote desktop will appear in the window

## Web Dashboard

The server includes a **built-in web dashboard** that lets you monitor your laptop's status from any browser without needing the full client application.

### Accessing the Dashboard

Once the server is running, open your browser and go to:
```
http://localhost:8080
```

Or from another device on your network:
```
http://<laptop-ip>:8080
```

### Dashboard Features

- **Server Status**: Real-time status showing if the server is online and if any clients are connected
- **Connected Clients**: Lists all currently connected remote clients with their connection time
- **Connection History**: Shows recent connection/disconnection events with timestamps
- **Live Preview**: Displays the last captured screenshot from your laptop (auto-refreshes)
- **Auto-refresh**: Dashboard updates every 2 seconds automatically

### Use Cases

The dashboard is perfect for:
- **Quick status checks** - See if your laptop is online without opening the full client
- **Monitoring** - Track who/when connected to your laptop
- **Mobile access** - View status from your phone/tablet browser
- **Debugging** - Check connection history if you're having issues

## Internet Access

To connect over the internet, you have several options:

### Option 1: Ngrok (Easiest)

1. Install ngrok: https://ngrok.com/download
2. Run on the server laptop:
   ```bash
   ngrok tcp 5000
   ```
3. Copy the forwarding URL (e.g., `tcp://0.tcp.ngrok.io:12345`)
4. Enter this URL in the client

### Option 2: Port Forwarding

1. Configure your router to forward port 5000 to your laptop
2. Find your public IP: https://whatismyipaddress.com
3. Enter the public IP in the client

### Option 3: VPN

Use a VPN service (like Tailscale, ZeroTier, or your own VPN) to create a secure tunnel between devices.

## File Structure

```
.
├── remote_server.py      # Server application (run on controlled laptop)
├── remote_client.py      # Client application (run on connecting PC)
├── windows_impl.py       # Windows-specific screen/input handling
├── generate_certs.py     # SSL certificate generator
├── setup.py              # Setup and dependency installer
└── README.md             # This file
```

## Customization

### Change port:
Edit `remote_server.py` and `remote_client.py`:
```python
SERVER_PORT = 5000  # Change to your preferred port
```

### Adjust screen quality:
Edit `windows_impl.py`:
```python
screenshot.save(buffer, format='JPEG', quality=70)  # 1-100
```

### Add more security:
- Use stronger authentication (replace simple token with JWT)
- Add IP whitelist
- Implement rate limiting
- Add connection timeout

## Troubleshooting

### "Connection refused"
- Check firewall settings (allow port 5000)
- Verify the server is running
- Check IP address is correct

### "Authentication failed"
- Verify passwords match in both files
- Check for typos

### Slow performance
- Reduce screen quality in `windows_impl.py`
- Decrease update frequency in `remote_client.py`
- Use a faster network connection

### Antivirus warnings
If you still get warnings:
1. Add an exception for Python/python.exe
2. Run from source code (not compiled)
3. Consider using a different port (some AVs flag 5000)

## Security Considerations

⚠️ **Important:** This is a basic implementation. For production use:

1. Use proper SSL certificates (not self-signed)
2. Implement stronger authentication
3. Add session management
4. Log all connections
5. Use a VPN for internet access
6. Keep the software updated
7. Don't expose directly to the internet without additional security

## License

This project is for educational and personal use. Use responsibly and only on systems you own or have permission to access.

## Disclaimer

This software is provided as-is. The authors are not responsible for misuse or damage caused by this software. Always use strong passwords and secure connections.
