"""System tray entry point for Workflow Link Organizer.

Runs the Waitress server in a daemon thread while pystray shows a system-tray
icon and owns the Windows message loop on the main thread. This is the normal
launch path (started by Start.bat); no console window appears.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

from wlo.config import APP_NAME, HOST, PORT


def _make_icon(size: int = 64) -> Image.Image:
    # RGB (solid background); RGBA transparent backgrounds cause silent HICON
    # creation failures on some Windows 11 pystray setups.
    img = Image.new("RGB", (size, size), (15, 30, 60))
    d = ImageDraw.Draw(img)
    m, w = size // 6, max(2, size // 12)
    for y in (size // 3, size // 2, 2 * size // 3):
        d.line([(m, y), (size - m, y)], fill=(80, 160, 255), width=w)
    return img


def _serve() -> None:
    from wlo.app import create_app
    from waitress import serve
    os.environ.setdefault("WLO_DEV", "0")
    app = create_app()
    serve(app, host=HOST, port=PORT, threads=8, channel_timeout=600)


class TrayApp:

    def __init__(self) -> None:
        self._restarting = False

    def _open(self, icon, item) -> None:
        import webbrowser
        webbrowser.open(f"http://{HOST}:{PORT}/")

    def _restart(self, icon, item) -> None:
        self._restarting = True
        icon.stop()

    def _quit(self, icon, item) -> None:
        icon.stop()

    def run(self) -> None:
        threading.Thread(target=_serve, daemon=True, name="wlo-waitress").start()

        icon = pystray.Icon(
            "WorkflowLinkOrganizer",
            _make_icon(),
            APP_NAME,
            pystray.Menu(
                pystray.MenuItem("Open", self._open, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Restart", self._restart),
                pystray.MenuItem("Quit", self._quit),
            ),
        )
        icon.run()

        if self._restarting:
            _spawn_self()


def _spawn_self() -> None:
    """Restart the tray app as a fresh detached process."""
    import time
    time.sleep(0.3)  # let the daemon Waitress thread finish shutting down
    pyw = Path(sys.executable).parent / "pythonw.exe"
    exe = str(pyw) if pyw.exists() else sys.executable
    subprocess.Popen(
        [exe, "-m", "wlo.tray.tray_app"],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )


def main() -> None:
    TrayApp().run()


if __name__ == "__main__":
    main()


