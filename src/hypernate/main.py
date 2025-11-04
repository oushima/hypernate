import argparse  # CLI parsing.
import logging  # Logging.
from logging.handlers import RotatingFileHandler  # Rotating logs.
from pathlib import Path  # Paths

from .deps import verify_dependencies  # Dependency check.
from .singleton import enforce_single_instance  # Single instance.
from .tray import TrayApp  # Tray UI.
from .paths import script_dir  # Paths.

APP_NAME = "Hypernate"  # Display name.
APP_SLUG = "hypernate"  # Slug.
DEFAULT_INTERVAL_SECONDS = 30  # Default interval.
LOG_FILE_NAME = f"{APP_SLUG}.log"  # Log name.

def setup_logging() -> Path:
    log_path = script_dir() / LOG_FILE_NAME  # Log file path.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_path, maxBytes=512 * 1024, backupCount=2)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
    logging.info(f"{APP_NAME} starting up.")
    return log_path

def build_standalone() -> None:
    # Build an EXE/.app/ELF and also bundle the icon so the tray finds it at runtime.
    import shutil  # File ops.
    import platform  # OS detection.
    from .icon_loader import _discover_icon_path  # Icon finder.
    try:
        import PyInstaller.__main__ as pyi_main  # Build engine.
    except Exception:
        print("PyInstaller is not installed. Run: pip install pyinstaller")  # User hint.
        raise SystemExit(1)
    # Use the top-level launcher so people can run Hypernate.exe directly.
    src = Path(__file__).resolve().parent.parent.parent / "hypernate.py"
    dist = script_dir() / "dist"
    build = script_dir() / "build"
    spec = script_dir() / f"{APP_SLUG}.spec"

    for p in (dist, build, spec):
        try:
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
        except Exception:
            pass

    icon_hint = _discover_icon_path()  # Finds assets/hypernate.ico, _MEIPASS copy, or CWD.
    icon_arg = ["--icon", str(icon_hint)] if icon_hint else []

    sys_name = platform.system()
    console_flags = ["--noconsole"] if sys_name in ("Windows", "Darwin") else []
    mac_flags = ["--windowed"] if sys_name == "Darwin" else []

    # Bundle the icon as data so the tray can discover it at runtime inside _MEIPASS.
    add_data = []
    if icon_hint:
        sep = ";" if sys_name == "Windows" else ":"
        add_data = ["--add-data", f"{icon_hint}{sep}."]

    args = [
        "--name", APP_NAME,
        "--onefile",
        "--clean",
        "--distpath", str(dist),
        "--workpath", str(build),
        *console_flags,
        *mac_flags,
        *icon_arg,
        *add_data,
        str(src)
    ]
    pyi_main.run(args)

def parse_args():
    ap = argparse.ArgumentParser(prog=APP_SLUG, add_help=True)
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help="Nudge interval in seconds.")
    ap.add_argument("--start-off", action="store_true", help="Start with Hypernate disabled.")
    ap.add_argument("--build", action="store_true", help="Build a standalone app (CLI only).")
    return ap.parse_args()

def main():
    log_path = setup_logging()
    verify_dependencies()
    enforce_single_instance(APP_SLUG, APP_NAME)

    args = parse_args()
    if args.build:
        build_standalone()
        return

    app = TrayApp(app_name=APP_NAME, interval_seconds=args.interval, start_active=not args.start_off, log_path=log_path)
    app.run()

if __name__ == "__main__":
    main()
