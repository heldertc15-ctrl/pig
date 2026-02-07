#!/usr/bin/env python3
"""
Quick test to verify installation and connectivity
"""
import sys
import subprocess

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    try:
        from PIL import Image, ImageGrab
        print("✓ PIL/Pillow installed")
    except ImportError:
        print("✗ PIL/Pillow not found. Run: pip install Pillow")
        return False
    
    try:
        import pyautogui
        print("✓ pyautogui installed")
    except ImportError:
        print("✗ pyautogui not found. Run: pip install pyautogui")
        return False
    
    return True

def test_screen_capture():
    """Test screen capture functionality"""
    print("\nTesting screen capture...")
    
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        print(f"✓ Screen capture works ({screenshot.size[0]}x{screenshot.size[1]})")
        return True
    except Exception as e:
        print(f"✗ Screen capture failed: {e}")
        return False

def test_input_simulation():
    """Test input simulation"""
    print("\nTesting input simulation...")
    
    try:
        import pyautogui
        # Just test if we can get current position (doesn't actually move)
        pos = pyautogui.position()
        print(f"✓ Input simulation works (current mouse: {pos.x}, {pos.y})")
        return True
    except Exception as e:
        print(f"✗ Input simulation failed: {e}")
        return False

def test_certificates():
    """Test if SSL certificates exist"""
    print("\nTesting SSL certificates...")
    
    import os
    if os.path.exists("server.crt") and os.path.exists("server.key"):
        print("✓ SSL certificates found")
        return True
    else:
        print("✗ SSL certificates not found. Run: python generate_certs.py")
        return False

def main():
    print("="*50)
    print("Remote Desktop - Installation Test")
    print("="*50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Screen Capture", test_screen_capture()))
    results.append(("Input Simulation", test_input_simulation()))
    results.append(("SSL Certificates", test_certificates()))
    
    print("\n" + "="*50)
    print("Test Results")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("\n✓ All tests passed! You're ready to use Remote Desktop.")
        print("\nNext steps:")
        print("1. Set your password in remote_server.py and remote_client.py")
        print("2. Run: python remote_server.py  (on the laptop to control)")
        print("3. Run: python remote_client.py  (on the connecting PC)")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
