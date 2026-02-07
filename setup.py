#!/usr/bin/env python3
"""
Simple setup script for Remote Desktop
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    
    packages = [
        'Pillow',      # Image handling
        'pyautogui',   # Input simulation
        'pyngrok',     # For internet tunneling (optional)
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
    
    print("✓ All packages installed!")

def main():
    print("="*50)
    print("Remote Desktop Setup")
    print("="*50)
    print()
    
    # Install requirements
    install_requirements()
    
    # Generate certificates
    print("\nGenerating SSL certificates...")
    subprocess.run([sys.executable, 'generate_certs.py'], check=True)
    
    print("\n" + "="*50)
    print("Setup complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit remote_server.py and remote_client.py")
    print("   Change AUTH_TOKEN to a secure password")
    print("2. On the laptop to control:")
    print("   python remote_server.py")
    print("3. On the connecting PC:")
    print("   python remote_client.py")
    print("4. Enter the laptop's IP address to connect")
    print("\nFor internet access, consider using ngrok:")
    print("   ngrok tcp 5000")
    print("   Then use the ngrok URL in the client")

if __name__ == "__main__":
    main()
