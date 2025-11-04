from pathlib import Path  # Paths.
import os  # Env overrides.
import platform  # OS detection.
from typing import Optional  # Types.

from .paths import resource_roots  # Resource search roots.

def _win_target_tray_px() -> int:
    # Pick a crisp tray size based on DPI (Windows) or a sane default elsewhere.
    if platform.system() != "Windows":
        return 24  # Default on non-Windows.
    try:
        import ctypes  # DPI query.
        user32 = ctypes.windll.user32
        dpi = 96
        try:
            dpi = user32.GetDpiForSystem()
        except Exception:
            try:
                user32.SetProcessDPIAware()
                hdc = user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) or 96  # LOGPIXELSX.
                user32.ReleaseDC(0, hdc)
            except Exception:
                dpi = 96
        scale = max(1.0, float(dpi) / 96.0)
        target = int(round(16 * scale))
        for s in (16, 20, 24, 32, 40):
            if target <= s:
                return s
        return 32
    except Exception:
        return 24

def _discover_icon_path() -> Optional[Path]:
    # 1) Explicit override via env var.
    override = os.environ.get("HYPERNATE_ICON")
    if override:
        p = Path(override)
        if p.exists():
            return p
    # 2) Search common names across all resource roots (handles _MEIPASS, src/, project root, CWD, /assets).
    preferred = ("hypernate.ico", "hypernate.png", "app.ico", "app.png")
    for root in resource_roots():
        for name in preferred:
            p = root / name
            if p.exists():
                return p
        # Fallback to any .ico / .png in that root.
        any_ico = list(root.glob("*.ico"))
        if any_ico:
            return any_ico[0]
        any_png = list(root.glob("*.png"))
        if any_png:
            return any_png[0]
    return None  # Nothing found.

def load_icon_image():
    # Return a PIL Image for the tray icon. Picks the best ICO frame for DPI; resizes if needed.
    from PIL import Image, ImageDraw
    path = _discover_icon_path()
    target = _win_target_tray_px()
    if path:
        try:
            img = Image.open(path)
            if path.suffix.lower() == ".ico" and getattr(img, "n_frames", 1) > 1:
                # Choose the ICO frame closest to target size for crisp rendering.
                best = None
                best_delta = 1e9
                for i in range(img.n_frames):
                    img.seek(i)
                    w, h = img.size
                    delta = abs(max(w, h) - target)
                    if delta < best_delta:
                        best_delta = delta
                        best = img.copy()
                img = best
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            if max(img.size) != target:
                img = img.resize((target, target), Image.LANCZOS)
            return img
        except Exception:
            pass
    # Embedded fallback: crisp green "H" circle.
    size = target
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((1, 1, size - 2, size - 2), fill=(34, 197, 94, 255), outline=(22, 163, 74, 255), width=max(1, size // 16))
    bar = max(2, size // 6)
    pad = size // 5
    d.rectangle((pad, pad, pad + bar, size - pad), fill=(255, 255, 255, 255))
    d.rectangle((size - pad - bar, pad, size - pad, size - pad), fill=(255, 255, 255, 255))
    d.rectangle((pad, (size // 2) - bar // 2, size - pad, (size // 2) + bar // 2), fill=(255, 255, 255, 255))
    return img
