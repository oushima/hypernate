import time  # Sleep utility.
import threading  # Background thread.

class NudgeWorker:
    def __init__(self, interval_seconds: int):
        self.interval = max(5, int(interval_seconds))  # Enforce sane lower bound.
        self._active = True  # Start active by default.
        self._stop_evt = threading.Event()  # Stop flag.
        self._thread = threading.Thread(target=self._run, name="hypernate-worker", daemon=True)  # Daemon thread.

    def start(self) -> None:
        self._thread.start()  # Launch worker thread.

    def stop(self) -> None:
        self._stop_evt.set()  # Signal stop.
        try:
            self._thread.join(timeout=2.0)  # Wait briefly.
        except Exception:
            pass  # Ignore join errors.

    def set_active(self, active: bool) -> None:
        self._active = active  # Set state.

    def toggle(self) -> bool:
        self._active = not self._active  # Flip state.
        return self._active  # Return new state.

    def _run(self) -> None:
        import pyautogui  # Lazy import for speed.
        pyautogui.FAILSAFE = False  # Ignore screen corner failsafe.
        while not self._stop_evt.is_set():  # Loop until stopped.
            try:
                if self._active:  # Only when active.
                    x, y = pyautogui.position()  # Current position.
                    pyautogui.moveRel(1, 0, duration=0)  # Nudge right.
                    pyautogui.moveTo(x, y, duration=0)  # Move back.
            except Exception:
                pass  # Ignore transient errors.
            for _ in range(self.interval):  # Sleep in 1s chunks.
                if self._stop_evt.is_set():  # Early exit.
                    break  # Break loop.
                time.sleep(1)  # Sleep one second.
