#!/usr/bin/env python3
"""
Build script to create .exe for Computer 2
Auto-configures settings - just run and go!
"""
import subprocess
import sys
import os
import socket
import random
import string

def get_pc_ip():
    """Auto-detect PC's IP address"""
    try:
        # Connect to a public DNS to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Fallback
        return socket.gethostbyname(socket.gethostname())

def generate_password():
    """Generate a random password"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(16))

def configure_client(pc_ip, password):
    """Auto-configure computer2_client.py"""
    print("\n📝 Auto-configuring settings...")
    
    # Read current file
    with open('computer2_client.py', 'r') as f:
        content = f.read()
    
    # Replace settings
    content = content.replace(
        'PC_IP = "10.0.0.177"  # <-- EDIT THIS: Your PC\'s IP address',
        f'PC_IP = "{pc_ip}"  # Auto-detected'
    )
    content = content.replace(
        'AUTH_TOKEN = "MySecretPassword123"  # <-- EDIT THIS: Must match PC\'s password',
        f'AUTH_TOKEN = "{password}"  # Auto-generated'
    )
    content = content.replace(
        'COMPUTER_NAME = "Computer2"  # <-- EDIT THIS: Name shown on dashboard',
        'COMPUTER_NAME = "RemotePC"  # Auto-set'
    )
    
    # Write back
    with open('computer2_client.py', 'w') as f:
        f.write(content)
    
    print(f"  ✓ PC IP: {pc_ip}")
    print(f"  ✓ Password: {password}")
    print(f"  ✓ Computer Name: RemotePC")

def update_dashboard_password(password):
    """Update dashboard with same password"""
    with open('pc_dashboard.py', 'r') as f:
        content = f.read()
    
    # Find and replace the auth token
    if 'AUTH_TOKEN = "' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('AUTH_TOKEN = "') and 'your_secure_password' not in line.lower():
                lines[i] = f'AUTH_TOKEN = "{password}"  # Auto-generated (must match client)'
                break
        content = '\n'.join(lines)
        
        with open('pc_dashboard.py', 'w') as f:
            f.write(content)
        print("  ✓ Dashboard password updated")

def check_pyinstaller():
    """Check if pyinstaller is installed"""
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                      capture_output=True, check=True)
        return True
    except:
        return False

def install_pyinstaller():
    """Install pyinstaller"""
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    print("✓ PyInstaller installed")

def build_exe():
    """Build the executable"""
    print("\n" + "="*60)
    print("🔨 Building .exe for Computer 2")
    print("="*60)
    
    # Auto-configure
    pc_ip = get_pc_ip()
    password = generate_password()
    configure_client(pc_ip, password)
    update_dashboard_password(password)
    
    print("\n🔨 Building .exe...")
    print("(This may take 2-3 minutes)\n")
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',              # Single .exe file
        '--windowed',             # No console window
        '--name', 'RemoteDesktop-Connect',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL.ImageGrab',
        '--hidden-import', 'PIL.Image',
        '--clean',                # Clean build
        'computer2_client.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*60)
        print("✅ BUILD SUCCESSFUL!")
        print("="*60)
        print("\n📦 Your .exe is ready:")
        exe_path = os.path.join('dist', 'RemoteDesktop-Connect.exe')
        print(f"   📁 {exe_path}")
        print("\n📋 Setup Instructions:")
        print("   1️⃣  On your PC, run: python pc_dashboard.py")
        print("   2️⃣  Open browser: http://localhost:8080")
        print("   3️⃣  Copy RemoteDesktop-Connect.exe to Computer 2")
        print("   4️⃣  On Computer 2, double-click the .exe")
        print("   5️⃣  Watch dashboard - it will show 'RemotePC CONNECTED!'")
        print("\n⚙️  Configuration:")
        print(f"   🖥️  Your PC IP: {pc_ip}")
        print(f"   🔑 Password: {password}")
        print("\n💡 The .exe will auto-connect when opened!")
        print("="*60)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False

def main():
    print("="*60)
    print("🚀 Remote Desktop - Auto Build Tool")
    print("="*60)
    print("\n✨ This will:")
    print("   • Auto-detect your PC's IP")
    print("   • Generate a secure password")
    print("   • Configure all settings")
    print("   • Build the .exe file")
    print("   • Ready to transfer to Computer 2")
    print()
    
    input("Press Enter to start building...")
    
    # Check/install pyinstaller
    if not check_pyinstaller():
        install_pyinstaller()
    else:
        print("✓ PyInstaller already installed")
    
    # Build
    if build_exe():
        print("\n✨ Done! Press Enter to exit...")
        input()
    else:
        print("\n❌ Build failed. Press Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()
