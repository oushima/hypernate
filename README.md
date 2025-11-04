# Hypernate

Hypernate is a tiny, cross‑platform tray app that **keeps your computer awake** by micro‑nudging the mouse **1 pixel every N seconds** (default: 30). It sits quietly in your system tray/menu bar, has a single **On/Off** toggle, enforces a **single instance**, and writes a small rotating log.

## What it solves
- Prevents sleep/idle during long calls, demos, reads, or downloads.
- Helps avoid “Away/Idle” presence in collaboration tools.
- Non‑intrusive: the cursor returns to the exact position immediately.

---

## Features
- ✅ System tray app (Windows / macOS / Linux with tray support).
- ✅ **Single‑instance** guard (mutex/file‑lock) — no duplicate icons.
- ✅ Tray menu: `Hypernate On/Off`, `Open Log`, `Quit`.
- ✅ DPI‑aware **custom icon** loading from multiple locations (works in PyInstaller bundles).
- ✅ Configurable interval (`--interval 15`) and start disabled (`--start-off`).
- ✅ Optional **one‑file build** via PyInstaller (`--build`).
- ✅ Rotating log: `hypernate.log` next to the running file.

---

## Project layout
```
Hypernate/
├─ assets/
│  └─ hypernate.ico               # Your tray/exe icon (recommended for Windows).
├─ src/
│  └─ hypernate/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ main.py                  # CLI entry, logging, build command.
│     ├─ tray.py                  # Tray UI & menu.
│     ├─ nudge.py                 # Mouse nudge worker.
│     ├─ icon_loader.py           # Smart icon discovery & DPI-aware loading.
│     ├─ singleton.py             # Single-instance guard.
│     ├─ ui.py                    # Native message boxes / fallbacks.
│     └─ paths.py                 # Safe paths for script/exe + PyInstaller.
├─ hypernate.py                   # Root launcher (run this).
├─ requirements.txt               # Project dependencies (platform-aware).
└─ README.md
```

---

## Requirements
Install with `pip` (venv recommended but optional):

```bash
python -m pip install -r requirements.txt
# or on macOS/Linux if python points to 2.x:
python3 -m pip install -r requirements.txt
```

> macOS will prompt for **Accessibility** permission on first run so the app can move the mouse.  
> Linux requires a desktop environment with a **system tray/appindicator**.

---

## Run
From the project root:

```bash
python hypernate.py
# macOS/Linux alternative:
python3 hypernate.py
```

The tray/menu‑bar icon appears. Click it for **On/Off**, **Open Log**, and **Quit**.

---

## CLI options
Change interval (seconds):
```bash
python hypernate.py --interval 15
```

Start disabled (toggle on from the tray later):
```bash
python hypernate.py --start-off
```

Force a specific icon path for this run:
```bash
# Windows
set HYPERNATE_ICON=assets\hypernate.ico && python hypernate.py

# macOS/Linux
HYPERNATE_ICON=assets/hypernate.ico python3 hypernate.py
```

---

## Build a one‑file app
Create a single distributable (EXE on Windows, .app on macOS, ELF on Linux) in `./dist`:

```bash
python -m src.hypernate.main --build
```

**Outputs**
- Windows: `dist/Hypernate.exe`
- macOS: `dist/Hypernate.app`
- Linux: `dist/Hypernate`

> The build step sets the application icon and **also bundles** the icon as data so the tray can find it at runtime inside the one‑file bundle.

---

## Icon notes
- Put your icon at **`assets/hypernate.ico`** (best for Windows); `.png` also works.
- The loader searches (in order): PyInstaller bundle (`_MEIPASS`), the module/exe folder, the project root, your current working directory, and each `/assets` under those folders.
- Multi‑size `.ico` files are supported; the loader picks the best frame for your DPI for a crisp tray icon.

---

## Logging
- A rotating log named **`hypernate.log`** is created next to the running file.
- Open it directly via the tray menu (**Open Log**).

---

## Troubleshooting
**Tray icon not visible**
- Windows: check the hidden/overflow tray area.
- macOS: allow **Accessibility** in System Settings → Privacy & Security.
- Linux: ensure your DE has a tray/appindicator (some Wayland sessions need an extension).

**Icon shows as generic**
- Ensure `assets/hypernate.ico` exists **before** building.
- Rebuild with `python -m src.hypernate.main --build` to embed the icon again.

**Multiple icons start showing**
- The app enforces **single instance**. If you killed it “hard” on macOS/Linux and a lock lingers, close all instances and remove `/tmp/hypernate.lock` (rare).

**Missing dependencies**
- Run `python -m pip install -r requirements.txt` again (inside your venv if you use one).

---

## Security & etiquette
Hypernate prevents idle/sleep by simulating minimal mouse movement. Use it responsibly and in line with your organization’s policies.

---

## License
MIT
