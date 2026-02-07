#!/usr/bin/env python3
"""
Platform-specific implementations for Windows
This module provides screen capture and input simulation for Windows
"""
import base64
from io import BytesIO

def get_screen_capture():
    """Capture screen on Windows"""
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        
        # Convert to base64
        buffer = BytesIO()
        screenshot.save(buffer, format='JPEG', quality=70)
        screenshot_bytes = buffer.getvalue()
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    except Exception as e:
        print(f"Screen capture error: {e}")
        return None

def move_mouse(x, y):
    """Move mouse to position on Windows"""
    try:
        import pyautogui
        pyautogui.moveTo(x, y)
    except Exception as e:
        print(f"Mouse move error: {e}")

def mouse_click(x, y, button='left'):
    """Simulate mouse click on Windows"""
    try:
        import pyautogui
        pyautogui.click(x, y, button=button)
    except Exception as e:
        print(f"Mouse click error: {e}")

def press_key(key):
    """Simulate key press on Windows"""
    try:
        import pyautogui
        pyautogui.press(key)
    except Exception as e:
        print(f"Key press error: {e}")
