# Simple 2-Computer Remote Desktop

For accessing 1 computer (Computer 2) from your PC.

## Files

- **`pc_dashboard.py`** - Run on your PC (waits for connection)
- **`computer2_client.py`** - Run on Computer 2 (connects to PC)

## How It Works

```
┌─────────────────────────────────────┐
│  YOUR PC                            │
│  Run: python pc_dashboard.py        │
│  Dashboard: http://localhost:8080   │
└─────────────────────────────────────┘
              ▲
              │ Computer 2 connects here
              │
┌─────────────────────────────────────┐
│  COMPUTER 2                         │
│  Run: python computer2_client.py    │
│  OR: computer2_client.exe           │
│  Shows window: "Remote Desktop"     │
└─────────────────────────────────────┘
```

## Quick Setup

### 1. Get Your PC's IP
On your PC, run:
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100`)

### 2. Configure Computer 2 Client
Edit `computer2_client.py` and change:
```python
PC_IP = "192.168.1.100"  # Your PC's IP
AUTH_TOKEN = "your_secure_password"  # Set a password
COMPUTER_NAME = "Computer2"  # Name shown on dashboard
```

### 3. Configure PC Dashboard
Edit `pc_dashboard.py` and set the same password:
```python
AUTH_TOKEN = "your_secure_password"
```

## Usage

### On Your PC:
```bash
python pc_dashboard.py
```
Then open browser: http://localhost:8080

You'll see: "Waiting for Computer 2 to connect..."

### On Computer 2:
```bash
python computer2_client.py
```

A window opens showing:
- Computer name
- Target PC IP
- "Connect" button

**Click "Connect"** → Dashboard shows "✓ Computer2 CONNECTED!"

Screenshots stream automatically (updates every second).

---

## Creating .exe File (Optional)

To make Computer 2 run without Python installed:

### Install PyInstaller:
```bash
pip install pyinstaller
```

### Create the .exe:
```bash
pyinstaller --onefile --windowed --add-data "computer2_client.py;." computer2_client.py
```

Or create a spec file for more control:

**computer2_client.spec:**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['computer2_client.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PIL', 'PIL.ImageGrab'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RemoteDesktop-Computer2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window, just GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Then build:
```bash
pyinstaller computer2_client.spec
```

The .exe will be in `dist/RemoteDesktop-Computer2.exe`

### Important Notes:

**Before distributing the .exe:**
1. Edit `computer2_client.py` and set the correct PC_IP
2. Set a strong AUTH_TOKEN
3. Change COMPUTER_NAME if needed
4. Then create the .exe

**The .exe will:**
- ✅ Show a visible window (not hidden)
- ✅ Show computer name and target IP
- ✅ Require clicking "Connect" button
- ✅ Show "Connected" status
- ✅ Stream screen to your PC

**User on Computer 2 sees:**
- Window titled "Remote Desktop - Computer2"
- Status: "Ready to connect..."
- Button: "Connect"
- When connected: "✓ Connected! Streaming screen..."

---

## For Internet Access

If Computer 2 is not on same network:

### Option 1: Ngrok (Easiest)
On your PC:
```bash
ngrok tcp 5000
```
Copy the URL (e.g., `tcp://0.tcp.ngrok.io:12345`)

In `computer2_client.py`:
```python
PC_IP = "0.tcp.ngrok.io"
PC_PORT = 12345
```

### Option 2: Port Forwarding
1. Forward port 5000 on your router to your PC
2. Use your public IP in Computer 2's config

---

## Troubleshooting

### "Configuration Error" popup
Edit `computer2_client.py` and change:
```python
PC_IP = "YOUR_PC_IP_HERE"
```
to your actual PC IP.

### "Connection failed"
- Check Windows Firewall (allow port 5000)
- Verify IP addresses
- Check both computers on same network

### No screenshots showing
- Check if Computer 2 shows "Connected"
- Refresh browser (Ctrl+R)
- Check browser console for errors (F12)

### Antivirus warnings
- The .exe may trigger Windows Defender
- Add exception if you trust it
- Or run from Python source instead

---

## Security Tips

1. **Use strong password** (20+ random characters)
2. **Don't share the .exe** - anyone with it can connect
3. **Use VPN for internet** instead of exposing ports
4. **Monitor connections** - dashboard shows who connected
5. **Disable when not needed** - close pc_dashboard.py

---

## Dashboard Features

- ✓ Shows "COMPUTER CONNECTED!" notification
- ✓ Live screenshot streaming
- ✓ Connection history
- ✓ Auto-refresh every second
- ✓ Works in any browser

## Multiple Computers

You can connect multiple computers! Just:
1. Give each a unique `COMPUTER_NAME`
2. Run `computer2_client.py` on each
3. All appear on the same dashboard

Example:
- Computer 1: `COMPUTER_NAME = "Server-Room-1"`
- Computer 2: `COMPUTER_NAME = "Office-PC"`
- Computer 3: `COMPUTER_NAME = "Laptop-Kitchen"`

All connect to your PC and show on dashboard!
