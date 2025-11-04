from pathlib import Path  # Path utilities.
import sys  # Interpreter info.
from typing import List  # Type hints.

def is_frozen() -> bool:
    return getattr(sys, "frozen", False)  # True when running as PyInstaller one-file exe.

def script_dir() -> Path:
    # Directory containing the running file (exe when frozen, this module when not).
    return Path(sys.executable if is_frozen() else __file__).resolve().parent

def _find_project_root(start: Path, max_up: int = 5) -> Path:
    # Walk upward to locate the project root that contains markers like assets/ or hypernate.py.
    cur = start
    for _ in range(max_up):
        if (cur / "assets").exists() or (cur / "hypernate.py").exists() or (cur / "requirements.txt").exists():
            return cur  # Found a likely project root.
        cur = cur.parent
    return start  # Fallback to starting directory.

def resource_roots() -> List[Path]:
    # Order matters: embedded (_MEIPASS) → folder of running file → detected project root → CWD.
    roots: List[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        roots.append(Path(meipass))  # PyInstaller temp extraction dir.
    here = script_dir()
    roots.append(here)  # Where the module/exe lives.
    roots.append(_find_project_root(here))  # Detected project root (where assets/ usually is).
    roots.append(Path.cwd())  # Current working directory.
    # Also search /assets under each root.
    with_assets = []
    for r in roots:
        assets = r / "assets"
        if assets.exists():
            with_assets.append(assets)
    # De-duplicate while preserving order.
    seen = set()
    ordered = []
    for p in [*roots, *with_assets]:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            ordered.append(rp)
    return ordered  # Return all candidate search roots.
