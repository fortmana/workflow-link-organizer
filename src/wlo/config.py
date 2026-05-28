from pathlib import Path
import os

APP_NAME = os.environ.get("WLO_APP_NAME", "Workflow Link Organizer")
PORT = int(os.environ.get("WLO_PORT", "5757"))
HOST = "127.0.0.1"

_data_dir_name = os.environ.get("WLO_DATA_DIR_NAME", "WorkflowLinkOrganizer")
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / _data_dir_name
DB_PATH = DATA_DIR / "wlo.db"

# config.py lives at src/wlo/ - go up 3 levels to reach the repo root,
# where the migrations/ directory lives.
MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"

BROWSER_EXES = {
    "chrome": Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    "edge":   Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
}

BROWSER_USER_DATA = {
    "chrome": Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Google" / "Chrome" / "User Data",
    "edge":   Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Microsoft" / "Edge" / "User Data",
}

DEV = os.environ.get("WLO_DEV", "").lower() in ("1", "true", "yes")

