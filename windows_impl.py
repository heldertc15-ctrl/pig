#!/usr/bin/env python3
"""
Platform-specific implementations for Windows
This module provides screen capture and input simulation for Windows
"""
import base64
from io import BytesIO
from PIL import Image

def get_screen_capture():
    """Capture screen on Windows"""
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        
        # Resize to reduce data size (max 1280x720)
        max_width = 1280
        max_height = 720
        width, height = screenshot.size
        
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
            screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to base64 with lower quality for faster transfer
        buffer = BytesIO()
        screenshot.save(buffer, format='JPEG', quality=50, optimize=True)
        screenshot_bytes = buffer.getvalue()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        print(f"Screenshot captured: {len(screenshot_b64)} bytes")
        return screenshot_b64
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
