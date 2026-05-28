# Workflow Link Organizer - Instructions for Claude Code

You are helping a **non-technical user** set up and run this app. They likely do
not know Python, the terminal, or web servers. Be patient, explain in plain
language, never assume prior knowledge, and do the technical work for them. When
something fails, diagnose it and fix it yourself where possible - don't hand them
a stack trace.

This is a Windows desktop app: a small local web server (Flask + Waitress) with a
browser UI, run from a system-tray icon. It stores data in a local SQLite file.
There is no cloud, no account, and no network access beyond the user's own machine.

---

## When the user asks to "set it up" / "install it"

Do these steps in order. Report progress in plain language as you go.

### Step 1 - Confirm Python is installed and recent enough
Run:
```
python --version
```
- If it prints `Python 3.10` or higher: good, continue.
- If it prints a version below 3.10: tell them to update Python from
  https://www.python.org/downloads/ and continue once they have.
- If the command is not found: Python isn't installed or isn't on PATH. Tell
  them to install it from https://www.python.org/downloads/ **with the
  "Add python.exe to PATH" checkbox ticked**, then come back. If it's installed
  but not on PATH, offer to locate `python.exe` and use its full path.

### Step 2 - Run the setup script
From the project root:
```
powershell -ExecutionPolicy Bypass -File setup.ps1
```
This checks Python, installs dependencies (`pip install -e .`), and creates the
data folder. It's non-interactive and safe to re-run.

If it fails:
- **pip/network errors**: retry once; if it persists, run
  `python -m pip install -e .` directly and read the actual error.
- **"Access is denied" / permissions**: suggest running from a folder the user
  owns (e.g. under Documents), not Program Files.

### Step 3 - Start the app
From the project root:
```
.\Start.bat
```
This launches the tray app and opens the browser. The first launch can take a few
seconds.

### Step 4 - Verify it's actually running
```
curl http://127.0.0.1:5757/health
```
Expect `{"status": "ok", "port": 5757}`. If you get it, tell the user the app is
running and visible at **http://127.0.0.1:5757**. If not, wait a few seconds and
retry; then check Step 3's output for errors.

### Step 5 - Offer the next thing
Once it's running, offer to help them set up browser profiles (the feature that
makes this app valuable). See "Browser profiles" below.

---

## Customization (only if the user asks)

Defaults work with zero configuration. Change them with **User**-scope environment
variables, then restart the app (`.\Restart.bat`):

| Variable | Default | What it does |
|---|---|---|
| `WLO_PORT` | `5757` | Port the local server uses. Change if 5757 is taken. |
| `WLO_DATA_DIR_NAME` | `WorkflowLinkOrganizer` | Folder name under `%LOCALAPPDATA%` for the database. |
| `WLO_APP_NAME` | `Workflow Link Organizer` | Display name in the title bar and tray. |

Set one like this (example), then restart:
```
[System.Environment]::SetEnvironmentVariable("WLO_PORT", "5800", "User")
```
Note: a new value is picked up only by newly started terminals/processes.

**Port already in use?** If Step 4 fails and something else owns 5757, set
`WLO_PORT` to another value (e.g. 5800) and restart. Update the bookmark URL.

---

## Browser profiles (the key feature - help them set this up)

The app opens each link in a specific **browser profile**. Profiles keep separate
logins, cookies, and saved passwords - one per client/project/context. This is
what makes one click open a link already signed in to the right account.

To create a profile:
- **Chrome:** click the profile avatar (top-right), then **Add**, name it, done.
- **Edge:** click the profile avatar (top-right), then **Add profile**, name it, done.

After they create profiles, the app detects them automatically (they appear under
**Settings > Browser Profiles**). They can give each a friendly label there. If
none appear, confirm the profile was fully created (it opens its own window) and
reload the page.

---

## How the app is structured (for your reference)

```
workflow-link-organizer/
  setup.ps1                 # first-run setup (Python check, pip install, data dir)
  Start.bat / Stop.bat / Restart.bat
  pyproject.toml            # package metadata; entry points: wlo, wlo-dev
  migrations/001_initial_schema.sql
  src/wlo/
    app.py                  # Flask app factory (create_app)
    config.py               # PORT, DATA_DIR, browser paths - all WLO_* env-driven
    tray/tray_app.py        # system-tray launcher (the normal way it runs)
    db/                     # sqlite connection, migrations, config store
    models/bookmarks.py     # pydantic models
    sections/
      bookmarks/            # projects + links API and logic
      config/               # /api/config key-value settings
```

- Data lives at `%LOCALAPPDATA%\WorkflowLinkOrganizer\wlo.db`. Deleting it resets
  everything. Migrations apply automatically on every startup.
- Dev mode (auto-reload, console logs): set `WLO_DEV=1` and run `python -m wlo.app`
  from `src/`, or use the `wlo-dev` command after install.

---

## Common issues

| Symptom | Fix |
|---|---|
| `python` not recognized | Python not on PATH - reinstall with the PATH checkbox, or use the full path to python.exe. |
| Browser opens but page won't load | Server didn't start - re-run `.\Start.bat`, check for errors, verify with the `/health` curl. |
| Port 5757 in use | Set `WLO_PORT` to another value and `.\Restart.bat`. |
| No browser profiles listed | Create a named profile in Chrome/Edge first, then reload Settings. |
| Links open in the wrong account | The link/project is pointed at the wrong profile - fix it in the link's edit form or the project's default profile. |
| Want to move it to another PC | Copy the project folder, run `setup.ps1` there. To carry data, also copy `%LOCALAPPDATA%\WorkflowLinkOrganizer\wlo.db`. |
