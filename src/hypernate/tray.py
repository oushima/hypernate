import os  # OS helpers.
import platform  # OS detection.
import subprocess  # Open file helpers.
from pathlib import Path  # Paths.

from .icon_loader import load_icon_image  # Icon loader.
from .nudge import NudgeWorker  # Worker.
from .ui import message_box  # UI helper.

class TrayApp:
    def __init__(self, app_name: str, interval_seconds: int, start_active: bool, log_path: Path):
        from pystray import Icon, Menu, MenuItem  # Import backend.
        self.Icon = Icon  # Save class.
        self.Menu = Menu  # Save class.
        self.MenuItem = MenuItem  # Save class.
        self.app_name = app_name  # Save name.
        self.icon_img = load_icon_image()  # Load tray icon.
        self.log_path = log_path  # Save log path.
        self.worker = NudgeWorker(interval_seconds)  # Create worker.
        self.worker.set_active(start_active)  # Apply initial state.

        menu = self.Menu(  # Build menu.
            self.MenuItem(f"{self.app_name} On/Off", self._toggle_action, checked=lambda _: self.worker._active),  # Toggle item.
            self.Menu.SEPARATOR,  # Separator.
            self.MenuItem("Open Log", self._open_log),  # Open log.
            self.Menu.SEPARATOR,  # Separator.
            self.MenuItem("Quit", self._quit_action)  # Quit app.
        )

        self.icon = self.Icon(name=self.app_name, title=f"{self.app_name}", icon=self.icon_img, menu=menu)  # Create tray icon.

    def _toggle_action(self, _icon, _item):
        active = self.worker.toggle()  # Flip active state.
        try:
            self.icon.title = f"{self.app_name} ({'On' if active else 'Off'})"  # Update tooltip.
        except Exception:
            pass  # Not critical.

    def _open_log(self, _icon, _item):
        try:
            p = str(self.log_path)  # Path string.
            if platform.system() == "Windows":
                os.startfile(p)  # Open with default app.
            elif platform.system() == "Darwin":
                subprocess.run(["open", p], check=False)  # macOS open.
            else:
                subprocess.run(["xdg-open", p], check=False)  # Linux open.
        except Exception:
            message_box(self.app_name, "Failed to open log file.", is_error=True)  # Show error.

    def _quit_action(self, _icon, _item):
        try:
            self.worker.stop()  # Stop worker.
        finally:
            self.icon.stop()  # Stop tray icon.

    def run(self):
        try:
            self.worker.start()  # Start background worker.
            try:
                self.icon.title = f"{self.app_name} ({'On' if self.worker._active else 'Off'})"  # Initial tooltip.
            except Exception:
                pass  # Ignore tooltip error.
            self.icon.run()  # Enter event loop.
        except Exception as e:
            message_box(self.app_name, f"Tray failed to start: {e}", is_error=True)  # Show error.
