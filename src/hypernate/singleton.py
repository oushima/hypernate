import platform  # OS detection.
import tempfile  # Temp directory.
import atexit  # Cleanup hooks.
from pathlib import Path  # Paths.

# Windows.
_mutex_handle = None  # Global mutex handle.
# POSIX.
_lock_file = None  # Global file lock stream.

def enforce_single_instance(app_slug: str, app_name: str) -> None:
    system = platform.system()  # Current OS.  # Detect system.
    if system == "Windows":
        import ctypes  # Win32 API.
        from ctypes import wintypes  # Types.
        global _mutex_handle  # Use global.
        name = f"Global\\{app_slug}_SingleInstance_Mutex"  # Global mutex name.
        ctypes.windll.kernel32.SetLastError(0)  # Reset last error.
        _mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, True, wintypes.LPCWSTR(name))  # Create mutex.
        last_err = ctypes.windll.kernel32.GetLastError()  # Get result.
        if last_err == 183 or _mutex_handle == 0:  # Already exists.
            from .ui import message_box  # Import lazily.
            message_box(app_name, f"{app_name} is already running in the system tray.")  # Inform user.
            raise SystemExit(0)  # Exit second instance.
        @atexit.register
        def _release_mutex():  # Cleanup on exit.
            try:
                ctypes.windll.kernel32.ReleaseMutex(_mutex_handle)  # Release mutex.
                ctypes.windll.kernel32.CloseHandle(_mutex_handle)  # Close handle.
            except Exception:
                pass  # Ignore cleanup errors.
    else:
        import fcntl  # File locks.
        global _lock_file  # Use global.
        lock_path = Path(tempfile.gettempdir()) / f"{app_slug}.lock"  # Lockfile path.
        _lock_file = open(lock_path, "w")  # Open lockfile.
        try:
            fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try non-blocking lock.
        except BlockingIOError:
            from .ui import message_box  # Import lazily.
            message_box(app_name, f"{app_name} is already running.")  # Inform user.
            raise SystemExit(0)  # Exit second instance.
        @atexit.register
        def _release_lock():  # Cleanup on exit.
            try:
                fcntl.flock(_lock_file.fileno(), fcntl.LOCK_UN)  # Unlock.
                _lock_file.close()  # Close file.
                try:
                    lock_path.unlink()  # Remove lock file.
                except Exception:
                    pass  # Ignore delete error.
            except Exception:
                pass  # Ignore unlock error.
