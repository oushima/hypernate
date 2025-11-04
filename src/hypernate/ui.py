import platform  # OS detection.
import subprocess  # Spawn helpers.
import sys  # IO fallback.

def message_box(title: str, text: str, is_error: bool = False) -> None:
    system = platform.system()  # Current OS.  # Detect system.
    try:
        if system == "Windows":
            import ctypes  # Win32 API.
            MB_ICON = 0x10 if is_error else 0x40  # Error or info icon.  # Icon flag.
            ctypes.windll.user32.MessageBoxW(0, text, title, MB_ICON | 0x00001000)  # Show message box.
            return  # Done.
        elif system == "Darwin":
            osa = f'display alert "{title}" message "{text.replace(chr(34), chr(39))}" as {"critical" if is_error else "informational"}'  # AppleScript command.
            subprocess.run(["osascript", "-e", osa], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Show alert.
            return  # Done.
        elif system == "Linux":
            subprocess.run(["notify-send", "-i", "dialog-information", title, text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Desktop notify.
            return  # Done.
    except Exception:
        pass  # Fall through to print.  # Graceful fallback.
    print(f"[{title}] {text}", file=sys.stderr if is_error else sys.stdout)  # Console fallback.
