#!/usr/bin/env python3
"""
Build script to create .exe for Computer 2
Run this on your PC after configuring computer2_client.py
"""
import subprocess
import sys
import os

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
    print("Building .exe for Computer 2")
    print("="*60)
    
    # Check if computer2_client.py is configured
    with open('computer2_client.py', 'r') as f:
        content = f.read()
        if 'YOUR_PC_IP_HERE' in content:
            print("\n✗ ERROR: Please configure computer2_client.py first!")
            print("\nEdit these lines in computer2_client.py:")
            print('  PC_IP = "10.0.0.177"          # <-- Your PC IP')
            print('  AUTH_TOKEN = "MySecretPassword" # <-- Your password')
            print('  COMPUTER_NAME = "Computer2"     # <-- Computer name')
            print("\nThen run this script again.")
            return False
    
    print("\n✓ Configuration looks good")
    print("\nBuilding .exe...")
    print("(This may take a few minutes)\n")
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',              # Single .exe file
        '--windowed',             # No console window
        '--name', 'RemoteDesktop-Computer2',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL.ImageGrab',
        '--hidden-import', 'PIL.Image',
        'computer2_client.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*60)
        print("✓ BUILD SUCCESSFUL!")
        print("="*60)
        print("\nYour .exe is ready:")
        exe_path = os.path.join('dist', 'RemoteDesktop-Computer2.exe')
        print(f"  {exe_path}")
        print("\nNext steps:")
        print("  1. Copy this .exe to Computer 2")
        print("  2. On your PC, run: python pc_dashboard.py")
        print("  3. On Computer 2, double-click the .exe")
        print("  4. The .exe will auto-connect to your PC!")
        print("\n" + "="*60)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False

def main():
    print("="*60)
    print("Remote Desktop - Build .exe Tool")
    print("="*60)
    
    # Check/install pyinstaller
    if not check_pyinstaller():
        install_pyinstaller()
    else:
        print("✓ PyInstaller already installed")
    
    # Build
    if build_exe():
        print("\nPress Enter to exit...")
        input()
    else:
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()
