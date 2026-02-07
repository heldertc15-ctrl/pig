# Remote Desktop Software

A secure remote desktop solution with reverse connection architecture. Your PC hosts the dashboard, and your laptop connects to it.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  YOUR PC (Work From Here)                               │
│  ┌─────────────────────────────┐                        │
│  │  dashboard_server.py        │                        │
│  │  - Listens for connections  │                        │
│  │  - Hosts web dashboard      │                        │
│  │  - Shows connected laptops  │                        │
│  └─────────────────────────────┘                        │
│  Dashboard URL: http://localhost:8080                   │
└─────────────────────────────────────────────────────────┘
                              ▲
                              │ Laptop connects TO PC
                              │
┌─────────────────────────────────────────────────────────┐
│  LAPTOP (Remote Device)                                 │
│  ┌─────────────────────────────┐                        │
│  │  laptop_client.py           │                        │
│  │  - Connects to your PC      │                        │
│  │  - Sends screenshots        │                        │
│  │  - Works from anywhere      │                        │
│  └─────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## How It Works

1. **PC** runs `dashboard_server.py` - waits for laptop to connect
2. **Laptop** runs `laptop_client.py` - connects TO your PC
3. **Dashboard** on PC shows "MyLaptop CONNECTED!"
4. Laptop sends screenshots every 2 seconds
5. View laptop screen on PC dashboard

## Files

- **`dashboard_server.py`** - Run on PC, hosts dashboard and waits for connections
- **`laptop_client.py`** - Run on laptop, connects to PC and sends screenshots
- **`remote_client.py`** - Old file (not used anymore)
- **`remote_server.py`** - Old file (not used anymore)

## Installation

### Prerequisites

- Python 3.7+
- pip
- Both computers on same network (or PC has public IP/ngrok)

### Setup

1. **Install dependencies on BOTH computers:**
   ```bash
   pip install Pillow pyautogui
   ```

2. **Clone repo on BOTH computers:**
   ```bash
   git clone https://github.com/heldertc15-ctrl/pig.git
   cd pig
   ```

## Usage

### Step 1: Get Your PC's IP Address

On your **PC**, run:
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100` or `10.0.0.177`)

### Step 2: Configure the Laptop

On the **LAPTOP**, edit `laptop_client.py`:
```python
PC_IP = "YOUR_PC_IP_HERE"  # e.g., "192.168.1.100"
AUTH_TOKEN = "your_secure_password_here"
LAPTOP_ID = "MyLaptop"  # Name shown on dashboard
```

### Step 3: Configure the PC

On your **PC**, edit `dashboard_server.py`:
```python
AUTH_TOKEN = "your_secure_password_here"  # Same as laptop!
```

### Step 4: Start the Dashboard (on PC)

```bash
python dashboard_server.py
```

You'll see:
```
==================================================
🖥️ Connection Listener Started
==================================================
Listening on: 0.0.0.0:5000
Dashboard: http://localhost:8080
Waiting for laptops to connect...
==================================================
```

**Open browser on PC and go to:** `http://localhost:8080`

### Step 5: Start the Laptop Client

On the **LAPTOP**:
```bash
python laptop_client.py
```

You'll see:
```
==================================================
🖥️ Remote Desktop - Laptop Client
==================================================
Laptop ID: MyLaptop
PC Address: 192.168.1.100:5000
Update interval: 2s
==================================================

Starting... Press Ctrl+C to stop

Connecting to PC at 192.168.1.100:5000...
✓ Connected to PC! Authenticated as: MyLaptop
📸 Screenshot sent (45231 bytes)
📸 Screenshot sent (44892 bytes)
```

### Step 6: View on Dashboard

On your PC's browser, you'll see:
- ✅ "MyLaptop CONNECTED!"
- Live screenshots updating every 2 seconds
- Connection history
- Laptop IP address

## For Internet Access

If laptop is not on same network as PC:

### Option 1: Ngrok (Recommended)

On your **PC**:
```bash
# Install ngrok first from https://ngrok.com
ngrok tcp 5000
```

Copy the forwarding URL (e.g., `tcp://0.tcp.ngrok.io:12345`)

On **LAPTOP**, edit `laptop_client.py`:
```python
PC_IP = "0.tcp.ngrok.io"
PC_PORT = 12345  # Port from ngrok
```

### Option 2: Port Forwarding

1. Forward port 5000 on your router to your PC
2. Use your public IP in laptop_client.py

## Troubleshooting

### "Connection refused"
- Check PC's IP address (may have changed)
- Disable Windows Firewall temporarily
- Ensure both on same network

### "Authentication failed"
- Check passwords match in both files
- Check for typos

### Dashboard shows offline
- Refresh browser (Ctrl+R)
- Check laptop client is running
- Check laptop can ping PC: `ping PC_IP`

### No screenshots
- Check laptop has permissions to capture screen
- Try running as Administrator on laptop

## Security

- Change default password!
- Use strong password (16+ characters)
- For internet, use VPN or ngrok
- Don't expose PC directly to internet without firewall

## Dashboard Features

- **Real-time status**: Shows when laptop connects/disconnects
- **Live screenshots**: Auto-refresh every 2 seconds
- **Connection history**: Track connect/disconnect events
- **Multiple laptops**: Can connect multiple devices (each needs unique LAPTOP_ID)

## License

For personal use only. Use responsibly.
