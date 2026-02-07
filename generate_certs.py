#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for secure communication
Run this once before starting the server
"""
import subprocess
import sys
import os

def generate_certs():
    """Generate self-signed SSL certificates"""
    
    # Check if openssl is available
    try:
        subprocess.run(['openssl', 'version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: OpenSSL is not installed or not in PATH")
        print("Please install OpenSSL first:")
        print("  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("  - Linux: sudo apt-get install openssl")
        print("  - macOS: brew install openssl")
        sys.exit(1)
    
    print("Generating SSL certificates...")
    
    # Generate private key
    subprocess.run([
        'openssl', 'genrsa', '-out', 'server.key', '2048'
    ], check=True)
    
    # Generate certificate signing request
    subprocess.run([
        'openssl', 'req', '-new', '-key', 'server.key', 
        '-out', 'server.csr', '-subj', '/CN=RemoteDesktop'
    ], check=True)
    
    # Generate self-signed certificate
    subprocess.run([
        'openssl', 'x509', '-req', '-days', '365', 
        '-in', 'server.csr', '-signkey', 'server.key', 
        '-out', 'server.crt'
    ], check=True)
    
    # Clean up CSR
    os.remove('server.csr')
    
    print("✓ Certificates generated successfully!")
    print("  - server.key (private key)")
    print("  - server.crt (certificate)")
    print("\nIMPORTANT: Keep these files secure. They are needed for encrypted connections.")

if __name__ == "__main__":
    generate_certs()
