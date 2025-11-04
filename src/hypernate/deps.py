import platform  # OS detection.
from .ui import message_box  # UI helper.

def verify_dependencies() -> None:
    missing = []  # Missing package names.  # Start empty.
    try:
        import pystray  # noqa  # Tray library.
    except Exception:
        missing.append("pystray")  # Record missing.
    try:
        import PIL  # noqa  # Pillow imaging.
    except Exception:
        missing.append("Pillow")  # Record missing.
    try:
        import pyautogui  # noqa  # Mouse automation.
    except Exception:
        missing.append("pyautogui")  # Record missing.
    if platform.system() == "Windows":
        try:
            import win32api  # noqa  # Win32 support.
        except Exception:
            missing.append("pywin32")  # Record missing.
    if platform.system() == "Darwin":
        try:
            import AppKit  # noqa  # macOS bridge.
        except Exception:
            missing.append("pyobjc")  # Record missing.
    if missing:
        message_box("Hypernate", f"Missing dependencies: {', '.join(missing)}.\nInstall with: pip install -r requirements.txt", is_error=True)  # Show error.
        raise SystemExit(1)  # Exit early.
